#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
static int test_focus=1;
static HWND WINAPI test_foreground(void){return test_focus?(HWND)1:NULL;}
static DWORD WINAPI test_thread(HWND h,DWORD *p){return 1;}
static BOOL WINAPI test_gui(DWORD id,PGUITHREADINFO info){info->hwndFocus=(HWND)1;return TRUE;}
#define GetForegroundWindow test_foreground
#define GetWindowThreadProcessId test_thread
#define GetGUIThreadInfo test_gui
#define main lifecycle_main
#include "lifecycle.c"
#undef main
#undef assert
#define assert(x) do{if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static U *binding(B *table,int scan,U callback,U context){
 U *a=(U*)obj(),*l=(U*)obj(),*b=(U*)(table+scan*16);
 b[0]=(U)a;a[1]=(U)l;l[0]=callback;l[1]=context;l[3]=0x106;
 return l;
}
int main(void){
 B *head,*node,*device,*input,*bits,*table,*ctl,*train,*car,*body,*freight,*fb;U *l,*a;int type;double before;
 lifecycle_main();clear_activity();
 head=obj();node=obj();device=obj();input=obj();bits=obj();table=obj();ctl=obj();train=obj();car=vehicle(1);body=(B*)ru(car+0x5c);freight=vehicle(0);fb=(B*)ru(freight+0x5c);
 putu((B*)G(0x8299a0),(U)head);putu(head,(U)node);putu(node,(U)head);putu(node+8,(U)device);
 putu(device+0x14,238);putu(device+4,(U)input);putu(device+0x18,(U)table);input[0x2d]=1;putu(input+0x24,(U)bits);
 for(type=1;type<=3;type++){
  memset(table,0,4096);memset(bits,0,32);
  binding(table,0x39,0x489a25,(U)ctl+(type==1?0x368:0x1c4));
  binding(table,0x27,0x489987,(U)ctl+(type==1?0xe0:0x10c));
  l=binding(table,0x28,0x4898dd,(U)ctl+(type==1?0xe0:0x10c));
  assert(!crawl_keyboard_controls((U)ctl,type));
  bits[0x39/8]|=1<<(0x39%8);assert(crawl_keyboard_controls((U)ctl,type)==CRAWL_RIGHTING);
  bits[0x27/8]|=1<<(0x27%8);bits[0x28/8]|=1<<(0x28%8);assert(crawl_keyboard_controls((U)ctl,type)==7);
  l[4]=1;assert(crawl_keyboard_controls((U)ctl,type)==3);l[4]=0;
  a=(U*)ru(table+0x28*16);a[4]=0x20000;assert(crawl_keyboard_controls((U)ctl,type)==3);a[4]=0;
  /* Native binding mask: Ctrl required; then suppress when Ctrl is released. */
  putu(table+0x28*16+8,0x404);assert(crawl_keyboard_controls((U)ctl,type)==3);
  bits[0x1d/8]|=1<<(0x1d%8);assert(crawl_keyboard_controls((U)ctl,type)==7);
  memset(bits,0,32);
  /* User remapping follows the action, not the default scan code. */
  memcpy(table+0x20*16,table+0x28*16,16);memset(table+0x28*16,0,16);putu(table+0x20*16+8,0);
  bits[4]=1;assert(crawl_keyboard_controls((U)ctl,type)==CRAWL_RIGHT);
  putu((B*)G(0x829980),2);assert(!crawl_keyboard_controls((U)ctl,type));putu((B*)G(0x829980),0);
 }
 /* Actual MSTS layout: 238 bindings and 30 bytes, followed by allocator data.
    Guard pages make either of alpha.14's oversized reads fail, independent of
    whether the adjacent allocation happens to be readable in this run. */
 {B *kb=VirtualAlloc(NULL,8192,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE),*tb=VirtualAlloc(NULL,8192,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);DWORD old;
  assert(kb&&tb&&VirtualProtect(kb+4096,4096,PAGE_NOACCESS,&old)&&VirtualProtect(tb+4096,4096,PAGE_NOACCESS,&old));
  kb+=4096-30;tb+=4096-238*16;memcpy(tb,table,238*16);kb[0x39/8]=1<<(0x39%8);
  putu(input+0x24,(U)kb);putu(device+0x18,(U)tb);crawl_shortcut_ctl=0;
  assert(crawl_keyboard_controls((U)ctl,3)==CRAWL_RIGHTING);assert(!strcmp(crawl_shortcuts[0],"Space"));
  assert(!strcmp(crawl_shortcuts[2],"D"));
  kb[0x39/8]=0;kb[0x27/8]|=1<<(0x27%8);assert(crawl_keyboard_controls((U)ctl,3)==CRAWL_LEFT);
  putu(input+0x24,(U)bits);putu(device+0x18,(U)table);
  /* Reproduce the live allocation tail (0x5b,0x03) and bogus extra entries. */
  bits[30]=0x5b;bits[31]=3;putu(table+240*16,1);assert(crawl_keyboard_controls((U)ctl,3)==CRAWL_RIGHT);
  bits[30]=bits[31]=0;putu(table+240*16,0);
 }
 putu((B*)G(0x82813a),1);putu((B*)G(0x7c2ac0),(U)train);putu(train+0x6a,(U)car);putu((B*)G(0x7b6440),(U)ctl);putu((B*)G(0x7b6438),3);
 /* Down and up can both arrive in the same IOM poll, before any physics
    frame. The buffered command must survive the now-released key bitset. */
 {Registers r;U stack[12]={0},event[4]={0x1002b,1,0,0};memset(&r,0,sizeof(r));
  r.esp=(U)stack-4;stack[6]=(U)event;stack[9]=(U)device;
  crawl_derail_down=crawl_derail_pending=0;hook_enter(MANUAL_KEY,&r);assert(crawl_derail_pending&&crawl_derail_down);
  event[1]=0;hook_enter(MANUAL_KEY,&r);assert(crawl_derail_pending&&!crawl_derail_down);
  crawl_derail_pending=0;event[1]=1;stack[10]=4;hook_enter(MANUAL_KEY,&r);assert(!crawl_derail_pending);
  stack[10]=0;event[1]=0;hook_enter(MANUAL_KEY,&r);test_focus=0;event[1]=1;hook_enter(MANUAL_KEY,&r);assert(!crawl_derail_pending);test_focus=1;
  event[1]=0;hook_enter(MANUAL_KEY,&r);putu((B*)G(0x829980),2);event[1]=1;hook_enter(MANUAL_KEY,&r);assert(!crawl_derail_pending);putu((B*)G(0x829980),0);
  event[1]=0;hook_enter(MANUAL_KEY,&r);putu((B*)G(0x7be0f4),1);event[1]=1;hook_enter(MANUAL_KEY,&r);assert(!crawl_derail_pending);putu((B*)G(0x7be0f4),0);
 }
 putu(car+0xa8,(U)freight);putu(freight+0xa0,(U)car);body[0xf2]=fb[0xf2]=12;
 /* Locomotive on its side: its up points left, so right steering is -world X. */
 wf((U)body+0xc,0);wf((U)body+0x10,1);wf((U)body+0x18,-1);wf((U)body+0x1c,0);
 wf((U)body+0x64,1e-6);wf((U)body+0x74,2e-6);wf((U)body+0x84,3e-6);
 wf(G(0x828fb4),.1);wf(G(0x80acd4),100);strength=10;tick();
 assert(enabled&&!blocked&&active_count==1&&rotation_inputs==CRAWL_RIGHT);
 assert(fabs(rf(body+0x94)+.015)<1e-6&&fabs(rf(body+0x58)+15000)<.1);assert(rf(fb+0x94)==0);
 before=rf(body+0x58);tick();assert(rf(body+0x58)==before); /* same simulation instant */
 test_focus=0;wf(G(0x80acd4),101);tick();assert(!rotation_inputs&&rf(body+0x58)==before);test_focus=1;
 putu((B*)G(0x7be0f4),1);wf(G(0x80acd4),102);tick();assert(!rotation_inputs&&rf(body+0x58)==before);putu((B*)G(0x7be0f4),0);
 strength=0;wf(G(0x80acd4),103);tick();assert(!rotation_inputs&&rf(body+0x58)==before);strength=10;
 /* At full throttle, steering must reach both native derivative helpers. */
 wf((U)ctl+0x8c,1);wf(G(0x80acd4),104);tick();
 {PitchContext ctx,helper;ThreadCalls *t;memset(&ctx,0,sizeof(ctx));ctx.stack[0]=1234;ctx.stack[2]=(U)body;
  hook_enter(PITCH,&ctx.r);t=TlsGetValue(tls_index);assert(t->calls[0].filtered[0]==rf(body+0x94));
  memset(&helper,0,sizeof(helper));helper.r.ecx=(U)body+0x94;helper.stack[0]=0x5f8796;hook_enter(VECTOR,&helper.r);assert(helper.r.ecx==(U)t->calls[0].filtered);hook_leave(PITCH,&ctx.r);
 }
 memset(bits,0,32);wf(G(0x80acd4),105);tick();assert(!rotation_inputs);
 {PitchContext ctx;ThreadCalls *t;memset(&ctx,0,sizeof(ctx));ctx.stack[0]=1234;ctx.stack[2]=(U)body;hook_enter(PITCH,&ctx.r);t=TlsGetValue(tls_index);assert(fabs(t->calls[0].filtered[0])<1e-8);hook_leave(PITCH,&ctx.r);}
 /* Horn righting reaches momentum, not just the isolated calculation. */
 bits[0x39/8]=1<<(0x39%8);wf((U)ctl+0x8c,0);wf(G(0x80acd4),106);tick();
 assert(rotation_inputs==CRAWL_RIGHTING&&rf(body+0x9c)<0&&rf(body+0x60)<0);
 {PitchContext ctx;memset(&ctx,0,sizeof(ctx));ctx.r.ecx=(U)body+0x94;ctx.stack[0]=0x62b207;wf((U)&ctx.stack[2],-10);hook_enter(DRAG,&ctx.r);assert(rf(&ctx.stack[2])==0);
  ctx.r.ecx=(U)body+0x88;ctx.stack[0]=0x62b18a;wf((U)&ctx.stack[2],-10);hook_enter(DRAG,&ctx.r);assert(rf(&ctx.stack[2])==-10);
 }
 before=rf(body+0x60);wf(G(0x828fb4),0);wf(G(0x80acd4),107);tick();assert(!active_count&&rf(body+0x60)==before);wf(G(0x828fb4),.1);
 /* Invalid later engine must not leave an earlier one partially modified. */
 {B *bad=vehicle(1),*badbody=(B*)ru(bad+0x5c);putu(freight+0xa8,(U)bad);putu(bad+0xa0,(U)freight);badbody[0xf2]=4;
  wf((U)badbody+0x1c,1);wf(G(0x80acd4),108);tick();assert(blocked&&!enabled&&rf(body+0x60)==before);
 }
 clear_activity();assert(!rotation_inputs&&!control_id);
 puts("PASS crawl controls: steam/diesel/electric bindings, remapping/modifiers, disabled actions, release/menu/focus/pause/strength gates, standstill local-up impulse, freight exclusion and full-throttle pitch interaction.");return 0;
}
