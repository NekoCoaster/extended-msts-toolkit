/* Portable scrollbar/layout regression tests; no OS, GUI or game required. */
#include <assert.h>
#include <stdio.h>
#include "../src/viewport_model.h"
static unsigned long checks,cases;
#define CHECK(x) do {++checks;assert(x);}while(0)
static void expect(int width,int height,int h,int v,int vw,int vh,int x,int y) {
    ViewportLayout r;viewport_layout(&r,width,height,760,840,17,17,x,y);++cases;
    CHECK(r.horizontal==h && r.vertical==v);
    CHECK(r.width==vw && r.height==vh);
    CHECK(r.x>=0 && r.x<=r.max_x && r.y>=0 && r.y<=r.max_y);
}
int main(void) {
    ViewportLayout r,again;int scale,i,j,state,cw,ch,bar,width,height,x,y;
    expect(784,864,0,0,784,864,0,0); /* new default client area */
    expect(760,840,0,0,760,840,100,200); /* exact fit clears old scroll offsets */
    expect(780,600,0,1,763,600,0,200); /* short display: vertical only */
    expect(600,880,1,0,600,863,200,0); /* narrow but tall: horizontal only */
    expect(760,600,1,1,743,583,200,200); /* vertical bar causes horizontal */
    expect(600,840,1,1,583,823,200,200); /* horizontal bar causes vertical */
    expect(0,0,1,1,0,0,-100,-100); /* minimized/zero-size arithmetic */
    expect(600,600,1,1,583,583,10000,10000); /* large offsets clamp */
    /* Near-threshold grid at 100%, 125%, 150% and 200% scaling. Test both
     * scroll directions, negative offsets and offsets beyond the end. */
    for(scale=4;scale<=8;++scale) {
        if(scale==7) continue;
        cw=760*scale/4;ch=840*scale/4;bar=17*scale/4;
        for(i=-40;i<=40;++i) for(j=-40;j<=40;++j) for(state=0;state<4;++state) {
            width=cw+i;height=ch+j;
            x=state==0?0:(state==1?-100:(state==2?10:100000));y=x;
            viewport_layout(&r,width,height,cw,ch,bar,bar,x,y);++cases;
            CHECK(r.horizontal==(cw>r.width));CHECK(r.vertical==(ch>r.height));
            CHECK(r.width==width-(r.vertical?bar:0));CHECK(r.height==height-(r.horizontal?bar:0));
            CHECK(r.x>=0 && r.x<=r.max_x);CHECK(r.y>=0 && r.y<=r.max_y);
            if(width>=cw && height>=ch) {
                CHECK(!r.horizontal && !r.vertical);CHECK(r.x==0 && r.y==0);
            }
            /* Recover the full client area as production does; layout must
             * not depend on the previous scrollbar/scroll-position state. */
            viewport_layout(&again,r.width+(r.vertical?bar:0),r.height+(r.horizontal?bar:0),cw,ch,bar,bar,r.x,r.y);
            CHECK(again.width==r.width && again.height==r.height);
            CHECK(again.horizontal==r.horizontal && again.vertical==r.vertical);
            CHECK(again.x==r.x && again.y==r.y);
        }
    }
    printf("viewport layout: %lu cases, %lu assertions passed\n",cases,checks);
    return 0;
}
