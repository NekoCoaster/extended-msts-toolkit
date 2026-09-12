/* MIT. Experimental high-FPS timing, enabled only by the FPS option.
   Original frame bookkeeping, pause decisions and calendar updates remain native. */
#ifndef TIMING_ADDR
#define TIMING_ADDR(a) (a)
#endif
#define TF(a) (*(float*)TIMING_ADDR(a))
#define TI(a) (*(U*)TIMING_ADDR(a))
static int (*timing_frame_original)(void)=(void*)0x6ad0f0;
static void (*timing_step_original)(void)=(void*)0x4b7b20;
static BOOL (WINAPI *timing_counter)(LARGE_INTEGER*)=QueryPerformanceCounter;
static LARGE_INTEGER timing_frequency,timing_previous;
static int timing_started;
static Hook timing_hooks[4];static B *timing_code;
typedef struct {double error;float last;int valid;} TimingRemainder;
static TimingRemainder timing_remainders[2];
static double timing_add(TimingRemainder *r,float current,float dt){
 double next;float rounded;
 if(!finite_number(current)||!finite_number(dt)){r->valid=0;return (double)current+dt;}
 if(!r->valid||current!=r->last)r->error=0;
 next=(double)current+(double)dt+r->error;rounded=(float)next;
 r->error=next-(double)rounded;r->last=rounded;r->valid=1;return rounded;
}
static double __fastcall timing_accumulate(float *field,U dt_bits){
 float dt;int index;memcpy(&dt,&dt_bits,4);
 if(TI(0x7be0ec)==2){memset(timing_remainders,0,sizeof(timing_remainders));return (double)*field+dt;}
 if(field==(float*)TIMING_ADDR(0x80acd0))index=0;
 else if(field==(float*)TIMING_ADDR(0x80acd4))index=1;
 else return (double)*field+dt;
 return timing_add(&timing_remainders[index],*field,dt);
}
static double timing_elapsed(LARGE_INTEGER now){
 double dt=0;
 if(timing_started&&now.QuadPart>=timing_previous.QuadPart)
  dt=(double)(now.QuadPart-timing_previous.QuadPart)/(double)timing_frequency.QuadPart;
 timing_previous=now;timing_started=1;
 /* No catch-up burst after loading, suspend or a long frame stall. */
 if(dt>0.3)dt=0.3;
 if(dt<0.000001)dt=0.000001;
 return dt;
}
static int timing_frame(void){
 int accepted=timing_frame_original();LARGE_INTEGER now;
 if(!accepted)return accepted;
 if(timing_counter(&now))TF(0x828fb4)=(float)timing_elapsed(now);
 else {timing_started=0;if(!(TF(0x828fb4)>0&&TF(0x828fb4)<=0.3f))TF(0x828fb4)=0.000001f;}
 TF(0x828f6c)=1.0f/TF(0x828fb4);
 return accepted;
}
static void timing_step(void){
 float raw=TF(0x828fb4),scale=TF(0x80acd8);
 if(TI(0x7be0ec)==2){timing_step_original();return;}
 if(!finite_number(raw)||!finite_number(scale)||raw<=0||scale<0||scale>1024){timing_step_original();return;}
 if(raw>0.3f)raw=0.3f;
 TF(0x80ace0)=raw;TF(0x828fb4)=raw*scale;TF(0x828f6c)=1.0f/raw;
}
/* Replace FLD local-step / FADD clock-field, returning the corrected value
   on ST0. Preserve all three volatile registers; EBP belongs to native clock. */
static void timing_adapter(B *p,int second){
 emit8(&p,0x50);emit8(&p,0x51);emit8(&p,0x52);
 emit8(&p,0x8d);emit8(&p,second?0x4a:0x48);emit8(&p,second?0x1c:0x18);
 emit8(&p,0x8b);emit8(&p,0x55);emit8(&p,0xfc);
 branch(&p,0xe8,timing_accumulate);
 emit8(&p,0x5a);emit8(&p,0x59);emit8(&p,0x58);emit8(&p,0xc3);
}
static int install_timing_hooks(void){
 U i;DWORD old;Hook *h;
 if(!unlock_fps)return 1;
 if(!QueryPerformanceFrequency(&timing_frequency)||timing_frequency.QuadPart<=0)return 0;
 if(memcmp((void*)0x645af0,"\x55\x8b\xec\x83\xec\x10",6))return 0;
 timing_code=VirtualAlloc(NULL,128,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!timing_code)return 0;
 timing_adapter(timing_code,0);timing_adapter(timing_code+64,1);
 if(!VirtualProtect(timing_code,128,PAGE_EXECUTE_READ,&old))goto failed;
 FlushInstructionCache(GetCurrentProcess(),timing_code,128);
 startup_call(&timing_hooks[0],0x6ba183,0x6ad0f0,(U)timing_frame);
 startup_call(&timing_hooks[1],0x48fdd6,0x403661,(U)timing_step);
 for(i=0;i<2;i++){
  h=&timing_hooks[i+2];memset(h,0,sizeof(*h));h->address=i?0x645b22:0x645b13;h->length=6;h->raw=1;
  memcpy(h->original,i?"\xd9\x45\xfc\xd8\x42\x1c":"\xd9\x45\xfc\xd8\x40\x18",6);
  h->replacement[0]=0xe8;*(U*)(h->replacement+1)=(U)(timing_code+i*64)-h->address-5;h->replacement[5]=0x90;
 }
 if(prepare_hooks(timing_hooks,4)&&install_hooks(timing_hooks,4))return 1;
failed:VirtualFree(timing_code,0,MEM_RELEASE);timing_code=NULL;return 0;
}
