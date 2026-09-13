/* Operate on native buffered events, before IOM lookup, rather than injecting
   Windows keys. A release follows the mapping chosen by its matching press. */
static unsigned editor_key_routes[256],editor_key_masks[256];
static B editor_key_held[256],editor_key_consumed[256];
static U editor_key_event[4],*editor_key_mask_slot,editor_key_mask_saved;
static U editor_key_ctrl_saved[2];static int editor_key_ctrl_changed;
static int editor_keyboard_focus(void){
 return editor_swap_keys&&editor_route_focus();
}
static void editor_key_restore(void){
 if(editor_key_mask_slot){*editor_key_mask_slot=editor_key_mask_saved;editor_key_mask_slot=NULL;}
 if(editor_key_ctrl_changed){memcpy((void*)0x7ba9c0,editor_key_ctrl_saved,8);editor_key_ctrl_changed=0;}
}
static void editor_key_restore_hook(U unused,Registers *r){editor_key_restore();}
static void editor_key_event_hook(U unused,Registers *r){
 U *stack=(U*)(r->esp+4),*event=(U*)stack[6],*device=(U*)stack[9];
 unsigned scan,mapped,consume=0,mask;
 if(!device||!device[1]||*((B*)device[1]+0x2d)!=1||(event[0]>>16)!=1)return;
 scan=event[0]&0xffff;if(scan>=256)return;
 mask=stack[10];mapped=scan;
 if(event[1]){
  if(editor_keyboard_focus())mapped=editor_key_swap(scan,mask,&consume);
  editor_key_routes[scan]=mapped;editor_key_masks[scan]=mask;
  editor_key_consumed[scan]=(B)consume;editor_key_held[scan]=1;
 }else if(editor_key_held[scan]){
  mapped=editor_key_routes[scan];consume=editor_key_consumed[scan];
  mask=editor_key_masks[scan];editor_key_held[scan]=0;
 }
 if(mapped==scan&&!consume)return;
 memcpy(editor_key_event,event,16);editor_key_event[0]=0x10000|mapped;stack[6]=(U)editor_key_event;
 editor_key_mask_slot=&stack[10];editor_key_mask_saved=stack[10];stack[10]=mask&~(consume?4:0);
 if(consume){memcpy(editor_key_ctrl_saved,(void*)0x7ba9c0,8);memset((void*)0x7ba9c0,0,8);editor_key_ctrl_changed=1;}
}
static int editor_physical_key(const B *bits,unsigned scan){return (bits[scan>>3]>>(scan&7))&1;}
static const B *editor_keyboard_bits(void){
 U *head=*(U**)0x8299a0,*node;U *device;B *input;
 if(!head)return NULL;
 for(node=(U*)*head;node!=head;node=(U*)*node){
  device=(U*)node[2];input=(B*)device[1];
  if(input&&input[0x2d]==1)return *(B**)(input+0x24);
 }
 return NULL;
}
static void editor_camera_keys(void){
 U saved[4];const B *bits;float speed,cooldown;int enabled,ctrl,alt,shift;
 enabled=editor_swap_keys&&editor_mode()==1;
 if(enabled){
  memcpy(saved,(void*)0x7ba9d0,16);
  /* Bare arrows now dispatch their displaced tools. Keep Ctrl+Left/Right's
     native rotation, but neither arrow can move the camera vertically. */
  if(!*(U*)0x7ba9c0&&!*(U*)0x7ba9c4)memset((void*)0x7ba9d0,0,8);
  memset((void*)0x7ba9d8,0,8);
 }
 cooldown=*(float*)0x7c2a70;
 ((void(*)(void))0x4a8d27)();
 editor_pan_apply();
 if(!enabled)return;
 memcpy((void*)0x7ba9d0,saved,16);
 if(!editor_keyboard_focus()||(bits=editor_keyboard_bits())==NULL)return;
 ctrl=editor_physical_key(bits,0x1d)||editor_physical_key(bits,0x9d);
 alt=editor_physical_key(bits,0x38)||editor_physical_key(bits,0xb8)||editor_physical_key(bits,0xdb)||editor_physical_key(bits,0xdc);
 if(ctrl||alt)return;
 shift=editor_physical_key(bits,0x2a)||editor_physical_key(bits,0x36);
 speed=shift?(*(U*)0x7baa20?50.f:10.f):(*(U*)0x7baa20?.1f:1.f);
 if(cooldown<=*(float*)0x828fb4){
  if(editor_physical_key(bits,editor_keys[2]))*(float*)0x7c2a58=-speed;
  if(editor_physical_key(bits,editor_keys[3]))*(float*)0x7c2a58=speed;
  if(*(float*)0x7c2a58&&*(U*)0x7c2a88&&!*(U*)(*(U*)0x7c2a88+0x11c))*(float*)0x7c2a70=.5f;
 }
 if(editor_physical_key(bits,editor_keys[0]))*(float*)0x7c2a60=speed;
 if(editor_physical_key(bits,editor_keys[1]))*(float*)0x7c2a60=-speed;
 if(editor_physical_key(bits,editor_keys[4]))*(float*)0x7c2a5c=-speed;
 if(editor_physical_key(bits,editor_keys[5]))*(float*)0x7c2a5c=speed;
}
