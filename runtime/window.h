/* Native window module. Only the game's IAT is redirected; dgVoodoo is chained. */
#include "window_math.h"
typedef LPSTR (WINAPI *CmdLineFn)(void);
typedef BOOL (WINAPI *WindowPosFn)(HWND,HWND,int,int,int,int,UINT);
typedef BOOL (WINAPI *ShowFn)(HWND,int);
static CmdLineFn original_command_line;
static WindowPosFn original_window_pos;
static ShowFn original_show;
static volatile LONG window_initialized;
static char *normalized_command_line;
static int requested_window_mode,window_mode;
static HWND arranged_window;
static int window_busy;
static Hook window_hooks[2];
#ifndef WINDOW_ADDR
#define WINDOW_ADDR(a) (a)
#endif
static int main_window(HWND h){return h&&h==*(HWND*)WINDOW_ADDR(0x82813a);}
static int strip_frame(HWND h){
 LONG style=GetWindowLongA(h,GWL_STYLE),ex=GetWindowLongA(h,GWL_EXSTYLE);
 LONG desired=(style&~(WS_CAPTION|WS_THICKFRAME))|WS_POPUP;
 LONG desired_ex=ex&~(WS_EX_CLIENTEDGE|WS_EX_WINDOWEDGE|WS_EX_DLGMODALFRAME|WS_EX_STATICEDGE);
 if(style==desired&&ex==desired_ex)return 0;
 SetWindowLongA(h,GWL_STYLE,desired);SetWindowLongA(h,GWL_EXSTYLE,desired_ex);
 /* MSTS caches these for subsequent AdjustWindowRectEx calls. */
 *(LONG*)WINDOW_ADDR(0x82818a)=desired;*(LONG*)WINDOW_ADDR(0x82818e)=desired_ex;
 return 1;
}
static void frame_extent(HWND h,int *w,int *v){
 RECT r={0,0,0,0};AdjustWindowRectEx(&r,GetWindowLongA(h,GWL_STYLE),GetMenu(h)!=NULL,GetWindowLongA(h,GWL_EXSTYLE));
 *w=r.right-r.left;*v=r.bottom-r.top;
}
static void center_for(HWND h,int width,int height,int *x,int *y){
 MONITORINFO info;HMONITOR monitor=MonitorFromWindow(h,MONITOR_DEFAULTTONEAREST);RECT r;
 info.cbSize=sizeof(info);
 if(GetMonitorInfoA(monitor,&info))r=window_mode==2?info.rcMonitor:info.rcWork;
 else{r.left=r.top=0;r.right=GetSystemMetrics(SM_CXSCREEN);r.bottom=GetSystemMetrics(SM_CYSCREEN);}
 centered_position(r.left,r.top,r.right,r.bottom,width,height,x,y);
}
static BOOL WINAPI toolkit_window_pos(HWND h,HWND after,int x,int y,int cx,int cy,UINT flags){
 RECT old;int fw=0,fh=0,nw=0,nh=0,changed=0,resize;
 if(!window_mode||window_busy||!main_window(h)||IsIconic(h))return original_window_pos(h,after,x,y,cx,cy,flags);
 window_busy=1;GetWindowRect(h,&old);
 if(window_mode==2){frame_extent(h,&fw,&fh);changed=strip_frame(h);if(changed){frame_extent(h,&nw,&nh);if(!(flags&SWP_NOSIZE)){cx+=nw-fw;cy+=nh-fh;}else{cx=old.right-old.left+nw-fw;cy=old.bottom-old.top+nh-fh;flags&=~SWP_NOSIZE;}flags|=SWP_FRAMECHANGED;}}
 resize=!(flags&SWP_NOSIZE)&&(cx!=old.right-old.left||cy!=old.bottom-old.top);
 if(arranged_window!=h||changed||resize){
  if(flags&SWP_NOSIZE){cx=old.right-old.left;cy=old.bottom-old.top;}
  if(cx>0&&cy>0){center_for(h,cx,cy,&x,&y);flags&=~SWP_NOMOVE;arranged_window=h;}
 }
 {BOOL result=original_window_pos(h,after,x,y,cx,cy,flags);window_busy=0;return result;}
}
static BOOL WINAPI toolkit_show(HWND h,int command){
 if(window_mode&&!window_busy&&main_window(h)&&!IsIconic(h)&&command!=SW_HIDE&&command!=SW_MINIMIZE&&command!=SW_SHOWMINIMIZED&&command!=SW_SHOWMINNOACTIVE){
  toolkit_window_pos(h,NULL,0,0,0,0,SWP_NOSIZE|SWP_NOMOVE|SWP_NOZORDER|SWP_NOACTIVATE);
 }
 return original_show(h,command);
}
static int install_window_hooks(void){
 U i;static const U addresses[]={0x84df30,0x84df40};U destinations[2];
 original_window_pos=*(WindowPosFn*)addresses[0];original_show=*(ShowFn*)addresses[1];
 destinations[0]=(U)toolkit_window_pos;destinations[1]=(U)toolkit_show;
 for(i=0;i<2;i++){Hook *h=&window_hooks[i];h->address=addresses[i];h->length=4;h->raw=1;memcpy(h->original,(void*)addresses[i],4);memcpy(h->replacement,&destinations[i],4);}
 return prepare_hooks(window_hooks,2)&&install_hooks(window_hooks,2);
}
static LPSTR WINAPI toolkit_command_line(void){
 LPSTR actual=original_command_line();LONG state=InterlockedCompareExchange(&window_initialized,1,0);
 if(state==0){
  WCHAR *slash;SIZE_T length=lstrlenA(actual);requested_window_mode=normalize_vm(actual,NULL);
  if(requested_window_mode&&length<32768&&GetModuleFileNameW(NULL,root,MAX_PATH)&& (slash=wcsrchr(root,L'\\'))!=NULL){
   slash[1]=0;
   if(wcslen(root)+45<MAX_PATH&&supported_image()){
    /* This runs from the EXE's CRT entry, outside DllMain/loader lock. */
    read_config();normalized_command_line=HeapAlloc(GetProcessHeap(),0,length+1);
    if(normalized_command_line){
     normalize_vm(actual,normalized_command_line);
     if(config_valid&&window_features&&(requested_window_mode==2||center_windowed)){
      window_mode=requested_window_mode;if(!install_window_hooks())window_mode=0;
     }
    }
   }
  }
  InterlockedExchange(&window_initialized,2);
 }else while(window_initialized!=2)Sleep(0);
 return normalized_command_line?normalized_command_line:actual;
}
/* Bootstrap only: no User32, configuration, hashing, thread creation or waits
   under loader lock. The identified images have no EXE TLS callbacks. */
