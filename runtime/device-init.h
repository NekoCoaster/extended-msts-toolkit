/* Verified native Direct3D7 device-probe repair; no renderer replacement. */
typedef HRESULT (WINAPI *DeviceCreateFn)(void*,const GUID*,void*,void**);
static Hook device_hooks[3];
static HRESULT WINAPI device_create_checked(void *self,const GUID *kind,void *surface,void **out){
 DWORD saved=GetLastError(),id=0,start=GetTickCount(),error;HRESULT hr;char detail[180],guid[100];
 DeviceCreateFn create=(DeviceCreateFn)(*(void***)self)[4];
 if(startup_log){deep_guid(guid,kind);snprintf(detail,sizeof(detail),"%s; surface=%p",guid,surface);id=deep_begin("IDirect3D7::CreateDevice",detail);}
 SetLastError(saved);hr=create(self,kind,surface,out);error=GetLastError();
 if(startup_log){deep_end("IDirect3D7::CreateDevice HRESULT",id,start,(DWORD)hr,error);snprintf(detail,sizeof(detail),"returned device=%p; HRESULT=0x%08lx",out?*out:NULL,(DWORD)hr);startup_write("D3D DEVICE",detail,id);}
 if(hr==0&&(!out||!*out)){hr=E_FAIL;if(startup_log)startup_write("D3D REJECTED","Success without a device; returning failure to native cleanup",id);}
 SetLastError(error);return hr;
}
static void device_prepare(Hook *h,U stub){
 U i;static const U calls[]={0x7061c8,0x7062b4};
 for(i=0;i<2;i++){
  memset(&h[i],0,sizeof(Hook));h[i].address=calls[i];h[i].length=5;h[i].raw=1;
  memcpy(h[i].original,i?"\xff\x50\x10\x3b\xc6":"\xff\x52\x10\x3b\xc6",5);
  h[i].replacement[0]=0xe8;*(U*)(h[i].replacement+1)=stub-calls[i]-5;
 }
 memset(&h[2],0,sizeof(Hook));h[2].address=0x7061dd;h[2].length=6;h[2].raw=1;
 memcpy(h[2].original,"\x0f\x85\xdd\x00\x00\x00",6);
 /* Nonzero errors other than the existing pixel-format fallback must clean up. */
 memcpy(h[2].replacement,"\x0f\x85\x05\x01\x00\x00",6);
}
static B *device_stub(void){
 B *code=VirtualAlloc(NULL,64,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE),*p;DWORD old;int i;if(!code)return NULL;p=code;
 /* Copy four stdcall arguments; preserve the original CMP EAX,ESI flags on return. */
 for(i=0;i<4;i++){memcpy(p,"\xff\x74\x24\x10",4);p+=4;}
 branch(&p,0xe8,(void*)device_create_checked);memcpy(p,"\x3b\xc6\xc2\x10\x00",5);p+=5;
 if(!VirtualProtect(code,64,PAGE_EXECUTE_READ,&old)){VirtualFree(code,0,MEM_RELEASE);return NULL;}
 FlushInstructionCache(GetCurrentProcess(),code,p-code);return code;
}
static int install_device_hooks(void){
 B *code=device_stub();if(!code)return 0;device_prepare(device_hooks,(U)code);
 if(!prepare_hooks(device_hooks,3)||!install_hooks(device_hooks,3)){VirtualFree(code,0,MEM_RELEASE);return 0;}return 1;
}
