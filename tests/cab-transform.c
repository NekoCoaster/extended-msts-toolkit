/* Investigation only: geometric acceptance tests, not an installed game hook. */
#include <assert.h>
#include <math.h>
#include <stdio.h>
typedef struct { double x,y; } Point;
static Point rotate(Point v,double angle){Point r;double c=cos(angle),s=sin(angle);r.x=c*v.x-s*v.y;r.y=s*v.x+c*v.y;return r;}
/* Proposed wrapper around the original rotation: S * R * inverse(S). */
static Point corrected(Point already_scaled,double sx,double sy,double angle){Point r;r.x=already_scaled.x/sx;r.y=already_scaled.y/sy;r=rotate(r,angle);r.x*=sx;r.y*=sy;return r;}
static void close_point(Point a,Point b){assert(fabs(a.x-b.x)<1e-9&&fabs(a.y-b.y)<1e-9);}
int main(void){
 const double pi=3.14159265358979323846;
 const double scales[][2]={{1,1},{2,2},{2,1.5},{3,2.25},{4,3},{2.25,1.875}};
 /* Acela's CVF needle: 9 x 65; pivot 44 from the top. */
 const Point corners[]={{-4.5,-44},{4.5,-44},{4.5,21},{-4.5,21},{0,0}};
 unsigned i,j;int degrees,count=0;
 for(i=0;i<6;i++)for(j=0;j<5;j++)for(degrees=-360;degrees<=360;degrees+=5){
  double sx=scales[i][0],sy=scales[i][1],a=degrees*pi/180;
  Point scaled={corners[j].x*sx,corners[j].y*sy},expected=rotate(corners[j],a),actual;
  expected.x*=sx;expected.y*=sy;actual=corrected(scaled,sx,sy,a);close_point(actual,expected);
  if(sx==sy)close_point(actual,rotate(scaled,a));
  if(degrees==0)close_point(actual,scaled);
  count++;
 }
 {Point v={0,-44},scaled={0,-66},wrong=rotate(scaled,pi/4),right=corrected(scaled,2,1.5,pi/4);
  assert(right.x-wrong.x>15.55&&right.x-wrong.x<15.56);
  printf("1280x720 example: current tip=(%.3f,%.3f), screen-relative tip=(%.3f,%.3f)\n",wrong.x,wrong.y,right.x,right.y);
 }
 printf("PASS %d geometric cases: angle sweep, anisotropic scaling, 4:3 equivalence, zero angle and fixed pivot.\n",count);
 return 0;
}
