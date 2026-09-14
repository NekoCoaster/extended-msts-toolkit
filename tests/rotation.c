#include <stdio.h>
#include <stdlib.h>
#include "../runtime/physics.h"
#include "../runtime/rotation.h"
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static double dot3(const double *a,const float *b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
int main(void){
 int y,r,e,k,i,j,n=0;float right[3],up[3],forward[3],omega[3]={0},inv[9];double dw[3],dl[3],expected[3],delta[3];
 for(y=0;y<12;y++)for(r=0;r<32;r++)for(e=-2;e<=2;e++){
  double yaw=y*6.283185307179586/12,roll=r*6.283185307179586/32,pitch=e*.6;
  double baseR[3]={cos(yaw),0,-sin(yaw)},baseU[3]={-sin(yaw)*sin(pitch),cos(pitch),-cos(yaw)*sin(pitch)};
  forward[0]=sin(yaw)*cos(pitch);forward[1]=sin(pitch);forward[2]=cos(yaw)*cos(pitch);
  for(i=0;i<3;i++){right[i]=baseR[i]*cos(roll)+baseU[i]*sin(roll);up[i]=baseU[i]*cos(roll)-baseR[i]*sin(roll);}
  CHECK(calc_rotation(right,up,forward,omega,1,0,.1,10,dw));
  /* Independent derivative of roof height: (omega cross up).y. */
  CHECK(dw[2]*up[0]-dw[0]*up[2]>-1e-8);
  CHECK(fabs(dot3(dw,up))<1e-7);
  if(r!=0&&r!=16)CHECK(fabs(dot3(dw,forward))>.001);
  for(k=-1;k<=1;k+=2){
   CHECK(calc_rotation(right,up,forward,omega,0,k,.1,10,dw));
   CHECK(fabs(dot3(dw,up)-k*.015)<1e-7);CHECK(fabs(dot3(dw,forward))<1e-7);
  }
  /* Rotated anisotropic inertia, solved against an independent basis formula. */
  for(i=0;i<3;i++)for(j=0;j<3;j++)inv[i*3+j]=right[i]*right[j]/1e6+up[i]*up[j]/3e6+forward[i]*forward[j]/2e5;
  dw[0]=.012;dw[1]=-.021;dw[2]=.007;
  for(i=0;i<3;i++)expected[i]=right[i]*dot3(dw,right)*1e6+up[i]*dot3(dw,up)*3e6+forward[i]*dot3(dw,forward)*2e5;
  CHECK(rotation_momentum(inv,dw,dl));
  for(i=0;i<3;i++)CHECK(fabs(dl[i]-expected[i])<.08);
  n++;
 }
 /* Both shortest directions converge without flipping back and forth. */
 for(r=-1;r<=1;r+=2)for(k=30;k<=120;k*=2){
  double angle=r*2.9,w=0,dt=1.0/k;
  forward[0]=forward[1]=0;forward[2]=1;
  for(i=0;i<k*30;i++){
   right[0]=cos(angle);right[1]=sin(angle);right[2]=0;up[0]=-sin(angle);up[1]=cos(angle);up[2]=0;
   omega[0]=omega[1]=0;omega[2]=w;
   CHECK(calc_rotation(right,up,forward,omega,1,0,dt,10,dw));w+=dw[2];angle+=w*dt;
   CHECK(fabs(w)<.351);
  }
  CHECK(fabs(angle)<.0001);
 }
 right[0]=1;right[1]=right[2]=0;up[0]=up[2]=0;up[1]=1;omega[0]=omega[1]=omega[2]=0;
 CHECK(calc_rotation(right,up,forward,omega,1,1,0,10,dw)&&dot3(dw,up)==0);
 CHECK(calc_rotation(right,up,forward,omega,1,1,.1,0,dw)&&dot3(dw,up)==0);
 CHECK(calc_rotation(right,up,forward,omega,1,1,4,10,dw));
 CHECK(calc_rotation(right,up,forward,omega,1,1,.25,10,delta));for(i=0;i<3;i++)CHECK(dw[i]==delta[i]);
 CHECK(!calc_rotation(right,up,forward,omega,1,1,-1,10,dw));
 forward[1]=1;forward[2]=0;up[1]=0;up[2]=-1;
 CHECK(calc_rotation(right,up,forward,omega,1,0,.1,10,dw));for(i=0;i<3;i++)CHECK(dw[i]==0);
 for(i=0;i<9;i++)inv[i]=0;CHECK(!rotation_momentum(inv,dw,dl));
 inv[0]=inv[4]=inv[8]=1e-6;CHECK(rotation_momentum(inv,dw,dl));inv[4]=-1e-6;CHECK(!rotation_momentum(inv,dw,dl));
 inv[4]=1e-6;inv[1]=1;CHECK(!rotation_momentum(inv,dw,dl));
 printf("PASS rotation: %d orientations, shortest-path convergence at 30/60/120 Hz, local-up steering, anisotropic inertia, zero/capped time, zero strength, vertical poles and invalid tensors.\n",n);
 return 0;
}
