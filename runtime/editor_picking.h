/* Route Editor converts client mouse positions into camera coordinates.
   Its four selection/placement paths hard-code a 640x480 camera. Redirect
   those operands to the actual camera extent while retaining native rays,
   hit testing and drag behavior. The simulator never installs these hooks. */
static float editor_pick_width=640,editor_pick_height=480;
static const U editor_pick_x_sites[]={0x57eb37,0x57eb70,0x57ecc3,0x57f1f8,0x57f4ff,0x57f538,0x581014,0x581047,0x5810f0,0x581273,0x5812ac,0x581373};
static const U editor_pick_y_sites[]={0x57ebb4,0x57ebe9,0x57ecf4,0x57f229,0x57f57c,0x57f5b1,0x58107f,0x5810ae,0x58111b,0x5812f0,0x581325,0x5813a4};
static void editor_picking_hooks(Hook *hooks){
 U i;Hook *h;
 for(i=0;i<24;i++){
  h=&hooks[i];memset(h,0,sizeof(*h));h->address=i<12?editor_pick_x_sites[i]:editor_pick_y_sites[i-12];h->length=6;h->raw=1;
  h->original[0]=h->replacement[0]=0xd8;h->original[1]=h->replacement[1]=0x3d;
  *(U*)(h->original+2)=i<12?0x770560:0x77055c;
  *(float**)(h->replacement+2)=i<12?&editor_pick_width:&editor_pick_height;
 }
}
