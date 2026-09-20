/* MIT. Restart-only feature configuration. Missing features default off. */
static int write_status_json,prevent_end,unlock_cameras,crawl_requested,config_valid,window_features,center_windowed,verbose_loading,startup_log,unlock_fps,crawl_hud;
static int crawl_hud_left,cab_needles,background_audio,ignore_red_signal,restore_movie_focus,skip_startup_movie;
static int counter_tilt,prefer_pcores,limit_vsync;
static char window_monitor[32];
static int editor_windows,editor_free_tools,editor_idle_audio,editor_swap_keys,editor_unlimited_pan;
#include "editor_keys.h"
static DWORD max_log_bytes=8*1024*1024;static int max_backup_logs;
static WCHAR runtime_dir[MAX_PATH];
static int read_bool(const WCHAR *path,const WCHAR *section,const WCHAR *key){
 WCHAR value[32];GetPrivateProfileStringW(section,key,L"false",value,32,path);
 if(!lstrcmpiW(value,L"true")||!lstrcmpW(value,L"1"))return 1;
 if(lstrcmpiW(value,L"false")&&lstrcmpW(value,L"0"))config_valid=0;
 return 0;
}
static long read_limit(const WCHAR *path,const WCHAR *key,const WCHAR *fallback,long low,long high){WCHAR value[32],*end;long n;GetPrivateProfileStringW(L"Startup",key,fallback,value,32,path);n=wcstol(value,&end,10);if(end==value||*end||n<low||n>high){config_valid=0;return low;}return n;}
static void read_config(void){
 WCHAR path[MAX_PATH],value[32],*end;long parsed;
 config_valid=1;wcscpy(runtime_dir,root);wcscat(runtime_dir,L"NEMT\\");
 wcscpy(path,runtime_dir);wcscat(path,L"settings.ini");
 verbose_loading=read_bool(path,L"Startup",L"VerboseLoading");
 startup_log=read_bool(path,L"Startup",L"WriteLog");
 max_log_bytes=1024*read_limit(path,L"MaxLogSizeKB",L"8192",4,65536);max_backup_logs=read_limit(path,L"MaxBackupLogs",L"0",0,20);
 prefer_pcores=read_bool(path,L"Startup",L"PreferPCores");
 unlock_fps=read_bool(path,L"Startup",L"UnlockFPS");
 limit_vsync=read_bool(path,L"Startup",L"LimitToVSync");
 skip_startup_movie=read_bool(path,L"Startup",L"SkipStartupMovie");
 restore_movie_focus=read_bool(path,L"Startup",L"RestoreMovieFocus");
 cab_needles=read_bool(path,L"Cab",L"CorrectNeedleAspect");
 background_audio=read_bool(path,L"Audio",L"UnmuteInBackground");
 ignore_red_signal=read_bool(path,L"Activity",L"IgnoreRedSignal");
 window_features=read_bool(path,L"Window",L"Enabled");
 center_windowed=read_bool(path,L"Window",L"CenterWindowed");
 {WCHAR monitor[32];int i;GetPrivateProfileStringW(L"Window",L"Monitor",L"",monitor,32,path);
  for(i=0;i<31 && monitor[i] && monitor[i]<128;i++)window_monitor[i]=(char)monitor[i];
  window_monitor[i]=0;if(monitor[i])window_monitor[0]=0;}
 editor_windows=read_bool(path,L"Editors",L"ResizableViewports");
 editor_free_tools=read_bool(path,L"Editors",L"FreeToolWindows");
 editor_idle_audio=read_bool(path,L"Editors",L"SmoothIdleAudio");
 editor_swap_keys=read_bool(path,L"Editors",L"SwapArrowKeys");
 editor_unlimited_pan=read_bool(path,L"Editors",L"UnlimitedMousePan");
 if(editor_swap_keys){int i,j;for(i=0;i<6;i++){
  GetPrivateProfileStringW(L"Editors",editor_key_names[i],editor_key_defaults[i],value,32,path);
  editor_keys[i]=editor_key_parse(value);if(!editor_key_allowed(editor_keys[i]))config_valid=0;
  for(j=0;j<i;j++)if(editor_keys[i]==editor_keys[j])config_valid=0;
 }}
 prevent_end=read_bool(path,L"Derailment",L"PreventActivityEnd");
 unlock_cameras=read_bool(path,L"Derailment",L"UnlockCameras");
 crawl_requested=read_bool(path,L"Derailment",L"EnableCrawl");
 counter_tilt=read_bool(path,L"Derailment",L"CounterTilt");
 GetPrivateProfileStringW(L"Derailment",L"DerailKey",L"BACKSLASH",value,32,path);
 crawl_derail_scan=!lstrcmpW(value,L"\\")?0x2b:editor_key_parse(value);
 if(!lstrcmpiW(value,L"NONE")){crawl_derail_scan=0;strcpy(crawl_derail_name,"Disabled");}
 else if(!crawl_derail_scan||crawl_derail_scan>=238||crawl_derail_scan==1||
         crawl_derail_scan==0x1d||crawl_derail_scan==0x9d||crawl_derail_scan==0x2a||crawl_derail_scan==0x36||
         crawl_derail_scan==0x38||crawl_derail_scan==0xb8||crawl_derail_scan==0xdb||crawl_derail_scan==0xdc||crawl_derail_scan==0xdd)config_valid=0;
 else if(crawl_derail_scan==0x2b)strcpy(crawl_derail_name,"\\");
 else crawl_key_name(crawl_derail_scan,0,crawl_derail_name);
 write_status_json=read_bool(path,L"Diagnostics",L"WriteStatusJson");
 crawl_hud=read_bool(path,L"Diagnostics",L"ShowCrawlHUD");
 GetPrivateProfileStringW(L"Diagnostics",L"CrawlHUDAnchor",L"BottomLeft",value,32,path);
 crawl_hud_left=!lstrcmpiW(value,L"BottomLeft");if(!crawl_hud_left&&lstrcmpiW(value,L"BottomRight"))config_valid=0;
 GetPrivateProfileStringW(L"Derailment",L"CrawlStrength",L"10",value,32,path);
 parsed=wcstol(value,&end,10);if(end==value||*end||parsed<0||parsed>100)config_valid=0;
 strength=(int)parsed;
 if(crawl_requested&&!prevent_end)config_valid=0;
}
