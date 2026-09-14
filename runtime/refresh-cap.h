/* Display-rate cap, not a swap/presentation VSync override. */
static HANDLE refresh_timer;
static double refresh_hz=60;
static DWORD refresh_checked;
static int refresh_known,refresh_started;
static LARGE_INTEGER refresh_previous;
static double refresh_display_rate(void){
 HWND hwnd=NULL;struct {DWORD cbSize;RECT rcMonitor,rcWork;DWORD dwFlags;char szDevice[32];} info;DEVMODEA mode;
 read_memory(TIMING_ADDR(0x82813a),&hwnd,sizeof(hwnd));
 memset(&info,0,sizeof(info));info.cbSize=sizeof(info);
 memset(&mode,0,sizeof(mode));mode.dmSize=sizeof(mode);
 if(GetMonitorInfoA(MonitorFromWindow(hwnd,MONITOR_DEFAULTTONEAREST),(MONITORINFO*)&info)&&
    EnumDisplaySettingsA(info.szDevice,ENUM_CURRENT_SETTINGS,&mode)&&mode.dmDisplayFrequency>=10&&mode.dmDisplayFrequency<=1000)return mode.dmDisplayFrequency;
 return 60; /* Unknown/default (0/1) refresh cannot be used as a frame rate. */
}
static void refresh_wait(double seconds){
 LARGE_INTEGER due;
 if(refresh_timer){due.QuadPart=-(LONGLONG)(seconds*10000000.0+1);
  if(SetWaitableTimer(refresh_timer,&due,0,NULL,NULL,FALSE)){WaitForSingleObject(refresh_timer,200);return;}}
 Sleep((DWORD)(seconds*1000.0+1));
}
static void (*refresh_sleep)(double)=refresh_wait;
static int refresh_pace(LARGE_INTEGER *now){
 double remaining;DWORD tick=GetTickCount();
 if(!limit_vsync){refresh_started=0;return 1;}
 if(!refresh_known||(DWORD)(tick-refresh_checked)>=1000){refresh_hz=refresh_display_rate();refresh_checked=tick;refresh_known=1;}
 if(refresh_started&&now->QuadPart>=refresh_previous.QuadPart){
  remaining=1.0/refresh_hz-(double)(now->QuadPart-refresh_previous.QuadPart)/timing_frequency.QuadPart;
  if(remaining>0){refresh_sleep(remaining);if(!timing_counter(now)){refresh_started=0;return 0;}}
 }
 refresh_previous=*now;refresh_started=1;return 1;
}
static void refresh_initialize(void){
 typedef HANDLE (WINAPI *CreateTimer)(LPSECURITY_ATTRIBUTES,LPCWSTR,DWORD,DWORD);
 CreateTimer create=(CreateTimer)GetProcAddress(GetModuleHandleA("kernel32.dll"),"CreateWaitableTimerExW");
 if(limit_vsync&&create)refresh_timer=create(NULL,NULL,2,0x1f0003); /* high-resolution timer; no global timer-resolution change */
}
