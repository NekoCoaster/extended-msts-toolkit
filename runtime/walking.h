/* MIT. Experimental native walking adapter, supported MSTS Bin images only.
   All native world queries and camera changes run on MSTS's own frame thread. */
#include "walking-model.h"
typedef int (__fastcall *WalkGroundFn)(float*,U,float,float);
typedef void (__fastcall *WalkActivateFn)(void*);
static WalkGroundFn walking_query=(WalkGroundFn)0x530635;
static WalkActivateFn walking_activate=(WalkActivateFn)0x51cd5f;
static WalkState walking_state;
static U walking_view[0x1a8/4],walking_previous,walking_train;
static int walking_ready,walking_pending,walking_toggle_down,walking_pan;
static const char *walking_status="Not initialized";
static void (*walking_camera_original)(void),(*walking_input_original)(void);
static Hook walking_hooks[3];static B *walking_code;
static U walking_event_copy[4];
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
static void walking_key_edge(U scan,int down,int allowed){
 U i;int edge;if(scan>=238)return;
 edge=down&&!walking_event_held[scan];walking_event_held[scan]=down!=0;
 if(walking_input_active&&edge&&allowed){
  for(i=0;i<6;i++)if(scan==editor_keys[i])walking_pulses|=1<<i;
  if(scan==0x39)walking_pulses|=64;if(scan==0x2f)walking_pulses|=128;
 }
 if(scan==walking_toggle_scan){if(edge&&allowed)walking_pending=1;walking_toggle_down=down!=0;}
}
static void walking_event(Registers *r){
 U *stack=(U*)(r->esp+4),*event=(U*)stack[6],*device=(U*)stack[9],scan;
 if(!walking_ready||!event||!device||!device[1]||*((B*)device[1]+0x2d)!=1||(event[0]>>16)!=1||event[1]>1)return;
 scan=event[0]&0xffff;if(scan>=238)return;
 walking_key_edge(scan,event[1]!=0,!stack[10]&&!paused()&&crawl_control_focus());
 if(scan!=walking_toggle_scan)return;
 memcpy(walking_event_copy,event,16);walking_event_copy[0]=0x10000;stack[6]=(U)walking_event_copy;
}
static void walking_event_gateway(U id,Registers *r){walking_event(r);}
static void walking_reset(void){
 walking_state.active=walking_input_active=walking_pending=walking_pan=0;
 walking_previous=walking_train=0;walking_status="Standby";
 walking_pulses=0;memset(walking_event_held,0,sizeof(walking_event_held));
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
  if(view==(U)walking_view&&walking_previous)walking_activate((void*)walking_previous);
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
 /* Static view is deliberately NOT registered in MSTS's owning view list. */
 memcpy(walking_view,(void*)view,sizeof(walking_view));memset(walking_view,0,20);
 walking_view[0x9c/4]=walking_view[0x118/4]=0;walking_view[0x11c/4]=9;
 walking_view[0x90/4]=walking_view[0x94/4]=walking_view[0x98/4]=0;
 walking_previous=view;walking_train=*(U*)G(0x7c2ac0);walking_matrix();
 walking_activate(walking_view);walking_input_active=1;walking_pending=0;walking_status="Walking";return 1;
}
static void walking_camera(void){
 WalkInput in;B bits[32];POINT point,center;RECT rect;HWND window;U i;double dt=*(float*)G(0x828fb4);
 if(walking_state.active&&(*(U*)G(0x7c2ac0)!=walking_train||*(U*)G(0x7c2a88)!=(U)walking_view))walking_reset();
 if(walking_state.active){
  memset(&in,0,sizeof(in));
  if(!paused()&&crawl_control_focus()&&walking_keys(bits)){
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
    SetCursorPos(center.x,center.y);walking_pan=1;
   }else walking_pan=0;
   walk_step(&walking_state,&in,dt,0,walking_ground,NULL);
  }else{
   walking_pan=0;walking_state.previous_jump=walking_state.previous_up=walking_state.previous_down=walking_state.previous_noclip=1;
  }
  walking_pulses=0;
  walking_matrix();walking_status=walking_state.noclip?"Noclip":walking_state.grounded?"Walking":"Jumping";
 }
 walking_camera_original();
}
/* Suppress action dispatch, including the native held-callback queue. Native
   event bookkeeping still runs, so releases do not leave stuck counters. */
typedef struct {U address,identity;B disabled;} WalkActionMask;
static WalkActionMask walking_masks[1024];
static int walking_masks_count;
typedef struct {U address,first,last;} WalkDeviceMask;
static WalkDeviceMask walking_devices[32];static int walking_device_count;
static U walking_allowed[32];static int walking_allowed_count;
static int walking_collect_allowed(void){
 U head,node,n[3],device[7],input,bind[4],scan,k,budget=64;B kind;
 walking_allowed_count=0;
 if(!read_memory(G(0x8299a0),&head,4)||!head||!read_memory(head,&node,4))return 0;
 while(node!=head&&budget--){
  if(!read_memory(node,n,12)||!read_memory(n[2],device,sizeof(device)))return 0;node=n[0];input=device[1];
  if(!input||!read_memory(input+0x2d,&kind,1)||kind!=1)continue;
  for(k=0;k<2;k++){
   scan=k?0x3f:1;if(device[5]-device[4]<=scan)return 0;
   if(!read_memory(device[6]+(device[4]+scan)*16,bind,16))return 0;
   for(;;){
    if(bind[0]){if(walking_allowed_count==32)return 0;walking_allowed[walking_allowed_count++]=bind[0];}
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
  if(i==(U)walking_allowed_count)*(B*)(action+0x12)=flags|2;
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
   if(*(U*)G(0x7c2a88)==(U)walking_view&&walking_previous)walking_activate((void*)walking_previous);
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
 B *p,*tail,*entry;DWORD old;U count=2;
 if(!walking_requested)return 1;
 if(memcmp((void*)0x530635,"\x55\x8b\xec\x83\xec\x08",6)||memcmp((void*)0x51cd5f,"\x55\x8b\xec",3))return 0;
 walking_code=VirtualAlloc(NULL,1024,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!walking_code)return 0;p=walking_code;
 walking_camera_original=(void*)p;p=walking_detour(&walking_hooks[0],p,0x51cfd5,(B*)"\x55\x8b\xec\x83\xec\x44",6,walking_camera);
 walking_input_original=(void*)p;p=walking_detour(&walking_hooks[1],p,0x6bad60,(B*)"\x83\xec\x44\x53\x55",5,walking_input);
 if(!crawl_requested){
  tail=p;memcpy(p,"\x8b\x7c\x24\x18\x8b\x07",6);p+=6;branch(&p,0xe9,(void*)0x6bae14);
  entry=p;gateway(&p,0,walking_event_gateway,tail,0);
  walking_detour(&walking_hooks[count++],p,0x6bae0e,(B*)"\x8b\x7c\x24\x18\x8b\x07",6,entry);
 }
 if(!VirtualProtect(walking_code,1024,PAGE_EXECUTE_READ,&old))return 0;FlushInstructionCache(GetCurrentProcess(),walking_code,1024);
 if(!prepare_hooks(walking_hooks,count)||!install_hooks(walking_hooks,count))return 0;
 walking_reset();walking_ready=1;return 1;
}
