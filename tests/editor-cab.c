#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "../runtime/editor_layout.h"
int main(void){
 int sizes[][2]={{640,480},{1920,1080},{3440,1440},{900,1600},{1918,829},{800,600},{8192,8192}};
 int i,x,y;EditorRect r;
 for(i=0;i<sizeof(sizes)/sizeof(sizes[0]);i++){
  int w=sizes[i][0],h=sizes[i][1];r=editor_cab_fit(w,h);
  assert(r.left>=0&&r.top>=0&&r.right<=w&&r.bottom<=h);
  assert(w-r.right-r.left>=0&&w-r.right-r.left<=1);
  assert(h-r.bottom-r.top>=0&&h-r.bottom-r.top<=1);
  assert(abs((r.right-r.left)*3-(r.bottom-r.top)*4)<=3);
  for(x=0;x<640;x+=19)for(y=0;y<480;y+=17){
   int sx=editor_cab_screen_coordinate(x,r.left,r.right-r.left,640);
   int sy=editor_cab_screen_coordinate(y,r.top,r.bottom-r.top,480);
   assert(editor_cab_coordinate(sx,r.left,r.right-r.left,640)==x);
   assert(editor_cab_coordinate(sy,r.top,r.bottom-r.top,480)==y);
  }
  assert(editor_cab_coordinate(r.left-1,r.left,r.right-r.left,640)==-1);
  assert(editor_cab_coordinate(r.right,r.left,r.right-r.left,640)==640);
 }
 puts("PASS cab aspect ratio, centered fit, letterbox exclusion and mouse round trips at seven display sizes.");return 0;
}
