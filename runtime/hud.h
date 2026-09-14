/* MIT. Four lines at the end of the extended white F5 renderer. */
typedef U (__fastcall *HudDrawFn)(void*,int,int,U,const WCHAR*);
typedef int (__fastcall *HudHeightFn)(void*);
typedef int (__fastcall *HudWidthFn)(void*,const WCHAR*);
static void (*hud_end_original)(void)=(void*)0x6ae6f0;
static Hook hud_hook;
enum {HUD_LINE_COUNT=4};
static void hud_lines(char lines[HUD_LINE_COUNT][240]){
 const char *status="Standby",*reverser="Neutral";U powered=0,applying=0,i,rotation=0;double force=0,t=0;int boost=strength;
 char keys[3][40]={"Space",";","'"};
 if(crawl_requested&&crawl_state_ready){EnterCriticalSection(&state_lock);
  boost=strength;t=clamp_throttle(throttle);reverser=direction>0?"Forward":direction<0?"Reverse":"Neutral";
  if(enabled&&!blocked&&!paused())status="Active";
  for(i=0;i<car_count;i++){Car *c=&cars[i];if(c->engine)powered++;
   if(c->active&&enabled&&!blocked&&!paused()){applying++;if(applied_dt>0)force+=sqrt(c->dp[0]*c->dp[0]+c->dp[1]*c->dp[1]+c->dp[2]*c->dp[2])/applied_dt;}}
  if(direction<0&&force>0)force=-force;
  memcpy(keys,crawl_shortcuts,sizeof(keys));if(enabled&&!blocked&&!paused())rotation=rotation_inputs;
  LeaveCriticalSection(&state_lock);
 }
 snprintf(lines[0],240,"Crawl system: %s; Strength: %dx; Force: %.2f kN",status,boost,force/1000);
 snprintf(lines[1],240,"Direction: %.0f%% - %s; Applied on engines: %u of %u;",t*100,reverser,applying,powered);
 snprintf(lines[2],240,"Active rotation nudge: %s%s%s",rotation&CRAWL_LEFT?"LEFT":rotation&CRAWL_RIGHT?"RIGHT":"",(rotation&(CRAWL_LEFT|CRAWL_RIGHT))&&(rotation&CRAWL_RIGHTING)?" + ":"",rotation&CRAWL_RIGHTING?"UPRIGHT":rotation?"":"None");
 snprintf(lines[3],240,"Controls: Derail = %s  Steer Left = %s  Steer Right = %s  Rotate Upright = %s",crawl_derail_name,keys[1],keys[2],keys[0]);
}
static void hud_render_end(void){
 void *font=*(void**)G(0x7b64d4);int screen_height=*(int*)G(0x7a8964),screen_width=*(int*)G(0x7a8960),height,x,y,i;char lines[HUD_LINE_COUNT][240];WCHAR wide[240];
 if(crawl_hud&&font){HudDrawFn draw=*(HudDrawFn*)(*(U*)font+0x34);HudHeightFn get_height=*(HudHeightFn*)(*(U*)font+0x18);HudWidthFn get_width=*(HudWidthFn*)(*(U*)font+0x24);height=get_height(font);
  if(height>0&&height<100&&screen_height>height*HUD_LINE_COUNT+10){hud_lines(lines);y=screen_height-height*HUD_LINE_COUNT-8;
   for(i=0;i<HUD_LINE_COUNT;i++){wide[0]=0;MultiByteToWideChar(0,0,lines[i],-1,wide,240);x=crawl_hud_left?8:screen_width-8-get_width(font,wide);if(x<8)x=8;draw(font,x,y+i*height,0xffffffff,wide);}
  }
 }
 hud_end_original();
}
static int install_hud_hook(void){
 if(!crawl_hud)return 1;
 startup_call(&hud_hook,0x60c996,0x6ae6f0,(U)hud_render_end);
 return prepare_hooks(&hud_hook,1)&&install_hooks(&hud_hook,1);
}
