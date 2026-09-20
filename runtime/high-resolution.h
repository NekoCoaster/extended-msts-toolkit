/* Limit-removal idea adapted from UCyborg's LegacyD3DResolutionHack (MIT-0).
 * See docs/licenses/LegacyD3DResolutionHack.txt. Called outside loader lock.
 * Restrict edits to paired dimension checks inside executable PE sections. */
static const char *high_resolution_state="disabled";
static HMODULE high_resolution_module;
static int highres_pair(const B *p,U available,int *patched){
 int a,b;U jump1,jump2;int len;
 if(available<23 || p[0]!=0xb8)return 0;
 if(memcmp(p+1,"\x00\x08\x00\x00",4) && memcmp(p+1,"\xff\xff\xff\xff",4))return 0;
 if(p[5]!=0x39)return 0;
 if(p[6]==0x45){a=(signed char)p[7];len=3;}
 else if(p[6]==0x85 && available>=29){memcpy(&a,p+7,4);len=6;}
 else return 0;
 jump1=5+len;
 if(p[jump1]!=0x0f || p[jump1+1]!=0x87)return 0;
 if(p[jump1+6]!=0x39 || p[jump1+7]!=p[6])return 0;
 if(len==3)b=(signed char)p[jump1+8];else memcpy(&b,p+jump1+8,4);
 if(a< -4096 || a> -4 || b!=a-4)return 0;
 jump2=jump1+6+len;
 if(p[jump2]!=0x0f || p[jump2+1]!=0x87)return 0;
 {int d1,d2;memcpy(&d1,p+jump1+2,4);memcpy(&d2,p+jump2+2,4);
  /* Both unsigned checks must branch to the same forward failure block. */
  if(d1<0 || d2<0 || (U)d1>=available-jump1-6 || (U)d2>=available-jump2-6 || jump1+6+d1!=jump2+6+d2)return 0;}
 *patched=p[1]==0xff;return 1;
}
static int highres_plan(B *base,U size,Hook *patches,U *count,int *already){
 IMAGE_DOS_HEADER dos;IMAGE_NT_HEADERS nt;IMAGE_SECTION_HEADER section;U i,j,table;B *copy;
 *count=0;*already=0;
 if(size<sizeof(dos)||!read_memory((U)base,&dos,sizeof(dos))||dos.e_magic!=IMAGE_DOS_SIGNATURE||dos.e_lfanew<0)return 0;
 if((U)dos.e_lfanew>size-sizeof(nt)||!read_memory((U)base+dos.e_lfanew,&nt,sizeof(nt)))return 0;
 if(nt.Signature!=IMAGE_NT_SIGNATURE||nt.FileHeader.Machine!=IMAGE_FILE_MACHINE_I386||nt.OptionalHeader.Magic!=0x10b ||
  nt.OptionalHeader.SizeOfImage!=size || nt.FileHeader.SizeOfOptionalHeader!=sizeof(nt.OptionalHeader) ||
  !nt.FileHeader.NumberOfSections || nt.FileHeader.NumberOfSections>32)return 0;
 table=dos.e_lfanew+4+sizeof(IMAGE_FILE_HEADER)+nt.FileHeader.SizeOfOptionalHeader;
 if(table>size || nt.FileHeader.NumberOfSections>(size-table)/sizeof(section))return 0;
 for(i=0;i<nt.FileHeader.NumberOfSections;i++){
  if(!read_memory((U)base+table+i*sizeof(section),&section,sizeof(section)))return 0;
  if(!(section.Characteristics&IMAGE_SCN_MEM_EXECUTE))continue;
  if(section.VirtualAddress>=size || section.Misc.VirtualSize>size-section.VirtualAddress || !section.Misc.VirtualSize)return 0;
  copy=HeapAlloc(GetProcessHeap(),0,section.Misc.VirtualSize);if(!copy)return 0;
  if(!read_memory((U)base+section.VirtualAddress,copy,section.Misc.VirtualSize)){HeapFree(GetProcessHeap(),0,copy);return 0;}
  for(j=0;j+6<=section.Misc.VirtualSize;j++){
   int patched=0;
   /* An unrecognized 2048 comparison makes the entire plan ambiguous. */
   if(copy[j]!=0xb8 || copy[j+5]!=0x39 ||
    (memcmp(copy+j+1,"\x00\x08\x00\x00",4)&&memcmp(copy+j+1,"\xff\xff\xff\xff",4)))continue;
   if(!highres_pair(copy+j,section.Misc.VirtualSize-j,&patched) || *count+*already>=8){HeapFree(GetProcessHeap(),0,copy);return 0;}
   if(patched)(*already)++;
   else {Hook *h=&patches[(*count)++];memset(h,0,sizeof(*h));h->address=(U)base+section.VirtualAddress+j;h->length=5;h->raw=1;
    memcpy(h->original,copy+j,5);memcpy(h->replacement,"\xb8\xff\xff\xff\xff",5);}
  }HeapFree(GetProcessHeap(),0,copy);
 }return *count+*already>0;
}
static int highres_external(void){
 const WCHAR *names[]={L"D3DIM700.dll",L"ddraw.dll"};WCHAR path[MAX_PATH],system[MAX_PATH];int i;DWORD n;
 for(i=0;i<2;i++){
  if(wcslen(root)+wcslen(names[i])>=MAX_PATH)return 1;
  wcscpy(path,root);wcscat(path,names[i]);
  if(GetFileAttributesW(path)!=INVALID_FILE_ATTRIBUTES)return 1;
  {HMODULE module=GetModuleHandleW(names[i]);if(!module)continue;
   n=GetSystemDirectoryW(system,MAX_PATH);if(!n||n+1+wcslen(names[i])>=MAX_PATH)return 1;
   wcscat(system,L"\\");wcscat(system,names[i]);
   n=GetModuleFileNameW(module,path,MAX_PATH);if(!n||n>=MAX_PATH||lstrcmpiW(path,system))return 1;}
 }return 0;
}
static int apply_high_resolution(void){
 WCHAR path[MAX_PATH],loaded[MAX_PATH];DWORD n,saved=GetLastError();IMAGE_DOS_HEADER dos;IMAGE_NT_HEADERS nt;
 Hook patches[8];U count;int already,ok=0;
 if(!high_resolution){high_resolution_state="disabled";return 1;}
 if(highres_external()){high_resolution_state="external graphics DLL present; compatibility unverified; NEMT stood down";ok=1;goto done;}
 n=GetSystemDirectoryW(path,MAX_PATH);if(!n || n+14>=MAX_PATH)goto failed;
 wcscat(path,L"\\d3dim700.dll");
 /* Retain a reference for process lifetime so patched code cannot unload. */
 high_resolution_module=LoadLibraryW(path);if(!high_resolution_module)goto failed;
 n=GetModuleFileNameW(high_resolution_module,loaded,MAX_PATH);
 if(!n||n>=MAX_PATH||lstrcmpiW(path,loaded))goto failed;
 if(!read_memory((U)high_resolution_module,&dos,sizeof(dos))||dos.e_magic!=IMAGE_DOS_SIGNATURE||dos.e_lfanew<0||dos.e_lfanew>1048576)goto failed;
 if(!read_memory((U)high_resolution_module+dos.e_lfanew,&nt,sizeof(nt))||nt.OptionalHeader.SizeOfImage>16777216)goto failed;
 if(!highres_plan((B*)high_resolution_module,nt.OptionalHeader.SizeOfImage,patches,&count,&already))goto failed;
 if(count && (!prepare_hooks(patches,count)||!install_hooks(patches,count)))goto failed;
 high_resolution_state=count?"enabled: system Direct3D dimension limits removed in memory":"already patched: no changes needed";ok=1;goto done;
failed:high_resolution_state="unavailable: unrecognized or inaccessible Direct3D; no compatibility fix installed";
done:startup_write("HIGH RESOLUTION",high_resolution_state,0);SetLastError(saved);return ok;
}
