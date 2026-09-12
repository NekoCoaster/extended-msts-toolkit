#include <assert.h>
static unsigned char timing_globals[0x100000];
#define TIMING_ADDR(a) ((unsigned int)timing_globals+(a)-0x7b0000)
#include "../runtime/loader.c"
static LARGE_INTEGER fake_now;
static int accepted=1,counter_ok=1,delegated;
static int frame_original(void){return accepted;}
static BOOL WINAPI counter(LARGE_INTEGER *out){*out=fake_now;return counter_ok;}
static void step_original(void){delegated++;}
typedef double (__fastcall *AddFn)(float*,U);
static AddFn make_caller(B *p,B *adapter,int second){
 AddFn entry=(void*)p;
 emit8(&p,0x55);emit8(&p,0x89);emit8(&p,0xe5);emit8(&p,0x83);emit8(&p,0xec);emit8(&p,4);
 emit8(&p,0x89);emit8(&p,0x55);emit8(&p,0xfc);
 emit8(&p,0x89);emit8(&p,second?0xca:0xc8); /* mov edx/eax,ecx */
 emit8(&p,0x83);emit8(&p,second?0xea:0xe8);emit8(&p,second?0x1c:0x18);
 branch(&p,0xe8,adapter);emit8(&p,0x89);emit8(&p,0xec);emit8(&p,0x5d);emit8(&p,0xc3);
 return entry;
}
int main(void){
 int rates[]={60,144,300,1000},scales[]={1,2,4,16};int r,s,i;U bits;double sum,expected;float dt,*a=(float*)TIMING_ADDR(0x80acd0),*b=(float*)TIMING_ADDR(0x80acd4);
 B *page=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);DWORD old;AddFn add[2];assert(page);
 timing_adapter(page,0);timing_adapter(page+64,1);add[0]=make_caller(page+128,page,0);add[1]=make_caller(page+192,page+64,1);
 assert(VirtualProtect(page,4096,PAGE_EXECUTE_READ,&old));FlushInstructionCache(GetCurrentProcess(),page,4096);
 timing_frequency.QuadPart=72000000;timing_frame_original=frame_original;timing_counter=counter;timing_step_original=step_original;
 for(r=0;r<4;r++)for(s=0;s<4;s++){
  timing_started=0;fake_now.QuadPart=720000000000LL;TF(0x80acd8)=scales[s];TI(0x7be0ec)=0;
  memset(timing_remainders,0,sizeof(timing_remainders));*a=70000;*b=1000;sum=0;assert(timing_frame());
  for(i=0;i<rates[r]*600;i++){
   fake_now.QuadPart+=timing_frequency.QuadPart/rates[r];assert(timing_frame());timing_step();dt=TF(0x828fb4);
   assert(fabs(TF(0x828f6c)-rates[r])<0.01);sum+=dt;memcpy(&bits,&dt,4);
   *a=(float)add[0](a,bits);*b=(float)add[1](b,bits);
  }
  expected=600.0*scales[s];assert(fabs(sum-expected)<0.001);
 assert(fabs(*a-(70000+expected))<0.01&&fabs(*b-(1000+expected))<0.01);
 }
 /* Uneven frame intervals and live multiplier changes use tick differences. */
 timing_started=0;fake_now.QuadPart=720000000000LL;timing_frame();sum=0;expected=0;
 for(i=0;i<20000;i++){
  int ticks=40000+(i*7919)%900000;TF(0x80acd8)=(i/5000)%2?4:1;
  fake_now.QuadPart+=ticks;timing_frame();timing_step();sum+=TF(0x828fb4);
  expected+=(double)ticks/72000000*TF(0x80acd8);
 }assert(fabs(sum-expected)<0.0001);
 /* Model native pause ownership: frames continue but calendar is not called. */
 {float before=*a;for(i=0;i<15000;i++){fake_now.QuadPart+=72000;timing_frame();timing_step();}assert(*a==before);
  TF(0x80acd8)=1;fake_now.QuadPart+=72000;timing_frame();timing_step();assert(fabs(TF(0x828fb4)-0.001)<1e-7);}
 /* External clock reset rebases fractional remainder. Other clock objects bypass. */
 *a=0;dt=0.001f;memcpy(&bits,&dt,4);*a=(float)add[0](a,bits);assert(fabs(*a-dt)<1e-8);
 {float other=5;assert(fabs(add[0](&other,bits)-5.001)<1e-6);}
 /* A rejected frame does not sample time. Stalls cap at 0.3s, no catch-up debt. */
 accepted=0;{LARGE_INTEGER previous=timing_previous;fake_now.QuadPart+=720000000;assert(!timing_frame());assert(previous.QuadPart==timing_previous.QuadPart);}
 accepted=1;assert(timing_frame());assert(fabs(TF(0x828fb4)-0.3)<1e-6);
 fake_now.QuadPart+=72000;assert(timing_frame());assert(fabs(TF(0x828fb4)-0.001)<1e-7);
 TI(0x7be0ec)=2;timing_step();assert(delegated==1);TI(0x7be0ec)=0;
 TF(0x80acd8)=0;timing_step();assert(TF(0x828fb4)==0);
 counter_ok=0;TF(0x828fb4)=0;assert(timing_frame());assert(!timing_started&&TF(0x828fb4)>0);
 VirtualFree(page,0,MEM_RELEASE);
 puts("PASS timing: actual x86 clock adapters; 16 ten-minute FPS/multiplier cases; float-clock compensation; rebase, mode bypass, zero scale, stalls, rejected frames and counter failure.");return 0;
}
