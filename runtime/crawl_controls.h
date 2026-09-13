/* Read held native keyboard bindings, including modifiers and action masks.
   Brake lever position is not a held input (and may already be at its stop).
   Rotation needs no synthetic keys or controller writes; manual derail events
   are handled separately. */
enum {CRAWL_RIGHTING=1,CRAWL_LEFT=2,CRAWL_RIGHT=4,CRAWL_DERAIL=8};
static int crawl_derail_down=1,crawl_derail_pending;
static int crawl_derail_edge(U input,int allowed){
 int down=(input&CRAWL_DERAIL)!=0,pressed=allowed&&down&&!crawl_derail_down;
 crawl_derail_down=allowed?down:1;return pressed;
}
static char crawl_shortcuts[3][40]={"Space",";","'"};
static U crawl_shortcut_ctl,crawl_shortcut_type;static DWORD crawl_shortcut_time;
static void crawl_shortcuts_reset(void){
 crawl_shortcut_ctl=crawl_shortcut_type=0;
 strcpy(crawl_shortcuts[0],"Space");strcpy(crawl_shortcuts[1],";");strcpy(crawl_shortcuts[2],"'");
}
static void crawl_key_name(U scan,U mods,char *out){
 char key[32];LONG code=((scan&127)<<16)|(scan>=128?0x1000000:0);
 if(scan==0x39)strcpy(key,"Space");else if(scan==0x27)strcpy(key,";");else if(scan==0x28)strcpy(key,"'");
 else if(!GetKeyNameTextA(code,key,sizeof(key)))snprintf(key,sizeof(key),"key %02X",scan);
 snprintf(out,40,"%s%s%s%s%s",mods&4?"Ctrl+":"",mods&8?"Shift+":"",mods&2?"Alt+":"",mods&1?"Win+":"",key);
}
static int crawl_key(const B *bits,U scan){return (bits[scan>>3]>>(scan&7))&1;}
static int crawl_control_focus(void){
 HWND h;GUITHREADINFO info;
 if(!read_memory(G(0x82813a),&h,4)||!h||GetForegroundWindow()!=h)return 0;
 memset(&info,0,sizeof(info));info.cbSize=sizeof(info);
 return GetGUIThreadInfo(GetWindowThreadProcessId(h,NULL),&info)&&info.hwndFocus==h&&!(info.flags&0x1c);
}
static U crawl_keyboard_controls(U ctl,U type){
 U head,node,n[3],device[7],binding[4],action[6],listener[5],table[1024];
 U input,bits_address,scan,mods,link,handler,mask,result=0,budget=1024,devices=0,mode,count,command,i;
 DWORD now=GetTickCount();int refresh=ctl!=crawl_shortcut_ctl||type!=crawl_shortcut_type||now-crawl_shortcut_time>=1000;
 char names[3][40]={"unbound","unbound","unbound"};U named=0;
 B bits[32],kind;
 if(!ctl||type<1||type>3||!read_memory(G(0x829980),&mode,4)||mode!=0||
    !read_memory(G(0x8299a0),&head,4)||!head||!read_memory(head,&node,4))return 0;
 while(node!=head){
  if(!node||++devices>32||!read_memory(node,n,sizeof(n))||!read_memory(n[2],device,sizeof(device)))return 0;
  input=device[1];node=n[0];
  if(!input||!read_memory(input+0x2d,&kind,1)||kind!=1)continue;
  /* MSTS's keyboard has 238 entries, not 256. Its bitset is only 30 bytes.
     Reading the allocator tail as keys can follow bogus bindings and reject
     every real command. +0x14 is the native table end, +0x10 its key offset. */
  if(device[5]<=device[4]||device[5]>65535||(count=device[5]-device[4])>256)return 0;
  memset(bits,0,sizeof(bits));
  if(!read_memory(input+0x24,&bits_address,4)||!read_memory(bits_address,bits,(count+7)/8)||
     !read_memory(device[6]+device[4]*16,table,count*16))return 0;
  mods=(crawl_key(bits,0x2a)||crawl_key(bits,0x36)?8:0)|
       (crawl_key(bits,0x1d)||crawl_key(bits,0x9d)?4:0)|
       (crawl_key(bits,0x38)||crawl_key(bits,0xb8)?2:0)|
       (crawl_key(bits,0xdb)||crawl_key(bits,0xdc)?1:0);
  if(count>0x2b&&!mods&&crawl_key(bits,0x2b))result|=CRAWL_DERAIL;
  for(scan=0;scan<count;scan++)if(refresh||crawl_key(bits,scan)){
   memcpy(binding,table+scan*4,16);
   for(;;){
    if(!budget--)return 0;
    mask=(binding[2]>>8)&255;
    if(binding[0]&&!(binding[3]&1)){
     if(!read_memory(binding[0],action,sizeof(action)))return 0;
     if(!(action[4]&0x20000))for(handler=action[1];handler;handler=listener[2]){
      if(!budget--||!read_memory(handler,listener,sizeof(listener)))return 0;
      if(listener[4]&3)continue;
      if(!(listener[3]&0x100))continue;
      command=0;
      if(listener[0]==0x489a25&&listener[1]==ctl+(type==1?0x368:0x1c4))command=CRAWL_RIGHTING;
      if(listener[1]==ctl+(type==1?0xe0:0x10c)){
       if(listener[0]==0x4898dd)command=CRAWL_RIGHT;
       if(listener[0]==0x489987)command=CRAWL_LEFT;
      }
      if(command){
       if(crawl_key(bits,scan)&&(mods&mask)==(binding[2]&mask))result|=command;
       if(refresh&&!(named&command)){
        i=command==CRAWL_RIGHTING?0:command==CRAWL_LEFT?1:2;
        crawl_key_name(scan,binding[2]&mask,names[i]);named|=command;
       }
      }
     }
    }
    link=binding[1];if(!link)break;if(!read_memory(link,binding,16))return 0;
   }
  }
 }
 if(refresh){memcpy(crawl_shortcuts,names,sizeof(names));crawl_shortcut_ctl=ctl;crawl_shortcut_type=type;crawl_shortcut_time=now;}
 return result;
}
