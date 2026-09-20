#include <windows.h>
#include <string.h>
#include <assert.h>
static MONITORINFOEXA displays[2];static int connected=2;
static BOOL WINAPI test_info(HMONITOR monitor,LPMONITORINFO info){
 int i=(int)(INT_PTR)monitor-1;if(i<0||i>=connected)return FALSE;
 memcpy(info,&displays[i],info->cbSize);return TRUE;
}
static BOOL WINAPI test_enum(HDC dc,LPCRECT rect,MONITORENUMPROC callback,LPARAM data){
 int i;for(i=0;i<connected;i++)if(!callback((HMONITOR)(INT_PTR)(i+1),NULL,&displays[i].mi.rcMonitor,data))break;return TRUE;
}
static HMONITOR WINAPI test_primary(POINT p,DWORD flags){return (HMONITOR)1;}
#define GetMonitorInfoA test_info
#define EnumDisplayMonitors test_enum
#define MonitorFromPoint test_primary
#include "../runtime/display-monitor.h"
#include "../runtime/window_math.h"
#include <stdio.h>
int main(void){int x,y;MONITORINFO info;
 strcpy(displays[0].szDevice,"\\\\.\\DISPLAY1");strcpy(displays[1].szDevice,"\\\\.\\DISPLAY2");
 displays[0].mi.rcMonitor.right=1920;displays[0].mi.rcMonitor.bottom=1080;
 displays[1].mi.rcMonitor.left=-2560;displays[1].mi.rcMonitor.top=-200;displays[1].mi.rcMonitor.bottom=1240;
 assert(nemt_selected_monitor("")==(HMONITOR)1);
 assert(nemt_selected_monitor("\\\\.\\display2")==(HMONITOR)2);
 info.cbSize=sizeof(info);assert(test_info(nemt_selected_monitor(displays[1].szDevice),&info));
 centered_position(info.rcMonitor.left,info.rcMonitor.top,info.rcMonitor.right,info.rcMonitor.bottom,1280,720,&x,&y);
 assert(x==-1920 && y==160);
 connected=1;assert(nemt_selected_monitor("\\\\.\\DISPLAY2")==(HMONITOR)1);
 assert(!nemt_large_display(2048,2048));assert(nemt_large_display(2049,1080));assert(nemt_large_display(1080,2049));
 assert(!nemt_large_display(1920,1080));
 puts("PASS two-monitor selection, negative coordinates, disconnected fallback and strict per-monitor threshold.");return 0;
}
