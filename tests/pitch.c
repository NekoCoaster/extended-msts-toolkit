/* World-relative pitch properties; no game or Windows dependencies. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../runtime/physics.h"
static void near(double a,double b){assert(fabs(a-b)<.00002);}
int main(void){
 int yaw,elevation,step,i,count=0;double pi=3.141592653589793;
 float f[3],back[3],omega[3],out[3],reverse[3];
 /* Independent nose-height derivative: (omega x forward).y. Test heading,
    slope, throttle, yaw preservation, longitudinal roll and dissipativity. */
 for(yaw=0;yaw<360;yaw+=15)for(elevation=-80;elevation<=80;elevation+=10)for(step=0;step<=10;step++){
  double y=yaw*pi/180,e=elevation*pi/180,scale=step/10.0,along=0,filtered=0,energy=0,before=0;
  f[0]=sin(y)*cos(e);f[1]=sin(e);f[2]=cos(y)*cos(e);
  omega[0]=2*cos(y)+4*f[0];omega[1]=3+4*f[1];omega[2]=-2*sin(y)+4*f[2];
  assert(calc_pitch(omega,f,scale,out));
  for(i=0;i<3;i++){
   double expected=4*f[i]+(i==0?2*scale*cos(y):i==1?3:-2*scale*sin(y));
   near(out[i],expected);back[i]=-f[i];along+=omega[i]*f[i];filtered+=out[i]*f[i];
   energy+=(double)out[i]*out[i];before+=(double)omega[i]*omega[i];
  }
  near(out[1],omega[1]);near(filtered,along);assert(energy<=before+.0001);
  near(out[2]*f[0]-out[0]*f[2],scale*(omega[2]*f[0]-omega[0]*f[2]));
  assert(calc_pitch(omega,back,scale,reverse));for(i=0;i<3;i++)near(out[i],reverse[i]);
  /* Small integration drift in the matrix must not change filter strength. */
  for(i=0;i<3;i++)back[i]=f[i]*1.05f;
  assert(calc_pitch(omega,back,scale,reverse));for(i=0;i<3;i++)near(out[i],reverse[i]);
  count++;
 }
 /* Vertical and near-vertical wrecks: bounded, continuous fade, no NaNs or
    abrupt full-strength correction chosen by an almost zero heading. */
 omega[0]=2;omega[1]=3;omega[2]=4;
 for(step=-1;step<=1;step+=2)for(yaw=0;yaw<360;yaw+=45)for(i=0;i<=100;i++){
  double h=i*.0002,y=yaw*pi/180,gain=minimum(1,h*h/.0001),pitch=2*cos(y)-4*sin(y);
  f[0]=h*sin(y);f[1]=step*sqrt(1-h*h);f[2]=h*cos(y);
  assert(calc_pitch(omega,f,0,out));near(out[0],2-gain*pitch*cos(y));near(out[1],3);near(out[2],4+gain*pitch*sin(y));
 }
 f[0]=f[1]=0;f[2]=1;
 assert(calc_pitch(omega,f,1,out)&&!memcmp(omega,out,sizeof(out)));
 assert(!calc_pitch(omega,f,-.1,out));assert(!calc_pitch(omega,f,1.1,out));
 {unsigned int bits=0x7fc00000;float invalid;memcpy(&invalid,&bits,4);
  assert(!calc_pitch(omega,f,invalid,out));f[0]=invalid;assert(!calc_pitch(omega,f,0,out));
  f[0]=0;omega[2]=invalid;assert(!calc_pitch(omega,f,0,out));
  bits=0x7f800000;memcpy(&omega[2],&bits,4);assert(!calc_pitch(omega,f,0,out));
 }
 omega[2]=4;f[2]=0;assert(!calc_pitch(omega,f,0,out));f[2]=2;assert(!calc_pitch(omega,f,0,out));
 printf("PASS world pitch: %d heading/slope/throttle cases, reverse-axis invariance, yaw/roll preservation, 1616 vertical-limit cases and invalid inputs.\n",count);
 return 0;
}
