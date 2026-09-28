/* MIT. Platform-independent walking physics. Native adapter owns input,
   camera lifetime and terrain queries. Positions are metres, Y is up. */
#ifndef NEMT_WALKING_MODEL_H
#define NEMT_WALKING_MODEL_H
#include <math.h>
#include <string.h>
typedef struct {
 double x,y,z,eye_height,yaw,pitch,vertical_speed;
 double velocity_x,velocity_z,height_hold,height_next,height_repeat_delay,height_fraction;
 int height_direction,air_carry;
 int active,noclip,grounded,previous_jump,previous_up,previous_down,previous_noclip;
} WalkState;
typedef struct {
 double forward,right,up,look_x,look_y;
 int jump,height_up,height_down,toggle_noclip,look;
 int slow,sprint;
} WalkInput;
/* A failed query must never be treated as terrain at zero metres. */
typedef int (*WalkGround)(void *context,double x,double z,double *height);
static double walk_limit(double x,double lo,double hi){return x<lo?lo:x>hi?hi:x;}
static int walk_finite(double x){return x==x&&x>-1e20&&x<1e20;}
static double walk_speed(int noclip,const WalkInput *in){return (noclip?17.0:3.0)*(in->sprint?2:1)*(in->slow?0.5:1);}
static void walk_height_reset(WalkState *s){s->height_hold=s->height_next=s->height_fraction=0;s->height_direction=0;}
static double walk_height_step(double height,int direction){
 double grid=height*20,nearest=floor(grid+0.5);
 if(fabs(grid-nearest)<1e-6)grid=nearest;
 return walk_limit((direction>0?floor(grid)+1:ceil(grid)-1)/20,0.1,100);
}
static double walk_height_input(WalkState *s,const WalkInput *in,double dt,int up,int down){
 int direction=(in->height_up!=0)-(in->height_down!=0);double change=0,delay;
 if(!direction){walk_height_reset(s);return 0;}
 delay=walk_limit(s->height_repeat_delay,0.05,5);
 if(direction!=s->height_direction||(direction>0?up:down)){
  s->height_direction=direction;s->height_hold=s->height_fraction=0;s->height_next=delay;
  return walk_height_step(s->eye_height,direction)-s->eye_height;
 }
 s->height_hold+=dt;
 while(s->height_hold+1e-9>=s->height_next){
  /* 60 Hz repeat, 5 cm grid. First repeat steps at the configured delay;
     subsequent ticks carry fractional travel at the existing 2..2.5 m/s. */
  double steps;
  s->height_fraction+=s->height_next==delay?0.05:
   (2.0/60)*pow(2,walk_limit(s->height_next-delay,0,0.3219280948873623));
  steps=floor((s->height_fraction+1e-9)/0.05);s->height_fraction-=steps*0.05;
  change+=direction*steps*0.05;s->height_next+=1.0/60;
 }
 return change;
}
/* Snap to adjacent five-degree stops, tolerating native float roundoff. */
static double walk_fov_step(double degrees,int direction){
 double nearest;
 if(!walk_finite(degrees))degrees=60;
 degrees=walk_limit(degrees,1,179);nearest=floor(degrees/5+0.5)*5;
 if(fabs(degrees-nearest)<0.0001)degrees=nearest;
 if(direction>0)degrees=(floor(degrees/5)+1)*5;
 else if(direction<0)degrees=(ceil(degrees/5)-1)*5;
 return walk_limit(degrees,1,179);
}
static int walk_begin(WalkState *s,double x,double z,double eye_height,double yaw,
                      WalkGround ground,void *context){
 double h;
 if(!ground||!walk_finite(x)||!walk_finite(z)||!walk_finite(eye_height)||!walk_finite(yaw)||
    !ground(context,x,z,&h)||!walk_finite(h))return 0;
 memset(s,0,sizeof(*s));s->x=x;s->z=z;s->y=h;
 s->eye_height=walk_limit(eye_height,0.1,100.0);s->yaw=yaw;s->active=s->grounded=1;
 s->height_repeat_delay=0.5;
 return 1;
}
static void walk_step(WalkState *s,const WalkInput *in,double dt,int paused,
                      WalkGround ground,void *context){
 double length,f,r,u,dx,dy,dz,h,nx,nz,step,v,remaining,speed,decay;
 int jump=in->jump&&!s->previous_jump,up=in->height_up&&!s->previous_up;
 int down=in->height_down&&!s->previous_down,toggle=in->toggle_noclip&&!s->previous_noclip;
 s->previous_jump=in->jump;s->previous_up=in->height_up;
 s->previous_down=in->height_down;s->previous_noclip=in->toggle_noclip;
 if(!s->active||paused||!walk_finite(dt)||dt<=0){walk_height_reset(s);return;}
 /* Bound stalls rather than teleporting across unloaded terrain. */
 dt=walk_limit(dt,0,0.1);
 if(toggle){
  walk_height_reset(s);
  if(!s->noclip){s->noclip=1;s->grounded=0;s->vertical_speed=0;s->air_carry=0;}
  else if(ground&&ground(context,s->x,s->z,&h)&&walk_finite(h)){
   s->noclip=0;s->grounded=s->y<=h;s->vertical_speed=0;s->air_carry=!s->grounded;
   if(s->grounded){s->y=h;s->velocity_x=s->velocity_z=0;}
  }
 }
 if(in->look&&walk_finite(in->look_x)&&walk_finite(in->look_y)){
  s->yaw=fmod(s->yaw+in->look_x*0.0025,6.283185307179586);
  s->pitch=walk_limit(s->pitch+in->look_y*0.0025,-1.553343034,1.553343034);
 }
 if(!s->noclip)s->eye_height=walk_limit(s->eye_height+walk_height_input(s,in,dt,up,down),0.1,100.0);
 else walk_height_reset(s);
 speed=walk_speed(s->noclip,in);
 f=walk_finite(in->forward)?walk_limit(in->forward,-1,1):0;
 r=walk_finite(in->right)?walk_limit(in->right,-1,1):0;
 u=s->noclip&&walk_finite(in->up)?walk_limit(in->up,-1,1):0;
 length=sqrt(f*f+r*r+u*u);if(length>1){f/=length;r/=length;u/=length;}
 dx=sin(s->yaw)*f+cos(s->yaw)*r;dz=cos(s->yaw)*f-sin(s->yaw)*r;dy=0;
 if(s->noclip){
  dx=sin(s->yaw)*cos(s->pitch)*f+cos(s->yaw)*r;
  dz=cos(s->yaw)*cos(s->pitch)*f-sin(s->yaw)*r;dy=sin(s->pitch)*f+u;
  length=sqrt(dx*dx+dy*dy+dz*dz);if(length>1){dx/=length;dy/=length;dz/=length;}
  s->velocity_x=dx*speed;s->velocity_z=dz*speed;
  s->x+=s->velocity_x*dt;s->z+=s->velocity_z*dt;s->y+=dy*speed*dt;return;
 }
 if(!ground||!ground(context,s->x,s->z,&h)||!walk_finite(h))return;
 if(jump&&s->grounded){s->vertical_speed=sqrt(9.81*s->eye_height);s->grounded=0;}
 /* Small steps limit terrain tunnelling; exact ballistic integration keeps
    jump height independent of frame rate on level terrain. */
 remaining=dt;
 while(remaining>0.0000001){
  step=remaining>0.01?0.01:remaining;remaining-=step;
  if(s->air_carry){
   /* Ease inherited flight velocity toward walking input (0.46 s half-life). */
   decay=exp(-1.5*step);
   nx=s->x+dx*speed*step+(s->velocity_x-dx*speed)*(1-decay)/1.5;
   nz=s->z+dz*speed*step+(s->velocity_z-dz*speed)*(1-decay)/1.5;
   s->velocity_x=dx*speed+(s->velocity_x-dx*speed)*decay;
   s->velocity_z=dz*speed+(s->velocity_z-dz*speed)*decay;
  }else {s->velocity_x=dx*speed;s->velocity_z=dz*speed;nx=s->x+s->velocity_x*step;nz=s->z+s->velocity_z*step;}
  if(ground(context,nx,nz,&h)&&walk_finite(h)){
   s->x=nx;s->z=nz;
  }else if(!ground(context,s->x,s->z,&h)||!walk_finite(h))return;
  if(s->grounded)s->y=h;
  else {v=s->vertical_speed;s->y+=v*step-0.5*9.81*step*step;s->vertical_speed-=9.81*step;
   if(s->y<=h){s->y=h;s->vertical_speed=0;s->grounded=1;s->air_carry=0;}
  }
 }
}
#endif