static void bootstrap_window_module(void){
 B *base=(B*)GetModuleHandleW(NULL);DWORD old,unused;IMAGE_NT_HEADERS *nt;volatile LONG *slot=(LONG*)0x84dbec;LONG previous;
 if(base!=(B*)0x400000||*(WORD*)base!=IMAGE_DOS_SIGNATURE)return;
 nt=(IMAGE_NT_HEADERS*)(base+((IMAGE_DOS_HEADER*)base)->e_lfanew);
 if(nt->Signature!=IMAGE_NT_SIGNATURE||nt->FileHeader.TimeDateStamp!=0x3c1625d7||nt->OptionalHeader.AddressOfEntryPoint!=0x31edf8||nt->OptionalHeader.SizeOfImage!=0x481000||nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_TLS].VirtualAddress)return;
 if(!normalize_vm(GetCommandLineA(),NULL))return;
 previous=*slot;if(previous!=(LONG)GetCommandLineA)return;original_command_line=(CmdLineFn)previous;
 if(!VirtualProtect((void*)slot,4,PAGE_READWRITE,&old))return;
 if(InterlockedCompareExchange(slot,(LONG)toolkit_command_line,previous)==previous){claimed[claim_count].address=(U)slot;claimed[claim_count++].length=4;}
 VirtualProtect((void*)slot,4,old,&unused);
}
