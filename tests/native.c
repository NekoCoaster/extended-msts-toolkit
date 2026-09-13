#include <stdio.h>
#include <assert.h>
#include "../runtime/hooks.h"
#include "../runtime/physics.h"
static Hook test_hook;
static U original_return,enter_count,leave_count,seen_ecx,fp_mode,gate_open=1,pause_gate;
static volatile double calculation;
static void hook_enter(U id,Registers *r){U *s=(U*)(r+1);enter_count++;seen_ecx=r->ecx;if(!fp_mode)s[1]+=10;original_return=s[0];s[0]=(U)test_hook.leave;calculation=sqrt(2.0);}
static void hook_leave(U id,Registers *r){leave_count++;*((U*)(r+1))=original_return;if(!fp_mode)r->eax+=100;calculation=sqrt(3.0);}
int main(void){
 B *code,*p;DWORD old;int i;double dp[3],dv[3],speed;float a[3]={0,0,1},v[3]={0,0,10},omega[3]={2,3,4},out[3];
 typedef int (__stdcall *Fn)(int);Fn fn;
 assert(calc_impulse(a,v,100000,200000,1000000,1,1,.1,10,dp,dv));assert(fabs(dp[2]-100000)<.01);assert(fabs(dv[2]-1)<.00001);
 assert(calc_impulse(a,v,100000,200000,1000000,.5,-1,5,100,dp,dv));assert(fabs(dp[2]+1250000)<.01);
 assert(calc_impulse(a,v,100000,200000,1000000,1,1,.1,0,dp,dv)&&dp[2]==0);
 assert(!calc_impulse(a,v,0,200000,1000000,1,1,.1,10,dp,dv));
 assert(calc_pitch(omega,a,0,out)&&out[0]==0&&out[1]==3&&out[2]==4);
 assert(calc_pitch(omega,a,.5,out)&&out[0]==1);
 assert(calc_wheel(v,a,.5,10,&speed)&&speed==50);
 assert(calc_wheel(v,a,1,100,&speed)&&speed==1000);
 /* Synthetic stdcall target: ordinary verified prologue, argument return, RET 4.
    The real gateways must preserve stack cleanup and propagate onLeave EAX. */
 code=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);assert(code);
 memcpy(code,"\x55\x8b\xec\x83\xec\x08\x8b\x45\x08\xc9\xc2\x04\x00",13);
 VirtualProtect(code,4096,PAGE_EXECUTE_READ,&old);test_hook.address=(U)code;test_hook.length=6;memcpy(test_hook.original,code,6);
 test_hook.gate=(U)&gate_open;test_hook.pause=(U)&pause_gate;
 assert(prepare_hooks(&test_hook,1));assert(install_hooks(&test_hook,1));fn=(Fn)code;
 for(i=0;i<10000;i++)assert(fn(i)==i+110);
 assert(enter_count==10000&&leave_count==10000);
 gate_open=0;for(i=0;i<10000;i++)assert(fn(i)==i);assert(enter_count==10000);
 gate_open=1;pause_gate=1;for(i=0;i<10000;i++)assert(fn(i)==i);assert(enter_count==10000);pause_gate=0;
 fp_mode=1;
 code=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);assert(code);
 memcpy(code,"\x55\x8b\xec\x83\xec\x08\xdd\x45\x08\xc9\xc2\x08\x00",13);
 VirtualProtect(code,4096,PAGE_EXECUTE_READ,&old);test_hook.address=(U)code;test_hook.length=6;memcpy(test_hook.original,code,6);
 assert(prepare_hooks(&test_hook,1));assert(install_hooks(&test_hook,1));
 {typedef double (__stdcall *DoubleFn)(double);DoubleFn f=(DoubleFn)code;for(i=0;i<10000;i++)assert(f(i+.125)==i+.125);}
 {B *caller;U sites[6]={1,2,3,4,5,6};Fn callfn;fp_mode=0;
  code=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);assert(code);
  memcpy(code,"\x55\x8b\xec\x83\xec\x08\x8b\x45\x08\xc9\xc2\x04\x00",13);VirtualProtect(code,4096,PAGE_EXECUTE_READ,&old);
  caller=p=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);assert(caller);
  memcpy(p,"\x55\x8b\xec\xff\x75\x08",6);p+=6;branch(&p,0xe8,code);sites[5]=(U)p;memcpy(p,"\xc9\xc2\x04\x00",4);
  VirtualProtect(caller,4096,PAGE_EXECUTE_READ,&old);test_hook.address=(U)code;test_hook.length=6;memcpy(test_hook.original,code,6);test_hook.sites=sites;test_hook.site_count=6;
  assert(prepare_hooks(&test_hook,1));assert(install_hooks(&test_hook,1));fn=(Fn)code;callfn=(Fn)caller;
  for(i=0;i<10000;i++){assert(fn(i)==i);assert(callfn(i)==i+110);}
 }
 puts("PASS native math; integer/x87 return detours; inactive/paused bypasses; six-site caller filter; 60,000 total checked calls and preserved stack cleanup.");return 0;
}
