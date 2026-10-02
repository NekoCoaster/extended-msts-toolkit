#include <windows.h>
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
typedef unsigned int U;
static unsigned char globals[0x110000],view[0x1a8];
#define G(a) ((U)globals+(a)-0x790000)
static int focus=1,pause_state,button=1,calls,warps,move_ok=1;
static POINT cursor={100,100};static HCURSOR icon=(HCURSOR)123;
static int paused(void){return pause_state;}
static int crawl_control_focus(void){return focus;}
static SHORT key(int k){return button?(SHORT)0x8000:0;}
static HCURSOR get_icon(void){return icon;}
static HCURSOR set_icon(HCURSOR c){HCURSOR old=icon;icon=c;return old;}
static BOOL get_point(POINT*p){*p=cursor;return TRUE;}
static BOOL set_point(int x,int y){warps++;cursor.x=x;cursor.y=y;return move_ok;}
static BOOL client(HWND h,RECT*r){r->left=r->top=0;r->right=800;r->bottom=600;return TRUE;}
static BOOL convert(HWND h,POINT*p){return TRUE;}
static HWND capture(void){return NULL;}
#define GetAsyncKeyState key
#define GetCursor get_icon
#define SetCursor set_icon
#define GetCursorPos get_point
#define SetCursorPos set_point
#define GetClientRect client
#define ClientToScreen convert
#define ScreenToClient convert
#define GetCapture capture
#include "../runtime/external-camera.h"
static float seen[3];static U look_seen[2];
static void original(void){calls++;memcpy(seen,(void*)G(0x7c2a58),12);memcpy(look_seen,(void*)G(0x7c2a64),8);}
static void setup(int mode){
 external_reset();memset(globals,0,sizeof(globals));memset(view,0,sizeof(view));
 *(U*)G(0x7c2a88)=(U)view;*(U*)G(0x7c2ac0)=1234;*(U*)G(0x82813a)=55;
 *(U*)(view+0x110)=1;*(U*)(view+0x11c)=mode;*(U*)(view+0xc)=0x51a69a;*(U*)(view+0x9c)=123;
 *(float*)G(0x80ace0)=.02f;external_ready=1;external_original=original;
 focus=button=move_ok=1;pause_state=0;cursor.x=cursor.y=100;icon=(HCURSOR)123;calls=warps=0;
}
int main(void){
 float d[3];int mode,i;double times[]={.01,.02,.1,.5};
 for(i=0;i<4;i++){
  assert(external_delta(times[i],100,-50,2,d));
  assert(fabs(d[0]*times[i]*.7853975296020508-.3)<.000001);
  assert(fabs(d[1]*times[i]*.7853975296020508+.15)<.000001);
  assert(fabs(d[2]*times[i]*10-4)<.000001);
 }
 assert(!external_delta(0,1,1,1,d));assert(!external_delta(-1,1,1,1,d));
 for(mode=0;mode<16;mode++){
  setup(mode);external_orbit();assert(calls==1);
  assert(external_pan==(mode==1||mode==2));assert(warps==external_pan);
 }
 for(mode=1;mode<=2;mode++){
  setup(mode);external_orbit();assert(external_pan&&!icon); /* no initial jump */
  assert(!seen[0]&&!seen[1]&&!seen[2]);
  *(float*)G(0x7c2a58)=.5f;*(U*)G(0x7c2a64)=17;*(U*)G(0x7c2a68)=19;
  cursor.x+=20;cursor.y-=10;
  assert(external_message((HWND)55,WM_MOUSEWHEEL,MAKEWPARAM(MK_RBUTTON,60),0));
  assert(!external_steps&&external_wheel_remainder==60);
  assert(external_message((HWND)55,WM_MOUSEWHEEL,MAKEWPARAM(MK_RBUTTON,60),0));
  external_orbit();assert(seen[0]>.5f&&seen[1]<0&&seen[2]>0);
  assert(!look_seen[0]&&!look_seen[1]);
  assert(*(float*)G(0x7c2a58)==.5f&&*(U*)G(0x7c2a64)==17&&*(U*)G(0x7c2a68)==19);
  assert(!external_steps);external_orbit();assert(seen[2]==0);
  assert(external_message((HWND)55,WM_MOUSEWHEEL,MAKEWPARAM(MK_RBUTTON,(WORD)-120),0));
  external_orbit();assert(seen[2]<0);
  external_message((HWND)55,WM_RBUTTONUP,0,0);assert(!external_pan&&icon==(HCURSOR)123);
  assert(!external_message((HWND)55,WM_MOUSEWHEEL,MAKEWPARAM(0,120),0));
 }
 /* Tracking toggles in either camera, including during an active drag. */
 for(mode=1;mode<=2;mode++){
  setup(mode);*(U*)(view+0x110)=0;
  *(float*)G(0x7c2a58)=.5f;*(U*)G(0x7c2a64)=17;*(U*)G(0x7c2a68)=19;
  external_orbit();assert(calls==1&&!external_pan&&!warps);
  assert(seen[0]==.5f&&look_seen[0]==17&&look_seen[1]==19&&icon==(HCURSOR)123);
  assert(!external_message((HWND)55,WM_MOUSEWHEEL,MAKEWPARAM(MK_RBUTTON,120),0));
  assert(!external_message((HWND)55,WM_SETCURSOR,0,0));
  *(U*)(view+0x110)=1;external_orbit();assert(external_pan&&warps==1);
  external_steps=2;external_wheel_remainder=60;cursor.x+=30;
  *(U*)(view+0x110)=0;external_orbit();
  assert(!external_pan&&!external_steps&&!external_wheel_remainder&&warps==1);
  assert(seen[0]==.5f&&seen[2]==0&&look_seen[0]==17&&look_seen[1]==19);
  assert(icon==(HCURSOR)123);
  *(U*)(view+0x110)=1;external_orbit();assert(external_pan&&warps==2);
  assert(seen[0]==.5f&&seen[1]==0&&seen[2]==0); /* no stale drag or zoom */
  *(U*)(view+0x110)=0;
  assert(!external_message((HWND)55,WM_MOUSEWHEEL,MAKEWPARAM(MK_RBUTTON,120),0));
  assert(!external_pan&&icon==(HCURSOR)123);
 }
 for(i=0;i<7;i++){
  setup(1);external_orbit();external_steps=1;external_wheel_remainder=60;
  if(i==0)focus=0;if(i==1)pause_state=1;if(i==2)button=0;
  if(i==3)*(U*)(view+0x11c)=0;if(i==4)*(U*)G(0x7c2ac0)=5678;
  if(i==5)*(U*)G(0x829980)=1;if(i==6)external_ready=0;
  external_maintain();assert(!external_pan&&!external_steps&&!external_wheel_remainder&&icon==(HCURSOR)123);
 }
 setup(1);move_ok=0;external_orbit();assert(!external_pan&&calls==1);
 puts("External camera: frame-rate mapping, modes, tracking toggles, wheel, keyboard preservation and cancellation passed.");return 0;
}
