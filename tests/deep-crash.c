/* Child deliberately terminates without closing the logger; parent verifies tail. */
#include <assert.h>
#include "../runtime/loader.c"
static LONG WINAPI terminate_unhandled(EXCEPTION_POINTERS *p){TerminateProcess(GetCurrentProcess(),77);return EXCEPTION_CONTINUE_SEARCH;}
int main(int argc,char **argv){
 char command[1000],data[4096]={0};WCHAR path[MAX_PATH];DWORD n,exit_code;HANDLE file;STARTUPINFOA si;PROCESS_INFORMATION pi;
 assert(argc>=2);mbstowcs(runtime_dir,argv[1],MAX_PATH);wcscat(runtime_dir,L"\\");
 if(argc==3){
  InitializeCriticalSection(&startup_lock);startup_lock_ready=1;max_log_bytes=65536;CreateDirectoryW(runtime_dir,NULL);assert(startup_open_log());
  startup_write("API BEGIN","unfinished-operation-marker",1);
  startup_write("TAIL","last-record-before-abrupt-termination",2);
  if(!strcmp(argv[2],"exception")){
   typedef LONG (WINAPI *HandlerFn)(EXCEPTION_POINTERS*);
   typedef void *(WINAPI *AddFn)(ULONG,HandlerFn);
   AddFn add=(AddFn)GetProcAddress(GetModuleHandleA("kernel32.dll"),"AddVectoredExceptionHandler");
   assert(add&&add(1,deep_exception));SetUnhandledExceptionFilter(terminate_unhandled);
   RaiseException(0xc0000005,0,0,NULL);
  }
  TerminateProcess(GetCurrentProcess(),77);return 1;
 }
 memset(&si,0,sizeof(si));memset(&pi,0,sizeof(pi));si.cb=sizeof(si);snprintf(command,sizeof(command),"\"%s\" \"%s\" %s",argv[0],argv[1],argc==4?"exception":"terminate");
 assert(CreateProcessA(NULL,command,NULL,NULL,FALSE,CREATE_NO_WINDOW,NULL,NULL,&si,&pi));assert(WaitForSingleObject(pi.hProcess,15000)==WAIT_OBJECT_0);assert(GetExitCodeProcess(pi.hProcess,&exit_code)&&exit_code==77);CloseHandle(pi.hThread);CloseHandle(pi.hProcess);
 startup_log_name(path,0);file=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);assert(file!=INVALID_HANDLE_VALUE);assert(ReadFile(file,data,sizeof(data)-1,&n,NULL));CloseHandle(file);
 assert(strstr(data,"unfinished-operation-marker")&&strstr(data,"last-record-before-abrupt-termination"));
 if(argc==4)assert(strstr(data,"EXCEPTION OBSERVED"));
 puts("PASS log tail persists after child termination without logger close or normal process cleanup.");return 0;
}
