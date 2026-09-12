/* MIT. Give the legacy movie its own owned window, outside the game's render
   surface. No new process, codec installation, topmost flag or focus forcing. */
static HWND movie_window;
typedef BOOL (WINAPI *MovieShowFn)(HWND,int);
static BOOL WINAPI movie_show_chain(HWND h,int command){return (*(MovieShowFn*)MOVIE_ADDR(0x84df40))(h,command);}
static MovieShowFn movie_show_original=movie_show_chain;
static int movie_detach(HWND h){
 HWND main=*(HWND*)MOVIE_ADDR(0x82813a);LONG style;
 if(!separate_movie_window||!h||!main||h==main||!IsWindow(h)||!IsWindow(main))return 0;
 style=GetWindowLongA(h,GWL_STYLE);
 if(style&WS_CHILD){
  SetLastError(0);if(!SetParent(h,NULL)&&GetLastError())return 0;
  SetWindowLongA(h,GWL_STYLE,(style&~(WS_CHILD|WS_BORDER|WS_CAPTION|WS_THICKFRAME))|WS_POPUP);
 }else SetWindowLongA(h,GWL_STYLE,style&~(WS_BORDER|WS_CAPTION|WS_THICKFRAME));
 SetWindowLongA(h,GWL_HWNDPARENT,(LONG)main);
 SetWindowPos(h,NULL,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_NOZORDER|SWP_NOACTIVATE|SWP_FRAMECHANGED);
 movie_window=h;return 1;
}
static RECT movie_fit(RECT client,RECT source){
 LONG cw=client.right-client.left,ch=client.bottom-client.top,sw=source.right-source.left,sh=source.bottom-source.top,w,h;
 RECT result=client;
 if(cw<=0||ch<=0||sw<=0||sh<=0||cw>16384||ch>16384||sw>16384||sh>16384)return result;
 if(cw*sh>ch*sw){h=ch;w=ch*sw/sh;}else{w=cw;h=cw*sh/sw;}
 result.left=client.left+(cw-w)/2;result.top=client.top+(ch-h)/2;result.right=result.left+w;result.bottom=result.top+h;return result;
}
static BOOL WINAPI movie_show(HWND h,int command){
 HWND main=*(HWND*)MOVIE_ADDR(0x82813a);RECT owner,outer,client,source={0,0,0,0},dest;POINT origin={0,0};BOOL result;LONG put=-1;char log[240];
 if(!separate_movie_window||h!=movie_window)return movie_show_original(h,command);
 if(GetClientRect(main,&owner)&&GetWindowRect(h,&outer)&&ClientToScreen(main,&origin)){
  SetWindowPos(h,NULL,origin.x+(owner.right-(outer.right-outer.left))/2,origin.y+(owner.bottom-(outer.bottom-outer.top))/2,0,0,SWP_NOSIZE|SWP_NOZORDER|SWP_NOACTIVATE);
 }
 result=movie_show_original(h,command);
 if(GetClientRect(h,&client)&&client.right>0&&client.bottom>0){
  movie_send(h,0x48c,0,(LPARAM)&source); /* MCIWNDM_GET_SOURCE */
  dest=movie_fit(client,source);
  put=movie_send(h,0x48f,0,(LPARAM)&dest); /* MCIWNDM_PUT_DEST */
  InvalidateRect(h,NULL,TRUE);UpdateWindow(h);
  if(startup_log&&startup_active){
   snprintf(log,sizeof(log),"owned=%u; client=%ldx%ld; source=%ldx%ld; destination=%ld,%ld,%ld,%ld; put-result=%ld",GetWindow(h,GW_OWNER)==main,client.right,client.bottom,source.right-source.left,source.bottom-source.top,dest.left,dest.top,dest.right,dest.bottom,put);
   EnterCriticalSection(&startup_lock);startup_write("MOVIE WINDOW",log,0);LeaveCriticalSection(&startup_lock);
  }
 }
 return result;
}
