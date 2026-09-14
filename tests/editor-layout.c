#include <assert.h>
#include <stdio.h>
#include "../runtime/editor_layout.h"
int main(void){
 EditorRect work={0,0,1920,1080},outer={100,100,1100,800},client={108,130,1092,792};EditorLayout p;int ox,oy,r,b,cases=0;
 for(ox=-1920;ox<=1920;ox+=1920)for(oy=-1080;oy<=1080;oy+=1080)for(r=0;r<2;r++)for(b=0;b<2;b++){
  work.left=ox;work.top=oy;work.right=ox+1920;work.bottom=oy+1080;
  outer.left=ox+(r?850:100);outer.right=outer.left+1000;
  outer.top=oy+(b?380:100);outer.bottom=outer.top+700;
  client.left=outer.left+8;client.top=outer.top+30;client.right=outer.right-8;client.bottom=outer.bottom-8;
  p=editor_layout(outer,client,work,354,648,646,178);
  assert(p.fold_right==r&&p.fold_bottom==b);
  assert(p.right_x>=work.left&&p.right_x+354<=work.right&&p.right_y>=work.top&&p.right_y+648<=work.bottom);
  assert(p.bottom_x>=work.left&&p.bottom_x+646<=work.right&&p.bottom_y>=work.top&&p.bottom_y+178<=work.bottom);
  if(r&&b)assert(p.min_width>=1000&&p.min_height>=648);
  cases++;
 }
 /* Both groups fit inside the minimum client without overlapping. */
 work=(EditorRect){0,0,1016,686};outer=work;client=(EditorRect){8,30,1008,678};
 p=editor_layout(outer,client,work,354,648,646,178);
 assert(p.fold_right&&p.fold_bottom&&p.bottom_x+646<=p.right_x);
 /* Clamp safely even on a desktop smaller than the native palettes. */
 work=(EditorRect){-300,-200,300,200};p=editor_layout(outer,client,work,354,648,646,178);
 assert(p.right_x>=-300&&p.right_y>=-200&&p.bottom_x>=-300&&p.bottom_y>=-200);
 printf("PASS %d independent folding / monitor-origin cases, minimum layout and small-desktop fallback.\n",cases);
 return 0;
}
