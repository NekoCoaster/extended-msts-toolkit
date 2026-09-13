/* Exercise production buffered-event routing and camera integration against
   an isolated native-memory fixture, without attaching to the game. */
#include <windows.h>
#include <assert.h>
static HWND focus=(HWND)1;
static HWND WINAPI test_focus(void){return focus;}
static BOOL WINAPI test_gui(DWORD thread,GUITHREADINFO *info){info->hwndFocus=focus;return TRUE;}
#define GetFocus test_focus
#define GetForegroundWindow test_focus
#define GetGUIThreadInfo test_gui
#include "../runtime/loader.c"
static B native_fixture_space[0x450000];
#undef assert
#define assert(x) do{if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static U event[4],device[12],stack[32],head[3],node[3];
static B input[64],bits[32];static Registers regs;
static void native_camera(void){
 *(float*)0x7c2a58=*(float*)0x7c2a5c=*(float*)0x7c2a60=0;
 assert(!*(U*)0x7ba9d8&&!*(U*)0x7ba9dc);
}
static void key(unsigned scan,int down,unsigned mask){
 memset(stack,0,sizeof(stack));event[0]=0x10000|scan;event[1]=down;
 stack[6]=(U)event;stack[9]=(U)device;stack[10]=mask;
 regs.esp=(U)stack-4;editor_key_event_hook(0,&regs);
}
static unsigned routed(void){return (*(U**) &stack[6])[0]&0xffff;}
static void held(unsigned scan){bits[scan>>3]|=1<<(scan&7);}
int main(void){
 B *p;unsigned consume;int i;
 assert((U)native_fixture_space<0x4a0000&&(U)(native_fixture_space+sizeof(native_fixture_space))>=0x830000);
 {DWORD old;assert(VirtualProtect((void*)0x4a0000,0x10000,PAGE_EXECUTE_READWRITE,&old));}
 p=(B*)0x4a8d27;branch(&p,0xe9,native_camera);
 assert(editor_key_parse(L"W")==0x11&&editor_key_parse(L"w")==0x11);
 assert(editor_key_parse(L"F1")==0x3b&&editor_key_parse(L"F12")==0x58);
 assert(!editor_key_parse(L"F13")&&!editor_key_parse(L"invalid"));
 assert(editor_key_parse(L"PageUp")==0xc9&&editor_key_parse(L"0x47")==0x47);
 assert(!editor_key_allowed(0xc8)&&!editor_key_allowed(0x1d)&&!editor_key_allowed(0));
 *(U*)0x7be0ec=1;*(U*)0x7be0f8=1;*(HWND*)0x82813a=(HWND)1;editor_swap_keys=1;
 device[1]=(U)input;input[0x2d]=1;*(B**)(input+0x24)=bits;
 head[0]=(U)node;node[0]=(U)head;node[2]=(U)device;*(U**)0x8299a0=head;
 *(float*)0x828fb4=.01f;
 for(i=0;i<6;i++){
  key(editor_keys[i],1,0);assert(routed()==0);editor_key_restore();
  key(editor_keys[i],0,4);assert(routed()==0&&stack[10]==0);editor_key_restore();assert(stack[10]==4);
 }
 key(0xc8,1,0);assert(routed()==0x11);editor_key_restore();
 key(0xc8,0,4);assert(routed()==0x11&&stack[10]==0);editor_key_restore();
 *(U*)0x7ba9c0=1;*(U*)0x7ba9c4=1;
 key(0xd0,1,12);assert(routed()==0x10&&stack[10]==8&&!*(U*)0x7ba9c0&&!*(U*)0x7ba9c4);
 editor_key_restore();assert(stack[10]==12&&*(U*)0x7ba9c0==1&&*(U*)0x7ba9c4==1);
 focus=(HWND)2;key(0xd0,0,0);assert(routed()==0x10&&stack[10]==8);editor_key_restore();
 key(0x11,1,0);assert(routed()==0x11);editor_key_restore();
 focus=(HWND)1;key(0x1f,1,4);assert(routed()==0x1f);editor_key_restore(); /* Ctrl+S */
 assert(editor_key_swap(0xc8,2,&consume)==0xc8&&!consume); /* Alt */
 assert(editor_key_swap(0xcb,4,&consume)==0xcb); /* native Ctrl+Left */
 *(U*)0x7ba9c0=*(U*)0x7ba9c4=0;
 held(0x11);held(0x20);held(0x12);editor_camera_keys();
 assert(*(float*)0x7c2a58==1&&*(float*)0x7c2a60==1&&*(float*)0x7c2a5c==-1);
 held(0x2a);editor_camera_keys();assert(*(float*)0x7c2a60==10&&*(float*)0x7c2a5c==-10);
 memset(bits,0,32);editor_camera_keys();assert(!*(float*)0x7c2a60&&!*(float*)0x7c2a5c);
 held(0x11);focus=(HWND)2;editor_camera_keys();assert(!*(float*)0x7c2a60);
 focus=(HWND)1;held(0x1d);editor_camera_keys();assert(!*(float*)0x7c2a60);
 memset(bits,0,32);held(0xc8);editor_camera_keys();assert(!*(float*)0x7c2a60);
 editor_keys[0]=0x17;held(0x17);editor_camera_keys();assert(*(float*)0x7c2a60==1);
 editor_swap_keys=0;key(0x17,1,0);assert(routed()==0x17);editor_key_restore();
 puts("PASS configurable swaps, displaced shortcuts, modifier/release pairing, focus, diagonal/vertical held movement and Shift speed.");return 0;
}
