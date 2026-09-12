#include <assert.h>
#include "../runtime/loader.c"
static int calls;
static LPSTR WINAPI compatibility_command_line(void){calls++;return "train.exe -vm:w,1280,720,32";}
int main(void){
 volatile LONG *slot=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);char translated[128];
 assert(slot);*slot=0;assert(!redirect_command_line(slot));
 *slot=(LONG)slot;assert(!redirect_command_line(slot));assert(claim_count==0);
 *slot=(LONG)compatibility_command_line;assert(*slot!=(LONG)GetCommandLineA);
 assert(redirect_command_line(slot));assert(original_command_line==compatibility_command_line);assert(claim_count==1);
 assert(normalize_vm(original_command_line(),translated)==1);assert(!strcmp(translated,"train.exe -vm:w,1280,720,32"));
 /* Exercise the installed forwarding path after initialization. */
 normalized_command_line=translated;window_initialized=2;
 assert(!strcmp(((CmdLineFn)*slot)(),translated));assert(calls==2);
 assert(!redirect_command_line(slot));assert(claim_count==1);
 puts("PASS redirected compatibility import chaining, argument translation, invalid target rejection and duplicate rejection.");return 0;
}
