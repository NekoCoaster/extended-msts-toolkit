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
 for(i=0;i<100;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(sqrt(s.x*s.x+s.z*s.z)-3)<1e-8);
 in.look_x=100;walk_step(&s,&in,0.01,0,flat,0);CHECK(s.yaw==0);
 in.look=1;walk_step(&s,&in,0.01,0,flat,0);CHECK(s.yaw==0.25);
 memset(&in,0,sizeof(in));in.toggle_noclip=1;walk_step(&s,&in,0.01,0,flat,0);CHECK(s.noclip);
 in.up=1;for(i=0;i<100;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(s.y-17)<1e-8);CHECK(s.noclip);
 in.toggle_noclip=0;walk_step(&s,&in,0.01,0,flat,0);in.toggle_noclip=1;walk_step(&s,&in,0.01,0,missing,0);CHECK(s.noclip);
 in.toggle_noclip=0;walk_step(&s,&in,0.01,0,flat,0);in.toggle_noclip=1;walk_step(&s,&in,0.01,0,flat,0);CHECK(!s.noclip&&!s.grounded&&s.y>17);
 memset(&in,0,sizeof(in));for(i=0;i<300;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(s.grounded&&s.y==0);
 CHECK(!walk_begin(&s,0,0,2,0,missing,0));
 CHECK(walk_begin(&s,0,0,2,0,slope,0));memset(&in,0,sizeof(in));in.forward=1;
 for(i=0;i<200;i++)walk_step(&s,&in,0.01,0,slope,0);CHECK(s.z<1&&s.z>0.98);CHECK(fabs(s.y-s.z*0.2)<1e-9);
 {double z=s.z;walk_step(&s,&in,1,1,slope,0);CHECK(s.z==z);}
 CHECK(walk_fov_step(1,1)==5);CHECK(walk_fov_step(5,-1)==1);
 CHECK(walk_fov_step(175,1)==179);CHECK(walk_fov_step(179,-1)==175);
 CHECK(walk_fov_step(179,1)==179);CHECK(walk_fov_step(1,-1)==1);
 CHECK(walk_fov_step(62,1)==65);CHECK(walk_fov_step(62,-1)==60);
 CHECK(walk_fov_step(59.9999538,-1)==55);CHECK(walk_fov_step(60.00001,1)==65);
 {double fov=1;for(i=5;i<=175;i+=5){fov=walk_fov_step(fov,1);CHECK(fov==i);}
  fov=walk_fov_step(fov,1);CHECK(fov==179);
  for(i=175;i>=5;i-=5){fov=walk_fov_step(fov,-1);CHECK(fov==i);}
  CHECK(walk_fov_step(fov,-1)==1);}
 {int mode,modifier;for(mode=0;mode<2;mode++)for(modifier=0;modifier<4;modifier++){
  double expected=(mode?17:3)*(modifier&1?2:1)*(modifier&2?0.5:1);
  walk_begin(&s,0,0,2,0,flat,0);s.noclip=mode;memset(&in,0,sizeof(in));in.forward=in.right=1;in.sprint=modifier&1;in.slow=modifier&2;
  for(i=0;i<100;i++)walk_step(&s,&in,0.01,0,flat,0);
  CHECK(fabs(sqrt(s.x*s.x+s.z*s.z)-expected)<1e-8);
 }}
 walk_begin(&s,0,0,2,0,flat,0);s.noclip=1;s.y=20;memset(&in,0,sizeof(in));in.forward=1;
 walk_step(&s,&in,0.01,0,flat,0);CHECK(s.velocity_z==17);
 {double z=s.z;in.forward=0;in.toggle_noclip=1;walk_step(&s,&in,0.01,0,flat,0);
  CHECK(!s.noclip&&s.air_carry&&s.y<20&&s.y>19.99&&s.z>z+0.16);
  CHECK(s.velocity_z>16&&s.velocity_z<17);
 }
 memset(&in,0,sizeof(in));for(i=0;i<300;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(s.grounded&&!s.air_carry&&s.y==0);
 s.noclip=1;s.y=-5;s.previous_noclip=0;in.toggle_noclip=1;walk_step(&s,&in,0.01,0,flat,0);CHECK(!s.noclip&&s.y==0&&s.grounded);
 walk_begin(&s,0,0,2,0,flat,0);memset(&in,0,sizeof(in));in.height_up=1;walk_step(&s,&in,0.01,0,flat,0);
 CHECK(fabs(s.eye_height-2.05)<1e-9);
 for(i=0;i<49;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(s.eye_height-2.05)<1e-9);
 walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(s.eye_height-2.10)<1e-9);
 for(i=0;i<10;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(s.eye_height>2.15);
 in.height_up=0;walk_step(&s,&in,0.01,0,flat,0);CHECK(!s.height_direction&&s.height_hold==0);
 {double eye=s.eye_height;in.height_down=1;walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(s.eye_height-eye+0.05)<1e-9);}
 walk_step(&s,&in,0.1,1,flat,0);CHECK(!s.height_direction&&s.height_hold==0);
 walk_begin(&s,0,0,2,0,flat,0);s.height_repeat_delay=0.2;memset(&in,0,sizeof(in));in.height_up=1;
 walk_step(&s,&in,0.01,0,flat,0);for(i=0;i<19;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(s.eye_height-2.05)<1e-9);
 walk_step(&s,&in,0.01,0,flat,0);CHECK(fabs(s.eye_height-2.10)<1e-9);
 for(i=0;i<5000;i++)walk_step(&s,&in,0.01,0,flat,0);CHECK(s.eye_height==100);
 {double change=walk_height_input(&s,&in,0.1,0,0);CHECK(change>0.24999&&change<0.25001);}
 in.height_down=1;walk_step(&s,&in,0.01,0,flat,0);CHECK(!s.height_direction);
 CHECK(fabs(walk_height_step(2.03,1)-2.05)<1e-9);CHECK(walk_height_step(2.03,-1)==2);
 CHECK(walk_height_step(100,1)==100);CHECK(walk_height_step(0.1,-1)==0.1);
 CHECK(fabs(walk_height_step(2.05,-1)-2)<1e-9);
 walk_begin(&s,0,0,2.03,0,flat,0);memset(&in,0,sizeof(in));in.height_up=1;
 walk_step(&s,&in,0.025,0,flat,0);CHECK(fabs(s.eye_height-2.05)<1e-9);
 for(i=0;i<20;i++)walk_step(&s,&in,0.025,0,flat,0);CHECK(fabs(s.eye_height-2.1)<1e-9);
 CHECK(fabs(s.height_next-(0.5+1.0/60))<1e-9);
 walk_step(&s,&in,0.016,0,flat,0);CHECK(s.height_fraction==0);
 walk_step(&s,&in,1.0/60-0.016,0,flat,0);CHECK(s.height_fraction>0&&s.height_fraction<0.05);
 CHECK(fabs(s.eye_height-2.1)<1e-9);
 walk_step(&s,&in,1.0/60,0,flat,0);CHECK(fabs(s.eye_height-2.15)<1e-9);
 for(i=0;i<180;i++){double old=s.eye_height;walk_step(&s,&in,1.0/60,0,flat,0);
  CHECK(s.eye_height>=old&&s.eye_height<=old+0.05001);
  CHECK(fabs(s.eye_height*20-floor(s.eye_height*20+0.5))<1e-6);
 }
 /* Equal elapsed time at 30/60/144 Hz gives equal travel and repeat budget. */
 {int rates[3]={30,60,144},j;double reference=0;
  for(j=0;j<3;j++){
   walk_begin(&s,0,0,2,0,flat,0);memset(&in,0,sizeof(in));in.height_up=1;
   walk_step(&s,&in,1.0/rates[j],0,flat,0);
   for(i=0;i<3*rates[j];i++)walk_step(&s,&in,1.0/rates[j],0,flat,0);
   if(!j)reference=s.eye_height;else CHECK(fabs(s.eye_height-reference)<1e-9);
   {double old=s.eye_height;
    for(i=0;i<rates[j];i++)walk_step(&s,&in,1.0/rates[j],0,flat,0);
    CHECK(fabs(s.eye_height-old-2.5)<1e-9);
   }
  }
 }
 CHECK(walk_begin(&s,0,0,100,0,flat,0)&&s.eye_height==100);
 printf("Walking model: %d checks passed\n",checks);return 0;
}
