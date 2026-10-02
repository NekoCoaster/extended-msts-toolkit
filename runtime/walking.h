/* MIT. Experimental native walking adapter, supported MSTS Bin images only.
   All native world queries and camera changes run on MSTS's own frame thread. */
#include "walking-model.h"
#include "flashlight.h"
typedef int (__fastcall *WalkGroundFn)(float*,U,float,float);
typedef void (__fastcall *WalkActivateFn)(void*);
static WalkGroundFn walking_query=(WalkGroundFn)0x530635;
static WalkActivateFn walking_activate=(WalkActivateFn)0x51cd5f;
static WalkActivateFn walking_activate_original;
static WalkState walking_state;
/* State and view positions are relative to this native floating origin. */
static int walking_origin_x,walking_origin_z;
static U walking_view[0x1a8/4],walking_previous,walking_train;
static int walking_ready,walking_pending,walking_toggle_down,walking_pan;
static int walking_flashlight,walking_flashlight_available;
static int walking_flashlight_key(U scan){
 U i;
 if(!walking_flashlight_available)return 0;
 if(scan!=0x26&&scan!=0x1a&&scan!=0x1b&&scan!=0x33&&scan!=0x34&&scan!=0x27&&scan!=0x28)return 0;
 if(scan==walking_toggle_scan)return 0;
 for(i=0;i<6;i++)if(scan==editor_keys[i])return 0;
 return 1;
}
static void walking_light_render(U id,Registers *r){
 int active=walking_state.active&&*(U*)G(0x7c2a88)==(U)walking_view&&*(U*)G(0x7c2ac0)==walking_train;
 flashlight_update(*(U*)G(0x829224),active&&walking_flashlight);
}
static void walking_light_terrain(U after,Registers *r){
 U patch=after?r->esi:r->ecx,descriptor=after?r->ebx:r->edx;
 if(flashlight_near_patch(patch,descriptor))*(U*)patch|=0x100;
}
static void walking_light_vertex(U coarse,Registers *r){
 const float *position=(const float*)(coarse?*(U*)(r->ebp-28):r->edi);
 U *packed=(U*)(r->ebp-4);
 *packed=flashlight_terrain_colour(position,*packed);
}
static void walking_light_object(U mode,Registers *r){
 U state=(mode==0||mode==4)?r->esi:r->ecx;const float *vertex,*matrix;U *output;
 if(!flashlight_frame_active||*(U*)(state+0x1e0)==flashlight_object)return;
 vertex=*(const float**)(state+0x188);matrix=*(const float**)G(0x82898c);output=*(U**)(state+0x190);
 output[4]=flashlight_object_colour(vertex,matrix,output[4],mode<2,mode==3);
}
static void walking_light_shutdown(U id,Registers *r){
 walking_flashlight=0;flashlight_renderer_shutdown();
}
static const char *walking_status="Not initialized";
static void (*walking_camera_original)(void),(*walking_input_original)(void);
static Hook walking_hooks[17];static B *walking_code;
static WNDPROC walking_original_proc;
static HCURSOR walking_saved_cursor;static int walking_cursor_hidden;
static HCURSOR (WINAPI *walking_set_cursor)(HCURSOR)=SetCursor;
static HCURSOR (WINAPI *walking_get_cursor)(void)=GetCursor;
static SHORT (WINAPI *walking_key_state)(int)=GetAsyncKeyState;
static void walking_modifiers(WalkInput *in){
 /* Called only in the active, focused, unpaused camera-input path. Native
    dispatch's key bitmap is not a reliable physical modifier-key snapshot. */
 in->sprint=(walking_key_state(VK_LSHIFT)&0x8000)!=0;
 in->slow=(walking_key_state(VK_LMENU)&0x8000)!=0;
}
static void walking_cursor(int hide){
 if(hide){if(!walking_cursor_hidden){walking_saved_cursor=walking_get_cursor();walking_cursor_hidden=1;}walking_set_cursor(NULL);}
 else if(walking_cursor_hidden){
  if(!walking_get_cursor())walking_set_cursor(walking_saved_cursor);
  walking_cursor_hidden=0;walking_saved_cursor=NULL;
 }
}
static double walking_fov=60,walking_initial_fov=60;static int walking_fov_dirty,walking_wheel_remainder;
static void walking_fov_adjust(int direction){
 double next=walk_fov_step(walking_fov,direction);
 if(next!=walking_fov){walking_fov=next;walking_fov_dirty=1;}
}
static void walking_apply_fov(void){
 if(!walking_fov_dirty)return;
 *(float*)((B*)walking_view+0x84)=(float)(walking_fov*0.017453292519943295);
 walking_activate(walking_view);walking_fov_dirty=0;
}
static int walking_wheel(int delta,int allowed){
 int steps;
 if(!allowed){walking_wheel_remainder=0;return 0;}
 walking_wheel_remainder+=delta;steps=walking_wheel_remainder/120;
 walking_wheel_remainder%=120;
 while(steps){walking_fov_adjust(steps>0?-1:1);steps+=steps>0?-1:1;}
 return 1;
}
static LRESULT CALLBACK walking_proc(HWND h,UINT msg,WPARAM w,LPARAM l){
 if(external_message(h,msg,w,l))return msg==WM_SETCURSOR?TRUE:0;
 if(msg==WM_RBUTTONUP||msg==WM_KILLFOCUS||msg==WM_CANCELMODE||msg==WM_DESTROY||(msg==WM_ACTIVATEAPP&&!w)){
  walking_pan=0;walking_cursor(0);
 }
 if(msg==WM_SETCURSOR&&walking_pan&&walking_input_active&&!paused()&&crawl_control_focus()){
  walking_cursor(1);return TRUE;
 }
 if(msg==WM_SYSCOMMAND&&(w&0xfff0)==SC_KEYMENU&&walking_input_active&&!paused()&&crawl_control_focus())return 0;
 if(msg==WM_KILLFOCUS||(msg==WM_ACTIVATEAPP&&!w))walking_wheel_remainder=0;
 if(msg==WM_MOUSEWHEEL&&h==*(HWND*)G(0x82813a)&&
    walking_wheel((short)HIWORD(w),walking_input_active&&!paused()&&crawl_control_focus()))return 0;
 return CallWindowProcA(walking_original_proc,h,msg,w,l);
}
static U walking_event_copy[4];
static void walking_sync_origin(void){
 int x=*(int*)G(0x79d118),z=*(int*)G(0x79d11c);double dx,dz;
 if(!walking_state.active)return;
 dx=((double)walking_origin_x-x)*2048.0;dz=((double)walking_origin_z-z)*2048.0;
 if(dx||dz){
  walking_state.x+=dx;walking_state.z+=dz;
  /* Native 0x5172f9 only rebases registered views. Our static view is not
     registered, so both its matrices must follow the same shift exactly once. */
  *(float*)((B*)walking_view+0x38)=(float)walking_state.x;
  *(float*)((B*)walking_view+0x40)=(float)walking_state.z;
  *(float*)((B*)walking_view+0x68)=(float)walking_state.x;
  *(float*)((B*)walking_view+0x70)=(float)walking_state.z;
  walking_origin_x=x;walking_origin_z=z;
 }
}
static B walking_event_held[256];static U walking_pulses;
static int walking_ground(void *context,double x,double z,double *height){
 float sample[8]={0};double normal;
 if(!*(U*)G(0x7c2e08)||!walk_finite(x)||!walk_finite(z))return 0;
 if(!walking_query(sample,2,(float)x,(float)z))return 0;
 normal=sample[1]*sample[1]+sample[2]*sample[2]+sample[3]*sample[3];
 /* The native triangle-hole path can return success without a triangle.
    Its zero normal is not usable ground, even if height happens to be zero. */
 if(!walk_finite(sample[0])||!walk_finite(normal)||normal<0.5||normal>1.5)return 0;
 *height=sample[0];return 1;
}
static int walking_keys(B bits[32]){
 U head,node,n[3],device[7],input,addr,count,budget=32;B kind;
 memset(bits,0,32);
 if(!read_memory(G(0x8299a0),&head,4)||!head||!read_memory(head,&node,4))return 0;
 while(node!=head&&budget--){
  if(!read_memory(node,n,12)||!read_memory(n[2],device,sizeof(device)))return 0;
  node=n[0];input=device[1];
  if(!input||!read_memory(input+0x2d,&kind,1)||kind!=1)continue;
  count=device[5]-device[4];if(!count||count>256)return 0;
  return read_memory(input+0x24,&addr,4)&&read_memory(addr,bits,(count+7)/8);
 }return 0;
}
static const U walking_flash_scans[]={0x1a,0x1b,0x33,0x34,0x27,0x28};
static double walking_flash_wait[6];static B walking_flash_armed[6];
static void walking_flash_repeat_reset(void){memset(walking_flash_armed,0,sizeof(walking_flash_armed));}
static void walking_flash_adjust(U key){
 int setting=key<2?FLASH_ANGLE:key<4?FLASH_RANGE:FLASH_BRIGHTNESS;
 flashlight_tuning[setting]=flash_adjust(flashlight_tuning[setting],setting,(key&1)?1:-1);
}
static void walking_flash_repeat(const B *bits,double dt){
 U i;if(!walking_input_active||!bits){walking_flash_repeat_reset();return;}
 if(!walk_finite(dt)||dt<=0)return;dt=walk_limit(dt,0,0.1);
 for(i=0;i<6;i++){
  if(!walking_flashlight_key(walking_flash_scans[i])||!crawl_key(bits,walking_flash_scans[i])){walking_flash_armed[i]=0;continue;}
  if(!walking_flash_armed[i])continue;
  walking_flash_wait[i]-=dt;
  while(walking_flash_wait[i]<=1e-9){walking_flash_adjust(i);walking_flash_wait[i]+=0.1;}
 }
}
static void walking_key_edge(U scan,int down,int allowed){
 U i;int edge;if(scan>=238)return;
 edge=down&&!walking_event_held[scan];walking_event_held[scan]=down!=0;
 for(i=0;i<6;i++)if(scan==walking_flash_scans[i]&&(!down||!allowed))walking_flash_armed[i]=0;
 if(walking_input_active&&edge&&allowed){
  if(walking_flashlight_key(scan)){
   if(scan==0x26)walking_flashlight=!walking_flashlight;
   for(i=0;i<6;i++)if(scan==walking_flash_scans[i]){
    walking_flash_adjust(i);walking_flash_wait[i]=walk_limit(walking_repeat_delay,0.05,5);walking_flash_armed[i]=1;
   }
  }
  if(scan==0x09){
   walking_state.eye_height=walking_initial_eye_height;walk_height_reset(&walking_state);
   walking_fov=walking_initial_fov;walking_fov_dirty=1;walking_wheel_remainder=0;walking_pulses&=~48u;
  }
  if(scan==0x0c||scan==0x0d)walking_fov_adjust(scan==0x0c?1:-1);
  for(i=0;i<6;i++)if(scan==editor_keys[i])walking_pulses|=1<<i;
  if(scan==0x39)walking_pulses|=64;if(scan==0x2f)walking_pulses|=128;
 }
 if(scan==walking_toggle_scan){if(edge&&allowed)walking_pending=1;walking_toggle_down=down!=0;}
}
static void walking_event(Registers *r){
 U *stack=(U*)(r->esp+4),*event=(U*)stack[6],*device=(U*)stack[9],scan;
 if(!walking_ready||!event||!device||!device[1]||*((B*)device[1]+0x2d)!=1||(event[0]>>16)!=1||event[1]>1)return;
 scan=event[0]&0xffff;if(scan>=238)return;
 walking_key_edge(scan,event[1]!=0,(!stack[10]||walking_input_active)&&!paused()&&crawl_control_focus());
 if(scan!=walking_toggle_scan&&!(walking_input_active&&(scan==0x09||walking_flashlight_key(scan))))return;
 memcpy(walking_event_copy,event,16);walking_event_copy[0]=0x10000;stack[6]=(U)walking_event_copy;
}
static void walking_event_gateway(U id,Registers *r){walking_event(r);}
static void walking_reset(void){
 walking_flashlight=0;flashlight_stop();walking_flash_repeat_reset();
 walking_cursor(0);walk_height_reset(&walking_state);
 walking_state.active=walking_input_active=walking_pending=walking_pan=0;
 walking_previous=walking_train=0;walking_status="Standby";
 walking_pulses=0;memset(walking_event_held,0,sizeof(walking_event_held));
 walking_fov_dirty=walking_wheel_remainder=0;
}
static int walking_registered_view(U view){
 U head,node,n[3],budget=256;
 if(!view||view==(U)walking_view||!read_memory(G(0x7c2ac8),&head,4)||!head||!read_memory(head,&node,4))return 0;
 while(node!=head&&budget--){
  if(!read_memory(node,n,12))return 0;if(n[2]==view)return 1;node=n[0];
 }return 0;
}
static U walking_handoff_car(U target){
 U car=0,owner=0,train=*(U*)G(0x7c2ac0);B transform[48];
 if(!train||train!=walking_train)return 0;
 if(read_memory(target+0x9c,&car,4)&&car&&read_memory(car+0x98,&owner,4)&&owner==train&&read_memory(car+0x20,transform,48))return car;
 if(read_memory(train+0x6a,&car,4)&&car&&read_memory(car+0x98,&owner,4)&&owner==train&&read_memory(car+0x20,transform,48))return car;
 return 0;
}
static void __fastcall walking_activate_bridge(void *target){
 int leaving=*(U*)G(0x7c2a88)==(U)walking_view&&target!=walking_view;
 U saved=walking_view[0x9c/4],car;
 walking_sync_origin();
 if(leaving&&target){
  if(!walking_registered_view((U)target)||(car=walking_handoff_car((U)target))==0){walking_status="Camera handoff unavailable";return;}
  /* Native activation invokes target +0x10 BEFORE changing active-view globals.
     0x51949a reads outgoing +0x9c without a null check during derail views. */
  walking_view[0x9c/4]=car;
 }
 walking_activate_original(target);walking_view[0x9c/4]=saved;
 if(leaving&&*(U*)G(0x7c2a88)!=(U)walking_view){walking_eye_height=walking_state.eye_height;walking_reset();}
}
static int walking_return_view(void){
 U target=walking_previous;
 if(!walking_registered_view(target))target=*(U*)G(0x7c2a8c);
 if(!walking_registered_view(target)){walking_status="Previous camera unavailable";return 0;}
 walking_activate((void*)target);return *(U*)G(0x7c2a88)!=(U)walking_view;
}
static void walking_matrix(void){
 float *m=(float*)((B*)walking_view+0x14);double sy=sin(walking_state.yaw),cy=cos(walking_state.yaw),sp=sin(walking_state.pitch),cp=cos(walking_state.pitch);
 m[0]=cy;m[1]=0;m[2]=-sy;m[3]=-sy*sp;m[4]=cp;m[5]=-cy*sp;m[6]=sy*cp;m[7]=sp;m[8]=cy*cp;
 m[9]=walking_state.x;m[10]=walking_state.y+walking_state.eye_height;m[11]=walking_state.z;
 memcpy((B*)walking_view+0x44,m,48);
}
static int walking_change(void){
 U view=*(U*)G(0x7c2a88);B keys[32];U i;float *m;
 if(!walking_keys(keys))return 0;
 for(i=0;i<238;i++)if(crawl_key(keys,i))return 0;
 if(GetAsyncKeyState(VK_LBUTTON)<0||GetAsyncKeyState(VK_RBUTTON)<0||GetAsyncKeyState(VK_MBUTTON)<0)return 0;
 if(walking_state.active){
  if(view==(U)walking_view&&!walking_return_view()){walking_pending=0;return 0;}
  walking_eye_height=walking_state.eye_height;walking_reset();return 1;
 }
 if(!view||!*(U*)G(0x7c2ac0)||*(U*)G(0x7c2ad8)){walking_status="Unavailable in tunnel transition";walking_pending=0;return 0;}
 m=(float*)(view+0x14);
 /* Cab/head-out/passenger starts should place the walker beside the vehicle,
    not inside its visible mesh. Exterior starts retain their current X/Z. */
 {double side=(*(U*)(view+0x11c)==0||*(U*)(view+0x11c)==4||*(U*)(view+0x11c)==7)?3:0;
 if(!walk_begin(&walking_state,m[9]+m[0]*side,m[11]+m[2]*side,walking_eye_height,atan2(m[6],m[8]),walking_ground,NULL)){
  walking_status="No usable ground here";walking_pending=0;return 0;
 }}
 walking_state.height_repeat_delay=walking_repeat_delay;
 memcpy(walking_state.tuning,walking_tuning,sizeof(walking_tuning));
 walking_origin_x=*(int*)G(0x79d118);walking_origin_z=*(int*)G(0x79d11c);
 /* Static view is deliberately NOT registered in MSTS's owning view list. */
 memcpy(walking_view,(void*)view,sizeof(walking_view));memset(walking_view,0,20);
 walking_view[0x9c/4]=walking_view[0x118/4]=0;walking_view[0x11c/4]=9;
 walking_view[0x90/4]=walking_view[0x94/4]=walking_view[0x98/4]=0;
 walking_previous=view;walking_train=*(U*)G(0x7c2ac0);walking_matrix();
 walking_fov=*(float*)((B*)walking_view+0x84)/0.017453292519943295;
 if(!walk_finite(walking_fov)||walking_fov<1||walking_fov>179){
  walking_fov=60;*(float*)((B*)walking_view+0x84)=(float)(walking_fov*0.017453292519943295);
 }
 walking_initial_fov=walking_fov;walking_fov_dirty=walking_wheel_remainder=0;
 walking_activate(walking_view);walking_input_active=1;walking_pending=0;walking_status="Walking";return 1;
}
static void walking_camera(void){
 WalkInput in;B bits[32];POINT point,center;RECT rect;HWND window;U i;double dt=*(float*)G(0x828fb4);
 external_maintain();
 if(walking_state.active&&(*(U*)G(0x7c2ac0)!=walking_train||*(U*)G(0x7c2a88)!=(U)walking_view))walking_reset();
 if(walking_state.active){
  walking_sync_origin();
  memset(&in,0,sizeof(in));
  if(!paused()&&crawl_control_focus()&&walking_keys(bits)){
   walking_modifiers(&in);walking_flash_repeat(bits,dt);
   in.forward=crawl_key(bits,editor_keys[0])-crawl_key(bits,editor_keys[1]);
   in.right=crawl_key(bits,editor_keys[3])-crawl_key(bits,editor_keys[2]);
   in.height_up=crawl_key(bits,editor_keys[4]);in.height_down=crawl_key(bits,editor_keys[5]);in.up=in.height_up-in.height_down;
   in.jump=crawl_key(bits,0x39);in.toggle_noclip=crawl_key(bits,0x2f);
   in.forward=((walking_pulses&1)||crawl_key(bits,editor_keys[0]))-((walking_pulses&2)||crawl_key(bits,editor_keys[1]));
   in.right=((walking_pulses&8)||crawl_key(bits,editor_keys[3]))-((walking_pulses&4)||crawl_key(bits,editor_keys[2]));
   if(walking_pulses&16){in.height_up=1;walking_state.previous_up=0;}
   if(walking_pulses&32){in.height_down=1;walking_state.previous_down=0;}
   in.up=in.height_up-in.height_down;
   if(walking_pulses&64){in.jump=1;walking_state.previous_jump=0;}
   if(walking_pulses&128){in.toggle_noclip=1;walking_state.previous_noclip=0;}
   window=*(HWND*)G(0x82813a);
   if(GetAsyncKeyState(VK_RBUTTON)<0&&GetClientRect(window,&rect)&&GetCursorPos(&point)){
    center.x=(rect.right-rect.left)/2;center.y=(rect.bottom-rect.top)/2;ClientToScreen(window,&center);
    in.look=walking_pan;in.look_x=point.x-center.x;in.look_y=center.y-point.y;
    SetCursorPos(center.x,center.y);walking_pan=1;walking_cursor(1);
   }else {walking_pan=0;walking_cursor(0);}
   walk_step(&walking_state,&in,dt,0,walking_ground,NULL);
  }else{
   walking_wheel_remainder=0;walking_flash_repeat_reset();
   walking_cursor(0);walk_height_reset(&walking_state);
   walking_pan=0;walking_state.previous_jump=walking_state.previous_up=walking_state.previous_down=walking_state.previous_noclip=1;
  }
  walking_pulses=0;
  walking_matrix();walking_status=walking_state.noclip?"Noclip":walking_state.grounded?"Walking":walking_state.vertical_speed>0?"Jumping":"Falling";
  if(!paused()&&crawl_control_focus())walking_apply_fov();
 }
 walking_camera_original();
 walking_sync_origin();
}
/* Suppress action dispatch, including the native held-callback queue. Native
   event bookkeeping still runs, so releases do not leave stuck counters. */
