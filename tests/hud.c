#include <assert.h>
static unsigned char globals[0x100000];
#define G(a) ((U)globals+(a)-0x7a0000)
#include "../runtime/loader.c"
static int draws,ends;
static int __fastcall fake_width(void *font,const WCHAR *text){return wcslen(text)*6;}
static int __fastcall fake_height(void *font){return 12;}
static U __fastcall fake_draw(void *font,int x,int y,U color,const WCHAR *text){assert(x==*(int*)G(0x7a8960)-8-fake_width(font,text)&&y==*(int*)G(0x7a8964)-44+(draws%3)*12&&color==0xffffffff&&text[0]);draws++;return 0;}
static void fake_end(void){ends++;}
int main(void){char lines[3][160];
 hud_lines(lines);assert(strstr(lines[0],"disabled"));
 crawl_requested=1;hud_lines(lines);assert(strstr(lines[0],"waiting"));
 InitializeCriticalSection(&state_lock);crawl_state_ready=1;enabled=1;strength=10;throttle=.5;direction=-1;applied_dt=.1;
 car_count=3;cars[0].engine=cars[1].engine=1;cars[0].active=1;cars[0].dp[0]=300;cars[0].dp[1]=400;
 hud_lines(lines);assert(strstr(lines[0],"active")&&strstr(lines[0],"-5.0 kN"));assert(strstr(lines[1],"50%")&&strstr(lines[1],"reverse"));assert(strstr(lines[2],"1 applying / 2 connected"));
 direction=1;hud_lines(lines);assert(strstr(lines[0],": 5.0 kN"));direction=-1;
 *(U*)G(0x7be0f4)=1;hud_lines(lines);assert(strstr(lines[0],"paused")&&strstr(lines[0],"0.0 kN"));assert(strstr(lines[2],"0 applying"));
 *(U*)G(0x7be0f4)=0;blocked=1;hud_lines(lines);assert(strstr(lines[0],"fault")&&strstr(lines[0],"0.0 kN"));
 clear_activity();hud_lines(lines);assert(strstr(lines[2],"0 applying / 0 connected"));
 {U table[16]={0};U font=(U)table;table[6]=(U)fake_height;table[9]=(U)fake_width;table[13]=(U)fake_draw;*(U*)G(0x7b64d4)=(U)&font;*(int*)G(0x7a8960)=640;*(int*)G(0x7a8964)=480;hud_end_original=fake_end;
 crawl_hud=1;hud_render_end();assert(draws==3&&ends==1);*(int*)G(0x7a8960)=1920;*(int*)G(0x7a8964)=1080;hud_render_end();assert(draws==6&&ends==2);crawl_hud=0;hud_render_end();assert(draws==6&&ends==3);}
 puts("PASS HUD disabled/waiting/active/paused/fault states, applied force, throttle, reverser, powered membership and activity exit.");return 0;
}
