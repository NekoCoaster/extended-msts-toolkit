#include <assert.h>
#include "../runtime/loader.c"
static void *draw_v[7],*surf_v[37];static void **draw=draw_v,**surf=surf_v;
static int released,queried,notices;static DWORD desc[31]={124,0x1007,16,16};
static HRESULT WINAPI create(void *self,void *d,void **out,void *outer){assert(self==&draw&&d==desc&&!outer&&GetLastError()==123);*out=&surf;SetLastError(456);return S_OK;}
static HRESULT WINAPI describe(void *self,DWORD *d){assert(self==&surf&&d[0]==124);memcpy(d,desc,sizeof(desc));SetLastError(777);return S_OK;}
static HRESULT WINAPI owner(void *self,void **out){assert(self==&surf);queried++;*out=&draw;return S_OK;}
static ULONG WINAPI release(void *self){assert(self==&draw);released++;return 1;}
static HRESULT WINAPI device_fail(void *self,const GUID *kind,void *surface,void **out){assert(GetLastError()==321);*out=NULL;SetLastError(654);return (HRESULT)0x88760082;}
static int WINAPI notice(HWND w,LPCSTR text,LPCSTR title,UINT flags){assert(strstr(text,"0x88760082")&&strstr(text,"normal error handling"));notices++;SetLastError(888);return IDOK;}
int main(int argc,char **argv){
 WCHAR path[MAX_PATH];char data[20000]={0};DWORD n;HANDLE f;void *out=NULL,*dv[5]={0},**d3d=dv;
 assert(argc==2);mbstowcs(runtime_dir,argv[1],MAX_PATH);wcscat(runtime_dir,L"\\");CreateDirectoryW(runtime_dir,NULL);InitializeCriticalSection(&startup_lock);startup_lock_ready=1;startup_log=1;max_log_bytes=65536;assert(startup_open_log());
 draw_v[6]=create;draw_v[2]=release;surf_v[22]=describe;surf_v[36]=owner;dv[4]=device_fail;device_message=notice;
 SetLastError(123);assert(device_surface_create(&draw,desc,&out,NULL)==S_OK&&out==&surf&&GetLastError()==456);
 SetLastError(321);assert(device_create_checked(&d3d,NULL,&surf,&out)==(HRESULT)0x88760082&&!out&&GetLastError()==654);
 SetLastError(321);assert(device_create_checked(&d3d,NULL,&surf,&out)==(HRESULT)0x88760082&&GetLastError()==654);
 assert(queried==2&&released==2&&notices==1);
 CloseHandle(startup_file);startup_file=INVALID_HANDLE_VALUE;startup_log_name(path,0);f=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);assert(f!=INVALID_HANDLE_VALUE);assert(ReadFile(f,data,sizeof(data)-1,&n,NULL));CloseHandle(f);
 assert(strstr(data,"SURFACE REQUEST")&&strstr(data,"SURFACE ACTUAL")&&strstr(data,"width=16; height=16")&&strstr(data,"SURFACE OWNER END")&&strstr(data,"D3D FAILURE NOTICE")&&strstr(data,"0x88760082"));
 puts("PASS surface diagnostics: file records, owner reference balance, API arguments/results/LastError and one-time failure notice.");return 0;
}
