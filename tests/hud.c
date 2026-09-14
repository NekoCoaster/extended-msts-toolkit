#include <assert.h>
static unsigned char globals[0x100000];
#define G(a) ((U)globals+(a)-0x7a0000)
#include "../runtime/loader.c"
static int draws,ends;
static int __fastcall fake_width(void *font,const WCHAR *text){return wcslen(text)*6;}
static int __fastcall fake_height(void *font){return 12;}
static U __fastcall fake_draw(void *font,int x,int y,U color,const WCHAR *text){assert(x==(crawl_hud_left?8:*(int*)G(0x7a8960)-8-fake_width(font,text))&&y==*(int*)G(0x7a8964)-(HUD_LINE_COUNT*12+8)+(draws%HUD_LINE_COUNT)*12&&color==0xffffffff&&text[0]);draws++;return 0;}
static void fake_end(void){ends++;}
int main(void){char lines[HUD_LINE_COUNT][240];
 hud_lines(lines);assert(strstr(lines[0],"Standby"));
 crawl_requested=1;hud_lines(lines);assert(strstr(lines[0],"Standby"));
 InitializeCriticalSection(&state_lock);crawl_state_ready=1;enabled=1;strength=10;throttle=.5;direction=-1;applied_dt=.1;
 car_count=3;cars[0].engine=cars[1].engine=1;cars[0].active=1;cars[0].dp[0]=300;cars[0].dp[1]=400;
 hud_lines(lines);assert(strstr(lines[0],"Active")&&strstr(lines[0],"-5.00 kN"));assert(strstr(lines[1],"50%")&&strstr(lines[1],"Reverse"));assert(strstr(lines[1],"Applied on engines: 1 of 2;"));
 strcpy(crawl_shortcuts[0],"H");strcpy(crawl_shortcuts[1],"Ctrl+J");strcpy(crawl_shortcuts[2],"K");crawl_shortcut_ctl=1;
 rotation_inputs=CRAWL_RIGHTING|CRAWL_LEFT;hud_lines(lines);assert(strstr(lines[3],"Nudge Left = Ctrl+J  Nudge Right = K  Rotate Upright = H"));assert(strstr(lines[2],"LEFT + UPRIGHT"));
 rotation_inputs=CRAWL_RIGHT;hud_lines(lines);assert(strstr(lines[2],"RIGHT"));
 strcpy(crawl_derail_name,"F12");hud_lines(lines);assert(strstr(lines[3],"Derail = F12"));
 direction=1;hud_lines(lines);assert(strstr(lines[0],": 5.00 kN"));direction=-1;
 *(U*)G(0x7be0f4)=1;hud_lines(lines);assert(strstr(lines[0],"Standby")&&strstr(lines[0],"0.00 kN"));assert(strstr(lines[1],"engines: 0 of"));assert(strstr(lines[2],"None"));
 *(U*)G(0x7be0f4)=0;blocked=1;hud_lines(lines);assert(strstr(lines[0],"Standby")&&strstr(lines[0],"0.00 kN"));
 clear_activity();hud_lines(lines);assert(strstr(lines[1],"engines: 0 of 0;"));
 {U table[16]={0};U font=(U)table;table[6]=(U)fake_height;table[9]=(U)fake_width;table[13]=(U)fake_draw;*(U*)G(0x7b64d4)=(U)&font;*(int*)G(0x7a8960)=640;*(int*)G(0x7a8964)=480;hud_end_original=fake_end;
 crawl_hud=1;hud_render_end();assert(draws==4&&ends==1);*(int*)G(0x7a8960)=1920;*(int*)G(0x7a8964)=1080;hud_render_end();assert(draws==8&&ends==2);crawl_hud_left=1;hud_render_end();assert(draws==12&&ends==3);crawl_hud=0;hud_render_end();assert(draws==12&&ends==4);}
 puts("PASS HUD disabled/waiting/active/paused/fault states, applied force, throttle, reverser, powered membership and activity exit.");return 0;
}
