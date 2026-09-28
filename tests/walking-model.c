#include <stdio.h>
#include <stdlib.h>
#include "../runtime/walking-model.h"
static int checks;
#define CHECK(x) do {checks++;if(!(x)){printf("FAIL line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static int flat(void *ctx,double x,double z,double *h){*h=ctx?*(double*)ctx:0;return 1;}
static int missing(void *ctx,double x,double z,double *h){return 0;}
static int slope(void *ctx,double x,double z,double *h){*h=z*0.2;return z<1;}
int main(void){
 WalkState s;WalkInput in;double peak=0,eye=2,ground=2000,dt=0.001;int i;
 memset(&in,0,sizeof(in));CHECK(walk_begin(&s,0,0,eye,0,flat,&ground));
 CHECK(s.y==2000&&s.eye_height==2&&s.grounded);
 in.jump=1;for(i=0;i<1200;i++){walk_step(&s,&in,dt,0,flat,&ground);if(s.y-ground>peak)peak=s.y-ground;}
 CHECK(fabs(peak-1)<0.00001);CHECK(s.grounded&&s.y==ground); /* Held Space does not repeat. */
 CHECK(s.y+s.eye_height==2002);
 in.jump=0;walk_step(&s,&in,dt,0,flat,&ground);in.jump=1;walk_step(&s,&in,dt,0,flat,&ground);CHECK(!s.grounded);
 memset(&in,0,sizeof(in));CHECK(walk_begin(&s,0,0,2,0,flat,0));in.height_up=1;
 for(i=0;i<20;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(s.eye_height-2.05)<1e-9);
 in.height_up=0;in.height_down=1;walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(s.eye_height-2)<1e-9);
 memset(&in,0,sizeof(in));in.forward=in.right=1;
 for(i=0;i<100;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(sqrt(s.x*s.x+s.z*s.z)-1.4)<1e-8);
 in.look_x=100;walk_step(&s,&in,0.01,0,flat,0);CHECK(s.yaw==0);
 in.look=1;walk_step(&s,&in,0.01,0,flat,0);CHECK(s.yaw==0.25);
 memset(&in,0,sizeof(in));in.toggle_noclip=1;walk_step(&s,&in,0.01,0,flat,0);CHECK(s.noclip);
 in.up=1;for(i=0;i<100;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(s.y-10)<1e-8);CHECK(s.noclip);
 in.toggle_noclip=0;walk_step(&s,&in,0.01,0,flat,0);in.toggle_noclip=1;walk_step(&s,&in,0.01,0,missing,0);CHECK(s.noclip);
 in.toggle_noclip=0;walk_step(&s,&in,0.01,0,flat,0);in.toggle_noclip=1;walk_step(&s,&in,0.01,0,flat,0);CHECK(!s.noclip&&s.grounded&&s.y==0);
 CHECK(!walk_begin(&s,0,0,2,0,missing,0));
 CHECK(walk_begin(&s,0,0,2,0,slope,0));memset(&in,0,sizeof(in));in.forward=1;
 for(i=0;i<200;i++)walk_step(&s,&in,0.01,0,slope,0);CHECK(s.z<1&&s.z>0.98);CHECK(fabs(s.y-s.z*0.2)<1e-9);
 {double z=s.z;walk_step(&s,&in,1,1,slope,0);CHECK(s.z==z);}
 printf("Walking model: %d checks passed\n",checks);return 0;
}
