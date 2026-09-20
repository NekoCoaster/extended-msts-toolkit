/* Only the system DirectInput import is adjusted; no synthetic input or game results. */
static int (WINAPI *mouse_real_metrics)(int)=GetSystemMetrics;
static LONG *mouse_metric_slot;
static int WINAPI mouse_compatible_metrics(int index){
 int value=mouse_real_metrics(index);DWORD error=GetLastError();
 if(!value && (index==SM_MOUSEPRESENT ||
    (index==SM_CMOUSEBUTTONS && !mouse_real_metrics(SM_MOUSEPRESENT))))
  value=index==SM_MOUSEPRESENT?1:3;
 SetLastError(error);return value;
}
static int mouse_image_read(BYTE *base,DWORD size,DWORD offset,void *out,DWORD length){
 return offset<=size && length<=size-offset && read_memory((DWORD)base+offset,out,length);
}
static int mouse_image_name(BYTE *base,DWORD size,DWORD offset,const char *name){
 char value[32];DWORD length=lstrlenA(name)+1;
 return length<=sizeof(value)&&mouse_image_read(base,size,offset,value,length)&&!lstrcmpiA(value,name);
}
static LONG *mouse_find_import(HMODULE module){
 BYTE *base=(BYTE*)module;IMAGE_DOS_HEADER dos;IMAGE_NT_HEADERS32 nt;
 IMAGE_IMPORT_DESCRIPTOR desc;DWORD size,start,length,i,j,name,slot;LONG *found=NULL;
 if(!read_memory((DWORD)base,&dos,sizeof(dos))||dos.e_magic!=IMAGE_DOS_SIGNATURE||dos.e_lfanew<0||dos.e_lfanew>0x100000)return NULL;
 if(!read_memory((DWORD)base+dos.e_lfanew,&nt,sizeof(nt))||nt.Signature!=IMAGE_NT_SIGNATURE||
    nt.FileHeader.Machine!=IMAGE_FILE_MACHINE_I386||nt.OptionalHeader.Magic!=IMAGE_NT_OPTIONAL_HDR32_MAGIC||
    nt.OptionalHeader.NumberOfRvaAndSizes<=IMAGE_DIRECTORY_ENTRY_IMPORT)return NULL;
 size=nt.OptionalHeader.SizeOfImage;if(size>0x10000000)return NULL;
 start=nt.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress;
 length=nt.OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].Size;
 if(!start||start>size||length>size-start)return NULL;
 for(i=0;i+sizeof(desc)<=length;i+=sizeof(desc)){
  if(!mouse_image_read(base,size,start+i,&desc,sizeof(desc)))return NULL;
  if(!desc.Name)return found;
  if(!mouse_image_name(base,size,desc.Name,"USER32.dll"))continue;
  if(!desc.OriginalFirstThunk||!desc.FirstThunk||desc.OriginalFirstThunk>size||desc.FirstThunk>size)return NULL;
  for(j=0;j<size-desc.OriginalFirstThunk;j+=4){
   if(!mouse_image_read(base,size,desc.OriginalFirstThunk+j,&name,4))return NULL;
   if(!name)break;
   if(name&IMAGE_ORDINAL_FLAG32)continue;
   if(name>size||size-name<2)return NULL;
   if(!mouse_image_name(base,size,name+2,"GetSystemMetrics"))continue;
   if(j>size-desc.FirstThunk||!mouse_image_read(base,size,desc.FirstThunk+j,&slot,4))return NULL;
   if(found||slot!=(DWORD)GetProcAddress(GetModuleHandleA("user32.dll"),"GetSystemMetrics")||((DWORD)base+desc.FirstThunk+j)%4)return NULL;
   found=(LONG*)(base+desc.FirstThunk+j);
  }
 }
 return NULL; /* Require a terminated descriptor table. */
}
/* Aligned atomic exchange leaves concurrent callers with either complete pointer. */
static int mouse_exchange(LONG *slot,LONG expected,LONG replacement){
 DWORD protection,unused;LONG previous;
 if(!VirtualProtect(slot,4,PAGE_READWRITE,&protection))return 0;
 previous=InterlockedCompareExchange(slot,replacement,expected);
 if(!VirtualProtect(slot,4,protection,&unused)){
  if(previous==expected)InterlockedCompareExchange(slot,expected,replacement);
  VirtualProtect(slot,4,protection,&unused);return 0;
 }
 return previous==expected;
}
static int restore_mouse_compatibility(void){
 if(!mouse_metric_slot)return 1;
 if(!mouse_exchange(mouse_metric_slot,(LONG)mouse_compatible_metrics,(LONG)mouse_real_metrics))return 0;
 mouse_metric_slot=NULL;return 1;
}
static int install_mouse_compatibility(void){
 WCHAR path[MAX_PATH],actual[MAX_PATH];UINT length;HMODULE module,pinned;LONG *slot;
 HANDLE requested,loaded;BY_HANDLE_FILE_INFORMATION a,b;int same;
 if(mouse_metric_slot)return 1;
 length=GetSystemDirectoryW(path,MAX_PATH);
 if(!length||length+12>=MAX_PATH)return 0;
 wcscat(path,L"\\dinput.dll");module=LoadLibraryW(path);if(!module)return 0;
 length=GetModuleFileNameW(module,actual,MAX_PATH);
 if(!length||length>=MAX_PATH){FreeLibrary(module);return 0;}
 /* WOW64 may spell the loaded system path differently. Compare file identity. */
 requested=CreateFileW(path,0,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,NULL,OPEN_EXISTING,0,NULL);
 loaded=CreateFileW(actual,0,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,NULL,OPEN_EXISTING,0,NULL);
 same=requested!=INVALID_HANDLE_VALUE&&loaded!=INVALID_HANDLE_VALUE&&
  GetFileInformationByHandle(requested,&a)&&GetFileInformationByHandle(loaded,&b)&&
  a.dwVolumeSerialNumber==b.dwVolumeSerialNumber&&a.nFileIndexHigh==b.nFileIndexHigh&&a.nFileIndexLow==b.nFileIndexLow;
 if(requested!=INVALID_HANDLE_VALUE)CloseHandle(requested);
 if(loaded!=INVALID_HANDLE_VALUE)CloseHandle(loaded);
 if(!same){FreeLibrary(module);return 0;}
 mouse_real_metrics=(void*)GetProcAddress(GetModuleHandleA("user32.dll"),"GetSystemMetrics");
 slot=mouse_find_import(module);
 if(!slot||!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,
   (LPCSTR)mouse_compatible_metrics,&pinned)){FreeLibrary(module);return 0;}
 if(!mouse_exchange(slot,(LONG)mouse_real_metrics,(LONG)mouse_compatible_metrics)){FreeLibrary(module);return 0;}
 mouse_metric_slot=slot; /* Retain system module and callback for process lifetime. */
 return 1;
}
static int apply_mouse_compatibility(void){
 int ok;DWORD error=GetLastError();
 if(mouse_real_metrics(SM_MOUSEPRESENT)){
  startup_write("MOUSE COMPATIBILITY","physical mouse reported; unchanged",0);ok=1;
 }else{
  ok=install_mouse_compatibility();
  startup_write("MOUSE COMPATIBILITY",ok?"enabled: system DirectInput mouse detection only":"unavailable: original DirectInput behavior retained",0);
 }
 SetLastError(error);return ok;
}
