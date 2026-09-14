/* Counter-tilt removal: native orientation and helper sites remain untouched. */
#include <assert.h>
#include "../runtime/loader.c"
int main(void){unsigned i,j;unsigned sites[]={0x5f874c,0x5f9ca0,0x5fd2ca};
 for(i=0;i<HOOK_COUNT;i++)for(j=0;j<3;j++)assert(hooks[i].address!=sites[j]);
 assert(HOOK_COUNT==9);puts("PASS no counter-tilt hooks in the crawl installation.");return 0;
}
