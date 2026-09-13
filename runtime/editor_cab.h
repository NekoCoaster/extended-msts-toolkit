/* Present the native 640x480 cab canvas with a centered proportional fit.
   Scaling the completed canvas keeps artwork, needles and selection outlines
   in the same coordinate system. Native window clipping preserves tools. */
static LPARAM editor_cab_mouse(HWND h,LPARAM l){
 RECT c;EditorRect fit;int x=(short)LOWORD(l),y=(short)HIWORD(l);
 if(!GetClientRect(h,&c)||c.right<1||c.bottom<1)return l;
 fit=editor_cab_fit(c.right,c.bottom);
 x=editor_cab_coordinate(x,fit.left,fit.right-fit.left,640);
 y=editor_cab_coordinate(y,fit.top,fit.bottom-fit.top,480);
 return MAKELPARAM((short)x,(short)y);
}
static int editor_cab_draw(void){
 typedef HRESULT (WINAPI *SurfaceBlt)(void*,RECT*,void*,RECT*,DWORD,void*);
 typedef HRESULT (WINAPI *SurfaceClipper)(void*,void*);
 void *src=*(void**)0x80ad2c,*dst=*(void**)0x80ad28;HWND h=*(HWND*)0x82813a;
 RECT client,bar,dest,source={0,0,640,480};EditorRect fit;POINT origin={0,0};DWORD fx[25];SurfaceBlt blt;
 if(!src||!dst||!h||IsIconic(h)||!GetClientRect(h,&client)||client.right<1||client.bottom<1)return 0;
 if(!ClientToScreen(h,&origin))return 0;
 if(((SurfaceClipper)(*(void***)dst)[28])(dst,*(void**)0x80ad30)<0)return 0;
 blt=(SurfaceBlt)(*(void***)dst)[5];memset(fx,0,sizeof(fx));fx[0]=sizeof(fx);fx[20]=0xffffffff;
 fit=editor_cab_fit(client.right,client.bottom);
 dest=*(RECT*)&fit;OffsetRect(&dest,origin.x,origin.y);OffsetRect(&client,origin.x,origin.y);
 bar=client;bar.right=dest.left;if(bar.right>bar.left&&blt(dst,&bar,NULL,NULL,0x1000400,fx)<0)return 0;
 bar=client;bar.left=dest.right;if(bar.right>bar.left&&blt(dst,&bar,NULL,NULL,0x1000400,fx)<0)return 0;
 bar=dest;bar.top=client.top;bar.bottom=dest.top;if(bar.bottom>bar.top&&blt(dst,&bar,NULL,NULL,0x1000400,fx)<0)return 0;
 bar=dest;bar.top=dest.bottom;bar.bottom=client.bottom;if(bar.bottom>bar.top&&blt(dst,&bar,NULL,NULL,0x1000400,fx)<0)return 0;
 return blt(dst,&dest,src,&source,0x1000000,NULL)>=0;
}
static void editor_cab_present(void){
 if(editor_windows&&editor_mode()==4&&editor_cab_draw())return;
 ((void(*)(void))0x6b6390)();
}
static void editor_cab_ui_present(void){
 if(editor_windows&&editor_mode()==4&&editor_cab_draw())return;
 ((void(*)(void))0x64653f)();
}
