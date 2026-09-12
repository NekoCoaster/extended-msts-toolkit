#include <assert.h>
static unsigned char signal_globals[0x60000];
#define SIGNAL_ADDR(a) ((unsigned int)signal_globals+(a)-0x7b0000)
#include "../runtime/loader.c"
static int notices,pauses,inits,texts;
static B controller[0x400],object_a[0x40],object_b[0x40];
static U *flags=(U*)(controller+0x378);
static SignalEntry entries[3];static SignalNode sentinel,nodes[3];
static U __fastcall dispatch(U gui,U method,U reason){assert(gui==99&&method==0x24&&reason==0x1c);notices++;*(U*)SIGNAL_ADDR(0x7b49d8)=1;return 1;}
static U __fastcall set_text(const WCHAR *name,const WCHAR *text){assert(!wcscmp(name,L"s_dlg_text"));assert(!wcscmp(text,L"Activity failed -- ignored red light."));texts++;return 1;}
static void __fastcall pause_game(U value,U unused){assert(value==1&&unused==0);pauses++;}
static void __fastcall init(U a,U b){assert(a==11&&b==12);inits++;}
static void __fastcall monitor(U c,U unused){
 SignalNode *n;assert(c==(U)controller);
 for(n=sentinel.next;n!=&sentinel;n=n->next){SignalEntry *e=n->entry;
  if((e->type==1||e->type==2)&&e->speed==0&&e->distance<15&&!(*(U*)(e->object+0x1c)&0x2000)){*flags|=0x100;return;}
 }
}
static void chain(int count){int i;sentinel.next=count?nodes:&sentinel;for(i=0;i<count;i++){nodes[i].next=i+1<count?nodes+i+1:&sentinel;nodes[i].entry=entries+i;}}
static void dismiss(void){*(U*)SIGNAL_ADDR(0x7b49d8)=0;}
int main(void){
 B *code,*p,*adapter;int i;U (__fastcall *call)(U,U);
 signal_original_monitor=monitor;signal_original_init=init;signal_dispatch=dispatch;signal_text=set_text;signal_pause=pause_game;
 *(U*)SIGNAL_ADDR(0x809f1c)=(U)&sentinel;*(U*)SIGNAL_ADDR(0x7b49c8)=99;
 entries[0].type=1;entries[0].object=(U)object_a;entries[0].distance=10;entries[1]=entries[0];entries[1].type=2;
 chain(2);*flags=0x10002;signal_monitor((U)controller,0);assert(*flags==0x10102&&signal_seen_count==1);
 signal_notice((U)controller,0x24,2);assert(notices==1&&texts==1&&pauses==1&&*flags==0x10002);dismiss();
 for(i=0;i<10000;i++){signal_monitor((U)controller,0);signal_notice((U)controller,0x24,2);}assert(notices==1&&*flags==0x10002);
 entries[0].speed=20;entries[1].speed=20;signal_monitor((U)controller,0);entries[0].speed=0;signal_monitor((U)controller,0);assert(!(*flags&0x100));
 entries[1].object=(U)object_b;entries[1].speed=0;signal_monitor((U)controller,0);assert(*flags&0x100);
 *(U*)SIGNAL_ADDR(0x7b49d8)=1;signal_notice((U)controller,0x24,2);assert(notices==1&&(*flags&0x100));dismiss();
 *(float*)SIGNAL_ADDR(0x80ad20)=1;signal_notice((U)controller,0x24,2);assert(notices==1);*(float*)SIGNAL_ADDR(0x80ad20)=0;
 signal_notice((U)controller,0x24,2);assert(notices==2&&*flags==0x10002);dismiss();
 chain(0);signal_monitor((U)controller,0);assert(!signal_seen_count);chain(1);signal_monitor((U)controller,0);signal_notice((U)controller,0x24,2);assert(notices==3);dismiss();
 signal_init(11,12);assert(inits==1&&!signal_seen_count&&!signal_pending);signal_monitor((U)controller,0);assert(*flags&0x100);
 signal_notice((U)controller,0x24,5);assert(notices==3&&(*flags&0x100));
 /* Execute the actual adapter with the verified EBP-4 caller layout. */
 code=VirtualAlloc(NULL,128,MEM_COMMIT|MEM_RESERVE,PAGE_EXECUTE_READWRITE);assert(code);p=code;adapter=code+64;signal_adapter(&adapter);adapter=code+64;
 emit8(&p,0x55);emit8(&p,0x89);emit8(&p,0xe5);emit8(&p,0x83);emit8(&p,0xec);emit8(&p,4);
 emit8(&p,0x89);emit8(&p,0x4d);emit8(&p,0xfc);emit8(&p,0x6a);emit8(&p,2);branch(&p,0xe8,adapter);
 emit8(&p,0x89);emit8(&p,0xec);emit8(&p,0x5d);emit8(&p,0xc3);call=(void*)code;
 for(i=0;i<10000;i++){*flags|=0x100;call((U)controller,0x24);assert(!(*flags&0x100));dismiss();}
 assert(notices==10003&&texts==notices&&pauses==notices);VirtualFree(code,0,MEM_RELEASE);
 puts("PASS native signal adapter ABI; duplicate signal objects; 10000 repeated checks; later signal; changed aspect; exit/reapproach; activity reset; deferred popup; other failure bits preserved.");return 0;
}
