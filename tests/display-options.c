#include <assert.h>
static unsigned char display_globals[0x100000];
#define G(a) ((U)display_globals+(a)-0x7b0000)
#define TIMING_ADDR(a) G(a)
#include "../runtime/loader.c"
static LARGE_INTEGER fake_time;static double waited;static int clock_ok=1;
static BOOL WINAPI fake_counter(LARGE_INTEGER *t){*t=fake_time;return clock_ok;}
static void fake_sleep(double seconds){waited+=seconds;fake_time.QuadPart+=(LONGLONG)(seconds*1000000+0.5);}
int main(void){
 int rates[]={60,144,240},i;LARGE_INTEGER now;
 timing_frequency.QuadPart=1000000;timing_counter=fake_counter;refresh_sleep=fake_sleep;limit_vsync=1;
 for(i=0;i<3;i++){
  refresh_known=1;refresh_checked=GetTickCount();refresh_hz=rates[i];refresh_started=0;now.QuadPart=1000000;fake_time=now;assert(refresh_pace(&now));
  fake_time.QuadPart+=100;now=fake_time;waited=0;assert(refresh_pace(&now));assert(fabs(waited-(1.0/rates[i]-0.0001))<0.000001);
  fake_time.QuadPart+=100000;now=fake_time;waited=0;assert(refresh_pace(&now)&&waited==0); /* No catch-up after a slow frame. */
 }
 limit_vsync=0;assert(refresh_pace(&now)&&!refresh_started);limit_vsync=1;refresh_previous=now;refresh_started=1;clock_ok=0;assert(!refresh_pace(&now)&&!refresh_started);
 puts("PASS refresh pacing at 60/144/240Hz, stalls/disable/clock failure.");return 0;
}
