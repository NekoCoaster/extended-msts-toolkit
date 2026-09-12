/* MIT. Restart-only feature configuration. Missing features default off. */
static int write_status_json,prevent_end,unlock_cameras,crawl_requested,config_valid,window_features,center_windowed,verbose_loading,startup_log,unlock_fps,crawl_hud;
static int crawl_hud_left;
static WCHAR runtime_dir[MAX_PATH];
static int read_bool(const WCHAR *path,const WCHAR *section,const WCHAR *key){
 WCHAR value[32];GetPrivateProfileStringW(section,key,L"false",value,32,path);
 if(!lstrcmpiW(value,L"true")||!lstrcmpW(value,L"1"))return 1;
 if(lstrcmpiW(value,L"false")&&lstrcmpW(value,L"0"))config_valid=0;
 return 0;
}
static void read_config(void){
 WCHAR path[MAX_PATH],value[32],*end;long parsed;
 config_valid=1;wcscpy(runtime_dir,root);wcscat(runtime_dir,L"NEMT\\");
 wcscpy(path,runtime_dir);wcscat(path,L"native.ini");
 verbose_loading=read_bool(path,L"Startup",L"VerboseLoading");
 startup_log=read_bool(path,L"Startup",L"WriteLog");
 unlock_fps=read_bool(path,L"Startup",L"UnlockFPS");
 window_features=read_bool(path,L"Window",L"Enabled");
 center_windowed=read_bool(path,L"Window",L"CenterWindowed");
 prevent_end=read_bool(path,L"Derailment",L"PreventActivityEnd");
 unlock_cameras=read_bool(path,L"Derailment",L"UnlockCameras");
 crawl_requested=read_bool(path,L"Derailment",L"EnableCrawl");
 write_status_json=read_bool(path,L"Diagnostics",L"WriteStatusJson");
 crawl_hud=read_bool(path,L"Diagnostics",L"ShowCrawlHUD");
 GetPrivateProfileStringW(L"Diagnostics",L"CrawlHUDAnchor",L"BottomRight",value,32,path);
 crawl_hud_left=!lstrcmpiW(value,L"BottomLeft");if(!crawl_hud_left&&lstrcmpiW(value,L"BottomRight"))config_valid=0;
 GetPrivateProfileStringW(L"Derailment",L"CrawlStrength",L"10",value,32,path);
 parsed=wcstol(value,&end,10);if(end==value||*end||parsed<0||parsed>100)config_valid=0;
 strength=(int)parsed;
 if(crawl_requested&&!prevent_end)config_valid=0;
}
