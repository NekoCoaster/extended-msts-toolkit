/* Optional host experiment, outside normal CI. Creates real off-screen D3D7
 * devices in this process only; no display-mode or on-disk changes. */
#include "../runtime/loader.c"
typedef HRESULT (WINAPI *DrawCreate)(GUID*,void**,const GUID*,void*);
typedef HRESULT (WINAPI *Query)(void*,const GUID*,void**);
typedef HRESULT (WINAPI *Cooperate)(void*,HWND,DWORD);
typedef ULONG (WINAPI *ComRelease)(void*);
static const GUID draw7={0x15e65ec0,0x3b9c,0x11d2,{0xb9,0x2f,0,0x60,0x97,0x97,0xea,0x5b}};
static const GUID d3d7={0xf5049e77,0x4861,0x11d2,{0xa4,7,0,0xa0,0xc9,6,0x29,0xa8}};
static const GUID hal={0x84e63de0,0x46aa,0x11cf,{0x81,0x6f,0,0,0xc0,0x20,0x15,0x6e}};
static void release(void *p){if(p)((ComRelease)(*(void***)p)[2])(p);}
static HRESULT probe(void *draw,void *d3d,int width,int height){
 DWORD desc[31]={124};void *surface=NULL,*device=NULL;HRESULT hr;
 desc[1]=0x1007;desc[2]=height;desc[3]=width;desc[18]=32;desc[19]=0x40;
 desc[21]=32;desc[22]=0xff0000;desc[23]=0xff00;desc[24]=0xff;desc[26]=0x2040;
 hr=((SurfaceCreateFn)(*(void***)draw)[6])(draw,desc,&surface,NULL);
 printf("%dx%d surface=%08lx",width,height,(DWORD)hr);
 if(hr==0){hr=((DeviceCreateFn)(*(void***)d3d)[4])(d3d,&hal,surface,&device);printf(" device=%08lx",(DWORD)hr);}
 puts("");release(device);release(surface);return hr;
}
int main(void){
 WCHAR path[MAX_PATH];HMODULE module;DrawCreate create;void *draw=NULL,*d3d=NULL;HRESULT low,before,after;
 GetSystemDirectoryW(path,MAX_PATH);wcscat(path,L"\\ddraw.dll");module=LoadLibraryW(path);if(!module)return 2;
 create=(DrawCreate)GetProcAddress(module,"DirectDrawCreateEx");if(!create)return 2;
 if(create(NULL,&draw,&draw7,NULL)!=0)return 2;
 if(((Cooperate)(*(void***)draw)[20])(draw,NULL,8)!=0)return 2;
 if(((Query)(*(void***)draw)[0])(draw,&d3d7,&d3d)!=0)return 2;
 low=probe(draw,d3d,640,480);before=probe(draw,d3d,2560,1440);
 GetModuleFileNameW(NULL,root,MAX_PATH);wcsrchr(root,L'\\')[1]=0;high_resolution=1;
 if(!apply_high_resolution()){puts(high_resolution_state);return 2;}puts(high_resolution_state);
 after=probe(draw,d3d,2560,1440);release(d3d);release(draw);
 if(low!=0 || before==0 || after!=0){puts("INCONCLUSIVE: host did not reproduce a repaired high-resolution device failure.");return 2;}
 puts("PASS host D3D7: low resolution succeeded; 2560x1440 failed before and succeeded after the integrated fix.");return 0;
}
