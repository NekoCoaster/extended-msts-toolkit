/* XP-compatible display selection shared by the panel and runtime. */
#ifndef NEMT_DISPLAY_MONITOR_H
#define NEMT_DISPLAY_MONITOR_H
typedef struct { const char *device; HMONITOR found; } NemtMonitorSearch;
static BOOL CALLBACK nemt_find_monitor(HMONITOR monitor,HDC dc,LPRECT rect,LPARAM data){
 NemtMonitorSearch *search=(NemtMonitorSearch*)data;MONITORINFOEXA info;
 memset(&info,0,sizeof(info));info.mi.cbSize=sizeof(info);
 if(GetMonitorInfoA(monitor,(MONITORINFO*)&info) && !lstrcmpiA(info.szDevice,search->device)){
  search->found=monitor;return FALSE;
 }return TRUE;
}
static HMONITOR nemt_selected_monitor(const char *device){
 NemtMonitorSearch search;POINT origin={0,0};search.device=device;search.found=NULL;
 if(device && *device)EnumDisplayMonitors(NULL,NULL,nemt_find_monitor,(LPARAM)&search);
 return search.found?search.found:MonitorFromPoint(origin,MONITOR_DEFAULTTOPRIMARY);
}
static int nemt_large_display(int width,int height){return width>2048 || height>2048;}
#endif
