/* Pure viewport arithmetic shared by the Win32 layout and portable tests.
 * The supplied width/height exclude nonclient borders AND any scrollbars.
 * All dimensions/offsets use the same (already DPI-scaled) pixel units. */
#ifndef NEMT_VIEWPORT_MODEL_H
#define NEMT_VIEWPORT_MODEL_H

typedef struct {
    int width,height,horizontal,vertical,max_x,max_y,x,y;
} ViewportLayout;

static int viewport_nonnegative(int n) {return n>0?n:0;}
static int viewport_clamp(int n,int maximum) {return n<0?0:(n>maximum?maximum:n);}
static void viewport_layout(ViewportLayout *v,int width,int height,int content_width,int content_height,
    int vertical_bar_width,int horizontal_bar_height,int x,int y) {
    int h=0,vert=0,next_h,next_v;
    width=viewport_nonnegative(width);height=viewport_nonnegative(height);
    vertical_bar_width=viewport_nonnegative(vertical_bar_width);
    horizontal_bar_height=viewport_nonnegative(horizontal_bar_height);
    /* Least fixed point: starting with neither bar avoids the both-bars latch.
     * Need only grows during this loop, so it takes at most three iterations. */
    for(;;) {
        next_h=content_width>viewport_nonnegative(width-(vert?vertical_bar_width:0));
        next_v=content_height>viewport_nonnegative(height-(h?horizontal_bar_height:0));
        if(next_h==h && next_v==vert) break;
        h=next_h;vert=next_v;
    }
    v->horizontal=h;v->vertical=vert;
    v->width=viewport_nonnegative(width-(vert?vertical_bar_width:0));
    v->height=viewport_nonnegative(height-(h?horizontal_bar_height:0));
    v->max_x=viewport_nonnegative(content_width-v->width);
    v->max_y=viewport_nonnegative(content_height-v->height);
    v->x=viewport_clamp(x,v->max_x);v->y=viewport_clamp(y,v->max_y);
}
#endif
