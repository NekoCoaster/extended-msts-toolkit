#include <assert.h>
static unsigned char display_globals[0x100000];
#define G(a) ((U)display_globals+(a)-0x7b0000)
#define TIMING_ADDR(a) G(a)
#include "../runtime/loader.c"
static LARGE_INTEGER fake_time;static double waited;static int clock_ok=1,updates;static WCHAR last_title[320];
static BOOL WINAPI fake_counter(LARGE_INTEGER *t){*t=fake_time;return clock_ok;}
static void fake_sleep(double seconds){waited+=seconds;fake_time.QuadPart+=(LONGLONG)(seconds*1000000+0.5);}
static U __fastcall update(U id,U message,const WCHAR *text){assert(id==1&&message==0x31);wcscpy(last_title,text);updates++;return 1;}
int main(void){
 int rates[]={60,144,240},i;LARGE_INTEGER now;U table[6]={0};B heading[128]={0},selector[128]={0};
 int a[4]={80,176,225,30},t[4]={0,0,225,30},sa[4]={88,209,197,15},st[4]={10,0,160,15};
 timing_frequency.QuadPart=1000000;timing_counter=fake_counter;refresh_sleep=fake_sleep;limit_vsync=1;
 for(i=0;i<3;i++){
  refresh_known=1;refresh_checked=GetTickCount();refresh_hz=rates[i];refresh_started=0;now.QuadPart=1000000;fake_time=now;assert(refresh_pace(&now));
  fake_time.QuadPart+=100;now=fake_time;waited=0;assert(refresh_pace(&now));assert(fabs(waited-(1.0/rates[i]-0.0001))<0.000001);
  fake_time.QuadPart+=100000;now=fake_time;waited=0;assert(refresh_pace(&now)&&waited==0); /* No catch-up after a slow frame. */
 }
 limit_vsync=0;assert(refresh_pace(&now)&&!refresh_started);limit_vsync=1;refresh_previous=now;refresh_started=1;clock_ok=0;assert(!refresh_pace(&now)&&!refresh_started);
 assert(!resolution_above_limit(L"2048 x 2048 x 32"));assert(resolution_above_limit(L"2560x1600x32"));assert(resolution_above_limit(L"1080 X 2560 X 32"));assert(!resolution_above_limit(L"1920x1080x32"));assert(!resolution_above_limit(L"garbage"));
 table[2]=(U)heading;table[4]=(U)selector;*(U*)G(0x828108)=(U)table;memcpy(heading+0x20,a,16);memcpy(heading+0x38,t,16);memcpy(selector+0x20,sa,16);memcpy(selector+0x38,st,16);welcome_set_original=update;
 assert(!wcscmp(resolution_note(1,L"Display resolution"),L"Display resolution"));resolution_note(2,L"2560x1600x32");assert(updates==1&&wcsstr(last_title,L"D3DIM700.DLL")&&ru(heading+0x28)==650);
 resolution_note(2,L"1920x1080x32");assert(!wcscmp(last_title,L"Display resolution")&&!memcmp(heading+0x20,a,16));
 sa[0]=90;memcpy(selector+0x20,sa,16);resolution_note(2,L"2560x1600x32");assert(updates==2); /* custom layout untouched */
 puts("PASS refresh pacing at 60/144/240Hz, stalls/disable/clock failure; resolution threshold, native note updates/restoration and custom layout exclusion.");return 0;
}
