#include <assert.h>
static unsigned char movie_globals[0x80000];
#define MOVIE_ADDR(a) ((unsigned int)movie_globals+(a)-0x7c0000)
#include "../runtime/loader.c"
static HWND main_window_test=(HWND)123,foreground_test,focus_test;
static int valid=1,enabled=1,iconic=0,focused,sent,opens,fallback,open_error,played;
static HWND WINAPI foreground(void){return foreground_test;}
static HWND WINAPI get_focus(void){return focus_test;}
static HWND WINAPI set_focus(HWND h){assert(h==main_window_test);focused++;focus_test=h;return NULL;}
static BOOL WINAPI is_valid(HWND h){return valid;}
static BOOL WINAPI is_enabled(HWND h){return enabled;}
static BOOL WINAPI is_iconic(HWND h){return iconic;}
static LRESULT WINAPI send(HWND h,UINT m,WPARAM w,LPARAM l){
 assert(h==main_window_test);
 if(m==0x499){assert(!w);assert(!strcmp((char*)l,"mpegvideo!C:\\MSTS\\GLOBAL\\startup.MPG"));opens++;return open_error;}
 assert(m==WM_ACTIVATEAPP&&w==TRUE&&l==GetCurrentThreadId());assert(focus_test==main_window_test);sent++;return 0;
}
static U __fastcall play(const char *path,U edx){assert(!strcmp(path,"startup.mpg")&&edx==7);played++;return 42;}
static U __fastcall old_open(HWND h,const char *path){assert(h==main_window_test);fallback++;return 8;}
int main(void){
 movie_original=play;movie_original_open=old_open;movie_foreground=foreground;movie_get_focus=get_focus;movie_set_focus=set_focus;movie_send=send;movie_valid=is_valid;movie_enabled=is_enabled;movie_iconic=is_iconic;
 *(HWND*)MOVIE_ADDR(0x82813a)=main_window_test;restore_movie_focus=1;foreground_test=main_window_test;
 assert(movie_play("startup.mpg",7)==42&&played==1&&focused==1&&sent==1);
 assert(movie_play("startup.mpg",7)==42&&focused==1&&sent==2);
 foreground_test=(HWND)999;movie_play("startup.mpg",7);assert(sent==2&&focused==1);
 foreground_test=main_window_test;iconic=1;movie_play("startup.mpg",7);assert(sent==2);iconic=0;
 enabled=0;movie_play("startup.mpg",7);assert(sent==2);enabled=1;
 valid=0;movie_play("startup.mpg",7);assert(sent==2);valid=1;
 *(U*)MOVIE_ADDR(0x7c2d90)=1;movie_play("startup.mpg",7);assert(sent==2);*(U*)MOVIE_ADDR(0x7c2d90)=0;
 restore_movie_focus=0;movie_play("startup.mpg",7);assert(sent==2);
 system_movie_decoder=1;assert(movie_open(main_window_test,"C:\\MSTS\\GLOBAL\\startup.MPG")==1&&opens==1&&!fallback);
 open_error=1;assert(movie_open(main_window_test,"C:\\MSTS\\GLOBAL\\startup.MPG")==8&&opens==2&&fallback==1);
 assert(movie_open(main_window_test,"other.avi")==8&&opens==2&&fallback==2);
 system_movie_decoder=0;assert(movie_open(main_window_test,"C:\\MSTS\\GLOBAL\\startup.MPG")==8&&opens==2&&fallback==3);
 puts("PASS movie driver selection/fallback and focus restoration: result preserved; active game only; no focus stealing, minimized/disabled/invalid window or still-installed movie WndProc.");return 0;
}
