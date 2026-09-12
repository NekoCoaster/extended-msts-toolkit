/* MIT. Native non-ending alert; callbacks run on the simulation/UI thread. */
#ifndef SIGNAL_ADDR
#define SIGNAL_ADDR(a) (a)
#endif
static Hook signal_hooks[3];static B *signal_code;
static void (__fastcall *signal_original_monitor)(U,U)=(void*)0x5864ee;
static void (__fastcall *signal_original_init)(U,U)=(void*)0x5aeeb3;
static U (__fastcall *signal_dispatch)(U,U,U)=(void*)0x58ea72;
static U (__fastcall *signal_text)(const WCHAR*,const WCHAR*)=(void*)0x44c54d;
static void (__fastcall *signal_pause)(U,U)=(void*)0x4b7d70;
#define SIGNAL_CAPACITY 64
 typedef struct {U type;float distance,radius,gradient,speed;U object;} SignalEntry;
 typedef struct SignalNode {struct SignalNode *next,*previous;SignalEntry *entry;} SignalNode;
static U signal_seen[SIGNAL_CAPACITY],signal_seen_count,signal_pending,signal_controller,signal_root;
static void signal_reset(void){signal_seen_count=signal_pending=signal_controller=signal_root=0;}
static void __fastcall signal_init(U ecx,U edx){signal_reset();signal_original_init(ecx,edx);}
static int signal_contains(const U *items,U count,U item){U i;for(i=0;i<count;i++)if(items[i]==item)return 1;return 0;}
/* The original monitor has just dereferenced this list on the same thread.
   Key by referenced signal object, not temporary list nodes. Keep identities
   until they leave the list, including transient aspect changes. */
static int signal_collect(SignalNode *root){
 U current[SIGNAL_CAPACITY],retained[SIGNAL_CAPACITY],count=0,keep=0,visits=0,i,added=0;
 SignalNode *n;SignalEntry *e;
 if(!root)return 0;
 for(n=root->next;n!=root;n=n->next){
  if(!n||!n->entry||++visits>256)return 0;
  e=n->entry;
  if((e->type!=1&&e->type!=2)||!e->object)continue;
  if(signal_contains(signal_seen,signal_seen_count,e->object)&&!signal_contains(retained,keep,e->object)){
   if(keep==SIGNAL_CAPACITY)return 0;retained[keep++]=e->object;
  }
  if(e->speed!=0||!(e->distance<15)||(*(U*)(e->object+0x1c)&0x2000))continue;
  if(!signal_contains(current,count,e->object)){
   if(count==SIGNAL_CAPACITY)return 0;current[count++]=e->object;
  }
 }
 for(i=0;i<count;i++)if(!signal_contains(retained,keep,current[i])){
  if(keep==SIGNAL_CAPACITY)return 0;retained[keep++]=current[i];added++;
 }
 memcpy(signal_seen,retained,keep*sizeof(U));signal_seen_count=keep;
 /* Simultaneous entries share one notice. */
 if(added)signal_pending=1;
 return 1;
}
static void __fastcall signal_monitor(U controller,U edx){
 U root,flags;
 signal_original_monitor(controller,edx);
 root=*(U*)SIGNAL_ADDR(0x809f1c);
 if(controller!=signal_controller||root!=signal_root){signal_reset();signal_controller=controller;signal_root=root;}
 flags=*(U*)(controller+0x378);
 if(!signal_collect((SignalNode*)root))return;
 if(signal_pending)flags|=0x100;else flags&=~0x100u;
 *(U*)(controller+0x378)=flags;
}
static U __fastcall signal_notice(U controller,U method,U reason){
 U flags,gui;
 if(method!=0x24||reason!=2||!controller||!read_memory(controller+0x378,&flags,4)||!(flags&0x100))return 0;
 /* Leave the failure bit latched while another native popup is active. */
 if(*(U*)SIGNAL_ADDR(0x7b49d8)||!(*(float*)SIGNAL_ADDR(0x80ad20)<=0))return 0;
 gui=*(U*)SIGNAL_ADDR(0x7b49c8);if(!gui)return 0;
 /* Existing ALERT/OK popup; OK dispatches reason 19 (hide and resume).
    This branch clears both activity-ending flags. */
 signal_dispatch(gui,0x24,0x1c);
 if(!*(U*)SIGNAL_ADDR(0x7b49d8))return 0;
 signal_text(L"s_dlg_text",L"Activity failed -- ignored red light.");
 signal_pause(1,0);
 *(U*)(controller+0x378)=flags&~0x100u;signal_pending=0;
 return 0;
}
static void signal_adapter(B **p){emit8(p,0x8b);emit8(p,0x4d);emit8(p,0xfc);branch(p,0xe9,signal_notice);}
static int install_signal_hook(void){
 DWORD old;B *p;
 if(!ignore_red_signal)return 1;
 if(memcmp((void*)0x586293,"\x55\x8b\xec\x83\xec\x08",6)||
    memcmp((void*)0x58643c,"\x6a\x02\xba\x24\x00\x00\x00\x8b\x0d\xc8\x49\x7b\x00",13)||
    memcmp((void*)0x447e61,"\x55\x8b\xec\x83\xec\x1c",6)||
    memcmp((void*)0x44c54d,"\x55\x8b\xec\x83\xec\x14",6))return 0;
 signal_code=VirtualAlloc(NULL,32,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!signal_code)return 0;
 p=signal_code;signal_adapter(&p);
 if(!VirtualProtect(signal_code,32,PAGE_EXECUTE_READ,&old))goto failed;
 FlushInstructionCache(GetCurrentProcess(),signal_code,32);
 startup_call(&signal_hooks[0],0x586449,0x58ea72,(U)signal_code);
 startup_call(&signal_hooks[1],0x4013c5,0x5864ee,(U)signal_monitor);
 signal_hooks[1].original[0]=signal_hooks[1].replacement[0]=0xe9;
 startup_call(&signal_hooks[2],0x403ecc,0x5aeeb3,(U)signal_init);
 signal_hooks[2].original[0]=signal_hooks[2].replacement[0]=0xe9;
 if(prepare_hooks(signal_hooks,3)&&install_hooks(signal_hooks,3))return 1;
failed:VirtualFree(signal_code,0,MEM_RELEASE);signal_code=NULL;return 0;
}
