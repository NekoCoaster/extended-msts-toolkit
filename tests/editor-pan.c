/* Run the real supported virtual-pointer routine from a local EXE fixture.
   Compare its clipped UI coordinates with the production camera delta path. */
#include <windows.h>
#include <assert.h>
static HWND focus=(HWND)1;static DWORD menu_flags;
static HWND WINAPI test_foreground(void){return focus;}
static BOOL WINAPI test_gui(DWORD thread,GUITHREADINFO *info){info->hwndFocus=focus;info->flags=menu_flags;return TRUE;}
#define GetForegroundWindow test_foreground
#define GetGUIThreadInfo test_gui
#include "../runtime/loader.c"
static B native_fixture_space[0x450000];
#undef assert
#define assert(x) do{if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static int pointer[16],other[16],events[48];
static void __fastcall pointer_event(int *event){
 if(!event[0]){*(int*)0x7baa48=event[1];*(int*)0x7baa4c=event[2];}
 if(event[0]==5)*(U*)0x7bac74=1;
 if(event[0]==4)*(U*)0x7bac74=0;
}
static void load_pointer(const char *path){
 FILE *f=fopen(path,"rb");B *file,*page,*p;long size;U pe,table,i,rva,raw,bytes;DWORD old;
 assert(f);fseek(f,0,SEEK_END);size=ftell(f);rewind(f);file=malloc(size);assert(file&&fread(file,1,size,f)==size);fclose(f);
 pe=*(U*)(file+60);table=pe+24+*(unsigned short*)(file+pe+20);
 for(i=0;i<*(unsigned short*)(file+pe+6);i++){
  B *s=file+table+i*40;rva=*(U*)(s+12);bytes=*(U*)(s+16);raw=*(U*)(s+20);
  if(rva<=0x2d3130&&0x2d3266<=rva+bytes){
   page=VirtualAlloc(NULL,4096,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);assert(page);
   memcpy(page,file+raw+0x2d3130-rva,0x136);
   assert(!memcmp(page,"\x83\xec\x0c\x53\x55",5));
   /* Execute the same five-byte prologue trampoline as the installed hook. */
   p=page+0x200;memcpy(p,page,5);p+=5;branch(&p,0xe9,page+5);
   assert(VirtualProtect(page,4096,PAGE_EXECUTE_READ,&old));FlushInstructionCache(GetCurrentProcess(),page,4096);
   editor_pointer_original=(EditorPointerMove)(page+0x200);break;
  }
 }
 free(file);assert(editor_pointer_original);
}
static void move(int kind,int x,int y){pointer[5]=pointer[6]=pointer[7]=0;assert(editor_pointer_move(pointer,kind,x,y));}
int main(int argc,char **argv){
 int i,lastx,lasty;
 assert(argc==2);assert((U)native_fixture_space<0x7b0000&&(U)(native_fixture_space+sizeof(native_fixture_space))>=0x830000);
 load_pointer(argv[1]);*(U*)0x7be0ec=1;*(U*)0x7be0f8=1;*(HWND*)0x82813a=(HWND)1;
 *(int**)0x7bac60=pointer;pointer[2]=320;pointer[3]=240;pointer[4]=(int)events;pointer[10]=639;pointer[11]=479;
 pointer[12]=pointer[13]=1;pointer[15]=(int)pointer_event;editor_unlimited_pan=1;
 move(5,0,0); /* native camera-pan button down */
 for(i=0;i<1000;i++){
  move(0,100,75);editor_pan_apply();
  assert(*(int*)0x7c2a64==100&&*(int*)0x7c2a68==75);
 }
 assert(pointer[2]==639&&pointer[3]==479); /* native UI still safely clipped */
 lastx=pointer[2];lasty=pointer[3];
 move(0,100,75);assert(pointer[2]-lastx==0&&pointer[3]-lasty==0);editor_pan_apply();
 assert(*(int*)0x7c2a64==100&&*(int*)0x7c2a68==75); /* native dead edge bypassed */
 for(i=0;i<1000;i++){move(0,-100,-75);editor_pan_apply();assert(*(int*)0x7c2a64==-100&&*(int*)0x7c2a68==-75);}
 assert(!pointer[2]&&!pointer[3]);
 pointer[12]=2;pointer[13]=3;move(0,5,-7);move(0,8,4);editor_pan_apply();assert(*(int*)0x7c2a64==26&&*(int*)0x7c2a68==-9);
 editor_pan_apply();assert(!*(int*)0x7c2a64&&!*(int*)0x7c2a68); /* consumed exactly once */
 move(0,20,10);editor_pan_reset();editor_pan_apply();assert(!*(int*)0x7c2a64&&!*(int*)0x7c2a68); /* skipped camera frame */
 move(0,20,10);move(4,0,0);editor_pan_apply();assert(!*(int*)0x7c2a64&&!*(int*)0x7c2a68);
 move(0,20,10);move(5,0,0);editor_pan_apply();assert(!*(int*)0x7c2a64&&!*(int*)0x7c2a68);
 move(0,20,10);focus=(HWND)2;editor_pan_apply();assert(!*(int*)0x7c2a64&&!editor_pan_x);
 focus=(HWND)1;menu_flags=4;move(0,20,10);editor_pan_apply();assert(!*(int*)0x7c2a64);menu_flags=0;
 memcpy(other,pointer,sizeof(pointer));assert(editor_pointer_move(other,0,5,5));assert(!editor_pan_x&&!editor_pan_y);
 editor_unlimited_pan=0;move(0,20,10);*(int*)0x7c2a64=9;editor_pan_apply();assert(*(int*)0x7c2a64==9);
 editor_unlimited_pan=1;*(U*)0x7be0ec=3;move(0,20,10);editor_pan_apply();assert(*(int*)0x7c2a64==9);
 assert(editor_pan_delta(1e20)==2147483647&&editor_pan_delta(-1e20)==-2147483647);
 puts("PASS native pointer edge reproduction; 2,000 unrestricted two-axis frames, reversal, sensitivity, release/repress, focus, menus, unrelated pointers and disabled/other-editor isolation.");return 0;
}
