/* MIT. Startup-only MPEG driver selection and input restoration.
   No artificial Alt-Tab, focus stealing, external player or polling. */
#ifndef MOVIE_ADDR
#define MOVIE_ADDR(a) (a)
#endif
static Hook movie_hooks[4];
static U (__fastcall *movie_original)(const char*,U)=(void*)0x52fc32;
static U (__fastcall *movie_original_open)(HWND,const char*)=(void*)0x52ffb3;
static HWND (WINAPI *movie_foreground)(void)=GetForegroundWindow;
static HWND (WINAPI *movie_get_focus)(void)=GetFocus;
static HWND (WINAPI *movie_set_focus)(HWND)=SetFocus;
static LRESULT (WINAPI *movie_send)(HWND,UINT,WPARAM,LPARAM)=SendMessageA;
static BOOL (WINAPI *movie_valid)(HWND)=IsWindow;
static BOOL (WINAPI *movie_enabled)(HWND)=IsWindowEnabled;
static BOOL (WINAPI *movie_iconic)(HWND)=IsIconic;
/* Movie diagnostics may occur after the main startup log has closed. Append
   bounded records to that same existing file; never rotate away its evidence. */
static void movie_log(const char *phase,U value){
 WCHAR path[MAX_PATH];HANDLE file;DWORD size,written,error=GetLastError();char line[160];int n;
 if(!startup_log||!startup_lock_ready)return;
 EnterCriticalSection(&startup_lock);
 if(startup_file!=INVALID_HANDLE_VALUE)startup_write("MOVIE",phase,value);
 else{
  startup_log_name(path,0);file=CreateFileW(path,FILE_APPEND_DATA|GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
  if(file!=INVALID_HANDLE_VALUE){
   size=GetFileSize(file,NULL);n=snprintf(line,sizeof(line),"%lu ms | MOVIE | %u | %s\r\n",GetTickCount()-startup_started,value,phase);
   if(size!=INVALID_FILE_SIZE&&n>0&&n<sizeof(line)&&size<=max_log_bytes&&(DWORD)n<=max_log_bytes-size)WriteFile(file,line,n,&written,NULL);
   CloseHandle(file);
  }
 }
 LeaveCriticalSection(&startup_lock);SetLastError(error);
}
static U (__fastcall *movie_get_option_original)(const WCHAR*,U*,U)=(void*)0x403247;
static U __fastcall movie_get_option(const WCHAR *name,U *value,U scope){
 U result=movie_get_option_original(name,value,scope);
 movie_log("ShowLogo preference (0 means movie disabled)",value?*value:0);return result;
}
#include "movie-window.h"
static U __fastcall movie_open(HWND window,const char *path){
 char file[MAX_PATH+16];size_t length;U result;
 movie_log("OPEN entered",0);
 if(!system_movie_decoder||!path){result=movie_original_open(window,path);movie_log("Original decoder open result",result);return result;}
 length=strlen(path);
 if(length>=4&&!lstrcmpiA(path+length-4,".mpg")&&length<MAX_PATH){
  strcpy(file,"mpegvideo!");strcat(file,path);
  result=movie_send(window,0x499,0,(LPARAM)file);movie_log("System decoder open error (0 means success)",result);
  if(!result)return 1; /* MCIWNDM_OPENA */
  /* The original fallback uses a 260-byte stack buffer plus its prefix. */
  if(length>240)return 0;
 }
 result=movie_original_open(window,path);movie_log("Fallback decoder open result",result);return result;
}
static void movie_restore_focus(HWND main){
 if(!main||!movie_valid(main)||movie_foreground()!=main||!movie_enabled(main)||movie_iconic(main))return;
 if(movie_get_focus()!=main)movie_set_focus(main);
 /* Movie WndProc swallows WM_ACTIVATEAPP. Replay only the current foreground
    state after the original WndProc has been restored, using its normal chain. */
 movie_send(main,WM_ACTIVATEAPP,TRUE,GetCurrentThreadId());
}
static U __fastcall movie_play(const char *path,U edx){
 U result;movie_log("PLAY entered",0);movie_window=NULL;result=movie_original(path,edx);movie_window=NULL;
 movie_log("PLAY returned; saved movie procedure",*(U*)MOVIE_ADDR(0x7c2d90));
 /* Do not send input messages into a still-installed movie procedure on a
    playback failure. The normal success/skip path clears this saved pointer. */
 if(restore_movie_focus&&!*(U*)MOVIE_ADDR(0x7c2d90))movie_restore_focus(*(HWND*)MOVIE_ADDR(0x82813a));
 return result;
}
static int install_movie_hook(void){
 if(!restore_movie_focus&&!system_movie_decoder&&!separate_movie_window)return 1;
 if(memcmp((void*)0x52fc32,"\x55\x8b\xec\x81\xec\x68\x01\x00\x00",9)||
    memcmp((void*)0x52ffb3,"\x55\x8b\xec",3))return 0;
 startup_call(&movie_hooks[0],0x52fc29,0x52fc32,(U)movie_play);
 startup_call(&movie_hooks[1],0x52fd4a,0x52ffb3,(U)movie_open);
 startup_call(&movie_hooks[2],0x52fe51,0,(U)movie_show);
 movie_hooks[2].length=6;memcpy(movie_hooks[2].original,"\xff\x15\x40\xdf\x84\x00",6);movie_hooks[2].replacement[5]=0x90;
 startup_call(&movie_hooks[3],0x52fbbe,0x403247,(U)movie_get_option);
 return prepare_hooks(movie_hooks,4)&&install_hooks(movie_hooks,4);
}
