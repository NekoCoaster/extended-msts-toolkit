/* Execute each production x87 picking operand in the native conversion:
   camera extent / client extent * cursor position. No game process needed. */
#include <assert.h>
#include "../runtime/loader.c"
int main(void){
 typedef float (*Convert)(float,float);
 Hook hooks[24];B *page,*p;DWORD old;int i,j,k,remainder=0;
 int sizes[][2]={{640,480},{800,600},{1920,1080},{1918,829},{3440,1440},{900,1600},{8192,8192}};
 float converted;Convert convert;
 editor_picking_hooks(hooks);
 page=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);assert(page);
 for(i=0;i<24;i++){
  p=page+i*32;memcpy(p,"\xd9\x44\x24\x04",4);p+=4;
  memcpy(p,hooks[i].replacement,6);p+=6;
  memcpy(p,"\xd8\x4c\x24\x08\xc3",5);
 }
 assert(VirtualProtect(page,4096,PAGE_EXECUTE_READ,&old));FlushInstructionCache(GetCurrentProcess(),page,4096);
 for(j=0;j<sizeof(sizes)/sizeof(sizes[0]);j++){
  editor_pick_width=(float)sizes[j][0];editor_pick_height=(float)sizes[j][1];
  for(i=0;i<24;i++){
   float extent=i<12?editor_pick_width:editor_pick_height;convert=(Convert)(page+i*32);
   for(k=0;k<=4;k++){
    float cursor=(extent-1)*k/4;converted=convert(extent,cursor);
    assert(fabs(converted-cursor)<.001);
    /* During deferred resize, client and camera extents can differ. */
    converted=convert(extent*1.5f,cursor*1.5f);assert(fabs(converted-cursor)<.002);
   }
  }
 }
 assert(editor_wheel_steps(&remainder,30)==0&&remainder==30);
 assert(editor_wheel_steps(&remainder,89)==0&&remainder==119);
 assert(editor_wheel_steps(&remainder,1)==1&&remainder==0);
 assert(editor_wheel_steps(&remainder,-60)==0&&remainder==-60);
 assert(editor_wheel_steps(&remainder,-300)==-3&&remainder==0);
 assert(editor_wheel_steps(&remainder,300)==2&&remainder==60);
 assert(editor_wheel_steps(&remainder,-120)==0&&remainder==-60);
 assert(editor_wheel_steps(&remainder,60)==0&&remainder==0);
 VirtualFree(page,0,MEM_RELEASE);
 puts("PASS 1680 native picking conversions across 24 sites/seven sizes, including deferred resize; wheel detents, partial deltas and reversals.");return 0;
}
