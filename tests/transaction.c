#include <assert.h>
#include "../runtime/hooks.h"
#include <stdio.h>
static void hook_enter(U id,Registers *r){}
static void hook_leave(U id,Registers *r){}
int main(void){
 B *page=VirtualAlloc(NULL,((MAX_HOOK_CLAIMS+1)*16),MEM_COMMIT|MEM_RESERVE,PAGE_EXECUTE_READWRITE);Hook plan[2];assert(page);memset(page,0x90,((MAX_HOOK_CLAIMS+1)*16));memset(plan,0,sizeof(plan));
 plan[0].address=(U)page;plan[0].length=2;plan[0].raw=1;memset(plan[0].original,0x90,2);memset(plan[0].replacement,0xcc,2);
 plan[1]=plan[0];plan[1].address=(U)page+1;assert(!prepare_hooks(plan,2));assert(page[0]==0x90);
 plan[1].address=(U)page+16;assert(prepare_hooks(plan,2));page[16]=0x91;
 assert(!install_hooks(plan,2));assert(page[0]==0x90&&page[1]==0x90&&page[16]==0x91);
 page[16]=0x90;assert(prepare_hooks(plan,2));assert(!code_memory);assert(install_hooks(plan,2));assert(claim_count==2);
 memcpy(plan[0].original,plan[0].replacement,2);assert(!prepare_hooks(plan,1));
 {Hook many[MAX_HOOK_CLAIMS];U i;
  claim_count=0;memset(claimed,0,sizeof(claimed));memset(page,0x90,((MAX_HOOK_CLAIMS+1)*16));memset(many,0,sizeof(many));
  for(i=0;i<MAX_HOOK_CLAIMS;i++){many[i].address=(U)page+i*16;many[i].length=2;many[i].raw=1;memset(many[i].original,0x90,2);memset(many[i].replacement,0xcc,2);}
  assert(prepare_hooks(many,51)&&install_hooks(many,51));
  /* Live regression: 51 existing claims plus 16 walking/light hooks. */
  assert(prepare_hooks(many+51,16)&&install_hooks(many+51,16));assert(claim_count==67&&page[66*16]==0xcc);
  assert(prepare_hooks(many+67,MAX_HOOK_CLAIMS-67)&&install_hooks(many+67,MAX_HOOK_CLAIMS-67));
  assert(claim_count==MAX_HOOK_CLAIMS);
  plan[0]=many[0];plan[0].address=(U)page+(MAX_HOOK_CLAIMS*16);
  assert(!prepare_hooks(plan,1)&&page[(MAX_HOOK_CLAIMS*16)]==0x90&&claim_count==MAX_HOOK_CLAIMS);
 }
 puts("PASS shared mutation transaction: overlapping claims rejected and partial write rolled back on byte mismatch.");return 0;
}
