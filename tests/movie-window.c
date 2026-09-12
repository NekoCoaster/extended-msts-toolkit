#include <assert.h>
static unsigned char movie_globals[0x90000];
#define MOVIE_ADDR(a) ((unsigned int)movie_globals+(a)-0x7c0000)
#include "../runtime/loader.c"
static int shows,destinations;static RECT observed;
static BOOL WINAPI show(HWND h,int c){assert(c==SW_SHOW);shows++;return 123;}
static LRESULT WINAPI message(HWND h,UINT m,WPARAM w,LPARAM l){
 RECT *r=(RECT*)l;
 if(m==0x48c){r->left=r->top=0;r->right=320;r->bottom=240;return 0;}
 assert(m==0x48f);observed=*r;destinations++;return 0;
}
int main(void){
 WNDCLASSA wc;HWND owner,child;RECT r,c,o;POINT p={0,0};int width,height;
 memset(&wc,0,sizeof(wc));wc.lpfnWndProc=DefWindowProcA;wc.hInstance=GetModuleHandleA(NULL);wc.lpszClassName="NEMTMovieLayoutTest";assert(RegisterClassA(&wc));
 owner=CreateWindowExA(0,wc.lpszClassName,"Hidden owner",WS_OVERLAPPEDWINDOW,100,100,800,600,NULL,NULL,wc.hInstance,NULL);assert(owner);
 child=CreateWindowExA(0,wc.lpszClassName,"Hidden movie",WS_CHILD|WS_BORDER,0,0,640,360,owner,NULL,wc.hInstance,NULL);assert(child);
 *(HWND*)MOVIE_ADDR(0x82813a)=owner;separate_movie_window=1;movie_show_original=show;movie_send=message;
 assert(movie_detach(child));assert(!(GetWindowLongA(child,GWL_STYLE)&WS_CHILD));assert(!(GetWindowLongA(child,GWL_STYLE)&WS_BORDER));assert(GetWindow(child,GW_OWNER)==owner);assert(!(GetWindowLongA(child,GWL_EXSTYLE)&WS_EX_TOPMOST));
 assert(movie_show(child,SW_SHOW)==123&&shows==1&&destinations==1);GetClientRect(child,&c);GetWindowRect(child,&r);GetClientRect(owner,&o);ClientToScreen(owner,&p);
 width=r.right-r.left;height=r.bottom-r.top;assert(r.left==p.x+(o.right-width)/2&&r.top==p.y+(o.bottom-height)/2);
 assert(observed.left>=0&&observed.top>=0&&observed.right<=c.right&&observed.bottom<=c.bottom);
 assert((observed.right-observed.left)*3==(observed.bottom-observed.top)*4);
 separate_movie_window=0;assert(movie_show(child,SW_SHOW)==123&&shows==2&&destinations==1);
 r.left=r.top=0;r.right=1920;r.bottom=1080;c.left=c.top=0;c.right=320;c.bottom=240;o=movie_fit(r,c);assert(o.left==240&&o.right==1680&&o.top==0&&o.bottom==1080);
 c.right=c.bottom=0;o=movie_fit(r,c);assert(!memcmp(&o,&r,sizeof(r)));
 DestroyWindow(child);DestroyWindow(owner);
 printf("PASS real hidden Win32 movie ownership, border removal, centering, aspect rectangle and bypass; no actual video decoding tested.\n");return 0;
}
