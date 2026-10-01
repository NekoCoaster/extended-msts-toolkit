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

static U light_head[3],light_node[3],other_node[3],light_data[36],other_light[36];
static U light_camera[16];static int light_creates,light_releases,light_sets,light_verify_ok=1;
static float light_params[12];
static int fake_light_verify(void){return light_verify_ok;}
static void __fastcall fake_light_set(void *p,const float *data){assert(p==light_data);memcpy(light_params,data,sizeof(light_params));memcpy((B*)p+0x1c,data,sizeof(light_params));light_sets++;}
static void *__fastcall fake_light_create(U type,U flags,const float *data){
 assert(type==2&&flags==0x21);light_creates++;memset(light_data,0,sizeof(light_data));
 light_data[0]=G(0x828868);light_data[1]=1;light_data[2]=2;light_data[3]=flags;
 light_node[0]=light_head[0];light_node[2]=(U)light_data;light_head[0]=(U)light_node;
 fake_light_set(light_data,data);return light_data;
}
static int __fastcall fake_light_release(void *p){assert(p==light_data);light_releases++;light_head[0]=light_node[0];return 0;}
static void test_flashlight(void){
 float *m=(float*)((B*)light_camera+12);int before;
 memset(globals,0,sizeof(globals));memset(light_camera,0,sizeof(light_camera));
 flashlight_create=fake_light_create;flashlight_set=fake_light_set;flashlight_release=fake_light_release;flashlight_verify=fake_light_verify;
 light_head[0]=(U)other_node;other_node[0]=(U)light_head;other_node[2]=(U)other_light;other_light[3]=5;
 *(U*)G(0x8287b4)=1;*(U*)G(0x828694)=(U)light_head;*(U*)G(0x8287b0)=(U)other_light;
 m[0]=m[4]=m[8]=1;m[9]=100;m[10]=2;m[11]=200;
 flashlight_update((U)light_camera,0);assert(!light_creates);
 flashlight_update((U)light_camera,1);assert(light_creates==1&&flashlight_object==(U)light_data);
 assert(*(U*)G(0x8287b0)==(U)other_light&&flashlight_frame_active);
 assert(light_params[4]==100&&light_params[5]==2&&fabs(light_params[6]-200.15)<0.001);
 assert(light_params[8]==0&&light_params[9]==0&&light_params[10]==1&&light_params[7]==45);
 {float point[3]={light_params[4],light_params[5],light_params[6]+25};U c,stack[16]={0};Registers r={0};
  c=flashlight_terrain_colour(point,0xff102030);assert((c&0xffffff)>0x102030&&(c>>24)==255);
  r.edi=(U)point;r.ebp=(U)(stack+8);stack[1]=(U)point;stack[7]=0xff102030;
  walking_light_vertex(0,&r);assert(stack[7]==c);stack[7]=0xff102030;walking_light_vertex(1,&r);assert(stack[7]==c);
  assert(flashlight_terrain_colour(point,0xffffffff)==0xffffffff);
  point[2]-=50;assert(flashlight_terrain_colour(point,0xff102030)==0xff102030);
  point[2]+=1000;assert(flashlight_terrain_colour(point,0xff102030)==0xff102030);
  point[2]=light_params[6]+25;*(U*)G(0x8287b0)=flashlight_object;assert(flashlight_terrain_colour(point,0xff102030)==0xff102030);
  *(U*)G(0x8287b0)=(U)other_light;
 }
 {float matrix[15]={1,0,0,0,1,0,0,0,1,0,0,0,0,0,0},v[10]={0,0,25.15f,0,0,-1};U lit;
  lit=flashlight_object_colour(v,matrix,0x7f102030,1,0);assert((lit>>24)==0x7f&&(lit&0xffffff)>0x102030);
  {U state[0x208/4]={0},output[8]={0,0,0,0,0x7f102030,0xa5123456,0x3f800000,0x40000000};Registers r={0};U expected,mode;
   *(U*)G(0x82898c)=(U)matrix;state[0x188/4]=(U)v;state[0x190/4]=(U)output;
   state[0x1e0/4]=0x1234;v[5]=1; /* Native track cone diffuse ignores Lambert facing. */
   expected=flashlight_object_colour(v,matrix,output[4],0,0);assert(expected!=output[4]);
   for(mode=4;mode<=5;mode++){
    r.esi=mode==4?(U)state:0;r.ecx=mode==5?(U)state:0;output[4]=0x7f102030;
    walking_light_object(mode,&r);assert(output[4]==expected);
    assert(output[5]==0xa5123456&&output[6]==0x3f800000&&output[7]==0x40000000);
    state[0x1e0/4]=flashlight_object;output[4]=0x7f102030;walking_light_object(mode,&r);assert(output[4]==0x7f102030);
    state[0x1e0/4]=0x1234;flashlight_frame_active=0;walking_light_object(mode,&r);assert(output[4]==0x7f102030);flashlight_frame_active=1;
   }v[5]=-1;
  }
  matrix[12]=100;v[0]=100;assert(flashlight_object_colour(v,matrix,0x7f102030,1,0)==lit);
  matrix[12]-=2048;v[0]-=2048;assert(flashlight_object_colour(v,matrix,0x7f102030,1,0)==lit);
  v[5]=1;assert(flashlight_object_colour(v,matrix,0x7f102030,1,0)==0x7f102030);
  assert(flashlight_object_colour(v,matrix,0x7f102030,0,0)==lit);
  *(U*)(v+6)=0;assert(flashlight_object_colour(v,matrix,0x7f102030,0,1)==0x7f102030);
  v[2]=25.15f;assert(flashlight_object_colour(v,matrix,0xffffffff,0,0)==0xffffffff);
  flashlight_frame_active=0;assert(flashlight_object_colour(v,matrix,0x7f102030,0,0)==0x7f102030);flashlight_frame_active=1;
  {float rotated[15]={0,0,1,0,1,0,-1,0,0,0,0,0,0,0,0},rv[10]={25.15f,0,0,-1,0,0};assert(flashlight_object_colour(rv,rotated,0x7f102030,1,0)==lit);}
  v[2]=1000;assert(flashlight_object_colour(v,matrix,0x7f102030,0,0)==0x7f102030);
  v[2]=-25;assert(flashlight_object_colour(v,matrix,0x7f102030,0,0)==0x7f102030);
 }
 /* Updated camera coordinates, including a floating-origin shift, are used
    directly; one light is reused while the view changes. */
 m[9]-=2048;m[6]=1;m[8]=0;flashlight_update((U)light_camera,1);
 assert(light_creates==1&&fabs(light_params[4]-(-1947.85))<0.001&&light_params[8]==1);

 {U tile[32]={0},patch[8]={0},descriptor[8]={0};Registers r={0};
  descriptor[0]=(U)tile;descriptor[2]=16;
  *(int*)(tile+4)=-1952;*(int*)(tile+5)=208;*(float*)(tile+7)=1;
  assert(flashlight_near_patch((U)patch,(U)descriptor));
  r.ecx=r.esi=(U)patch;r.edx=r.ebx=(U)descriptor;
  walking_light_terrain(0,&r);assert(patch[0]&0x100);
  patch[0]&=~0x100; /* native draw clears its rebuilt vertex cache */
  walking_light_terrain(1,&r);assert(patch[0]&0x100); /* next draw refreshes, even after off */
  *(int*)(tile+4)=10000;patch[0]=0;walking_light_terrain(0,&r);assert(!(patch[0]&0x100));
  *(float*)(tile+7)=0;assert(!flashlight_near_patch((U)patch,(U)descriptor));
 }
 flashlight_update((U)light_camera,0);assert(light_releases==1&&!flashlight_object);
 assert(*(U*)G(0x8287b0)==(U)other_light&&*(U*)G(0x8287b4)==1);
 flashlight_stop();assert(light_releases==1); /* idempotent */
 flashlight_update((U)light_camera,1);
 /* Train light disappears while flashlight is active: no stale restoration. */
 light_node[0]=(U)light_head;*(U*)G(0x8287b0)=0;flashlight_stop();assert(!*(U*)G(0x8287b0));
 *(U*)G(0x8287b0)=0;flashlight_update((U)light_camera,1);
 assert(*(U*)G(0x8287b0)==flashlight_object); /* solo beam uses native path */
 *(U*)G(0x8287b0)=(U)other_light; /* native train enables its beam later */
 flashlight_update((U)light_camera,1);assert(*(U*)G(0x8287b0)==(U)other_light);
 flashlight_stop();assert(*(U*)G(0x8287b0)==(U)other_light&&!flashlight_frame_active);
 *(U*)G(0x8287b0)=0;
 flashlight_update((U)light_camera,1);before=light_releases;
 /* Simulate renderer owning/freeing its list before the next NEMT callback. */
 light_head[0]=(U)light_head;flashlight_stop();assert(light_releases==before&&!flashlight_object);
 light_verify_ok=0;before=light_creates;flashlight_update((U)light_camera,1);
 assert(light_creates==before&&flashlight_failed);light_verify_ok=1;
 flashlight_update((U)light_camera,1);assert(!flashlight_failed);
 flashlight_update(0,1);assert(!flashlight_object); /* invalid camera cleans up */
 flashlight_update((U)light_camera,1);before=light_releases;
 flashlight_renderer_shutdown();assert(!flashlight_object&&!flashlight_frame_active&&!*(U*)G(0x8287b0));
 assert(light_releases==before); /* native shutdown, not NEMT, owns this release */
 light_head[0]=(U)light_head;
 walking_input_active=1;walking_flashlight_available=1;walking_flashlight=0;
 memset(walking_event_held,0,sizeof(walking_event_held));
 walking_key_edge(0x26,1,1);assert(walking_flashlight);
 walking_key_edge(0x26,1,1);assert(walking_flashlight); /* held key */
 walking_key_edge(0x26,0,1);walking_key_edge(0x26,1,0);assert(walking_flashlight); /* paused/unfocused */
 walking_key_edge(0x26,0,1);walking_key_edge(0x26,1,1);assert(!walking_flashlight);

 assert(flash_parse("",FLASH_RANGE)==45&&flash_parse("nan",FLASH_ANGLE)==70);
 assert(flash_parse("0",FLASH_RANGE)==45&&flash_parse("1001",FLASH_RANGE)==45);
 assert(flash_parse("151",FLASH_ANGLE)==70&&flash_parse("90 deg",FLASH_ANGLE)==70);
 assert(flash_parse(" 120.5 ",FLASH_RANGE)==120.5);
 flashlight_tuning[FLASH_RANGE]=45;flashlight_tuning[FLASH_ANGLE]=70;
 walking_key_edge(0x1a,1,1);assert(flashlight_tuning[FLASH_ANGLE]==65);
 walking_key_edge(0x1a,1,1);assert(flashlight_tuning[FLASH_ANGLE]==65);
 walking_key_edge(0x1b,1,1);assert(flashlight_tuning[FLASH_ANGLE]==70);
 walking_key_edge(0x33,1,1);assert(flashlight_tuning[FLASH_RANGE]==40);
 walking_key_edge(0x34,1,1);assert(flashlight_tuning[FLASH_RANGE]==45);
 walking_key_edge(0x34,0,1);walking_key_edge(0x34,1,0);assert(flashlight_tuning[FLASH_RANGE]==45);
 {U saved=editor_keys[0];editor_keys[0]=0x1b;walking_key_edge(0x1b,0,1);walking_key_edge(0x1b,1,1);assert(flashlight_tuning[FLASH_ANGLE]==70);editor_keys[0]=saved;}
 assert(flash_adjust(5,FLASH_RANGE,-1)==5&&flash_adjust(1000,FLASH_RANGE,1)==1000);
 assert(flash_adjust(10,FLASH_ANGLE,-1)==10&&flash_adjust(150,FLASH_ANGLE,1)==150);
 assert(flash_parse("101",FLASH_BRIGHTNESS)==100&&flash_parse("nan",FLASH_BRIGHTNESS)==100);
 assert(flash_parse("0",FLASH_BRIGHTNESS)==0&&flash_parse("35",FLASH_BRIGHTNESS)==35);
 assert(flash_adjust(0,FLASH_BRIGHTNESS,-1)==0&&flash_adjust(100,FLASH_BRIGHTNESS,1)==100);
 walking_key_edge(0x27,1,1);assert(flashlight_tuning[FLASH_BRIGHTNESS]==95);
 walking_key_edge(0x27,1,1);assert(flashlight_tuning[FLASH_BRIGHTNESS]==95);
 walking_key_edge(0x28,1,1);assert(flashlight_tuning[FLASH_BRIGHTNESS]==100);
 walking_key_edge(0x27,0,1);walking_key_edge(0x27,1,0);assert(flashlight_tuning[FLASH_BRIGHTNESS]==100);
 {U saved=editor_keys[0];editor_keys[0]=0x27;walking_key_edge(0x27,0,1);walking_key_edge(0x27,1,1);assert(flashlight_tuning[FLASH_BRIGHTNESS]==100);editor_keys[0]=saved;}
 flashlight_tuning[FLASH_BRIGHTNESS]=35;
 flashlight_update((U)light_camera,1);assert(fabs(light_params[1]-.35)<.00001&&fabs(light_params[2]-.3325)<.00001&&fabs(light_params[3]-.2975)<.00001);
 flashlight_tuning[FLASH_BRIGHTNESS]=0;flashlight_update((U)light_camera,1);assert(light_params[1]==0&&light_params[2]==0&&light_params[3]==0);
 flashlight_tuning[FLASH_BRIGHTNESS]=100;
 flashlight_tuning[FLASH_RANGE]=1000;flashlight_tuning[FLASH_ANGLE]=90;
 flashlight_update((U)light_camera,1);assert(light_params[7]==1000&&fabs(light_params[11]-0.785398163)<0.00001);
 flashlight_stop();flashlight_tuning[FLASH_RANGE]=45;flashlight_tuning[FLASH_ANGLE]=70;
 walking_flashlight_available=0;walking_key_edge(0x26,0,1);walking_key_edge(0x26,1,1);assert(!walking_flashlight);
 walking_flashlight=1;walking_reset();assert(!walking_flashlight);
 puts("PASS flashlight lifecycle, camera/rebase updates, native selection preservation, additive terrain colour, stale-list cleanup, verification failure and L-key edges.");
}
static void test_flash_repeat(void){
 B held[32]={0};U i,j,saved;int setting;double initial,step;
 walking_input_active=1;walking_flashlight_available=1;walking_repeat_delay=.5;
 assert(flash_parse("1000",FLASH_RANGE)==1000&&flash_parse("200.5",FLASH_RANGE)==200.5);
 for(i=0;i<6;i++){
  U scan=walking_flash_scans[i];setting=i<2?FLASH_ANGLE:i<4?FLASH_RANGE:FLASH_BRIGHTNESS;
  initial=setting==FLASH_BRIGHTNESS?50:100;step=(i&1)?5:-5;
  memset(held,0,sizeof(held));memset(walking_event_held,0,sizeof(walking_event_held));walking_flash_repeat_reset();
  held[scan>>3]=1<<(scan&7);flashlight_tuning[setting]=initial;
  walking_key_edge(scan,1,1);assert(flashlight_tuning[setting]==initial+step);
  walking_key_edge(scan,1,1);assert(flashlight_tuning[setting]==initial+step); /* OS repeat stays edge-only. */
  for(j=0;j<4;j++)walking_flash_repeat(held,.1);assert(flashlight_tuning[setting]==initial+step);
  walking_flash_repeat(held,.1);assert(flashlight_tuning[setting]==initial+2*step);
  walking_flash_repeat(held,.1);assert(flashlight_tuning[setting]==initial+3*step);
  walking_key_edge(scan,0,1);walking_flash_repeat(held,.1);assert(flashlight_tuning[setting]==initial+3*step);
  walking_key_edge(scan,1,1);walking_flash_repeat(NULL,.1);walking_flash_repeat(held,1);assert(flashlight_tuning[setting]==initial+4*step); /* Focus/pause cancellation. */
  walking_key_edge(scan,0,1);walking_key_edge(scan,1,0);walking_flash_repeat(held,.1);assert(flashlight_tuning[setting]==initial+4*step);
 }
 memset(walking_event_held,0,sizeof(walking_event_held));memset(held,0,sizeof(held));held[0x34>>3]=1<<(0x34&7);
 walking_repeat_delay=.05;flashlight_tuning[FLASH_RANGE]=990;walking_key_edge(0x34,1,1);
 walking_flash_repeat(held,.049);assert(flashlight_tuning[FLASH_RANGE]==995);
 walking_flash_repeat(held,.001);assert(flashlight_tuning[FLASH_RANGE]==1000);
 for(j=0;j<20;j++)walking_flash_repeat(held,.1);assert(flashlight_tuning[FLASH_RANGE]==1000);
 walking_key_edge(0x34,0,1);walking_key_edge(0x34,1,1);saved=editor_keys[0];editor_keys[0]=0x34;
 walking_flash_repeat(held,.1);assert(!walking_flash_armed[3]);editor_keys[0]=saved;
 walking_key_edge(0x34,0,1);walking_key_edge(0x34,1,1);walking_input_active=0;walking_flash_repeat(held,.1);assert(!walking_flash_armed[3]);
 walking_repeat_delay=.5;memcpy(flashlight_tuning,flash_defaults,sizeof(flash_defaults));walking_reset();
 puts("PASS flashlight repeat: six keys, initial delay/cadence, release/focus/pause/conflict cancellation and 1000 m clamp.");
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
 test_flashlight();test_flash_repeat();
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
 action_name[4]=(U)L"ToggleFrameRate";assert(walking_view_action((U)actions[0]));
 assert(walking_mask());assert(!(*(B*)((U)actions[0]+0x12)&2));walking_unmask(); /* Shift-Z HUD survives FPV isolation. */
 action_name[4]=(U)L"ThrottleIncrease";table[0x2c*4]=(U)actions[0];
 assert(walking_mask());assert(*(B*)((U)actions[0]+0x12)&2);walking_unmask(); /* Z does not whitelist train actions. */
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
