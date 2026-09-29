#include <assert.h>
static unsigned char globals[0x110000];
#define G(a) ((U)globals+(a)-0x790000)
#include "../runtime/loader.c"
static U head[3],node[3],device[11],table[238*4],actions[3][6],action_name[5];
static B input[48],bits[30];
static int ground_result=1;static float ground_normal=1;
static int fov_activations,proc_calls;
static int modifier_flags;
static SHORT WINAPI fake_key_state(int key){
 assert(key==VK_LSHIFT||key==VK_LMENU);
 return (modifier_flags&(key==VK_LSHIFT?1:2))?(SHORT)0x8000:0;
}
static HCURSOR fake_cursor=(HCURSOR)1234;
static HCURSOR WINAPI fake_set_cursor(HCURSOR c){HCURSOR old=fake_cursor;fake_cursor=c;return old;}
static HCURSOR WINAPI fake_get_cursor(void){return fake_cursor;}
static void __fastcall fake_activate(void *view){assert(view==walking_view);fov_activations++;}
static U camera_head[3],camera_node[3],native_view[0x1a8/4];
static B camera_train[512],camera_car[512];static int handoff_calls,handoff_reject;
static void __fastcall fake_handoff(void *view){
 U outgoing=*(U*)G(0x7c2a88),car=*(U*)(outgoing+0x9c);B transform[48];
 assert(view==native_view&&car==(U)camera_car);
 /* Mirror the native 0x51949a/0x5194ae outgoing-car matrix read. */
 memcpy(transform,(void*)(car+0x20),48);assert(transform[0]==0x42);
 handoff_calls++;if(!handoff_reject)*(U*)G(0x7c2a88)=(U)view;
}
static void setup_handoff(void){
 memset(native_view,0,sizeof(native_view));memset(camera_car,0,sizeof(camera_car));
 camera_head[0]=(U)camera_node;camera_node[0]=(U)camera_head;camera_node[2]=(U)native_view;
 *(U*)G(0x7c2ac8)=(U)camera_head;*(U*)G(0x7c2ac0)=(U)camera_train;
 *(U*)(camera_train+0x6a)=(U)camera_car;*(U*)(camera_car+0x98)=(U)camera_train;camera_car[0x20]=0x42;
 native_view[0x9c/4]=(U)camera_car;native_view[0x11c/4]=6;
 walking_train=(U)camera_train;walking_previous=(U)native_view;
 walking_state.active=walking_input_active=1;walking_state.eye_height=2;
 walking_view[0x9c/4]=0;*(U*)G(0x7c2a88)=(U)walking_view;
 walking_activate_original=fake_handoff;walking_activate=walking_activate_bridge;handoff_reject=0;
}
static void fake_camera_input(void){
 assert(table[3*4]==(U)actions[0]); /* Physical number-row 2. */
 assert(!(*(B*)((U)actions[0]+0x12)&2));assert(*(B*)((U)actions[1]+0x12)&2);
 assert(!device[8]&&!device[10]);walking_activate_bridge(native_view);
}
static LRESULT CALLBACK fake_proc(HWND h,UINT m,WPARAM w,LPARAM l){proc_calls++;return 123;}
static int __fastcall fake_ground(float *out,U flags,float x,float z){assert(flags==2);out[0]=123;out[1]=0;out[2]=ground_normal;out[3]=0;return ground_result;}
static void setup(void){
 memset(globals,0,sizeof(globals));memset(actions,0,sizeof(actions));memset(table,0,sizeof(table));
 head[0]=(U)node;node[0]=(U)head;node[2]=(U)device;
 device[1]=(U)input;device[4]=0;device[5]=238;device[6]=(U)table;device[8]=0x1234;device[10]=0x5678;
 input[0x2d]=1;*(U*)(input+0x24)=(U)bits;
 *(U*)G(0x8299a0)=(U)head;*(U*)G(0x829974)=(U)actions[0];
 actions[0][2]=(U)actions[1];actions[1][2]=(U)actions[2];
 table[1*4]=(U)actions[1];table[0x3f*4]=(U)actions[2];
}
static void fake_rebase_camera_frame(void){
 assert(walking_state.x==-1023.75);
 *(int*)G(0x79d11c)+=1;
}
static void test_tile_rebase(void){
 int mode,axis,sign,i;char lines[WALK_HUD_LINES][240];
 for(mode=0;mode<2;mode++)for(axis=0;axis<2;axis++)for(sign=-1;sign<=1;sign+=2){
  double wx,wz;
  memset(&walking_state,0,sizeof(walking_state));walking_state.active=1;walking_state.noclip=mode;
  walking_state.x=axis?17:sign*1024.25;walking_state.z=axis?sign*1024.25:17;
  walking_state.y=123;walking_state.eye_height=2;walking_state.velocity_x=3;walking_state.vertical_speed=-4;
  walking_origin_x=*(int*)G(0x79d118)=-5993;walking_origin_z=*(int*)G(0x79d11c)=14532;
  wx=walking_origin_x*2048.0+walking_state.x;wz=walking_origin_z*2048.0+walking_state.z;
  walking_matrix();
  /* Mirror the native origin shift, which skips our unregistered view. */
  *(int*)G(axis?0x79d11c:0x79d118)+=sign;
  walking_sync_origin();
  assert(walking_state.x+walking_origin_x*2048.0==wx&&walking_state.z+walking_origin_z*2048.0==wz);
  assert(walking_state.x>=-1024&&walking_state.x<1024&&walking_state.z>=-1024&&walking_state.z<1024);
  for(i=0;i<100;i++){walking_sync_origin();walking_matrix();}
  assert(walking_state.x+walking_origin_x*2048.0==wx&&walking_state.z+walking_origin_z*2048.0==wz);
  assert(*(float*)((B*)walking_view+0x38)==walking_state.x&&*(float*)((B*)walking_view+0x68)==walking_state.x);
  assert(*(float*)((B*)walking_view+0x40)==walking_state.z&&*(float*)((B*)walking_view+0x70)==walking_state.z);
  assert(walking_state.y==123&&walking_state.eye_height==2&&walking_state.velocity_x==3&&walking_state.vertical_speed==-4&&walking_state.noclip==mode);
  /* HUD can run before the next movement callback; diagonal/multi-tile shift. */
  *(int*)G(0x79d118)+=3;*(int*)G(0x79d11c)-=2;walking_hud_lines(lines);
  assert(walking_state.x+walking_origin_x*2048.0==wx&&walking_state.z+walking_origin_z*2048.0==wz);
 }
 /* Even paused/unfocused frames synchronize before native work and after it. */
 walking_origin_x=*(int*)G(0x79d118)=10;walking_origin_z=*(int*)G(0x79d11c)=10;
 walking_state.x=1024.25;walking_state.z=1024.25;walking_state.active=1;
 walking_train=*(U*)G(0x7c2ac0)=1234;*(U*)G(0x7c2a88)=(U)walking_view;
 *(U*)G(0x7be0f4)=1;*(int*)G(0x79d118)=11;
 walking_camera_original=fake_rebase_camera_frame;walking_camera();
 assert(walking_state.x==-1023.75&&walking_state.z==-1023.75);
 assert(walking_origin_x==11&&walking_origin_z==11);
 *(U*)G(0x7be0f4)=0;
 walking_reset();
}
int main(void){
 char lines[WALK_HUD_LINES][240];B readbits[32];int i;double height;
 walking_set_cursor=fake_set_cursor;walking_get_cursor=fake_get_cursor;
 {WalkInput in;walking_key_state=fake_key_state;
  for(modifier_flags=0;modifier_flags<4;modifier_flags++){
   memset(&in,0,sizeof(in));walking_modifiers(&in);
   assert(in.sprint==!!(modifier_flags&1)&&in.slow==!!(modifier_flags&2));
  }
  modifier_flags=0;walking_modifiers(&in);assert(!in.sprint&&!in.slow);
 }
 test_tile_rebase();
 walking_cursor(1);walking_cursor(1);assert(!fake_cursor&&walking_cursor_hidden);
 walking_cursor(0);assert(fake_cursor==(HCURSOR)1234&&!walking_cursor_hidden);
 walking_cursor(1);fake_cursor=(HCURSOR)5678;walking_cursor(0);assert(fake_cursor==(HCURSOR)5678);
 setup();bits[0x11>>3]=1<<(0x11&7);assert(walking_keys(readbits)&&crawl_key(readbits,0x11));
 assert(walking_toggle_scan==0x29&&editor_key_parse(L"`")==0x29&&editor_key_parse(L"BACKQUOTE")==0x29);
 walking_query=fake_ground;assert(!walking_ground(0,0,0,&height));*(U*)G(0x7c2e08)=1;
 assert(walking_ground(0,0,0,&height)&&height==123);ground_normal=0;assert(!walking_ground(0,0,0,&height));
 ground_normal=1;ground_result=0;assert(!walking_ground(0,0,0,&height));ground_result=1;
 assert(readbits[30]==0&&readbits[31]==0);
 assert(walking_mask());assert(*(B*)((U)actions[0]+0x12)&2);
 assert(!(*(B*)((U)actions[1]+0x12)&2));assert(!(*(B*)((U)actions[2]+0x12)&2));
 assert(!device[8]&&!device[10]);
 *(B*)((U)actions[0]+0x12)|=4; /* Native unrelated flag changes survive. */
 walking_unmask();assert(*(B*)((U)actions[0]+0x12)==4);assert(device[8]==0x1234&&device[10]==0x5678);
 *(B*)((U)actions[0]+0x12)=2;assert(walking_mask());walking_unmask();assert(*(B*)((U)actions[0]+0x12)==2);
 *(U*)G(0x7be0f4)=1;assert(walking_mask());assert(device[8]==0x1234&&device[10]==0x5678);walking_unmask();
 actions[0][2]=(U)actions[0];assert(!walking_mask());assert(walking_masks_count==0&&walking_device_count==0);
 setup();assert(walking_mask());*(U*)G(0x829974)=(U)actions[1];walking_unmask();assert(*(B*)((U)actions[0]+0x12)&2); /* Unregistered node was not touched. */
 for(i=0;i<238;i++)if(walking_function_key(i)){
  setup();table[i*4]=(U)actions[0];assert(walking_mask());assert(!(*(B*)((U)actions[0]+0x12)&2));walking_unmask();
 }
 setup();actions[0][0]=(U)action_name;action_name[4]=(U)L"Camera_FrontTracking";assert(walking_view_action((U)actions[0]));
 for(i=2;i<=11;i++){table[i*4]=(U)actions[0];assert(walking_mask());assert(!(*(B*)((U)actions[0]+0x12)&2));walking_unmask();}
 table[0x17*4]=(U)actions[0];assert(walking_mask());assert(!(*(B*)((U)actions[0]+0x12)&2));walking_unmask(); /* Remapped camera. */
 action_name[4]=(U)L"ThrottleIncrease";assert(!walking_view_action((U)actions[0]));
 assert(walking_mask());assert(*(B*)((U)actions[0]+0x12)&2);walking_unmask(); /* Numeric train remaps remain blocked. */
 action_name[4]=0;assert(!walking_view_action((U)actions[0]));
 setup();walking_reset();walking_hud_lines(lines);assert(strstr(lines[0],"Standby"));
 walking_initial_eye_height=1.75;walking_initial_fov=67;walking_input_active=walking_state.active=1;
 walking_state.noclip=1;walking_state.x=12;walking_state.y=50;walking_state.eye_height=99;walking_fov=5;
 walking_wheel_remainder=60;walking_state.height_hold=2;walking_state.height_fraction=0.02;
 walking_key_edge(0x09,1,1);assert(walking_state.eye_height==1.75&&walking_fov==67&&walking_fov_dirty);
 assert(walking_state.active&&walking_state.noclip&&walking_state.x==12&&walking_state.y==50&&!walking_pending);
 assert(!walking_wheel_remainder&&!walking_state.height_hold&&!walking_state.height_fraction);
 walking_state.eye_height=3;walking_key_edge(0x09,1,1);assert(walking_state.eye_height==3); /* No held reset repeat. */
 walking_key_edge(0x09,0,1);walking_key_edge(0x09,1,0);assert(walking_state.eye_height==3); /* Paused/unfocused. */
 walking_key_edge(0x09,0,1);walking_input_active=0;walking_key_edge(0x09,1,1);assert(walking_state.eye_height==3);
 walking_initial_eye_height=2;walking_initial_fov=60;walking_reset();
 {U stack[12]={0},event[4]={0x10009,1,0,0};Registers regs;
  memset(&regs,0,sizeof(regs));regs.esp=(U)stack-4;stack[6]=(U)event;stack[9]=(U)device;
  walking_ready=1;walking_input_active=1;*(U*)G(0x7be0f4)=1;
  walking_event(&regs);assert(stack[6]==(U)walking_event_copy&&walking_event_copy[0]==0x10000);
  walking_input_active=0;stack[6]=(U)event;walking_event(&regs);assert(stack[6]==(U)event);
  walking_input_active=1;event[0]=0x10008;walking_event(&regs);assert(stack[6]==(U)event);
  *(U*)G(0x7be0f4)=0;walking_reset();
 }
 walking_input_active=1;walking_key_edge(0x39,1,1);walking_key_edge(0x39,0,1);assert(walking_pulses==64);
 walking_pulses=0;walking_key_edge(0x39,1,1);walking_pulses=0;walking_key_edge(0x39,1,1);assert(!walking_pulses);
 walking_key_edge(0x39,0,1);walking_key_edge(0x39,1,0);assert(!walking_pulses);
 walking_key_edge(editor_keys[4],1,1);assert(walking_pulses==16);walking_pulses=0;
 walking_key_edge(0x2f,1,1);assert(walking_pulses==128);
 walking_key_edge(walking_toggle_scan,1,1);assert(walking_pending);walking_pending=0;
 walking_key_edge(walking_toggle_scan,1,1);assert(!walking_pending);
 walking_fov=60;walking_fov_dirty=0;walking_key_edge(0x0d,1,1);assert(walking_fov==55&&walking_fov_dirty);
 walking_key_edge(0x0d,1,1);assert(walking_fov==55); /* Held key does not repeat. */
 walking_key_edge(0x0d,0,1);walking_key_edge(0x0d,1,0);assert(walking_fov==55);
 walking_key_edge(0x0c,1,1);assert(walking_fov==60);
 walking_wheel_remainder=0;assert(walking_wheel(60,1)&&walking_fov==60);
 assert(walking_wheel(60,1)&&walking_fov==55);
 walking_wheel(-240,1);assert(walking_fov==65);
 walking_wheel(60,1);walking_wheel(-60,1);assert(walking_fov==65&&!walking_wheel_remainder);
 walking_wheel(60,1);assert(!walking_wheel(120,0)&&walking_fov==65&&!walking_wheel_remainder);
 walking_fov=1;walking_wheel(120,1);assert(walking_fov==1);walking_wheel(-120,1);assert(walking_fov==5);
 walking_fov=179;walking_wheel(-120,1);assert(walking_fov==179);walking_wheel(120,1);assert(walking_fov==175);
 walking_wheel(60,1);walking_reset();assert(!walking_wheel_remainder&&!walking_fov_dirty);
 walking_activate=fake_activate;walking_fov_adjust(1);walking_apply_fov();
 assert(fov_activations==1&&!walking_fov_dirty&&fabs(*(float*)((B*)walking_view+0x84)-179*0.017453292519943295)<1e-6);
 walking_apply_fov();assert(fov_activations==1);
 walking_original_proc=fake_proc;walking_wheel_remainder=60;
 assert(walking_proc(NULL,WM_KILLFOCUS,0,0)==123&&!walking_wheel_remainder&&proc_calls==1);
 assert(walking_proc(NULL,WM_MOUSEWHEEL,120<<16,0)==123&&proc_calls==2); /* Inactive: native path. */
 walking_cursor(1);walking_pan=1;walking_proc(NULL,WM_RBUTTONUP,0,0);assert(!walking_pan&&!walking_cursor_hidden&&fake_cursor==(HCURSOR)5678);
 walking_cursor(1);walking_reset();assert(!walking_cursor_hidden&&fake_cursor==(HCURSOR)5678);
 walking_state.active=walking_input_active=1;walking_state.x=2050;walking_state.z=-1025;walking_state.y=20;walking_state.eye_height=2;
 *(int*)G(0x79d118)=100;*(int*)G(0x79d11c)=-50;
 walking_origin_x=100;walking_origin_z=-50;
 walking_status="Walking";walking_hud_lines(lines);assert(strstr(lines[0],"BLOCKED"));assert(strstr(lines[1],"101 / -51"));assert(strstr(lines[2],"Eyes Y: 22.00"));
 walking_state.noclip=1;walking_hud_lines(lines);assert(strstr(lines[0],"Noclip: ON"));
 assert(strstr(lines[2],"FOV: 179.0 deg"));assert(strstr(lines[3],"wheel up/down or =/-"));
 editor_keys[0]=0x17;walking_toggle_scan=0x57;walking_hud_lines(lines);assert(strstr(lines[3],"Walk=F11")&&strstr(lines[3],"Move=I/"));
 setup_handoff();walking_activate_bridge(native_view);assert(handoff_calls==1&&!walking_state.active&&!walking_input_active&&!walking_view[0x9c/4]);
 setup_handoff();assert(walking_return_view());assert(handoff_calls==2&&!walking_state.active); /* Return to derailment view. */
 setup_handoff();native_view[0x9c/4]=0;walking_activate_bridge(native_view);assert(handoff_calls==3); /* First derail: use controlled car. */
 setup_handoff();walking_previous=1;*(U*)G(0x7c2a8c)=(U)native_view;assert(walking_return_view());assert(handoff_calls==4); /* Stale return pointer. */
 setup_handoff();walking_previous=1;*(U*)G(0x7c2a8c)=0;assert(!walking_return_view());assert(handoff_calls==4&&walking_state.active);
 setup_handoff();*(U*)(camera_car+0x98)=0;walking_activate_bridge(native_view);assert(handoff_calls==4&&walking_state.active&&!walking_view[0x9c/4]);
 setup_handoff();handoff_reject=1;walking_activate_bridge(native_view);assert(handoff_calls==5&&walking_state.active&&!walking_view[0x9c/4]);
 setup_handoff();camera_node[0]=(U)camera_node;assert(!walking_registered_view(123));
 setup();setup_handoff();actions[0][0]=(U)action_name;action_name[4]=(U)L"Camera_FrontTracking";
 table[1*4]=0;table[3*4]=(U)actions[0];walking_ready=1;walking_pending=0;walking_input_original=fake_camera_input;
 walking_input();assert(!walking_state.active&&!walking_input_active&&*(U*)G(0x7c2a88)==(U)native_view);
 assert(!(*(B*)((U)actions[1]+0x12)&2)&&device[8]==0x1234&&device[10]==0x5678);
 puts("PASS walking native adapter: key bounds, train action masking, F5/Escape allowance, raw device isolation, flag restoration, bounded corrupt-list rejection and walking HUD.");return 0;
}
