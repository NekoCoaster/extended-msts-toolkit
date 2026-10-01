/* MIT. Experimental camera light for the hash-gated MSTS Bin runtime.
   Call only on the game's frame/render thread, outside a geometry draw.
   Uses native allocation, registration, transforms and release, not D3D state. */
typedef void *(__fastcall *FlashCreateFn)(U,U,const float*);
typedef void (__fastcall *FlashSetFn)(void*,const float*);
typedef int (__fastcall *FlashReleaseFn)(void*);
static FlashCreateFn flashlight_create=(FlashCreateFn)0x69b0f0;
static FlashSetFn flashlight_set=(FlashSetFn)0x6a0ab0;
static FlashReleaseFn flashlight_release=(FlashReleaseFn)0x6a01d0;
static U flashlight_object;
static float flashlight_frame[12];
static double flashlight_cos,flashlight_cone_scale;
static int flashlight_frame_active;
static int flashlight_failed;

/* Membership is checked before dereferencing an object retained across frames:
   native renderer shutdown owns and releases both light lists. */
static int flashlight_member(U object,U global){
 U head,node,n[3],budget=512;
 if(!object||!read_memory(global,&head,4)||!head||!read_memory(head,&node,4))return 0;
 while(node!=head&&budget--){
  if(!node||!read_memory(node,n,12))return 0;
  if(n[2]==object)return 1;node=n[0];
 }return 0;
}
static int flashlight_owned(void){
 U v[3];
 return flashlight_member(flashlight_object,G(0x828694))&&
  read_memory(flashlight_object,v,12)&&v[0]==G(0x828868)&&v[1]==1&&v[2]==2;
}
static void flashlight_stop(void){
 int owned=flashlight_owned();
 if(flashlight_object&&*(U*)G(0x8287b0)==flashlight_object){
  *(U*)G(0x8287b0)=0;*(U*)G(0x8287b4)=0;
 }
 if(owned)flashlight_release((void*)flashlight_object);
 flashlight_object=0;flashlight_frame_active=0;
}

static void flashlight_renderer_shutdown(void){
 /* The native shutdown walks and frees its own lists. Drop our references
    before that happens, preventing an address reused by the next activity
    from being mistaken for our old allocation. Do not release twice. */
 if(flashlight_object&&*(U*)G(0x8287b0)==flashlight_object){
  *(U*)G(0x8287b0)=0;*(U*)G(0x8287b4)=0;
 }
 flashlight_object=0;flashlight_frame_active=0;flashlight_failed=0;
}
static int flashlight_supported(void){
 return !memcmp((void*)0x69b0f0,"\x53\x55\x8b\xe9\x56\xb9\x90\x00\x00\x00",10)&&
  *(U*)G(0x828868)==0x6a01c0&&*(U*)G(0x82886c)==0x6a01d0&&
  *(U*)G(0x828870)==0x6a0ab0&&*(U*)G(0x828888)==0x6a0c60&&
  *(U*)G(0x82888c)==0x6a0d80&&*(U*)G(0x828890)==0x6a0e50;
}
static int (*flashlight_verify)(void)=flashlight_supported;
static void flashlight_update(U camera,int enabled){
 float m[12],params[12];U selected,head;int i;
 flashlight_frame_active=0;
 if(!enabled){flashlight_stop();return;}
 if(!camera||!read_memory(camera+0xc,m,sizeof(m))||
    !read_memory(G(0x828694),&head,4)||!head){flashlight_stop();return;}
 for(i=0;i<12;i++)if(!(m[i]>-1e9f&&m[i]<1e9f)){flashlight_stop();return;}
 if(flashlight_object&&!flashlight_owned()){
  /* A renderer teardown already released our object. Never release it twice. */
  if(*(U*)G(0x8287b0)==flashlight_object){*(U*)G(0x8287b0)=0;*(U*)G(0x8287b4)=0;}
  flashlight_object=0;flashlight_frame_active=0;
 }
 if(!flashlight_verify()){flashlight_failed=1;return;}
 params[0]=1;params[1]=(float)(flash_safe(flashlight_tuning[FLASH_BRIGHTNESS],FLASH_BRIGHTNESS)/100.0);params[2]=params[1]*0.95f;params[3]=params[1]*0.85f;
 /* INI angle is the full beam; native light expects half-angle radians. */
 for(i=0;i<3;i++){params[4+i]=m[9+i]+m[6+i]*0.15f;params[8+i]=m[6+i];}
 params[7]=(float)flash_safe(flashlight_tuning[FLASH_RANGE],FLASH_RANGE);
 params[11]=(float)(flash_safe(flashlight_tuning[FLASH_ANGLE],FLASH_ANGLE)*0.008726646259971648);
 if(!flashlight_object){
  /* Native registration preserves the locomotive selection. */
  flashlight_object=(U)flashlight_create(2,0x21,params);
  if(!flashlight_object){flashlight_failed=1;return;}
 }else flashlight_set((void*)flashlight_object,params);
 /* Terrain consumes world-space direction even when its material has no
    additional-light list to invoke the native local transform method. */
 memcpy((void*)(flashlight_object+0x70),params+8,12);
 selected=*(U*)G(0x8287b0);
 if(!selected)*(U*)G(0x8287b0)=flashlight_object;
 memcpy(flashlight_frame,params,sizeof(params));
 flashlight_cos=cos(params[11]);flashlight_cone_scale=1/(1-flashlight_cos);
 flashlight_frame_active=1;
 flashlight_failed=0;
}
/* Terrain's lit vertices are cached. Rebuild nearby patches before drawing,
   and leave them dirty afterwards so switching off or moving away cannot
   leave a baked-in beam, including patches temporarily outside the view. */
