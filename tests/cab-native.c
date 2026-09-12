/* Executes the actual x86 adapter and production transform with synthetic
   renderer frames. No game binary or game process is needed. */
#include <assert.h>
#include "../runtime/loader.c"
static int test_mode=1,original_calls;
static int mode(void){return test_mode;}
static float *__fastcall rotate_original(float *v,U ignored,float angle){
 float x=v[0],y=v[1];original_calls++;v[0]=cos(angle)*x-sin(angle)*y;v[1]=sin(angle)*x+cos(angle)*y;return v;
}
int main(void){
 B *page=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE),*p;
 U parent[2]={0,0x41b771},frame[2];DWORD old;
 float scales[2]={2,1.5f},v[3],angle=0.785398163f;int i;
 CabRotateFn invoke;assert(page);frame[0]=(U)parent;frame[1]=0x44fe46;
 cab_original=rotate_original;cab_mode=mode;cab_scales=scales;
 cab_adapter(page,cab_rotate,cab_original);
 p=page+128;invoke=(void*)p;
 emit8(&p,0x55);emit8(&p,0xbd);emit32(&p,(U)frame);
 emit8(&p,0xff);emit8(&p,0x74);emit8(&p,0x24);emit8(&p,8);
 branch(&p,0xe8,page);emit8(&p,0x5d);emit8(&p,0xc2);emit8(&p,4);emit8(&p,0);
 assert(VirtualProtect(page,4096,PAGE_EXECUTE_READ,&old));FlushInstructionCache(GetCurrentProcess(),page,4096);
 for(i=0;i<100000;i++){
  v[0]=0;v[1]=-66;v[2]=123;
  assert(invoke(v,0,angle)==v);
  assert(fabs(v[0]-62.225397)<0.0001&&fabs(v[1]+46.669048)<0.0001&&v[2]==123);
 }
 /* Non-dial caller, different parent, editor mode, equal/invalid scales. */
 for(i=0;i<6;i++){
  parent[1]=i==0?0:0x41b771;frame[1]=i==1?0:0x44fe46;
  test_mode=i==2?0:1;scales[0]=i==3?1.5f:i==4?0:i==5?1000:2;
  v[0]=0;v[1]=-66;v[2]=123;assert(invoke(v,0,angle)==v);
  assert(fabs(v[0]-46.669048)<0.0001&&fabs(v[1]+46.669048)<0.0001&&v[2]==123);
 }
 assert(original_calls==100006);VirtualFree(page,0,MEM_RELEASE);
 puts("PASS actual x86 cab adapter: 100000 corrected calls, six bypass cases, native return pointer, stack cleanup and untouched Z.");return 0;
}
