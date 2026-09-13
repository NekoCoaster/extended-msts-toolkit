/* MIT. Pure calculations shared by the runtime and native tests. */
#include <math.h>
static int finite_number(double x){return x==x && x<=1.7976931348623157e308 && x>=-1.7976931348623157e308;}
static double clamp_throttle(double x){return x<0.0001?0:(x>1?1:x);}
static double minimum(double a,double b){return a<b?a:b;}
static double maximum(double a,double b){return a>b?a:b;}
static int unit_vector(const float *v,double *u){
 double n;int i;for(i=0;i<3;i++)if(!finite_number(v[i]))return 0;
 n=sqrt((double)v[0]*v[0]+(double)v[1]*v[1]+(double)v[2]*v[2]);
 if(n<.9||n>1.1)return 0;for(i=0;i<3;i++)u[i]=v[i]/n;return 1;
}
static int calc_impulse(float *axis,float *velocity,double mass,double force,double power,double throttle,double direction,double dt,double boost,double *dp,double *dv){
 double u[3],speed=0,f;int i;
 if(!finite_number(mass)||mass<100||mass>1e7||!finite_number(force)||force<=0||force>1e8||!finite_number(power)||power<=0||power>1e9||!finite_number(throttle)||!finite_number(direction)||!finite_number(dt)||dt<0||!finite_number(boost)||boost<0||boost>100||!unit_vector(axis,u))return 0;
 for(i=0;i<3;i++){if(!finite_number(velocity[i]))return 0;speed+=velocity[i]*u[i];}
 f=minimum(force,power/maximum(.5,fabs(speed)))*clamp_throttle(throttle)*(direction>0?1:direction<0?-1:0)*boost*minimum(dt,.25);
 for(i=0;i<3;i++){dp[i]=u[i]*f;dv[i]=dp[i]/mass;}return 1;
}
static int calc_pitch(const float *omega,const float *forward,double scale,float *out){
 double f[3],p[3],h2,pitch=0;int i;
 if(!finite_number(scale)||scale<0||scale>1||!unit_vector(forward,f))return 0;
 /* World Y is vertical. up x forward is horizontal regardless of body roll.
    Its projection preserves world yaw and rotation about the train's length.
    Below .01 horizontal length (~.57 degrees from vertical), fade to zero:
    a vertical train has no unique heading, and tiny X/Z noise must not select
    a full-strength axis. No body-local fallback or stored heading is needed. */
 p[0]=f[2];p[1]=0;p[2]=-f[0];h2=p[0]*p[0]+p[2]*p[2];
 for(i=0;i<3;i++){if(!finite_number(omega[i]))return 0;pitch+=omega[i]*p[i];}
 pitch*=(1-scale)/maximum(h2,.0001);
 for(i=0;i<3;i++)out[i]=omega[i]-pitch*p[i];return 1;
}
static int calc_wheel(float *velocity,float *axis,double throttle,double boost,double *speed){
 double u[3];int i;if(!unit_vector(axis,u)||!finite_number(throttle)||!finite_number(boost)||boost<0||boost>100)return 0;
 *speed=0;for(i=0;i<3;i++){if(!finite_number(velocity[i]))return 0;*speed+=velocity[i]*u[i];}
 /* V1 wheel scaling has no thrust deadband. */
 *speed*=maximum(1,boost*minimum(1,maximum(0,throttle)));return 1;
}