static int flashlight_near_patch(U patch,U descriptor){
 U tile,grid[2],size;int origin[2];float spacing,p[3];double x0,x1,z0,z1,dx=0,dz=0,t;
 if(!flashlight_frame_active||!read_memory(descriptor,&tile,4)||!tile||
    !read_memory(patch+4,grid,8)||!read_memory(descriptor+8,&size,4)||
    !read_memory(tile+0x10,origin,8)||!read_memory(tile+0x1c,&spacing,4))return 0;
 if(!(spacing>0&&spacing<2049)||grid[0]>65536||grid[1]>65536||size>65536)return 0;
 memcpy(p,flashlight_frame+4,12);
 x0=origin[0]+grid[0]*(double)spacing;x1=x0+size*(double)spacing;
 z1=origin[1]-grid[1]*(double)spacing;z0=z1-size*(double)spacing;
 if(p[0]<x0)dx=x0-p[0];else if(p[0]>x1)dx=p[0]-x1;
 if(p[2]<z0)dz=z0-p[2];else if(p[2]>z1)dz=p[2]-z1;
 t=flash_safe(flashlight_tuning[FLASH_RANGE],FLASH_RANGE);
 return dx*dx+dz*dz<=t*t;
}

/* Native terrain already includes its selected beam. Add only our extra beam,
   using a render-thread snapshot, with no object lookup or OS calls per vertex. */
static U flashlight_terrain_colour(const float *position,U packed){
 double dx,dy,dz,d2,d,cone,weight;U out;int i;
 if(!flashlight_frame_active||*(U*)G(0x8287b0)==flashlight_object||flashlight_frame[1]<=0)return packed;
 dx=position[0]-flashlight_frame[4];dy=position[1]-flashlight_frame[5];dz=position[2]-flashlight_frame[6];
 d2=dx*dx+dy*dy+dz*dz;
 if(!(d2>1e-12&&d2<flashlight_frame[7]*flashlight_frame[7]))return packed;
 d=sqrt(d2);cone=((dx*flashlight_frame[8]+dy*flashlight_frame[9]+dz*flashlight_frame[10])/d-flashlight_cos)*flashlight_cone_scale;
 if(!(cone>0))return packed;if(cone>1)cone=1;
 weight=(d<25?d*.04:1-(d-25)/flashlight_frame[7])*cone*cone;
 if(!(weight>0&&weight<=1.00001))return packed;
 out=packed&0xff000000;
 for(i=0;i<3;i++){int shift=16-i*8;double value=((packed>>shift)&255)+255*weight*flashlight_frame[1+i];U channel=value>=255?255:(U)(value+.5);out|=channel<<shift;}
 return out;
}

/* Optimized object shaders accept one native cone. Add the FPV cone in object
   coordinates. The camera-attached light is at (0,0,.15), facing +Z in camera
   space; inverse camera/object matrix uses rows 0..8 and translation 12..14. */
static U flashlight_object_colour(const float *vertex,const float *matrix,U packed,int normals,int vertex_colour){
 double delta[3],direction[3],d2=0,d,cone,face=1,weight,norm=0;U result;int i;
 if(!flashlight_frame_active||flashlight_frame[1]<=0)return packed;
 for(i=0;i<3;i++){
  direction[i]=matrix[i*3+2];delta[i]=vertex[i]-(matrix[12+i]+.15*direction[i]);d2+=delta[i]*delta[i];
 }
 if(!(d2>1e-12&&d2<flashlight_frame[7]*flashlight_frame[7]))return packed;
 d=sqrt(d2);cone=((delta[0]*direction[0]+delta[1]*direction[1]+delta[2]*direction[2])/d-flashlight_cos)*flashlight_cone_scale;
 if(!(cone>0))return packed;if(cone>1)cone=1;
 if(normals){
  for(i=0;i<3;i++)norm+=vertex[3+i]*vertex[3+i];if(!(norm>1e-12))return packed;
  face=-(delta[0]*vertex[3]+delta[1]*vertex[4]+delta[2]*vertex[5])/(d*sqrt(norm));
  if(!(face>0))return packed;if(face>1)face=1;
 }
 weight=(1-d/flashlight_frame[7])*cone*face;
 if(!(weight>0&&weight<=1.00001))return packed;result=packed&0xff000000;
 for(i=0;i<3;i++){
  int shift=16-i*8;double tint=vertex_colour?(((*(const U*)(vertex+6)>>shift)&255)/255.0):1;
  double value=((packed>>shift)&255)+255*weight*flashlight_frame[1+i]*tint;
  result|=(value>=255?255:(U)(value+.5))<<shift;
 }
 return result;
}
