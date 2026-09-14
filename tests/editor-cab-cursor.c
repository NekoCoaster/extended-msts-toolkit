#include <windows.h>
#include <assert.h>
static RECT client;static POINT origin,cursor;
static BOOL WINAPI test_client(HWND h,RECT *r){*r=client;return TRUE;}
static BOOL WINAPI test_origin(HWND h,POINT *p){p->x+=origin.x;p->y+=origin.y;return TRUE;}
static BOOL WINAPI test_cursor(int x,int y){cursor.x=x;cursor.y=y;return TRUE;}
#define GetClientRect test_client
#define ClientToScreen test_origin
#define SetCursorPos test_cursor
#include "../runtime/loader.c"
static B native_fixture_space[0x450000];
#undef assert
#define assert(x) do{if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
int main(void){
 int sizes[][2]={{640,480},{1920,1080},{3440,1440},{900,1600},{1918,829}};
 int i,x,y;LPARAM mapped;
 assert((U)native_fixture_space<0x4a0000&&(U)(native_fixture_space+sizeof(native_fixture_space))>=0x830000);
 *(U*)0x7be0ec=4;*(HWND*)0x82813a=(HWND)1;editor_windows=1;
 for(i=0;i<5;i++){
  client.right=sizes[i][0];client.bottom=sizes[i][1];origin.x=i&1?-1920:17;origin.y=i&1?-900:43;
  /* Native cached origin may predate a move; use only to recover canvas x/y. */
  *(int*)0x828196=91;*(int*)0x82819a=122;
  for(x=0;x<640;x+=7)for(y=0;y<480;y+=11){
   assert(editor_cab_cursor(x+91,y+122));
   mapped=editor_cab_mouse((HWND)1,MAKELPARAM(cursor.x-origin.x,cursor.y-origin.y));
   assert((short)LOWORD(mapped)==x&&(short)HIWORD(mapped)==y);
  }
 }
 editor_windows=0;editor_cab_cursor(97,211);assert(cursor.x==97&&cursor.y==211);
 editor_windows=1;*(U*)0x7be0ec=3;editor_cab_cursor(98,212);assert(cursor.x==98&&cursor.y==212);
 puts("PASS cab selection cursor round trips at five sizes, moved/negative monitor origins, disabled and other-editor fallback.");return 0;
}
