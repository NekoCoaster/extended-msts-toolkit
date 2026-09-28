/* MIT. Platform-independent walking physics. Native adapter owns input,
   camera lifetime and terrain queries. Positions are metres, Y is up. */
#ifndef NEMT_WALKING_MODEL_H
#define NEMT_WALKING_MODEL_H
#include <math.h>
#include <string.h>
typedef struct {
 double x,y,z,eye_height,yaw,pitch,vertical_speed;
 int active,noclip,grounded,previous_jump,previous_up,previous_down,previous_noclip;
} WalkState;
typedef struct {
 double forward,right,up,look_x,look_y;
 int jump,height_up,height_down,toggle_noclip,look;
} WalkInput;
/* A failed query must never be treated as terrain at zero metres. */
typedef int (*WalkGround)(void *context,double x,double z,double *height);
static double walk_limit(double x,double lo,double hi){return x<lo?lo:x>hi?hi:x;}
static int walk_finite(double x){return x==x&&x>-1e20&&x<1e20;}
static int walk_begin(WalkState *s,double x,double z,double eye_height,double yaw,
                      WalkGround ground,void *context){
 double h;
 if(!ground||!walk_finite(x)||!walk_finite(z)||!walk_finite(eye_height)||!walk_finite(yaw)||
    !ground(context,x,z,&h)||!walk_finite(h))return 0;
 memset(s,0,sizeof(*s));s->x=x;s->z=z;s->y=h;
 s->eye_height=walk_limit(eye_height,0.1,10.0);s->yaw=yaw;s->active=s->grounded=1;
 return 1;
}
static void walk_step(WalkState *s,const WalkInput *in,double dt,int paused,
                      WalkGround ground,void *context){
 double length,f,r,u,dx,dy,dz,h,nx,nz,step,v,remaining;
 int jump=in->jump&&!s->previous_jump,up=in->height_up&&!s->previous_up;
 int down=in->height_down&&!s->previous_down,toggle=in->toggle_noclip&&!s->previous_noclip;
 s->previous_jump=in->jump;s->previous_up=in->height_up;
 s->previous_down=in->height_down;s->previous_noclip=in->toggle_noclip;
 if(!s->active||paused||!walk_finite(dt)||dt<=0)return;
 /* Bound stalls rather than teleporting across unloaded terrain. */
 dt=walk_limit(dt,0,0.1);
 if(toggle){
  if(!s->noclip){s->noclip=1;s->grounded=0;s->vertical_speed=0;}
  else if(ground&&ground(context,s->x,s->z,&h)&&walk_finite(h)){
   s->noclip=0;s->y=h;s->grounded=1;s->vertical_speed=0;
  }
 }
 if(in->look&&walk_finite(in->look_x)&&walk_finite(in->look_y)){
  s->yaw=fmod(s->yaw+in->look_x*0.0025,6.283185307179586);
  s->pitch=walk_limit(s->pitch+in->look_y*0.0025,-1.553343034,1.553343034);
 }
 if(!s->noclip)s->eye_height=walk_limit(s->eye_height+0.05*(up-down),0.1,10.0);
 f=walk_finite(in->forward)?walk_limit(in->forward,-1,1):0;
 r=walk_finite(in->right)?walk_limit(in->right,-1,1):0;
 u=s->noclip&&walk_finite(in->up)?walk_limit(in->up,-1,1):0;
 length=sqrt(f*f+r*r+u*u);if(length>1){f/=length;r/=length;u/=length;}
 dx=sin(s->yaw)*f+cos(s->yaw)*r;dz=cos(s->yaw)*f-sin(s->yaw)*r;dy=0;
 if(s->noclip){
  dx=sin(s->yaw)*cos(s->pitch)*f+cos(s->yaw)*r;
  dz=cos(s->yaw)*cos(s->pitch)*f-sin(s->yaw)*r;dy=sin(s->pitch)*f+u;
  length=sqrt(dx*dx+dy*dy+dz*dz);if(length>1){dx/=length;dy/=length;dz/=length;}
  s->x+=dx*10*dt;s->z+=dz*10*dt;s->y+=dy*10*dt;return;
 }
 if(!ground||!ground(context,s->x,s->z,&h)||!walk_finite(h))return;
 if(jump&&s->grounded){s->vertical_speed=sqrt(9.81*s->eye_height);s->grounded=0;}
 /* Small steps limit terrain tunnelling; exact ballistic integration keeps
    jump height independent of frame rate on level terrain. */
 remaining=dt;
 while(remaining>0.0000001){
  step=remaining>0.01?0.01:remaining;remaining-=step;
  nx=s->x+dx*1.4*step;nz=s->z+dz*1.4*step;
  if(ground(context,nx,nz,&h)&&walk_finite(h)){
   s->x=nx;s->z=nz;
  }else if(!ground(context,s->x,s->z,&h)||!walk_finite(h))return;
  if(s->grounded)s->y=h;
  else {v=s->vertical_speed;s->y+=v*step-0.5*9.81*step*step;s->vertical_speed-=9.81*step;
   if(s->y<=h){s->y=h;s->vertical_speed=0;s->grounded=1;}
  }
 }
}
#endif
