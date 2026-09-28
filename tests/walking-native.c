#include <assert.h>
static unsigned char globals[0x110000];
#define G(a) ((U)globals+(a)-0x790000)
#include "../runtime/loader.c"
static U head[3],node[3],device[11],table[238*4],actions[3][6];
static B input[48],bits[30];
static int ground_result=1;static float ground_normal=1;
static int __fastcall fake_ground(float *out,U flags,float x,float z){assert(flags==2);out[0]=123;out[1]=0;out[2]=ground_normal;out[3]=0;return ground_result;}
static void setup(void){
 memset(globals,0,sizeof(globals));memset(actions,0,sizeof(actions));
 head[0]=(U)node;node[0]=(U)head;node[2]=(U)device;
 device[1]=(U)input;device[4]=0;device[5]=238;device[6]=(U)table;device[8]=0x1234;device[10]=0x5678;
 input[0x2d]=1;*(U*)(input+0x24)=(U)bits;
 *(U*)G(0x8299a0)=(U)head;*(U*)G(0x829974)=(U)actions[0];
 actions[0][2]=(U)actions[1];actions[1][2]=(U)actions[2];
 table[1*4]=(U)actions[1];table[0x3f*4]=(U)actions[2];
}
int main(void){
 char lines[WALK_HUD_LINES][240];B readbits[32];int i;double height;
 setup();bits[0x11>>3]=1<<(0x11&7);assert(walking_keys(readbits)&&crawl_key(readbits,0x11));
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
 setup();walking_reset();walking_hud_lines(lines);assert(strstr(lines[0],"Standby"));
 walking_input_active=1;walking_key_edge(0x39,1,1);walking_key_edge(0x39,0,1);assert(walking_pulses==64);
 walking_pulses=0;walking_key_edge(0x39,1,1);walking_pulses=0;walking_key_edge(0x39,1,1);assert(!walking_pulses);
 walking_key_edge(0x39,0,1);walking_key_edge(0x39,1,0);assert(!walking_pulses);
 walking_key_edge(editor_keys[4],1,1);assert(walking_pulses==16);walking_pulses=0;
 walking_key_edge(0x2f,1,1);assert(walking_pulses==128);
 walking_key_edge(walking_toggle_scan,1,1);assert(walking_pending);walking_pending=0;
 walking_key_edge(walking_toggle_scan,1,1);assert(!walking_pending);
 walking_state.active=walking_input_active=1;walking_state.x=2050;walking_state.z=-1025;walking_state.y=20;walking_state.eye_height=2;
 *(int*)G(0x79d118)=100;*(int*)G(0x79d11c)=-50;
 walking_status="Walking";walking_hud_lines(lines);assert(strstr(lines[0],"BLOCKED"));assert(strstr(lines[1],"101 / -51"));assert(strstr(lines[2],"Eyes Y: 22.00"));
 walking_state.noclip=1;walking_hud_lines(lines);assert(strstr(lines[0],"Noclip: ON"));
 editor_keys[0]=0x17;walking_toggle_scan=0x57;walking_hud_lines(lines);assert(strstr(lines[3],"Walk=F11")&&strstr(lines[3],"Move=I/"));
 puts("PASS walking native adapter: key bounds, train action masking, F5/Escape allowance, raw device isolation, flag restoration, bounded corrupt-list rejection and walking HUD.");return 0;
}
