/* MIT: limited x86 detours for explicitly verified MSTS prologues.
   Not a generic instruction relocator. Never use on an unverified executable. */
#include <windows.h>
/* TCC's compact Win32 headers omit tlhelp32.h. Win32 SDK ABI declarations. */
typedef struct {DWORD dwSize,cntUsage,th32ThreadID,th32OwnerProcessID;LONG tpBasePri,tpDeltaPri;DWORD dwFlags;} THREADENTRY32;
#define TH32CS_SNAPTHREAD 4
__declspec(dllimport) HANDLE WINAPI CreateToolhelp32Snapshot(DWORD,DWORD);
__declspec(dllimport) BOOL WINAPI Thread32First(HANDLE,THREADENTRY32*);
__declspec(dllimport) BOOL WINAPI Thread32Next(HANDLE,THREADENTRY32*);
#include <string.h>
typedef unsigned int U;
typedef unsigned char B;
typedef struct {U edi,esi,ebp,esp,ebx,edx,ecx,eax,flags;} Registers;
typedef struct {U address,length; B original[16]; B *entry,*leave,*trampoline;U gate,pause,site_count;const U *sites;U raw;B replacement[16];} Hook;
static void hook_enter(U id,Registers *r);
static void hook_leave(U id,Registers *r);
static B *code_memory;
static void emit8(B **p,U n){*(*p)++=(B)n;}
static void emit32(B **p,U n){memcpy(*p,&n,4);*p+=4;}
static void branch(B **p,U opcode,void *target){emit8(p,opcode);emit32(p,(U)target-(U)*p-4);}
static void fast_gate(B **p,Hook *h){
 B *closed=NULL,*paused_branch=NULL,*accepted[6],*skip,*normal;U i;
 if(!h->gate&&!h->site_count)return;
 emit8(p,0x9c); /* preserve flags; no GPR or floating-point state is touched */
 if(h->gate){
  emit8(p,0x83);emit8(p,0x3d);emit32(p,h->gate);emit8(p,0);
  emit8(p,0x0f);emit8(p,0x84);closed=*p;emit32(p,0);
 }
 if(h->pause){
  emit8(p,0x83);emit8(p,0x3d);emit32(p,h->pause);emit8(p,0);
  emit8(p,0x0f);emit8(p,0x85);paused_branch=*p;emit32(p,0);
 }
 for(i=0;i<h->site_count;i++){
  emit8(p,0x81);emit8(p,0x7c);emit8(p,0x24);emit8(p,4);emit32(p,h->sites[i]);
  emit8(p,0x0f);emit8(p,0x84);accepted[i]=*p;emit32(p,0);
 }
 if(!h->site_count){emit8(p,0xe9);normal=*p;emit32(p,0);}else normal=NULL;
 skip=*p;emit8(p,0x9d);branch(p,0xe9,h->trampoline);
 if(closed)*(U*)closed=(U)skip-(U)closed-4;
 if(paused_branch)*(U*)paused_branch=(U)skip-(U)paused_branch-4;
 if(normal)*(U*)normal=(U)*p-(U)normal-4;
 for(i=0;i<h->site_count;i++)*(U*)accepted[i]=(U)*p-(U)accepted[i]-4;
 emit8(p,0x9d);
}
static void gateway(B **p,U id,void *callback,void *tail,int leave){
 if(leave){emit8(p,0x6a);emit8(p,0);} /* return destination reserved above saved flags */
 emit8(p,0x9c);emit8(p,0x60);emit8(p,0xfc); /* flags, all GPRs, CLD */
 emit8(p,0x89);emit8(p,0xe3); /* ebx=register context */
 emit8(p,0x81);emit8(p,0xec);emit32(p,528);
 emit8(p,0x83);emit8(p,0xe4);emit8(p,0xf0); /* align FXSAVE area */
 emit8(p,0x0f);emit8(p,0xae);emit8(p,0x04);emit8(p,0x24);
 emit8(p,0xdb);emit8(p,0xe3); /* FNINIT: callbacks get an empty x87 stack */
 emit8(p,0x89);emit8(p,0xe5); /* ebp=FXSAVE area (callee saved) */
 emit8(p,0x53);emit8(p,0x68);emit32(p,id);branch(p,0xe8,callback);
 emit8(p,0x83);emit8(p,0xc4);emit8(p,8);
 emit8(p,0x0f);emit8(p,0xae);emit8(p,0x4d);emit8(p,0); /* FXRSTOR [ebp] */
 emit8(p,0x89);emit8(p,0xdc);emit8(p,0x61);emit8(p,0x9d);
 if(leave)emit8(p,0xc3);else branch(p,0xe9,tail);
}
static int prepare_hooks(Hook *hooks,U count){
 U i,j;DWORD old;B *p;
 code_memory=VirtualAlloc(NULL,count*512,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
 if(!code_memory)return 0;
 for(i=0;i<count;i++){
  Hook *h=&hooks[i];
  if(h->length<(h->raw?1:5)||h->length>16||h->site_count>6||memcmp((void*)h->address,h->original,h->length))goto fail;
  for(j=0;j<i;j++)if(h->address<hooks[j].address+hooks[j].length&&hooks[j].address<h->address+h->length)goto fail;
  if(h->raw)continue;
  h->trampoline=p=code_memory+i*512;
  memcpy(p,h->original,h->length);p+=h->length;
  /* Only relocated relative instruction: teardown prologue CALL at +4. */
  if(h->address==0x51d963){U target=h->address+9+*(U*)(h->original+5);*(U*)(h->trampoline+5)=target-(U)h->trampoline-9;}
  branch(&p,0xe9,(void*)(h->address+h->length));
  h->entry=p;fast_gate(&p,h);gateway(&p,i,hook_enter,h->trampoline,0);
  h->leave=p;gateway(&p,i,hook_leave,NULL,1);
  if(p>code_memory+(i+1)*512)goto fail;
 }
 if(!VirtualProtect(code_memory,count*512,PAGE_EXECUTE_READ,&old))goto fail;
 FlushInstructionCache(GetCurrentProcess(),code_memory,count*512);return 1;
fail:VirtualFree(code_memory,0,MEM_RELEASE);code_memory=NULL;return 0;
}
/* Prepare everything before suspending. No heap allocation or application calls
   while peers are suspended. Retry if a thread is inside displaced instructions. */
static int install_hooks(Hook *hooks,U count){
 HANDLE snapshot,threads[256];THREADENTRY32 te;U n=0,i,j,done=0;DWORD old;int ok=1;
 snapshot=CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0);if(snapshot==INVALID_HANDLE_VALUE)return 0;
 te.dwSize=sizeof(te);
 if(!Thread32First(snapshot,&te))ok=0;
 else do{
  if(te.th32OwnerProcessID!=GetCurrentProcessId()||te.th32ThreadID==GetCurrentThreadId())continue;
  if(n==256){ok=0;break;}
  threads[n]=OpenThread(THREAD_SUSPEND_RESUME|THREAD_GET_CONTEXT|THREAD_QUERY_INFORMATION,FALSE,te.th32ThreadID);
  if(!threads[n]){ok=0;break;}n++;
 }while(Thread32Next(snapshot,&te));CloseHandle(snapshot);
 if(!ok)goto close;
 for(i=0;i<n;i++){CONTEXT c;
  if(SuspendThread(threads[i])==(DWORD)-1){ok=0;break;}done++;
  memset(&c,0,sizeof(c));c.ContextFlags=CONTEXT_CONTROL;
  if(!GetThreadContext(threads[i],&c)){ok=0;break;}
  for(j=0;j<count;j++)if(c.Eip>=hooks[j].address&&c.Eip<hooks[j].address+hooks[j].length)ok=0;
  if(!ok)break;
 }
 if(ok){
  for(i=0;i<count;i++){
   Hook *h=&hooks[i];B *p=(B*)h->address;
   if(memcmp(p,h->original,h->length)||!VirtualProtect(p,h->length,PAGE_EXECUTE_READWRITE,&old)){ok=0;break;}
   if(h->raw)memcpy(p,h->replacement,h->length);else{branch(&p,0xe9,h->entry);while(p<(B*)(h->address+h->length))*p++=0x90;}
   VirtualProtect((void*)h->address,h->length,old,&old);
  }
  if(!ok)while(i){Hook *h=&hooks[--i];VirtualProtect((void*)h->address,h->length,PAGE_EXECUTE_READWRITE,&old);memcpy((void*)h->address,h->original,h->length);VirtualProtect((void*)h->address,h->length,old,&old);}
  FlushInstructionCache(GetCurrentProcess(),NULL,0);
 }
 while(done)ResumeThread(threads[--done]);
close:for(i=0;i<n;i++)CloseHandle(threads[i]);return ok;
}
