/* Read held native keyboard bindings, including modifiers and action masks.
   Brake lever position is not a held input (and may already be at its stop).
   No new event hooks, synthetic keys, or controller writes are needed. */
enum {CRAWL_RIGHTING=1,CRAWL_LEFT=2,CRAWL_RIGHT=4};
static int crawl_key(const B *bits,U scan){return (bits[scan>>3]>>(scan&7))&1;}
static int crawl_control_focus(void){
 HWND h;GUITHREADINFO info;
 if(!read_memory(G(0x82813a),&h,4)||!h||GetForegroundWindow()!=h)return 0;
 memset(&info,0,sizeof(info));info.cbSize=sizeof(info);
 return GetGUIThreadInfo(GetWindowThreadProcessId(h,NULL),&info)&&info.hwndFocus==h&&!(info.flags&0x1c);
}
static U crawl_keyboard_controls(U ctl,U type){
 U head,node,n[3],device[7],binding[4],action[6],listener[5],table[1024];
 U input,bits_address,scan,mods,link,handler,mask,result=0,budget=1024,devices=0,mode;
 B bits[32],kind;
 if(!ctl||type<1||type>3||!read_memory(G(0x829980),&mode,4)||mode!=0||
    !read_memory(G(0x8299a0),&head,4)||!head||!read_memory(head,&node,4))return 0;
 while(node!=head){
  if(!node||++devices>32||!read_memory(node,n,sizeof(n))||!read_memory(n[2],device,sizeof(device)))return 0;
  input=device[1];node=n[0];
  if(!input||!read_memory(input+0x2d,&kind,1)||kind!=1)continue;
  if(device[4]>65535||!read_memory(input+0x24,&bits_address,4)||!read_memory(bits_address,bits,32)||
     !read_memory(device[6]+device[4]*16,table,sizeof(table)))return 0;
  mods=(crawl_key(bits,0x2a)||crawl_key(bits,0x36)?8:0)|
       (crawl_key(bits,0x1d)||crawl_key(bits,0x9d)?4:0)|
       (crawl_key(bits,0x38)||crawl_key(bits,0xb8)?2:0)|
       (crawl_key(bits,0xdb)||crawl_key(bits,0xdc)?1:0);
  for(scan=0;scan<256;scan++)if(crawl_key(bits,scan)){
   memcpy(binding,table+scan*4,16);
   for(;;){
    if(!budget--)return 0;
    mask=(binding[2]>>8)&255;
    if(binding[0]&&!(binding[3]&1)&&(mods&mask)==(binding[2]&mask)){
     if(!read_memory(binding[0],action,sizeof(action)))return 0;
     if(!(action[4]&0x20000))for(handler=action[1];handler;handler=listener[2]){
      if(!budget--||!read_memory(handler,listener,sizeof(listener)))return 0;
      if(listener[4]&3)continue;
      if(!(listener[3]&0x100))continue;
      if(listener[0]==0x489a25&&listener[1]==ctl+(type==1?0x368:0x1c4))result|=CRAWL_RIGHTING;
      if(listener[1]==ctl+(type==1?0xe0:0x10c)){
       if(listener[0]==0x4898dd)result|=CRAWL_RIGHT;
       if(listener[0]==0x489987)result|=CRAWL_LEFT;
      }
     }
    }
    link=binding[1];if(!link)break;if(!read_memory(link,binding,16))return 0;
   }
  }
 }
 return result;
}
