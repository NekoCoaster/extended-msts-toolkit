/* Pure crawl rotational assist. Rates are radians/second, accelerations radians/s^2.
   Apply an angular impulse, never assign an orientation or erase collision spin. */
static double rotation_clamp(double x,double limit){return maximum(-limit,minimum(limit,x));}
static int calc_rotation(const float *right,const float *up,const float *forward,const float *omega,
                         int horn,int steer,double dt,double boost,double *dw){
 double r[3],u[3],f[3],roll=0,yaw=0,angle,horizon,target,dr=0,dy=0,dot=0;int i;
 for(i=0;i<3;i++)dw[i]=0;
 if(!finite_number(dt)||dt<0||!finite_number(boost)||boost<0||boost>100||steer<-1||steer>1)return 0;
 if(!boost||!dt||(!horn&&!steer))return 1;
 if(!unit_vector(right,r)||!unit_vector(up,u)||!unit_vector(forward,f))return 0;
 for(i=0;i<3;i++){if(!finite_number(omega[i]))return 0;dot+=u[i]*f[i];roll+=omega[i]*f[i];yaw+=omega[i]*u[i];}
 if(fabs(dot)>.01)return 0;
 /* Verify a right-handed basis before choosing the shortest roll direction. */
 if(fabs(r[0]-(u[1]*f[2]-u[2]*f[1]))>.02||fabs(r[1]-(u[2]*f[0]-u[0]*f[2]))>.02||fabs(r[2]-(u[0]*f[1]-u[1]*f[0]))>.02)return 0;
 dt=minimum(dt,.25);boost/=10;
 horizon=sqrt(r[1]*r[1]+u[1]*u[1]);
 if(horn&&horizon>.0001){
  /* At exactly inverted, either side is equally short. Choose positive roll.
     Near a vertical nose, smoothly fade the undefined upright roll target. */
  angle=(fabs(r[1])<1e-7&&u[1]<0)?3.141592653589793:atan2(-r[1],u[1]);
  target=rotation_clamp(angle*.6,.35);
  dr=rotation_clamp(target-roll,.25*boost*dt)*minimum(1,horizon/.01);
 }
 if(steer)dy=rotation_clamp(steer*.25-yaw,.15*boost*dt);
 for(i=0;i<3;i++)dw[i]=f[i]*dr+u[i]*dy;
 return 1;
}
/* Native +0x64 is the world inverse inertia tensor; omega = inverseI * L.
   Solve a scaled positive-definite matrix to keep both native state fields
   consistent, including rotated non-diagonal tensors. */
static int rotation_momentum(const float *inverse,const double *dw,double *dl){
 double a[9],scale=0,det,c00,c01,c02,c11,c12,c22;int i,j;
 for(i=0;i<9;i++){if(!finite_number(inverse[i]))return 0;scale=maximum(scale,fabs(inverse[i]));}
 if(scale<1e-14||scale>1)return 0;
 for(i=0;i<9;i++)a[i]=inverse[i]/scale;
 if(fabs(a[1]-a[3])>1e-4||fabs(a[2]-a[6])>1e-4||fabs(a[5]-a[7])>1e-4)return 0;
 a[1]=a[3]=(a[1]+a[3])*.5;a[2]=a[6]=(a[2]+a[6])*.5;a[5]=a[7]=(a[5]+a[7])*.5;
 c00=a[4]*a[8]-a[5]*a[5];c01=a[2]*a[5]-a[1]*a[8];c02=a[1]*a[5]-a[2]*a[4];
 c11=a[0]*a[8]-a[2]*a[2];c12=a[1]*a[2]-a[0]*a[5];c22=a[0]*a[4]-a[1]*a[1];
 det=a[0]*c00+a[1]*c01+a[2]*c02;
 if(a[0]<=0||c22<=0||det<1e-12)return 0;
 dl[0]=(c00*dw[0]+c01*dw[1]+c02*dw[2])/(det*scale);
 dl[1]=(c01*dw[0]+c11*dw[1]+c12*dw[2])/(det*scale);
 dl[2]=(c02*dw[0]+c12*dw[1]+c22*dw[2])/(det*scale);
 for(i=0;i<3;i++){
  double check=0;if(!finite_number(dl[i])||fabs(dl[i])>3.4e38)return 0;
  for(j=0;j<3;j++)check+=inverse[i*3+j]*dl[j];
  if(!finite_number(dw[i])||fabs(check-dw[i])>1e-5)return 0;
 }
 return 1;
}
