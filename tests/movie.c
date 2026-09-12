#include <assert.h>
static unsigned char movie_globals[0x80000];
#define MOVIE_ADDR(a) ((unsigned int)movie_globals+(a)-0x7c0000)
#include "../runtime/loader.c"
static HWND main_window_test=(HWND)123,foreground_test,focus_test;
static int valid=1,enabled=1,iconic=0,focused,sent,played;
static HWND WINAPI foreground(void){return foreground_test;}
static HWND WINAPI get_focus(void){return focus_test;}
static HWND WINAPI set_focus(HWND h){assert(h==main_window_test);focused++;focus_test=h;return NULL;}
static BOOL WINAPI is_valid(HWND h){return valid;}
static BOOL WINAPI is_enabled(HWND h){return enabled;}
static BOOL WINAPI is_iconic(HWND h){return iconic;}
static LRESULT WINAPI send(HWND h,UINT m,WPARAM w,LPARAM l){
 assert(h==main_window_test);
 assert(m==WM_ACTIVATEAPP&&w==TRUE&&l==GetCurrentThreadId());assert(focus_test==main_window_test);sent++;return 0;
}
static U __fastcall play(const char *path,U edx){assert(!strcmp(path,"startup.mpg")&&edx==7);played++;return 42;}
static U __fastcall option(const WCHAR *name,U *value,U scope){assert(scope==7);*value=1;return 99;}
int main(void){
 U preference=1;movie_get_option_original=option;assert(movie_get_option(L"ShowLogo",&preference,7)==99&&preference==1);
 skip_startup_movie=1;assert(movie_get_option(L"ShowLogo",&preference,7)==99&&preference==0);
 skip_startup_movie=0;assert(movie_get_option(L"ShowLogo",&preference,7)==99&&preference==1);
 movie_original=play;movie_foreground=foreground;movie_get_focus=get_focus;movie_set_focus=set_focus;movie_send=send;movie_valid=is_valid;movie_enabled=is_enabled;movie_iconic=is_iconic;
 *(HWND*)MOVIE_ADDR(0x82813a)=main_window_test;restore_movie_focus=1;foreground_test=main_window_test;
 assert(movie_play("startup.mpg",7)==42&&played==1&&focused==1&&sent==1);
 assert(movie_play("startup.mpg",7)==42&&focused==1&&sent==2);
 foreground_test=(HWND)999;movie_play("startup.mpg",7);assert(sent==2&&focused==1);
 foreground_test=main_window_test;iconic=1;movie_play("startup.mpg",7);assert(sent==2);iconic=0;
 enabled=0;movie_play("startup.mpg",7);assert(sent==2);enabled=1;
 valid=0;movie_play("startup.mpg",7);assert(sent==2);valid=1;
 *(U*)MOVIE_ADDR(0x7c2d90)=1;movie_play("startup.mpg",7);assert(sent==2);*(U*)MOVIE_ADDR(0x7c2d90)=0;
 restore_movie_focus=0;movie_play("startup.mpg",7);assert(sent==2);
 /* Diagnostics survive startup_finish without erasing earlier evidence. */
 {WCHAR dir[MAX_PATH],file[MAX_PATH];HANDLE h;char data[1024];DWORD read;U size;
  GetTempPathW(MAX_PATH,dir);swprintf(runtime_dir,L"%lsNEMT-movie-log-%lu\\",dir,GetCurrentProcessId());assert(CreateDirectoryW(runtime_dir,NULL));
  startup_log=1;max_log_bytes=1024;max_backup_logs=0;InitializeCriticalSection(&startup_lock);startup_lock_ready=1;startup_started=GetTickCount();startup_active=1;
  assert(startup_open_log());startup_write("TEST","keep this evidence",0);startup_finish();
  SetLastError(1234);movie_log("after startup",9);assert(GetLastError()==1234);
  startup_log_name(file,0);h=CreateFileW(file,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);assert(h!=INVALID_HANDLE_VALUE);assert(ReadFile(h,data,sizeof(data)-1,&read,NULL));data[read]=0;size=GetFileSize(h,NULL);CloseHandle(h);
  assert(strstr(data,"keep this evidence")&&strstr(data,"STARTUP COMPLETE")&&strstr(data,"after startup"));
  max_log_bytes=size;movie_log("must not overflow",10);h=CreateFileW(file,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);assert(GetFileSize(h,NULL)==size);CloseHandle(h);
  assert(DeleteFileW(file));assert(RemoveDirectoryW(runtime_dir));startup_log=0;
 }
 puts("PASS movie memory-only skip and focus restoration: result preserved; active game only; no focus stealing, minimized/disabled/invalid window or still-installed movie WndProc.");return 0;
}
