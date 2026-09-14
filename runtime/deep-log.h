/* Optional diagnostics at the verified command-line stage; no device probing. */
typedef HRESULT (WINAPI *DeepSoundFn)(GUID*,void**,void*);
typedef HRESULT (WINAPI *DeepDrawFn)(GUID*,void**,const GUID*,void*);
typedef HMODULE (WINAPI *DeepLibraryFn)(LPCSTR);
typedef int (WINAPI *DeepMessageFn)(HWND,LPCSTR,LPCSTR,UINT);
static DeepSoundFn deep_sound_original;
static DeepDrawFn deep_draw_original;
static DeepLibraryFn deep_library_original;
static DeepMessageFn deep_message_original;
static Hook deep_hooks[4];
static volatile LONG deep_sequence,deep_exceptions;
static void deep_module(HMODULE module){
 char path[MAX_PATH],line[400];
 if(!module)return;
 if(!GetModuleFileNameA(module,path,sizeof(path)))strcpy(path,"<path unavailable>");
 snprintf(line,sizeof(line),"base=%p; path=%s",module,path);startup_write("MODULE",line,0);
}
static DWORD deep_begin(const char *api,const char *detail){
 DWORD id=(DWORD)InterlockedIncrement(&deep_sequence);char line[740];
 snprintf(line,sizeof(line),"%s; %.680s",api,detail?detail:"");startup_write("API BEGIN",line,id);return id;
}
static void deep_end(const char *api,DWORD id,DWORD start,DWORD result,DWORD error){
 char line[180];snprintf(line,sizeof(line),"%s; result=0x%08lx; lastError=%lu; duration_ms=%lu",api,result,error,GetTickCount()-start);startup_write("API END",line,id);
}
static void deep_guid(char *out,const GUID *guid){
 if(!guid){strcpy(out,"device=default");return;}
 snprintf(out,100,"device=%08lx-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x",guid->Data1,guid->Data2,guid->Data3,guid->Data4[0],guid->Data4[1],guid->Data4[2],guid->Data4[3],guid->Data4[4],guid->Data4[5],guid->Data4[6],guid->Data4[7]);
}
static HRESULT WINAPI deep_sound(GUID *guid,void **out,void *outer){
 DWORD saved=GetLastError(),id,start,error;HRESULT result;char detail[100];deep_guid(detail,guid);id=deep_begin("DirectSoundCreate",detail);start=GetTickCount();
 SetLastError(saved);result=deep_sound_original(guid,out,outer);error=GetLastError();deep_end("DirectSoundCreate HRESULT",id,start,(DWORD)result,error);SetLastError(error);return result;
}
static HRESULT WINAPI deep_draw(GUID *guid,void **out,const GUID *iid,void *outer){
 DWORD saved=GetLastError(),id,start,error;HRESULT result;char detail[100];deep_guid(detail,guid);id=deep_begin("DirectDrawCreateEx",detail);start=GetTickCount();
 SetLastError(saved);result=deep_draw_original(guid,out,iid,outer);error=GetLastError();deep_end("DirectDrawCreateEx HRESULT",id,start,(DWORD)result,error);SetLastError(error);return result;
}
static HMODULE WINAPI deep_library(LPCSTR name){
 DWORD saved=GetLastError(),id=deep_begin("LoadLibraryA",name),start=GetTickCount(),error;HMODULE result;
 SetLastError(saved);result=deep_library_original(name);error=GetLastError();deep_end("LoadLibraryA",id,start,(DWORD)result,error);deep_module(result);SetLastError(error);return result;
}
static int WINAPI deep_message(HWND window,LPCSTR text,LPCSTR title,UINT type){
 DWORD saved=GetLastError(),id,start,error;int result;char detail[700];
 snprintf(detail,sizeof(detail),"title=%.180s; text=%.480s",title?title:"",text?text:"");id=deep_begin("MessageBoxA",detail);start=GetTickCount();
 SetLastError(saved);result=deep_message_original(window,text,title,type);error=GetLastError();deep_end("MessageBoxA (duration includes user wait)",id,start,result,error);SetLastError(error);return result;
}
static LONG WINAPI deep_exception(EXCEPTION_POINTERS *p){
 DWORD saved=GetLastError(),code=p->ExceptionRecord->ExceptionCode;char line[180];
 /* First-chance observations are not proof of an unhandled crash. Never swallow
    an exception, walk the stack or block on another thread's logging lock. */
 if(code==0xc0000005||code==0xc000001d||code==0xc0000094||code==0xc0000096){
  if(InterlockedIncrement(&deep_exceptions)<=8&&TryEnterCriticalSection(&startup_lock)){
   snprintf(line,sizeof(line),"code=0x%08lx; address=%p; first chance, may be handled by application",code,p->ExceptionRecord->ExceptionAddress);
   startup_write("EXCEPTION OBSERVED",line,0);LeaveCriticalSection(&startup_lock);
  }
 }
 SetLastError(saved);return EXCEPTION_CONTINUE_SEARCH;
}
static void deep_environment(void){
 SYSTEM_INFO info;char line[300];int i;DISPLAY_DEVICEA display;OSVERSIONINFOW version;
 typedef LONG (WINAPI *VersionFn)(OSVERSIONINFOW*);VersionFn query;
 static const char *modules[]={"DINPUT.dll","DDRAW.dll","DSOUND.dll","D3D11.dll","DXGI.dll","WINMM.dll"};
 startup_write("ENVIRONMENT BEGIN","Reporting environment before optional CPU preference; graphics settings unchanged",0);
 query=(VersionFn)GetProcAddress(GetModuleHandleA("ntdll.dll"),"RtlGetVersion");memset(&version,0,sizeof(version));version.dwOSVersionInfoSize=sizeof(version);
 if(query&&query(&version)==0){snprintf(line,sizeof(line),"Windows %lu.%lu build %lu",version.dwMajorVersion,version.dwMinorVersion,version.dwBuildNumber);startup_write("OS APPLICATION VIEW",line,0);}
 {
  HKEY key;DWORD type,size;char value[128];const char *names[]={"CurrentBuildNumber","DisplayVersion","ProductName"};int k;
  if(RegOpenKeyExA(HKEY_LOCAL_MACHINE,"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",0,KEY_READ|0x100,&key)==ERROR_SUCCESS){
   for(k=0;k<3;k++){size=sizeof(value);memset(value,0,sizeof(value));if(RegQueryValueExA(key,names[k],NULL,&type,(BYTE*)value,&size)==ERROR_SUCCESS&&type==REG_SZ){value[127]=0;snprintf(line,sizeof(line),"%s=%s; registry metadata, not proof of active compatibility settings",names[k],value);startup_write("OS REGISTRY",line,0);}}
   RegCloseKey(key);
  }
 }
 GetSystemInfo(&info);snprintf(line,sizeof(line),"pid=%lu; process=32-bit; visible logical processors=%lu; processor mask=0x%lx",GetCurrentProcessId(),info.dwNumberOfProcessors,(DWORD)info.dwActiveProcessorMask);startup_write("SYSTEM",line,0);
 deep_module(GetModuleHandleA(NULL));for(i=0;i<sizeof(modules)/sizeof(modules[0]);i++)deep_module(GetModuleHandleA(modules[i]));
 startup_write("DISPLAY ENUM BEGIN","Windows display adapters; listing is not proof of selected render GPU",0);
 for(i=0;i<32;i++){
  memset(&display,0,sizeof(display));display.cb=sizeof(display);if(!EnumDisplayDevicesA(NULL,i,&display,0))break;
  snprintf(line,sizeof(line),"name=%.32s; description=%.128s; flags=0x%lx",display.DeviceName,display.DeviceString,display.StateFlags);startup_write("DISPLAY",line,i);
 }
 startup_write("ENVIRONMENT END","Records flushed individually. Last event/file is not a crash diagnosis; HRESULT is authoritative, LastError can be stale on success",0);
}
static void deep_prepare_slots(const U *slots){
 U targets[4],i;
 deep_sound_original=*(DeepSoundFn*)slots[0];deep_draw_original=*(DeepDrawFn*)slots[1];deep_library_original=*(DeepLibraryFn*)slots[2];deep_message_original=*(DeepMessageFn*)slots[3];
 targets[0]=(U)deep_sound;targets[1]=(U)deep_draw;targets[2]=(U)deep_library;targets[3]=(U)deep_message;
 for(i=0;i<4;i++){
  Hook *h=&deep_hooks[i];memset(h,0,sizeof(*h));h->address=slots[i];h->length=4;h->raw=1;
  memcpy(h->original,(void*)slots[i],4);memcpy(h->replacement,&targets[i],4);
 }
}
static int install_deep_hooks(void){
 static const U slots[]={0x84d9a8,0x84d944,0x84db68,0x84de90};
 typedef LONG (WINAPI *DeepHandlerFn)(EXCEPTION_POINTERS*);
 typedef void *(WINAPI *AddHandlerFn)(ULONG,DeepHandlerFn);AddHandlerFn add;
 deep_prepare_slots(slots);
 if(!prepare_hooks(deep_hooks,4)||!install_hooks(deep_hooks,4))return 0;
 add=(AddHandlerFn)GetProcAddress(GetModuleHandleA("kernel32.dll"),"AddVectoredExceptionHandler");
 startup_write("EXCEPTION OBSERVER",add&&add(0,deep_exception)?"Installed; selected first-chance exceptions only":"Unavailable",0);
 return 1;
}
