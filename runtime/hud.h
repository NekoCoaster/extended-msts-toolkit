/* MIT. Add three lines only at the end of the extended white F5 renderer. */
typedef U (__fastcall *HudDrawFn)(void*,int,int,U,const WCHAR*);
typedef int (__fastcall *HudHeightFn)(void*);
typedef int (__fastcall *HudWidthFn)(void*,const WCHAR*);
static void (*hud_end_original)(void)=(void*)0x6ae6f0;
static Hook hud_hook;
static void hud_lines(char lines[3][160]){
 const char *status="disabled",*reverser="neutral";U powered=0,applying=0,i;double force=0,t=0;int boost=strength,is_paused=0;
 if(crawl_requested){status="waiting for activity";
  if(crawl_state_ready){EnterCriticalSection(&state_lock);is_paused=paused();status=blocked?"fault":is_paused?"paused":enabled?"active":have_sim?"ready":"armed";boost=strength;t=clamp_throttle(throttle);reverser=direction>0?"forward":direction<0?"reverse":"neutral";
   for(i=0;i<car_count;i++){Car *c=&cars[i];if(c->engine)powered++;if(c->active&&enabled&&!blocked&&!is_paused){applying++;if(applied_dt>0)force+=sqrt(c->dp[0]*c->dp[0]+c->dp[1]*c->dp[1]+c->dp[2]*c->dp[2])/applied_dt;}}
   if(direction<0&&force>0)force=-force;
   LeaveCriticalSection(&state_lock);
  }
 }
 snprintf(lines[0],160,"NEMT crawl: %s | %dx | Applied thrust: %.1f kN",status,boost,force/1000);
 snprintf(lines[1],160,"Throttle/regulator: %.0f%% | Reverser: %s",t*100,reverser);
 snprintf(lines[2],160,"Powered engines: %u applying / %u connected",applying,powered);
}
static void hud_render_end(void){
 void *font=*(void**)G(0x7b64d4);int screen_height=*(int*)G(0x7a8964),screen_width=*(int*)G(0x7a8960),height,x,y,i;char lines[3][160];WCHAR wide[160];
 if(crawl_hud&&font){HudDrawFn draw=*(HudDrawFn*)(*(U*)font+0x34);HudHeightFn get_height=*(HudHeightFn*)(*(U*)font+0x18);HudWidthFn get_width=*(HudWidthFn*)(*(U*)font+0x24);height=get_height(font);
  if(height>0&&height<100&&screen_height>height*3+10){hud_lines(lines);y=screen_height-height*3-8;
   for(i=0;i<3;i++){wide[0]=0;MultiByteToWideChar(0,0,lines[i],-1,wide,160);x=screen_width-8-get_width(font,wide);if(x<8)x=8;draw(font,x,y+i*height,0xffffffff,wide);}
  }
 }
 hud_end_original();
}
static int install_hud_hook(void){
 if(!crawl_hud)return 1;
 startup_call(&hud_hook,0x60c996,0x6ae6f0,(U)hud_render_end);
 return prepare_hooks(&hud_hook,1)&&install_hooks(&hud_hook,1);
}
