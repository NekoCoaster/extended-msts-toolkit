/* Run the original native probe from local fixtures with fake COM devices. */
#include <assert.h>
#include "../runtime/loader.c"
static GUID requested_kind;
static int scenario,creates,enums,releases,surfaces;static HRESULT last_hr;
static void *draw_v[7],*surface_v[37],*d3d_v[5],*device_v[5];
static void **draw=draw_v,**surface=surface_v,**d3d=d3d_v,**device=device_v;
static void *native_draw=&draw;
static int notices,owner_queries;
static int WINAPI notice(HWND w,LPCSTR text,LPCSTR title,UINT flags){assert(strstr(text,"0x")&&strstr(text,"normal error handling"));notices++;SetLastError(999);return IDOK;}
static HRESULT WINAPI owner(void *self,void **out){owner_queries++;*out=NULL;return E_NOINTERFACE;}
static ULONG WINAPI release(void *self){releases++;return 0;}
static HRESULT WINAPI description(void *self,B *desc){*(U*)(desc+84)=16;return scenario==7?E_FAIL:0;}
static HRESULT WINAPI create_surface(void *self,void *desc,void **out,void *outer){surfaces++;if(scenario==6||(scenario==11&&surfaces>=2)||(scenario==12&&surfaces==2))return E_FAIL;*out=&surface;return 0;}
static HRESULT WINAPI create_device(void *self,const GUID *kind,void *target,void **out){
 assert(self==&d3d&&target==&surface&&kind==&requested_kind);creates++;*out=NULL;
 if(scenario>=9&&scenario<=12&&creates==1)return (HRESULT)0x88760082;
 if(scenario==10)return (HRESULT)0x88760082;
 if(scenario==13){*out=&device;return (HRESULT)0x88760082;}
 if(scenario==1)return E_FAIL;
 if((scenario==2||scenario==3)&&creates==1)return (HRESULT)0x88760091;
 if(scenario==3)return E_FAIL;
 if(scenario==4)return 0;
 *out=&device;return scenario==5?E_FAIL:0;
}
static HRESULT WINAPI enumerate(void *self,void *callback,void *context){assert(self==&device&&callback==(void*)0x5678&&context==(void*)0x9abc);enums++;return scenario==8?E_FAIL:0;}
static B *load_probe(const char *path){
 FILE *f=fopen(path,"rb");B *file,*code,*stub;long bytes;U pe,table,i,j,rva,raw,size;DWORD old;Hook h[6];assert(f);
 fseek(f,0,SEEK_END);bytes=ftell(f);rewind(f);file=malloc(bytes);assert(file&&fread(file,1,bytes,f)==bytes);fclose(f);code=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);assert(code);
 pe=ru(file+60);table=pe+24+*(WORD*)(file+pe+20);
 for(i=0;i<*(WORD*)(file+pe+6);i++){B *s=file+table+40*i;rva=ru(s+12);size=ru(s+16);raw=ru(s+20);if(rva<=0x3060b0&&0x30632d<=rva+size){memcpy(code,file+raw+0x3060b0-rva,0x27d);break;}}
 assert(i<*(WORD*)(file+pe+6));free(file);assert(!memcmp(code,"\x81\xec\x8c\x04\0\0",6)&&code[0x27a]==0xc2);
 /* Remap only the two absolute game globals; all control flow is native. */
 for(i=0;i<0x27a;i++){U value=ru(code+i);if(value==0x8293b8){*(U*)(code+i)=(U)&native_draw;i+=3;}else if(value==0x829a00){*(U*)(code+i)=(U)&last_hr;i+=3;}}
 stub=device_stub();assert(stub);device_prepare(h,(U)stub);
 for(j=0;j<6;j++){U original=h[j].address;h[j].address=(U)code+original-0x7060b0;if(j!=2)*(U*)(h[j].replacement+1)=(U)stub+(j>=3?64:j==1?96:0)-h[j].address-5;}
 assert(prepare_hooks(h,6)&&install_hooks(h,6));assert(VirtualProtect(code,4096,PAGE_EXECUTE_READ,&old));FlushInstructionCache(GetCurrentProcess(),code,4096);return code;
}
int main(int argc,char **argv){
 typedef U (__fastcall *Probe)(void*,const GUID*,void*,void*);Probe probe;int i,logging;assert(argc==2);
 device_message=notice;surface_v[36]=owner;draw_v[6]=create_surface;surface_v[2]=release;surface_v[22]=description;d3d_v[4]=create_device;device_v[2]=release;device_v[4]=enumerate;
 probe=(Probe)load_probe(argv[1]);
 for(logging=0;logging<2;logging++)for(i=0;i<14;i++){U result;startup_log=logging;scenario=i;device_warned=notices=owner_queries=0;creates=enums=releases=surfaces=0;result=probe(&d3d,&requested_kind,(void*)0x5678,(void*)0x9abc);
 assert(result==(i==0||i==2||i==9||i==12));assert(enums==(i==0||i==2||i==8||i==9||i==12));if(i==2||i==3)assert(creates==2&&surfaces==2);if(i==1||i==4||i==5)assert(creates==1&&enums==0);if(i==6||i==7)assert(creates==0);assert(releases>0||i==6);assert(notices==(i==1||i==3||i==4||i==5||i==10||i==13));assert(owner_queries==(logging?creates:0));
 if(i==9||i==10)assert(creates==2&&surfaces==2&&releases== (i==9?3:2));
 if(i==11)assert(creates==1&&surfaces==3&&releases==1);
 if(i==12)assert(creates==2&&surfaces==3&&releases==3);
 if(i==13)assert(creates==1&&surfaces==1&&releases==2);
 }
 puts("PASS original native device probe: success, creation failures, null-success, pixel/INVALIDOBJECT fallback, bounded retry, surface failures, enumeration failure and cleanup; patched stdcall/flags exercised.");return 0;
}
