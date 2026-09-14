/* Verified native Direct3D7 device-probe repair; no renderer replacement. */
typedef HRESULT (WINAPI *DeviceCreateFn)(void*,const GUID*,void*,void**);
typedef HRESULT (WINAPI *SurfaceCreateFn)(void*,void*,void**,void*);
static int (WINAPI *device_message)(HWND,LPCSTR,LPCSTR,UINT)=MessageBoxA;
static LONG device_warned;
static void device_surface_desc(const char *event,void *desc,DWORD id){
 DWORD d[31];char text[400];
 if(!desc||!read_memory((U)desc,d,sizeof(d))){startup_write(event,"Descriptor unavailable",id);return;}
 snprintf(text,sizeof(text),"size=%lu; flags=0x%08lx; width=%lu; height=%lu; pitch=%ld; caps=0x%08lx/0x%08lx; pixelFlags=0x%08lx; bits=%lu; RGB masks=%08lx/%08lx/%08lx; fields meaningful only when corresponding flags are set",d[0],d[1],d[3],d[2],d[4],d[26],d[27],d[19],d[21],d[22],d[23],d[24]);
 startup_write(event,text,id);
}
static HRESULT WINAPI device_surface_create(void *self,void *desc,void **out,void *outer){
 DWORD saved=GetLastError(),id=0,start=GetTickCount(),error;HRESULT hr;char text[100];
 SurfaceCreateFn create=(SurfaceCreateFn)(*(void***)self)[6];
 if(startup_log){snprintf(text,sizeof(text),"DirectDraw=%p",self);id=deep_begin("IDirectDraw7::CreateSurface",text);device_surface_desc("SURFACE REQUEST",desc,id);}
 SetLastError(saved);hr=create(self,desc,out,outer);error=GetLastError();
 if(startup_log){deep_end("IDirectDraw7::CreateSurface HRESULT",id,start,(DWORD)hr,error);snprintf(text,sizeof(text),"returned surface=%p",out?*out:NULL);startup_write("SURFACE RESULT",text,id);}
 SetLastError(error);return hr;
}
static void device_surface_details(void *surface,DWORD id){
 typedef HRESULT (WINAPI *Describe)(void*,void*);
 typedef HRESULT (WINAPI *Owner)(void*,void**);
 typedef ULONG (WINAPI *Release)(void*);
 DWORD d[31]={124};HRESULT hr;void *owner=NULL;char text[140];
 if(!surface){startup_write("SURFACE INSPECT","Null surface",id);return;}
 startup_write("SURFACE INSPECT BEGIN","GetSurfaceDesc",id);
 hr=((Describe)(*(void***)surface)[22])(surface,d);
 snprintf(text,sizeof(text),"GetSurfaceDesc HRESULT=0x%08lx",(DWORD)hr);startup_write("SURFACE INSPECT END",text,id);
 if(hr==0)device_surface_desc("SURFACE ACTUAL",d,id);
 startup_write("SURFACE OWNER BEGIN","GetDDInterface",id);
 hr=((Owner)(*(void***)surface)[36])(surface,&owner);
 snprintf(text,sizeof(text),"GetDDInterface HRESULT=0x%08lx; DirectDraw=%p; interface addresses alone do not prove COM identity",(DWORD)hr,owner);startup_write("SURFACE OWNER END",text,id);
 if(hr==0&&owner)((Release)(*(void***)owner)[2])(owner);
}
static Hook device_hooks[6];
static HRESULT device_create_attempt(void *self,const GUID *kind,void *surface,void **out,int primary){
 DWORD saved=GetLastError(),id=0,start=GetTickCount(),error;HRESULT hr;char detail[400],guid[100];
 DeviceCreateFn create=(DeviceCreateFn)(*(void***)self)[4];
 if(startup_log){deep_guid(guid,kind);snprintf(detail,sizeof(detail),"%s; surface=%p",guid,surface);id=deep_begin("IDirect3D7::CreateDevice",detail);device_surface_details(surface,id);}
 SetLastError(saved);hr=create(self,kind,surface,out);error=GetLastError();
 if(startup_log){deep_end("IDirect3D7::CreateDevice HRESULT",id,start,(DWORD)hr,error);snprintf(detail,sizeof(detail),"returned device=%p; HRESULT=0x%08lx",out?*out:NULL,(DWORD)hr);startup_write("D3D DEVICE",detail,id);}
 if(hr==0&&(!out||!*out)){hr=E_FAIL;if(startup_log)startup_write("D3D REJECTED","Success without a device; returning failure to native cleanup",id);}
 /* Only the first native probe call can request the existing off-screen retry.
    Keep the actual HRESULT above; translate only the private branch signal. */
 if(primary&&(DWORD)hr==0x88760082&&out&&!*out){
  if(startup_log)startup_write("D3D PROBE RETRY","Primary probe returned DDERR_INVALIDOBJECT with no device; entering native 16x16 off-screen fallback; branch signal=0x88760091",id);
  hr=(HRESULT)0x88760091;
 }
 /* Pixel-format failure can still recover via the native retry. Do not interrupt it. */
 if(FAILED(hr)&&(DWORD)hr!=0x88760091&&!InterlockedCompareExchange(&device_warned,1,0)){
  snprintf(detail,sizeof(detail),"MSTS could not create a 3D device (error 0x%08lx).\n\nGraphics compatibility or surface setup may be responsible. Enable deep logging in NEMT and save NEMT/startup.log after this run.\n\nMSTS will continue its normal error handling.",(DWORD)hr);
  if(startup_log)startup_write("D3D FAILURE NOTICE", "Displaying graphics initialization warning",id);
  device_message(NULL,detail,"NEMT - Graphics initialization",MB_OK|MB_ICONERROR|MB_SETFOREGROUND);
 }
 SetLastError(error);return hr;
}
static HRESULT WINAPI device_create_checked(void *self,const GUID *kind,void *surface,void **out){return device_create_attempt(self,kind,surface,out,0);}
static HRESULT WINAPI device_create_primary(void *self,const GUID *kind,void *surface,void **out){return device_create_attempt(self,kind,surface,out,1);}
static void device_prepare(Hook *h,U stub){
 U i;static const U calls[]={0x7061c8,0x7062b4};static const U surfaces[]={0x70610b,0x70625e,0x70629a};
 for(i=0;i<2;i++){
  memset(&h[i],0,sizeof(Hook));h[i].address=calls[i];h[i].length=5;h[i].raw=1;
  memcpy(h[i].original,i?"\xff\x50\x10\x3b\xc6":"\xff\x52\x10\x3b\xc6",5);
  h[i].replacement[0]=0xe8;*(U*)(h[i].replacement+1)=stub+(i?96:0)-calls[i]-5;
 }
 memset(&h[2],0,sizeof(Hook));h[2].address=0x7061dd;h[2].length=6;h[2].raw=1;
 memcpy(h[2].original,"\x0f\x85\xdd\x00\x00\x00",6);
 /* Nonzero errors other than the existing pixel-format fallback must clean up. */
 memcpy(h[2].replacement,"\x0f\x85\x05\x01\x00\x00",6);
 for(i=3;i<6;i++){
  memset(&h[i],0,sizeof(Hook));h[i].address=surfaces[i-3];h[i].length=5;h[i].raw=1;
  memcpy(h[i].original,"\xff\x51\x18\x3b\xc6",5);h[i].replacement[0]=0xe8;*(U*)(h[i].replacement+1)=stub+64-h[i].address-5;
 }
}
static B *device_stub(void){
 B *code=VirtualAlloc(NULL,128,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE),*p;DWORD old;int i;if(!code)return NULL;p=code;
 /* Copy four stdcall arguments; preserve the original CMP EAX,ESI flags on return. */
 for(i=0;i<4;i++){memcpy(p,"\xff\x74\x24\x10",4);p+=4;}
 branch(&p,0xe8,(void*)device_create_primary);memcpy(p,"\x3b\xc6\xc2\x10\x00",5);p+=5;
 p=code+64;
 for(i=0;i<4;i++){memcpy(p,"\xff\x74\x24\x10",4);p+=4;}
 branch(&p,0xe8,(void*)device_surface_create);memcpy(p,"\x3b\xc6\xc2\x10\x00",5);p+=5;
 p=code+96;
 for(i=0;i<4;i++){memcpy(p,"\xff\x74\x24\x10",4);p+=4;}
 branch(&p,0xe8,(void*)device_create_checked);memcpy(p,"\x3b\xc6\xc2\x10\x00",5);p+=5;
 if(!VirtualProtect(code,128,PAGE_EXECUTE_READ,&old)){VirtualFree(code,0,MEM_RELEASE);return NULL;}
 FlushInstructionCache(GetCurrentProcess(),code,p-code);return code;
}
static int install_device_hooks(void){
 B *code=device_stub();if(!code)return 0;device_prepare(device_hooks,(U)code);
 if(!prepare_hooks(device_hooks,6)||!install_hooks(device_hooks,6)){VirtualFree(code,0,MEM_RELEASE);return 0;}return 1;
}
