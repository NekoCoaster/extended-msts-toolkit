/* Toolset-only hooks installed at the verified CRT command-line bootstrap.
   Resizing is deferred to the start of a native frame, outside rendering. */
#include "editor_audio.h"
#include "editor_layout.h"
#include <math.h>
static Hook editor_hooks[8];
static B *editor_code;
static WNDPROC editor_original_proc;
static int editor_busy,editor_sizing,editor_fullscreen,editor_last_mode,editor_pending;
static LONG editor_saved_style,editor_saved_ex;
static LONG editor_base_style,editor_base_ex;
static WINDOWPLACEMENT editor_saved_placement;
static WindowPosFn editor_original_pos;
static DWORD editor_resize_time;
static void editor_camera_size(int width,int height){
 typedef void (__fastcall *CameraRefresh)(void*);
 B *camera=*(B**)0x7c2a88;int oldw,oldh;float fov;
 if(!camera)return;
 oldw=*(int*)(camera+0x7c);oldh=*(int*)(camera+0x80);
 if(oldw==width&&oldh==height)return;
 if(oldw<=0||oldh<=0)return;
 /* Preserve vertical field of view while widening the world view. Updating
    the application camera also refreshes native projection and picking. */
 fov=*(float*)(camera+0x84);
 if(fov>0.01f&&fov<3.13f)*(float*)(camera+0x84)=(float)(2*atan(tan(fov*.5)*width*oldh/(height*(double)oldw)));
 *(int*)(camera+0x74)=0;*(int*)(camera+0x78)=0;
 *(int*)(camera+0x7c)=width;*(int*)(camera+0x80)=height;
 ((CameraRefresh)0x51cd5f)(camera);
}
static int editor_mode(void){
 U mode=*(U*)0x7be0ec;
 return mode==1&&*(U*)0x7be0f8?1:mode==4?4:mode==3?3:0;
}
#include "editor_cab.h"
static void editor_toggle_fullscreen(HWND h){
 MONITORINFO info;LONG style;
 if(!editor_fullscreen){
  info.cbSize=sizeof(info);if(!GetMonitorInfoA(MonitorFromWindow(h,MONITOR_DEFAULTTONEAREST),&info))return;
  editor_saved_placement.length=sizeof(editor_saved_placement);if(!GetWindowPlacement(h,&editor_saved_placement))return;
  editor_saved_style=GetWindowLongA(h,GWL_STYLE);editor_saved_ex=GetWindowLongA(h,GWL_EXSTYLE);
  editor_fullscreen=1;style=(editor_saved_style&~(WS_CAPTION|WS_THICKFRAME|WS_MINIMIZE|WS_MAXIMIZE))|WS_POPUP;
  SetWindowLongA(h,GWL_STYLE,style);SetWindowLongA(h,GWL_EXSTYLE,editor_saved_ex&~(WS_EX_CLIENTEDGE|WS_EX_WINDOWEDGE));
  *(LONG*)0x82818a=style;*(LONG*)0x82818e=GetWindowLongA(h,GWL_EXSTYLE);
  SetWindowPos(h,NULL,info.rcMonitor.left,info.rcMonitor.top,info.rcMonitor.right-info.rcMonitor.left,info.rcMonitor.bottom-info.rcMonitor.top,SWP_NOZORDER|SWP_FRAMECHANGED);
 }else{
  editor_fullscreen=0;SetWindowLongA(h,GWL_STYLE,editor_saved_style);SetWindowLongA(h,GWL_EXSTYLE,editor_saved_ex);
  *(LONG*)0x82818a=editor_saved_style;*(LONG*)0x82818e=editor_saved_ex;
  SetWindowPlacement(h,&editor_saved_placement);SetWindowPos(h,NULL,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_NOZORDER|SWP_FRAMECHANGED);
 }
 editor_pending=1;editor_resize_time=GetTickCount();
}
static void editor_panels(HWND main){
 HWND right=*(HWND*)0x80afec,left=*(HWND*)0x80b0e4,bottom=*(HWND*)0x80afd4;
 RECT r,c,rr,lr,br,grow;MONITORINFO mi;POINT p;int x,y,bh,rw,gw,gh;EditorLayout layout;U native_busy;
 if(editor_busy||editor_mode()!=3||!IsWindow(right)||!IsWindow(left)||!IsWindow(bottom)||IsIconic(main))return;
 mi.cbSize=sizeof(mi);if(!GetMonitorInfoA(MonitorFromWindow(main,MONITOR_DEFAULTTONEAREST),&mi))return;
 if(editor_fullscreen)mi.rcWork=mi.rcMonitor;
 GetWindowRect(main,&r);GetClientRect(main,&c);p.x=c.left;p.y=c.top;ClientToScreen(main,&p);OffsetRect(&c,p.x,p.y);
 GetWindowRect(right,&rr);GetWindowRect(left,&lr);GetWindowRect(bottom,&br);rw=rr.right-rr.left;bh=lr.bottom-lr.top;if(br.bottom-br.top>bh)bh=br.bottom-br.top;
 layout=editor_layout(*(EditorRect*)&r,*(EditorRect*)&c,*(EditorRect*)&mi.rcWork,rw,rr.bottom-rr.top,lr.right-lr.left+br.right-br.left,bh);
 editor_busy=1;native_busy=*(U*)0x80ae98;*(U*)0x80ae98=1;
 /* Keep fixed-size native controls usable when both groups fold inside.
    Grow only after dragging, and never beyond the selected monitor. */
 if(!editor_sizing&&!IsZoomed(main)&&!editor_fullscreen&&(layout.fold_right||layout.fold_bottom)&&
    (c.right-c.left<layout.min_width||c.bottom-c.top<layout.min_height)){
  grow.left=grow.top=0;grow.right=editor_max(c.right-c.left,layout.min_width);grow.bottom=editor_max(c.bottom-c.top,layout.min_height);
  AdjustWindowRectEx(&grow,GetWindowLongA(main,GWL_STYLE),GetMenu(main)!=NULL,GetWindowLongA(main,GWL_EXSTYLE));
  gw=grow.right-grow.left;gh=grow.bottom-grow.top;
  if(gw>mi.rcWork.right-mi.rcWork.left)gw=mi.rcWork.right-mi.rcWork.left;
  if(gh>mi.rcWork.bottom-mi.rcWork.top)gh=mi.rcWork.bottom-mi.rcWork.top;
  x=editor_clamp(r.left,mi.rcWork.left,mi.rcWork.right-gw);y=editor_clamp(r.top,mi.rcWork.top,mi.rcWork.bottom-gh);
  if(gw!=r.right-r.left||gh!=r.bottom-r.top){editor_original_pos(main,NULL,x,y,gw,gh,SWP_NOZORDER|SWP_NOACTIVATE);*(U*)0x80ae98=native_busy;editor_busy=0;editor_panels(main);return;}
 }
 /* Owned palettes remain above their viewport, without becoming global topmost. */
 SetWindowLongA(right,GWL_HWNDPARENT,(LONG)main);SetWindowLongA(left,GWL_HWNDPARENT,(LONG)main);SetWindowLongA(bottom,GWL_HWNDPARENT,(LONG)main);
 x=layout.right_x;y=layout.right_y;
 editor_original_pos(right,NULL,x,y,0,0,SWP_NOSIZE|SWP_NOZORDER|SWP_NOACTIVATE);
 x=layout.bottom_x;y=layout.bottom_y;
 editor_original_pos(left,NULL,x,y,0,0,SWP_NOSIZE|SWP_NOZORDER|SWP_NOACTIVATE);
 editor_original_pos(bottom,NULL,x+lr.right-lr.left,y,0,0,SWP_NOSIZE|SWP_NOZORDER|SWP_NOACTIVATE);
 *(U*)0x80ae98=native_busy;editor_busy=0;
}
static BOOL WINAPI editor_window_pos(HWND h,HWND after,int x,int y,int w,int v,UINT flags){
 BOOL result=editor_original_pos(h,after,x,y,w,v,flags);
 if(!editor_busy&&editor_mode()==3&&(h==*(HWND*)0x82813a||h==*(HWND*)0x80afec||h==*(HWND*)0x80b0e4||h==*(HWND*)0x80afd4))editor_panels(*(HWND*)0x82813a);
 return result;
}
static void editor_map_size(HWND h,int width,int height){
 typedef void (__fastcall *MapRefresh)(void*);
 int *map=(int*)0x80adb8;U activity=*(U*)0x80ae78;int oldw,oldh,cx,cy,span;
 RECT outer,client,right,left,bottom;MONITORINFO mi;EditorLayout layout;POINT p;
 if(!activity||!*(U*)(activity+0xc))return;
 if(IsWindow(*(HWND*)0x80afec)&&IsWindow(*(HWND*)0x80b0e4)&&IsWindow(*(HWND*)0x80afd4)){
  mi.cbSize=sizeof(mi);
  if(GetMonitorInfoA(MonitorFromWindow(h,MONITOR_DEFAULTTONEAREST),&mi)){
   if(editor_fullscreen)mi.rcWork=mi.rcMonitor;
   GetWindowRect(h,&outer);GetClientRect(h,&client);p.x=p.y=0;ClientToScreen(h,&p);OffsetRect(&client,p.x,p.y);
   GetWindowRect(*(HWND*)0x80afec,&right);GetWindowRect(*(HWND*)0x80b0e4,&left);GetWindowRect(*(HWND*)0x80afd4,&bottom);
   layout=editor_layout(*(EditorRect*)&outer,*(EditorRect*)&client,*(EditorRect*)&mi.rcWork,right.right-right.left,right.bottom-right.top,left.right-left.left+bottom.right-bottom.left,editor_max(left.bottom-left.top,bottom.bottom-bottom.top));
   if(layout.fold_right)width-=right.right-right.left;
   if(layout.fold_bottom)height-=editor_max(left.bottom-left.top,bottom.bottom-bottom.top);
  }
 }
 if(width<160)width=160;if(height<120)height=120;
 oldw=map[8]-map[6];oldh=map[9]-map[7];
 if(oldw<=0||oldh<=0||(oldw==width&&oldh==height))return;
 /* Keep the map's scale and center, exposing more map instead of stretching.
    Native drawing recomputes its selection transforms from these bounds. */
 cx=(int)(((double)map[2]+map[4])/2);cy=(int)(((double)map[3]+map[5])/2);
 span=(int)(((double)map[4]-map[2])*width/oldw/2);map[2]=cx-span;map[4]=cx+span;
 span=(int)(((double)map[5]-map[3])*height/oldh/2);map[3]=cy-span;map[5]=cy+span;
 map[6]=map[7]=0;map[8]=width;map[9]=height;*(float*)(map+14)=(float)height/width;
 ((MapRefresh)0x67360d)(map);
}
static LRESULT CALLBACK editor_proc(HWND h,UINT msg,WPARAM w,LPARAM l){
 LRESULT result;int active=editor_mode();
 if(editor_windows&&active){
  if(msg==WM_SYSKEYDOWN&&w==VK_RETURN){if(!(l&(1L<<30)))editor_toggle_fullscreen(h);return 0;}
  if((msg==WM_SYSKEYUP||msg==WM_SYSCHAR)&&w==VK_RETURN)return 0;
  if(msg==WM_ENTERSIZEMOVE)editor_sizing=1;
  if(msg==WM_EXITSIZEMOVE){editor_sizing=0;editor_pending=1;editor_resize_time=0;}
  if(msg==WM_SIZE&&w!=SIZE_MINIMIZED){editor_pending=1;editor_resize_time=GetTickCount();}
 }
 if(msg==WM_DESTROY)editor_sound_release();
 if(editor_windows&&active==4&&msg>=WM_MOUSEMOVE&&msg<=WM_MBUTTONDBLCLK)l=editor_cab_mouse(h,l);
 result=CallWindowProcA(editor_original_proc,h,msg,w,l);
 /* MSTS updates these dimensions only for SIZE_RESTORED. Its editor
    background and mouse calculations also need them when maximized. */
 if(editor_windows&&active&&msg==WM_SIZE&&w!=SIZE_MINIMIZED){*(U*)0x82819e=LOWORD(l);*(U*)0x8281a2=HIWORD(l);}
 if(editor_windows&&active&&msg==WM_GETMINMAXINFO){MINMAXINFO *m=(MINMAXINFO*)l;RECT r={0,0,640,480};AdjustWindowRectEx(&r,GetWindowLongA(h,GWL_STYLE),GetMenu(h)!=NULL,GetWindowLongA(h,GWL_EXSTYLE));m->ptMinTrackSize.x=r.right-r.left;m->ptMinTrackSize.y=r.bottom-r.top;}
 if(editor_windows&&active==3&&(msg==WM_MOVE||msg==WM_SIZE||msg==WM_EXITSIZEMOVE))editor_panels(h);
 return result;
}
static int editor_rebuild(int width,int height){
 U options[6];int result;typedef int (__fastcall *Resize)(U*,U);typedef void (__fastcall *Surfaces)(HWND,U,U,U);
 memcpy(options,(void*)0x7c2b98,sizeof(options));options[1]=(options[1]&~0x20)|0x90;options[2]=width;options[3]=height;
 ((void(*)(void))0x6469fa)();
 result=((Resize)0x521315)(options,1);
 if(result){
  /* Suppress native window placement for this resize only. Carrying 0x80
     into the next editor/launcher transition breaks its mouse scaling. */
  options[1]&=~0x80;*(U*)0x7c2b9c=options[1];*(U*)0x8297d0&=~0x80;
  *(int*)0x79ca60=width;*(int*)0x79ca64=height;
  *(float*)0x79ca68=1;*(float*)0x79ca6c=1;
  memcpy((void*)0x7a8958,options,sizeof(options));
  ((Surfaces)0x646210)(*(HWND*)0x82813a,**(U**)(*(U*)0x8297f0+0x34),**(U**)(*(U*)0x8297f4+0x34),0);
  if(editor_mode()==1)editor_camera_size(width,height);
 }
 return result;
}
static void editor_frame(void){
 HWND h=*(HWND*)0x82813a;int mode=editor_mode();RECT r;LONG style;U engine;
 if(editor_idle_audio&&mode==1&&!IsIconic(h)){engine=*(U*)0x7c32f0;editor_sound_tick(engine?*(void**)engine:NULL);}else editor_sound_release();
 if(editor_windows&&mode&&h){
  if(mode!=editor_last_mode){
   if(editor_fullscreen)editor_toggle_fullscreen(h);
   style=GetWindowLongA(h,GWL_STYLE);
   if(!editor_last_mode){editor_base_style=style&~(WS_MAXIMIZE|WS_MINIMIZE);editor_base_ex=GetWindowLongA(h,GWL_EXSTYLE);}
   style=(style&~WS_POPUP)|WS_CAPTION|WS_THICKFRAME|WS_MINIMIZEBOX|WS_MAXIMIZEBOX|WS_SYSMENU;
   SetWindowLongA(h,GWL_STYLE,style);*(LONG*)0x82818a=style;*(LONG*)0x8281a6=0;
   SetWindowPos(h,NULL,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_NOZORDER|SWP_FRAMECHANGED);
   editor_pending=1;
  }
  if(editor_pending&&!editor_busy&&!editor_sizing&&!IsIconic(h)&&*(U*)0x7c2b94&&(DWORD)(GetTickCount()-editor_resize_time)>=150){
   GetClientRect(h,&r);
   if(r.right>=320&&r.bottom>=200&&r.right<=8192&&r.bottom<=8192){
    editor_pending=0;
    if(r.right!=*(int*)0x7c2ba0||r.bottom!=*(int*)0x7c2ba4){int oldw=*(int*)0x7c2ba0,oldh=*(int*)0x7c2ba4;editor_busy=1;
     if(!editor_rebuild(r.right,r.bottom)){editor_rebuild(oldw,oldh);editor_windows=0;MessageBoxA(h,"The editor renderer could not accept this window size. Restart MSTS to try again.","NEMT editor resizing",MB_OK|MB_ICONWARNING);}
     editor_busy=0;if(mode==3)editor_panels(h);
    }
   }
  }
 }
 if(editor_windows&&mode==1&&*(U*)0x8083b8==1&&!editor_busy)editor_camera_size(*(int*)0x7c2ba0,*(int*)0x7c2ba4);
 if(editor_windows&&mode==3&&!editor_busy)editor_map_size(h,*(int*)0x7c2ba0,*(int*)0x7c2ba4);
 if(!mode&&editor_last_mode&&editor_windows&&h){
  MONITORINFO mi;int w=*(int*)0x7c2ba0,v=*(int*)0x7c2ba4,x=0,y=0;
  /* Native exit already rebuilt the launcher. Restore its frame around that
     client size instead of applying a stale maximized editor placement. */
  editor_fullscreen=0;SetWindowLongA(h,GWL_STYLE,editor_base_style);SetWindowLongA(h,GWL_EXSTYLE,editor_base_ex);
  *(LONG*)0x82818a=editor_base_style;*(LONG*)0x82818e=editor_base_ex;*(U*)0x8281a6=0;
  r.left=r.top=0;r.right=w;r.bottom=v;AdjustWindowRectEx(&r,editor_base_style,GetMenu(h)!=NULL,editor_base_ex);
  mi.cbSize=sizeof(mi);if(GetMonitorInfoA(MonitorFromWindow(h,MONITOR_DEFAULTTONEAREST),&mi)){x=mi.rcWork.left+(mi.rcWork.right-mi.rcWork.left-(r.right-r.left))/2;y=mi.rcWork.top+(mi.rcWork.bottom-mi.rcWork.top-(r.bottom-r.top))/2;}
  SetWindowPos(h,NULL,x,y,r.right-r.left,r.bottom-r.top,SWP_NOZORDER|SWP_FRAMECHANGED);editor_pending=0;
 }
 editor_last_mode=mode;
 ((void(*)(void))0x6bad60)();
}
static int install_editor_hooks(void){
 U count=0;Hook *h;DWORD old;B *p;
 if(!editor_windows&&!editor_free_tools&&!editor_idle_audio)return 1;
 /* Independent verified instruction ranges, committed as one transaction. */
 if(memcmp((void*)0x696c00,"\xa1\x54\x99\x82\x00",5)||memcmp((void*)0x55521c,"\x55\x8b\xec\x83\xec\x10",6))return 0;
 editor_code=VirtualAlloc(NULL,32,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!editor_code)return 0;
 p=editor_code;memcpy(p,(void*)0x696c00,5);p+=5;branch(&p,0xe9,(void*)0x696c05);
 if(!VirtualProtect(editor_code,32,PAGE_EXECUTE_READ,&old))goto failed;FlushInstructionCache(GetCurrentProcess(),editor_code,32);editor_original_proc=(WNDPROC)editor_code;
 h=&editor_hooks[count++];memset(h,0,sizeof(*h));h->address=0x696c00;h->length=5;h->raw=1;memcpy(h->original,(void*)h->address,5);h->replacement[0]=0xe9;*(U*)(h->replacement+1)=(U)editor_proc-h->address-5;
 startup_call(&editor_hooks[count++],0x4999b0,0x6bad60,(U)editor_frame);
 if(editor_windows){
  startup_call(&editor_hooks[count++],0x6764b3,0x6bad60,(U)editor_frame);
  startup_call(&editor_hooks[count++],0x451d4f,0x6bad60,(U)editor_frame);
  startup_call(&editor_hooks[count++],0x44a8e6,0x6b6390,(U)editor_cab_present);
  startup_call(&editor_hooks[count++],0x44a8ba,0x40171c,(U)editor_cab_ui_present);
 }
 if(editor_free_tools){h=&editor_hooks[count++];memset(h,0,sizeof(*h));h->address=0x55521c;h->length=1;h->raw=1;h->original[0]=0x55;h->replacement[0]=0xc3;}
 if(editor_windows){h=&editor_hooks[count++];memset(h,0,sizeof(*h));h->address=0x84df30;h->length=4;h->raw=1;editor_original_pos=*(WindowPosFn*)h->address;memcpy(h->original,(void*)h->address,4);*(WindowPosFn*)h->replacement=editor_window_pos;}
 if(prepare_hooks(editor_hooks,count)&&install_hooks(editor_hooks,count))return 1;
failed:VirtualFree(editor_code,0,MEM_RELEASE);editor_code=NULL;return 0;
}
