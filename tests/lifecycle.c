#include <assert.h>
static unsigned char *globals;
#define G(a) ((unsigned int)globals+(a)-0x7b0000)
#include "../runtime/loader.c"
static B *obj(void){B *p=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);assert(p);return p;}
static void putu(B *p,U n){memcpy(p,&n,4);}
static B *vehicle(int engine){
 B *car=obj(),*body=obj(),*def=obj(),*eng=obj();
 putu(car+0x5c,(U)body);putu(car+0x94,(U)def);putu(car+0x29a,(U)eng);putu(body+0x11d,(U)car);body[0xf0]=1;def[0x88]=engine;
 wf((U)body+0xc8,1.0/100000);wf((U)body+0x2c,1);wf((U)body+0xc,1);wf((U)eng+0x102,200000);wf((U)eng+0xfe,1000000);wf((U)eng+0x112,1);wf((U)def+0x4a0,2);
 return car;
}
static void tick(void){U i;for(i=0;i<6;i++)update_frame();}
typedef struct {Registers r;U stack[5];} PitchContext;
static void pitch_callbacks(B *source){
 B *body=obj(),*onrail=obj(),before[0x124];int yaw,roll,slope,step,i,helper,count=0;
 PitchContext outer,inner,call;ThreadCalls *t;double saved_scale=friction_scale;
 memcpy(body,source,0x124);memcpy(onrail,source,0x124);onrail[0xf2]=0;
 /* Use a different integration buffer from cars[].body, with the same owner.
    A rolled right vector must never choose the axis for either derivative. */
 for(yaw=0;yaw<8;yaw++)for(roll=0;roll<8;roll++)for(slope=-1;slope<=1;slope++)for(step=0;step<=2;step++){
  double y=yaw*3.141592653589793/4,r=roll*3.141592653589793/4,e=slope*.6;
  double f[3]={sin(y)*cos(e),sin(e),cos(y)*cos(e)},p[3]={cos(y),0,-sin(y)};
  double up[3]={-sin(y)*sin(e),cos(e),-cos(y)*sin(e)},expected[3];
  friction_scale=step*.5;
  for(i=0;i<3;i++){
   wf((U)body+0xc+4*i,p[i]*cos(r)+up[i]*sin(r));wf((U)body+0x18+4*i,up[i]*cos(r)-p[i]*sin(r));
   wf((U)body+0x24+4*i,f[i]);wf((U)body+0x94+4*i,2*p[i]+3*(i==1)+4*f[i]);
   expected[i]=2*friction_scale*p[i]+3*(i==1)+4*f[i];
  }
  memcpy(before,body,sizeof(before));memset(&outer,0,sizeof(outer));outer.stack[0]=1234;outer.stack[2]=(U)body;
  hook_enter(PITCH,&outer.r);t=TlsGetValue(tls_index);assert(t&&t->depth==1&&t->calls[0].pitch&&!blocked);
  for(helper=VECTOR;helper<=CROSS;helper++){
   memset(&call,0,sizeof(call));call.r.ecx=(U)body+0x94;call.stack[0]=7;
   hook_enter(helper,&call.r);assert(call.r.ecx==(U)body+0x94); /* unrelated caller */
   call.stack[0]=helper==VECTOR?0x5f8796:0x5f8876;hook_enter(helper,&call.r);
   assert(call.r.ecx==(U)t->calls[0].filtered);
   for(i=0;i<3;i++)assert(fabs(rf((B*)call.r.ecx+4*i)-expected[i])<.00002);
   memset(&inner,0,sizeof(inner));inner.stack[0]=5678;inner.stack[2]=(U)onrail;hook_enter(PITCH,&inner.r);
   assert(t->depth==2&&!t->calls[1].pitch);call.r.ecx=(U)onrail+0x94;hook_enter(helper,&call.r);
   assert(call.r.ecx==(U)onrail+0x94);hook_leave(PITCH,&inner.r);assert(inner.stack[0]==5678);
   call.r.ecx=(U)body+0x94;hook_enter(helper,&call.r);assert(call.r.ecx==(U)t->calls[0].filtered);
  }
  hook_leave(PITCH,&outer.r);assert(!t->depth&&outer.stack[0]==1234&&!memcmp(before,body,sizeof(before)));count++;
 }
 /* The callback gates must not start a derivative context while paused/off. */
 putu((B*)G(0x7be0f4),1);hook_enter(PITCH,&outer.r);assert(!t->depth);putu((B*)G(0x7be0f4),0);
 enabled=0;hook_enter(PITCH,&outer.r);assert(!t->depth);enabled=1;friction_scale=saved_scale;
 printf("PASS pitch callbacks: %d heading/roll/slope/throttle cases through both helpers; swapped buffers, nested on-rail exclusion, caller scope, pause/off gates and exact body preservation.\n",count);
}
int main(void){
 B *train,*ctl,*a,*freight,*b,*ab,*bb;U i;
 globals=VirtualAlloc(NULL,0x80000,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);assert(globals);
 train=obj();ctl=obj();a=vehicle(1);freight=vehicle(0);b=vehicle(1);ab=(B*)ru(a+0x5c);bb=(B*)ru(b+0x5c);
 putu((B*)G(0x7c2ac0),(U)train);putu(train+0x6a,(U)a);putu((B*)G(0x7b6440),(U)ctl);putu((B*)G(0x7b6438),3);
 putu(a+0xa8,(U)freight);putu(freight+0xa0,(U)a);putu(freight+0xa8,(U)b);putu(b+0xa0,(U)freight);
 wf((U)ctl+0x8c,1);wf((U)ctl+0xc8,1);wf(G(0x828fb4),.1);wf(G(0x80acd4),1);
 tick();assert(!enabled&&car_count==3);ab[0xf2]=4;bb[0xf2]=4;tick();assert(enabled&&active_count==2&&impulses==2);assert(rf(ab+0x90)>1.99&&rf(bb+0x90)>1.99);
 wf(G(0x80acd4),10000);tick();assert(enabled&&impulses==4); /* no deadline */
 putu((B*)G(0x7be0f4),1);tick();assert(!active_count&&impulses==4);putu((B*)G(0x7be0f4),0);
 putu(freight+0xa8,0);putu(b+0xa0,0);wf(G(0x80acd4),10001);tick();assert(car_count==2&&active_count==1&&impulses==5);
 clear_activity();assert(!enabled&&!car_count&&!active_count);ab[0xf2]=0;tick();assert(!enabled&&car_count==2);ab[0xf2]=4;wf(G(0x80acd4),1);tick();assert(enabled&&active_count==1);
 strength=0;wf(G(0x80acd4),2);tick();assert(enabled&&!active_count);
 clear_activity();putu((B*)G(0x7b6438),1);wf((U)ctl+0x54,.5);wf((U)ctl+0x8c,-.7);strength=10;tick();assert(enabled&&direction<0&&throttle==.5&&active_count==1);
 /* Scoped wheel replacement and exact restoration use the real callbacks. */
 tls_index=TlsAlloc();simulation_thread=GetCurrentThreadId();InitializeCriticalSection(&state_lock);
 counter_tilt=1;pitch_callbacks(ab);counter_tilt=0;
 {PitchContext ctx;memset(&ctx,0,sizeof(ctx));ctx.stack[0]=1234;ctx.stack[2]=(U)ab;hook_enter(PITCH,&ctx.r);assert(ctx.stack[0]==1234);assert(!TlsGetValue(tls_index)||!((ThreadCalls*)TlsGetValue(tls_index))->depth);}
 {struct {Registers r;U stack[5];} ctx;U original;memset(&ctx,0,sizeof(ctx));ctx.r.ecx=(U)a;ctx.stack[0]=1234;original=ru(a+0x2b2);hook_enter(ROD,&ctx.r);assert(rod_calls==1&&ru(a+0x2b2)!=original);hook_leave(ROD,&ctx.r);assert(ru(a+0x2b2)==original&&ctx.stack[0]==1234);}
 {B *rotated=obj();struct {Registers r;U stack[5];} ctx;memcpy(rotated,ab,0x124);rotated[0xf2]=12;
  putu(a+0x5c,(U)rotated);assert(cars[0].body!=(U)rotated);assert(eligible((U)rotated));
  memset(&ctx,0,sizeof(ctx));ctx.r.ecx=(U)rotated;hook_enter(BODY,&ctx.r);assert(!(rotated[0xf2]&8)&&wakes>0);
  ctx.r.ecx=(U)rotated+0x88;ctx.stack[0]=0x62b18a;wf((U)&ctx.stack[2],-10);hook_enter(DRAG,&ctx.r);assert(fabs(rf(&ctx.stack[2])+5)<.001);
 }
 putu(freight+0xa0,0);wf(G(0x80acd4),3);tick();assert(blocked&&!enabled);clear_activity();assert(!blocked);
 puts("PASS native lifecycle: graph, connected thrust, no deadline, pause, split, reused activity, zero strength, steam controls, scoped rod restore, invalid graph.");return 0;
}
