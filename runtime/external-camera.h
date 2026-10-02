/* MIT. Mouse input for native front/rear tracking cameras only.
   The original orbit callback owns all angles, distance limits and matrices. */
static U external_view,external_train;
static int external_pan,external_wheel_remainder,external_steps;
static POINT external_anchor;
static HCURSOR external_saved_cursor;
static void (*external_original)(void),(*external_frame_original)(void);
static WNDPROC external_proc_original;
static int external_ready;
static int external_eligible(void){
 U view=*(U*)G(0x7c2a88),mode;
 if(!external_ready||!view||!*(U*)G(0x7c2ac0)||paused()||!crawl_control_focus()||*(U*)G(0x829980))return 0;
 mode=*(U*)(view+0x11c);
 /* Shift+9 disables tracking: leave native FPS-style RMB look untouched. */
 return *(U*)(view+0x110)!=0&&(mode==1||mode==2)&&*(U*)(view+0xc)==0x51a69a&&*(U*)(view+0x9c)!=0;
}
static void external_reset(void){
 if(external_pan&&!GetCursor())SetCursor(external_saved_cursor);
 external_pan=external_wheel_remainder=external_steps=0;
 external_view=external_train=0;external_saved_cursor=NULL;
}
static void external_maintain(void){
 if(external_pan&&(!external_eligible()||!(GetAsyncKeyState(VK_RBUTTON)&0x8000)||
    external_view!=*(U*)G(0x7c2a88)||external_train!=*(U*)G(0x7c2ac0)))external_reset();
}
static int external_message(HWND h,UINT msg,WPARAM w,LPARAM l){
 if(!external_ready)return 0;
 if(msg==WM_RBUTTONUP||msg==WM_KILLFOCUS||msg==WM_CANCELMODE||msg==WM_DESTROY||
    msg==WM_CAPTURECHANGED||(msg==WM_ACTIVATEAPP&&!w)){external_reset();return 0;}
 external_maintain();
 if(h!=*(HWND*)G(0x82813a))return 0;
 if(msg==WM_MOUSEWHEEL){
  if(external_pan&&external_eligible()&&(w&MK_RBUTTON)){
   external_wheel_remainder+=(short)HIWORD(w);
   external_steps+=external_wheel_remainder/120;external_wheel_remainder%=120;
   if(external_steps>20)external_steps=20;if(external_steps< -20)external_steps=-20;
   return 1;
  }
  external_wheel_remainder=external_steps=0;
 }
 if(msg==WM_SETCURSOR&&external_pan){SetCursor(NULL);return 1;}
 return 0;
}
/* dt is the native orbit timestep, not wall time. Division cancels native
   integration so a pixel/detent has the same effect at different frame rates. */
static int external_delta(double dt,int dx,int dy,int steps,float out[3]){
 if(!(dt>=0.00001&&dt<=1.0))return 0;
 if(dx>1000)dx=1000;if(dx< -1000)dx=-1000;
 if(dy>1000)dy=1000;if(dy< -1000)dy=-1000;
 out[0]=(float)(dx*0.003/(0.7853975296020508*dt));
 out[1]=(float)(dy*0.003/(0.7853975296020508*dt));
 out[2]=(float)(steps*2.0/(10.0*dt));return 1;
}
static void external_orbit(void){
 float saved[3],delta[3];POINT point,center;RECT rect;HWND window;
 U look[2];int dx=0,dy=0,i,steps;
 external_maintain();
 if(!external_eligible()||!(GetAsyncKeyState(VK_RBUTTON)&0x8000)){external_original();return;}
 window=*(HWND*)G(0x82813a);
 if(!GetClientRect(window,&rect)||rect.right<=0||rect.bottom<=0||!GetCursorPos(&point)){
  external_reset();external_original();return;
 }
 center.x=rect.right/2;center.y=rect.bottom/2;
 if(!ClientToScreen(window,&center)){external_reset();external_original();return;}
 if(!external_pan){
  POINT client=point;ScreenToClient(window,&client);
  if(!PtInRect(&rect,client)||GetCapture()){external_original();return;}
  external_view=*(U*)G(0x7c2a88);external_train=*(U*)G(0x7c2ac0);
  external_saved_cursor=GetCursor();external_pan=1;
 }else {dx=point.x-external_anchor.x;dy=point.y-external_anchor.y;}
 if(!SetCursorPos(center.x,center.y)){external_reset();external_original();return;}
 external_anchor=center;SetCursor(NULL);
 steps=external_steps;external_steps=0;
 if(!external_delta(*(float*)G(0x80ace0),dx,dy,steps,delta)){external_original();return;}
 memcpy(saved,(void*)G(0x7c2a58),sizeof(saved));
 memcpy(look,(void*)G(0x7c2a64),sizeof(look));
 for(i=0;i<3;i++)*(float*)G(0x7c2a58+i*4)=saved[i]+delta[i];
 /* RMB's native free-look must not also turn the camera away from its target. */
 *(U*)G(0x7c2a64)=*(U*)G(0x7c2a68)=0;
 external_original();
 memcpy((void*)G(0x7c2a58),saved,sizeof(saved));
 memcpy((void*)G(0x7c2a64),look,sizeof(look));
}
static void external_frame(void){external_maintain();external_frame_original();}
static LRESULT CALLBACK external_proc(HWND h,UINT msg,WPARAM w,LPARAM l){
 if(external_message(h,msg,w,l))return msg==WM_SETCURSOR?TRUE:0;
 return CallWindowProcA(external_proc_original,h,msg,w,l);
}