typedef struct {U address,identity;B disabled;} WalkActionMask;
static WalkActionMask walking_masks[1024];
static int walking_masks_count;
typedef struct {U address,first,last;} WalkDeviceMask;
static WalkDeviceMask walking_devices[32];static int walking_device_count;
static U walking_allowed[128];static int walking_allowed_count;
static int walking_view_action(U action){
 static const WCHAR *names[]={L"Camera_CabView",L"Camera_NoCab",L"Camera_FrontTracking",L"Camera_RearTracking",L"Camera_Trainspotter",L"Camera_Passenger",L"CameraCoupling",L"CameraYardMaster",L"CameraCycle",L"CameraReset",L"CameraTracking",L"ToggleFrameRate"};
 WCHAR name[64];U identity,address,i;
 /* Action +0 is an interned-name object, NOT a direct string. Native
    0x6bca50 puts the UTF-16 text pointer at identity +0x10. */
 if(!read_memory(action,&identity,4)||!identity||!read_memory(identity+0x10,&address,4)||!address)return 0;
 for(i=0;i<64;i++){if(!read_memory(address+i*2,name+i,2))return 0;if(!name[i])break;}
 if(i==64)return 0;
 for(i=0;i<sizeof(names)/sizeof(names[0]);i++)if(!lstrcmpiW(name,names[i]))return 1;
 return 0;
}
static int walking_function_key(U scan){return (scan>=0x3b&&scan<=0x44)||scan==0x57||scan==0x58;}
static int walking_collect_allowed(void){
 U head,node,n[3],device[7],input,bind[4],scan,k,budget=64;B kind;
 walking_allowed_count=0;
 if(!read_memory(G(0x8299a0),&head,4)||!head||!read_memory(head,&node,4))return 0;
 while(node!=head&&budget--){
  if(!read_memory(node,n,12)||!read_memory(n[2],device,sizeof(device)))return 0;node=n[0];input=device[1];
  if(!input||!read_memory(input+0x2d,&kind,1)||kind!=1)continue;
  for(k=0;k<13;k++){
   scan=!k?1:k<=10?0x3a+k:0x57+k-11;if(device[5]-device[4]<=scan)return 0;
   if(!read_memory(device[6]+(device[4]+scan)*16,bind,16))return 0;
   for(;;){
    if(bind[0]){if(walking_allowed_count==128)return 0;walking_allowed[walking_allowed_count++]=bind[0];}
    if(!bind[1])break;if(!budget--||!read_memory(bind[1],bind,16))return 0;
   }
  }
 }return node==head;
}
static void walking_unmask(void){
 U action=*(U*)G(0x829974),budget=1024,identity,next;int i;
 /* A native menu transition may unregister actions. Never dereference a saved
    node after dispatch unless it is still in the live registry. */
 while(action&&budget--){
  if(!read_memory(action,&identity,4)||!read_memory(action+8,&next,4))break;
  for(i=0;i<walking_masks_count;i++)if(walking_masks[i].address==action&&walking_masks[i].identity==identity){
   B *flags=(B*)(action+0x12);*flags=(*flags&~2)|walking_masks[i].disabled;break;
  }action=next;
 }walking_masks_count=0;
 for(i=0;i<walking_device_count;i++){
  *(U*)(walking_devices[i].address+0x20)=walking_devices[i].first;
  *(U*)(walking_devices[i].address+0x28)=walking_devices[i].last;
 }walking_device_count=0;
}
static int walking_mask(void){
 U action=*(U*)G(0x829974),i,identity;B flags;walking_masks_count=0;
 if(!walking_collect_allowed())return 0;
 while(action){
  if(walking_masks_count>=1024||!read_memory(action+0x12,&flags,1)||!read_memory(action,&identity,4)){walking_unmask();return 0;}
  for(i=0;i<(U)walking_masks_count;i++)if(walking_masks[i].address==action){walking_unmask();return 0;}
  for(i=0;i<(U)walking_allowed_count&&action!=walking_allowed[i];i++);
  walking_masks[walking_masks_count].address=action;walking_masks[walking_masks_count].identity=identity;walking_masks[walking_masks_count++].disabled=flags&2;
  if(i==(U)walking_allowed_count&&!walking_view_action(action))*(B*)(action+0x12)=flags|2;
  if(!read_memory(action+8,&action,4)){walking_unmask();return 0;}
 }
 /* Unmapped/raw device callbacks bypass the action-disable flag. Keep menu
    mouse handling available while paused, but block cab/controller callbacks
    during driving. Relative look uses the OS cursor, not native cab panning. */
 if(!paused()){
  U head=*(U*)G(0x8299a0),node=*(U*)head,n[3],device[11];
  while(node!=head){
   if(walking_device_count==32||!read_memory(node,n,12)||!read_memory(n[2],device,sizeof(device))){walking_unmask();return 0;}
   walking_devices[walking_device_count].address=n[2];walking_devices[walking_device_count].first=device[8];walking_devices[walking_device_count++].last=device[10];
   *(U*)(n[2]+0x20)=*(U*)(n[2]+0x28)=0;node=n[0];
  }
 }return 1;
}
static void walking_input(void){
 int masked=0;
 if(walking_ready){
  if(walking_state.active&&(*(U*)G(0x7c2ac0)!=walking_train||*(U*)G(0x7c2a88)!=(U)walking_view))walking_reset();
  if(walking_pending&&!paused()&&crawl_control_focus())walking_change();
  if(walking_input_active){masked=walking_mask();if(!masked){
   if(*(U*)G(0x7c2a88)==(U)walking_view&&!walking_return_view())return;
   walking_reset();walking_status="Disabled: input isolation failed";
  }}
 }
 walking_input_original();if(masked)walking_unmask();
}
static B *walking_detour(Hook *h,B *p,U address,const B *expected,U length,void *replacement){
 memcpy(p,expected,length);p+=length;branch(&p,0xe9,(void*)(address+length));
 memset(h,0,sizeof(*h));h->address=address;h->length=length;h->raw=1;memcpy(h->original,expected,length);
 memset(h->replacement,0x90,length);h->replacement[0]=0xe9;*(U*)(h->replacement+1)=(U)replacement-address-5;
 return p;
}
static int install_walking_hooks(void){
 B *p,*tail,*entry;DWORD old;U i,count=16;
 if(!walking_requested)return 1;
 walking_flashlight_available=walking_toggle_scan!=0x26;
 for(i=0;i<6;i++)if(editor_keys[i]==0x26)walking_flashlight_available=0;
 if(memcmp((void*)0x530635,"\x55\x8b\xec\x83\xec\x08",6)||memcmp((void*)0x51cd5f,"\x55\x8b\xec",3))return 0;
 walking_code=VirtualAlloc(NULL,2048,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!walking_code)return 0;p=walking_code;
 walking_camera_original=(void*)p;p=walking_detour(&walking_hooks[0],p,0x51cfd5,(B*)"\x55\x8b\xec\x83\xec\x44",6,walking_camera);
 walking_input_original=(void*)p;p=walking_detour(&walking_hooks[1],p,0x6bad60,(B*)"\x83\xec\x44\x53\x55",5,walking_input);
 walking_original_proc=(WNDPROC)p;p=walking_detour(&walking_hooks[2],p,0x696c00,(B*)"\xa1\x54\x99\x82\x00",5,walking_proc);
 walking_activate_original=(WalkActivateFn)p;p=walking_detour(&walking_hooks[3],p,0x51cd5f,(B*)"\x55\x8b\xec\x83\xec\x50",6,walking_activate_bridge);
 /* Preserve all native registers, flags and x87/SSE state around our work. */
 tail=p;memcpy(p,"\xa1\x90\x89\x82\x00",5);p+=5;branch(&p,0xe9,(void*)0x6a1925);
 entry=p;gateway(&p,0,walking_light_render,tail,0);
 p=walking_detour(&walking_hooks[4],p,0x6a1920,(B*)"\xa1\x90\x89\x82\x00",5,entry);
 tail=p;memcpy(p,"\x83\xec\x08\x53\x55",5);p+=5;branch(&p,0xe9,(void*)0x6f1565);
 entry=p;gateway(&p,0,walking_light_terrain,tail,0);
 p=walking_detour(&walking_hooks[5],p,0x6f1560,(B*)"\x83\xec\x08\x53\x55",5,entry);
 tail=p;memcpy(p,"\x8b\x55\x00\x8b\x46\x48",6);p+=6;branch(&p,0xe9,(void*)0x6f17da);
 entry=p;gateway(&p,1,walking_light_terrain,tail,0);
 p=walking_detour(&walking_hooks[6],p,0x6f17d4,(B*)"\x8b\x55\x00\x8b\x46\x48",6,entry);
 tail=p;memcpy(p,"\xa1\x9c\x86\x82\x00",5);p+=5;branch(&p,0xe9,(void*)0x69fdd5);
 entry=p;gateway(&p,0,walking_light_shutdown,tail,0);
 p=walking_detour(&walking_hooks[7],p,0x69fdd0,(B*)"\xa1\x9c\x86\x82\x00",5,entry);
 tail=p;memcpy(p,"\x8b\x4d\xfc\x8b\x45\xec",6);p+=6;branch(&p,0xe9,(void*)0x6f1e47);
 entry=p;gateway(&p,0,walking_light_vertex,tail,0);
 p=walking_detour(&walking_hooks[8],p,0x6f1e41,(B*)"\x8b\x4d\xfc\x8b\x45\xec",6,entry);
 tail=p;memcpy(p,"\x8b\x4d\xe4\x8b\x55\xfc",6);p+=6;branch(&p,0xe9,(void*)0x6f2211);
 entry=p;gateway(&p,1,walking_light_vertex,tail,0);
 p=walking_detour(&walking_hooks[9],p,0x6f220b,(B*)"\x8b\x4d\xe4\x8b\x55\xfc",6,entry);
 tail=p;memcpy(p,"\x8b\x8e\x90\x01\x00\x00",6);p+=6;branch(&p,0xe9,(void*)0x69e0fa);
 entry=p;gateway(&p,0,walking_light_object,tail,0);
 p=walking_detour(&walking_hooks[10],p,0x69e0f4,(B*)"\x8b\x8e\x90\x01\x00\x00",6,entry);
 tail=p;memcpy(p,"\x8b\x91\x90\x01\x00\x00",6);p+=6;branch(&p,0xe9,(void*)0x69d801);
 entry=p;gateway(&p,1,walking_light_object,tail,0);
 p=walking_detour(&walking_hooks[11],p,0x69d7fb,(B*)"\x8b\x91\x90\x01\x00\x00",6,entry);
 tail=p;memcpy(p,"\x8b\x91\x88\x01\x00\x00",6);p+=6;branch(&p,0xe9,(void*)0x69e5c7);
 entry=p;gateway(&p,2,walking_light_object,tail,0);
 p=walking_detour(&walking_hooks[12],p,0x69e5c1,(B*)"\x8b\x91\x88\x01\x00\x00",6,entry);
 tail=p;memcpy(p,"\x8b\x91\x88\x01\x00\x00",6);p+=6;branch(&p,0xe9,(void*)0x69e9bb);
 entry=p;gateway(&p,3,walking_light_object,tail,0);
 p=walking_detour(&walking_hooks[13],p,0x69e9b5,(B*)"\x8b\x91\x88\x01\x00\x00",6,entry);
 /* Alternate shaders selected by 0x69eae0 for track materials. Native cone
    diffuse here is independent of the surface normal; retain native specular. */
 tail=p;memcpy(p,"\x8b\x86\x88\x01\x00\x00",6);p+=6;branch(&p,0xe9,(void*)0x69f70a);
 entry=p;gateway(&p,4,walking_light_object,tail,0);
 p=walking_detour(&walking_hooks[14],p,0x69f704,(B*)"\x8b\x86\x88\x01\x00\x00",6,entry);
 tail=p;memcpy(p,"\x8b\x91\x88\x01\x00\x00",6);p+=6;branch(&p,0xe9,(void*)0x69ef2b);
 entry=p;gateway(&p,5,walking_light_object,tail,0);
 p=walking_detour(&walking_hooks[15],p,0x69ef25,(B*)"\x8b\x91\x88\x01\x00\x00",6,entry);
 if(!crawl_requested){
  tail=p;memcpy(p,"\x8b\x7c\x24\x18\x8b\x07",6);p+=6;branch(&p,0xe9,(void*)0x6bae14);
  entry=p;gateway(&p,0,walking_event_gateway,tail,0);
  p=walking_detour(&walking_hooks[count++],p,0x6bae0e,(B*)"\x8b\x7c\x24\x18\x8b\x07",6,entry);
 }
 if(p>walking_code+2048)return 0;
 if(!VirtualProtect(walking_code,2048,PAGE_EXECUTE_READ,&old))return 0;FlushInstructionCache(GetCurrentProcess(),walking_code,2048);
 if(!prepare_hooks(walking_hooks,count)||!install_hooks(walking_hooks,count))return 0;
 walking_activate=walking_activate_bridge;
 walking_reset();walking_ready=1;return 1;
}
