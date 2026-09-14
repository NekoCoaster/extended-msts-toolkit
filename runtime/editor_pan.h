/* The editor's free camera already rotates without angle clamps. Its virtual
   mouse, however, clips accumulated coordinates to the original screen rect.
   Retain that pointer for native UI consumers, and collect relative movement
   separately for the camera while its native pan button is held. */
typedef int (__fastcall *EditorPointerMove)(int*,int,int,int);
static EditorPointerMove editor_pointer_original;
static double editor_pan_x,editor_pan_y;
static int editor_route_focus(void){
 HWND h=*(HWND*)0x82813a;GUITHREADINFO info;
 if(editor_mode()!=1||!h||GetForegroundWindow()!=h)return 0;
 memset(&info,0,sizeof(info));info.cbSize=sizeof(info);
 return GetGUIThreadInfo(GetWindowThreadProcessId(h,NULL),&info)&&info.hwndFocus==h&&!(info.flags&0x1c);
}
static void editor_pan_reset(void){editor_pan_x=editor_pan_y=0;}
static int __fastcall editor_pointer_move(int *pointer,int kind,int dx,int dy){
 int result,active=*(U*)0x7bac74;
 int route=editor_unlimited_pan&&editor_mode()==1&&pointer==*(int**)0x7bac60;
 /* Same per-axis integer sensitivity as the native virtual pointer. */
 double x=0,y=0;
 if(route&&!kind&&active){x=(double)dx*pointer[12];y=(double)dy*pointer[13];}
 result=editor_pointer_original(pointer,kind,dx,dy);
 if(route&&!kind&&active&&*(U*)0x7bac74){editor_pan_x+=x;editor_pan_y+=y;}
 else if(route&&active!=*(U*)0x7bac74)editor_pan_reset();
 return result;
}
static int editor_pan_delta(double value){
 return value>2147483647.0?2147483647:value< -2147483647.0?-2147483647:(int)value;
}
static void editor_pan_apply(void){
 if(editor_unlimited_pan&&editor_mode()==1){
  int active=*(U*)0x7bac74&&editor_route_focus();
  *(int*)0x7c2a64=active?editor_pan_delta(editor_pan_x):0;
  *(int*)0x7c2a68=active?editor_pan_delta(editor_pan_y):0;
 }
 editor_pan_reset();
}
