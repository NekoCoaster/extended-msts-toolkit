#include <assert.h>
#include "../runtime/hooks.h"
#include <stdio.h>
static void hook_enter(U id,Registers *r){}
static void hook_leave(U id,Registers *r){}
int main(void){
 B *page=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_EXECUTE_READWRITE);Hook plan[2];assert(page);memset(page,0x90,4096);memset(plan,0,sizeof(plan));
 plan[0].address=(U)page;plan[0].length=2;plan[0].raw=1;memset(plan[0].original,0x90,2);memset(plan[0].replacement,0xcc,2);
 plan[1]=plan[0];plan[1].address=(U)page+1;assert(!prepare_hooks(plan,2));assert(page[0]==0x90);
 plan[1].address=(U)page+16;assert(prepare_hooks(plan,2));page[16]=0x91;
 assert(!install_hooks(plan,2));assert(page[0]==0x90&&page[1]==0x90&&page[16]==0x91);
 page[16]=0x90;assert(prepare_hooks(plan,2));assert(!code_memory);assert(install_hooks(plan,2));assert(claim_count==2);
 memcpy(plan[0].original,plan[0].replacement,2);assert(!prepare_hooks(plan,1));
 puts("PASS shared mutation transaction: overlapping claims rejected and partial write rolled back on byte mismatch.");return 0;
}
