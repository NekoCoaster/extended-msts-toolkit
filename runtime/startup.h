/* MIT. Startup/activity diagnostics and native loading-text substitution. */
__declspec(dllimport) int WINAPI MultiByteToWideChar(UINT,DWORD,LPCSTR,int,LPWSTR,int);
#include "terrain.h"
typedef HANDLE (WINAPI *StartupOpenFn)(LPCSTR,DWORD,DWORD,LPSECURITY_ATTRIBUTES,DWORD,DWORD,HANDLE);
typedef HANDLE (WINAPI *StartupFindFn)(LPCSTR,LPWIN32_FIND_DATAA);
typedef WCHAR *(__fastcall *StartupStringFn)(U);
static StartupOpenFn startup_open_original;
static StartupFindFn startup_find_original;
static StartupStringFn startup_string_original=(StartupStringFn)0x402590;
static void (*startup_first_frame_original)(void)=(void*)0x6ad020;
static CRITICAL_SECTION startup_lock;
static int startup_lock_ready;
static volatile LONG startup_active;
static HANDLE startup_file=INVALID_HANDLE_VALUE;
static DWORD startup_bytes,startup_started,startup_sequence,startup_display_updates;
static WCHAR startup_text[96]=L"Loading: initializing MSTS";
static WCHAR startup_draw_text[96];
static Hook startup_hooks[13];
static U (__fastcall *loading_begin_original)(U)=(void*)0x401c53;
static void (*loading_end_original)(void)=(void*)0x4014d3;
static int activity_loading;
#include "startup-log.h"
static void startup_write(const char *operation,const char *name,DWORD number){
 char line[1024],clean[701];DWORD written,saved=GetLastError();int n;unsigned int i;SYSTEMTIME t;
 if(startup_lock_ready)EnterCriticalSection(&startup_lock);
 if(startup_file==INVALID_HANDLE_VALUE)goto done;
 for(i=0;name&&name[i]&&i<sizeof(clean)-1;i++)clean[i]=(unsigned char)name[i]<32?' ':name[i];clean[i]=0;
 GetLocalTime(&t);
 n=snprintf(line,sizeof(line),"%04u-%02u-%02u %02u-%02u-%02u.%03u: %s | id=%lu | tid=%lu | %.700s\r\n",t.wYear,t.wMonth,t.wDay,t.wHour,t.wMinute,t.wSecond,t.wMilliseconds,operation,number,GetCurrentThreadId(),clean);
 if(n<=0||n>=sizeof(line))goto done;
 if(startup_bytes+(DWORD)n>max_log_bytes&&!startup_open_log())goto done;
 if(!WriteFile(startup_file,line,n,&written,NULL)||written!=(DWORD)n){CloseHandle(startup_file);startup_file=INVALID_HANDLE_VALUE;goto done;}
 startup_bytes+=written;
 /* Debug-only cost: complete each record and request persistence before the
    intercepted operation proceeds. No user-space log queue survives a crash. */
 if(!FlushFileBuffers(startup_file)){CloseHandle(startup_file);startup_file=INVALID_HANDLE_VALUE;}
 done:if(startup_lock_ready)LeaveCriticalSection(&startup_lock);SetLastError(saved);
}
static DWORD startup_record(const char *operation,const char *path){
 char clean[700],short_path[64];DWORD id;unsigned int i,n;
 EnterCriticalSection(&startup_lock);
 if(!startup_active){LeaveCriticalSection(&startup_lock);return 0;}
 for(i=0;path&&path[i]&&i<sizeof(clean)-1;i++)clean[i]=(unsigned char)path[i]<32?' ':path[i];clean[i]=0;
 n=strlen(clean);if(n>54){strcpy(short_path,"...");strcpy(short_path+3,clean+n-54);}else strcpy(short_path,clean);
 if(verbose_loading){WCHAR wide[64];wide[0]=0;MultiByteToWideChar(0,0,short_path,-1,wide,64);wcscpy(startup_text,!strcmp(operation,"OPEN")?L"Reading: ":L"Scanning: ");wcscat(startup_text,wide);}
 id=++startup_sequence;startup_write(operation,clean,id);LeaveCriticalSection(&startup_lock);return id;
}
static void startup_result(DWORD id,HANDLE handle,DWORD error){
 if(!id)return;EnterCriticalSection(&startup_lock);
 if(startup_active){char detail[96];snprintf(detail,sizeof(detail),"operation=%lu; Win32 error=%lu%s",id,handle==INVALID_HANDLE_VALUE?error:0,handle==INVALID_HANDLE_VALUE?"; optional checks can fail normally":"");startup_write(handle==INVALID_HANDLE_VALUE?"FAILED":"OPENED",detail,id);}
 LeaveCriticalSection(&startup_lock);
}
static HANDLE WINAPI startup_open(LPCSTR name,DWORD access,DWORD share,LPSECURITY_ATTRIBUTES security,DWORD disposition,DWORD flags,HANDLE template){
 DWORD before=GetLastError(),id=0,error;HANDLE h;
 if(startup_active)id=startup_record("OPEN",name);
 SetLastError(before);h=startup_open_original(name,access,share,security,disposition,flags,template);error=GetLastError();
 if(id)startup_result(id,h,error);SetLastError(error);return h;
}
static HANDLE WINAPI startup_find(LPCSTR name,LPWIN32_FIND_DATAA data){
 DWORD before=GetLastError(),id=0,error;HANDLE h;
 if(startup_active)id=startup_record("SCAN",name);
 SetLastError(before);h=startup_find_original(name,data);error=GetLastError();
 if(id)startup_result(id,h,error);SetLastError(error);return h;
}
static WCHAR *__fastcall startup_loading_string(U resource){
 if(!startup_active||!verbose_loading)return startup_string_original(resource);
 EnterCriticalSection(&startup_lock);
 if(resource==53&&terrain_active){char text[96];terrain_format(text,sizeof(text),terrain_percent,GetTickCount()-terrain_started,terrain_updates);MultiByteToWideChar(0,0,text,-1,startup_draw_text,96);}
 else wcscpy(startup_draw_text,startup_text);
 startup_display_updates++;LeaveCriticalSection(&startup_lock);return startup_draw_text;
}
static U __fastcall loading_begin(U mode){
 U result;
 if(verbose_loading||startup_log){EnterCriticalSection(&startup_lock);activity_loading=1;startup_active=1;startup_write("ACTIVITY BEGIN","Selected activity loading",mode);terrain_active=0;wcscpy(startup_text,L"Preparing selected activity...");LeaveCriticalSection(&startup_lock);}
 result=loading_begin_original(mode);
 if(!result&&(verbose_loading||startup_log)){EnterCriticalSection(&startup_lock);startup_write("ACTIVITY FAILED","Native load returned zero",mode);activity_loading=0;startup_active=0;LeaveCriticalSection(&startup_lock);}
 return result;
}
static void loading_end(void){
 if(activity_loading){EnterCriticalSection(&startup_lock);startup_write("ACTIVITY COMPLETE","Native loading end reached",startup_sequence);startup_active=0;activity_loading=0;LeaveCriticalSection(&startup_lock);}
 loading_end_original();
}
static void startup_finish(void){
 if(!startup_active)return;EnterCriticalSection(&startup_lock);
 if(startup_active){startup_write("DISPLAY UPDATES","Native loading text substitutions",startup_display_updates);startup_write("STARTUP COMPLETE","Main event loop reached",startup_sequence);startup_active=0;}
 LeaveCriticalSection(&startup_lock);
}
static void (*loading_assets_original)(void)=(void*)0x401357;
static void loading_assets(void){
 if(verbose_loading&&startup_active){EnterCriticalSection(&startup_lock);terrain_active=0;wcscpy(startup_text,L"Preparing route assets...");LeaveCriticalSection(&startup_lock);terrain_progress_original(308,0);}
 loading_assets_original();
}
static void startup_first_frame(void){startup_finish();startup_first_frame_original();}
static void startup_call(Hook *h,U address,U target,U replacement){
 U relative=target-address-5,new_relative=replacement-address-5;
 memset(h,0,sizeof(*h));h->address=address;h->length=5;h->raw=1;h->original[0]=h->replacement[0]=0xe8;
 memcpy(h->original+1,&relative,4);memcpy(h->replacement+1,&new_relative,4);
}
#include "deep-log.h"
static int install_startup_hooks(void){
 U i;WCHAR path[MAX_PATH];static const U slots[]={0x84db34,0x84dc98};U targets[2];
 if(!verbose_loading&&!startup_log)return 1;
 startup_open_original=*(StartupOpenFn*)slots[0];startup_find_original=*(StartupFindFn*)slots[1];targets[0]=(U)startup_open;targets[1]=(U)startup_find;
 for(i=0;i<2;i++){Hook *h=&startup_hooks[i];h->address=slots[i];h->length=4;h->raw=1;memcpy(h->original,(void*)slots[i],4);memcpy(h->replacement,&targets[i],4);}
 startup_call(&startup_hooks[2],0x44cceb,0x402590,(U)startup_loading_string);
 startup_call(&startup_hooks[3],0x44cd0d,0x402590,(U)startup_loading_string);
 startup_call(&startup_hooks[4],0x6ba175,0x6ad020,(U)startup_first_frame);
 startup_call(&startup_hooks[5],0x490e1d,0x401c53,(U)loading_begin);
 startup_call(&startup_hooks[6],0x49105d,0x4014d3,(U)loading_end);
 startup_call(&startup_hooks[7],0x4900e7,0x4014d3,(U)loading_end);
 startup_call(&startup_hooks[8],0x566cc2,0x4023e2,(U)terrain_begin);
 startup_call(&startup_hooks[9],0x566d21,0x4023e2,(U)terrain_progress);
 for(i=10;i<12;i++){Hook *h=&startup_hooks[i];memset(h,0,sizeof(*h));h->address=i==10?0x566cbd:0x566d1c;h->length=5;h->raw=1;memcpy(h->original,"\xb9\x35\0\0\0",5);memcpy(h->replacement,i==10?"\x8b\x4d\xdc\x90\x90":"\x8b\x4d\xfc\x90\x90",5);}
 startup_call(&startup_hooks[12],0x494bc1,0x401357,(U)loading_assets);
 InitializeCriticalSection(&startup_lock);startup_lock_ready=1;startup_started=GetTickCount();startup_active=1;
 if(!prepare_hooks(startup_hooks,13)||!install_hooks(startup_hooks,13)){startup_active=0;return 0;}
 if(startup_log&&startup_open_log()){startup_write("STARTUP BEGIN","Deep logging; local wall time; durations use monotonic milliseconds. Paths use Windows ANSI encoding.",0);deep_environment();if(!install_deep_hooks())startup_write("DIAGNOSTICS UNAVAILABLE","Optional initialization hooks could not be installed",0);}
 return 1;
}
