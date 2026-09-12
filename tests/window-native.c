#include <assert.h>
static unsigned char window_globals[256];
#define WINDOW_ADDR(a) ((unsigned int)window_globals+(a)-0x828100)
#include "../runtime/loader.c"
static void dimensions(HWND h,int w,int v){RECT r;assert(GetClientRect(h,&r));assert(r.right==w&&r.bottom==v);}
int main(void){WNDCLASSA wc;HWND h;RECT r;int x,y;LONG style=WS_OVERLAPPEDWINDOW;
 memset(&wc,0,sizeof(wc));wc.lpfnWndProc=DefWindowProcA;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="NEMTWindowTest";assert(RegisterClassA(&wc));
 r.left=r.top=0;r.right=800;r.bottom=600;assert(AdjustWindowRectEx(&r,style,FALSE,0));
 h=CreateWindowExA(0,wc.lpszClassName,"NEMT window sizing test",style,10,10,r.right-r.left,r.bottom-r.top,NULL,NULL,wc.hInstance,NULL);assert(h);
 *(HWND*)WINDOW_ADDR(0x82813a)=h;original_window_pos=SetWindowPos;original_show=ShowWindow;
 window_mode=2;assert(toolkit_window_pos(h,NULL,0,0,0,0,SWP_NOSIZE|SWP_NOMOVE|SWP_NOZORDER|SWP_NOACTIVATE));
 dimensions(h,800,600);assert(!(GetWindowLongA(h,GWL_STYLE)&(WS_CAPTION|WS_THICKFRAME)));assert(*(LONG*)WINDOW_ADDR(0x82818a)==GetWindowLongA(h,GWL_STYLE));
 center_for(h,800,600,&x,&y);GetWindowRect(h,&r);assert(r.left==x&&r.top==y);
 assert(toolkit_window_pos(h,NULL,30,40,0,0,SWP_NOSIZE|SWP_NOZORDER|SWP_NOACTIVATE));GetWindowRect(h,&r);assert(r.left==30&&r.top==40);
 assert(toolkit_window_pos(h,NULL,0,0,640,480,SWP_NOZORDER|SWP_NOACTIVATE));dimensions(h,640,480);center_for(h,640,480,&x,&y);GetWindowRect(h,&r);assert(r.left==x&&r.top==y);
 window_mode=1;arranged_window=NULL;SetWindowLongA(h,GWL_STYLE,style);r.left=r.top=0;r.right=800;r.bottom=600;AdjustWindowRectEx(&r,style,FALSE,0);
 assert(toolkit_window_pos(h,NULL,0,0,r.right-r.left,r.bottom-r.top,SWP_FRAMECHANGED|SWP_NOZORDER|SWP_NOACTIVATE));dimensions(h,800,600);assert(GetWindowLongA(h,GWL_STYLE)&WS_CAPTION);
 DestroyWindow(h);puts("PASS native Win32 border removal, client dimensions, cached style, resize centering, manual movement and bordered mode.");return 0;
}
