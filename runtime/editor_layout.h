/* Integer desktop coordinates, including monitors left/above the primary. */
typedef struct {int left,top,right,bottom;} EditorRect;
static EditorRect editor_cab_fit(int width,int height){
 EditorRect r;int w=width,h=width*3/4;
 if(h>height){h=height;w=height*4/3;}
 r.left=(width-w)/2;r.top=(height-h)/2;r.right=r.left+w;r.bottom=r.top+h;return r;
}
static int editor_cab_coordinate(int value,int origin,int extent,int logical){
 if(extent<=0||value<origin)return -1;
 if(value>=origin+extent)return logical;
 return (value-origin)*logical/extent;
}
typedef struct {int right_x,right_y,bottom_x,bottom_y,fold_right,fold_bottom,min_width,min_height;} EditorLayout;
static int editor_max(int a,int b){return a>b?a:b;}
static int editor_clamp(int x,int lo,int hi){return x<lo?lo:x>hi?editor_max(lo,hi):x;}
static EditorLayout editor_layout(EditorRect outer,EditorRect client,EditorRect work,int rw,int rh,int bw,int bh){
 EditorLayout p;
 p.fold_right=outer.right+rw>work.right;
 p.fold_bottom=outer.bottom+bh>work.bottom;
 p.min_width=640;p.min_height=480;
 if(p.fold_right){p.min_width=editor_max(p.min_width,rw+320);p.min_height=editor_max(p.min_height,rh);}
 if(p.fold_bottom){p.min_width=editor_max(p.min_width,bw);p.min_height=editor_max(p.min_height,bh+200);}
 if(p.fold_right&&p.fold_bottom)p.min_width=editor_max(p.min_width,bw+rw);
 p.right_x=p.fold_right?client.right-rw:outer.right;
 p.right_y=p.fold_right?client.top:outer.top;
 p.bottom_x=p.fold_bottom?client.left:outer.left;
 p.bottom_y=p.fold_bottom?client.bottom-bh:outer.bottom;
 p.right_x=editor_clamp(p.right_x,work.left,work.right-rw);
 p.right_y=editor_clamp(p.right_y,work.top,work.bottom-rh);
 p.bottom_x=editor_clamp(p.bottom_x,work.left,work.right-bw);
 p.bottom_y=editor_clamp(p.bottom_y,work.top,work.bottom-bh);
 return p;
}
