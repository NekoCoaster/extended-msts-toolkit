/* MSTS Derailment: x86 DirectInput forwarding loader. No hooks in DllMain. */
#include <windows.h>
#define PROV_RSA_AES 24
#define CRYPT_VERIFYCONTEXT 0xF0000000
#define CALG_SHA_256 0x800c
#define HP_HASHVAL 2
typedef ULONG_PTR HCRYPTPROV;
typedef ULONG_PTR HCRYPTHASH;
__declspec(dllimport) BOOL WINAPI CryptAcquireContextW(HCRYPTPROV*,LPCWSTR,LPCWSTR,DWORD,DWORD);
__declspec(dllimport) BOOL WINAPI CryptCreateHash(HCRYPTPROV,DWORD,ULONG_PTR,DWORD,HCRYPTHASH*);
__declspec(dllimport) BOOL WINAPI CryptHashData(HCRYPTHASH,const BYTE*,DWORD,DWORD);
__declspec(dllimport) BOOL WINAPI CryptGetHashParam(HCRYPTHASH,DWORD,BYTE*,DWORD*,DWORD);
__declspec(dllimport) BOOL WINAPI CryptDestroyHash(HCRYPTHASH);
__declspec(dllimport) BOOL WINAPI CryptReleaseContext(HCRYPTPROV,DWORD);
#include <string.h>
#include <wchar.h>

static HMODULE system_input;
static volatile LONG initialized;
static WCHAR root[MAX_PATH];

static int read_memory(DWORD address, void *out, SIZE_T size) {
    SIZE_T actual=0;
    return ReadProcessMemory(GetCurrentProcess(),(void*)address,out,size,&actual) && actual==size;
}
static int supported_image(void) {
    WCHAR path[MAX_PATH]; HANDLE file; DWORD size,actual,len=32; BYTE *b,digest[32];
    HCRYPTPROV provider=0; HCRYPTHASH hash=0; int ok=0; char hex[65]; int i;
    static const char digits[]="0123456789abcdef";
    if(GetModuleHandleW(NULL)!=(HMODULE)0x400000)return 0;
    if(!GetModuleFileNameW(NULL,path,MAX_PATH))return 0;
    file=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);
    if(file==INVALID_HANDLE_VALUE)return 0;
    size=GetFileSize(file,NULL);
    if(size!=4091953){CloseHandle(file);return 0;}
    b=HeapAlloc(GetProcessHeap(),0,size);
    if(!b){CloseHandle(file);return 0;}
    if(!ReadFile(file,b,size,&actual,NULL)||actual!=size)goto finish;
    /* Require migrated on-disk bytes. Features are controlled only in memory. */
    if(b[0x1862dc]!=0x74||b[0x1862dd]!=0x16)goto finish;
    if(memcmp(b+0x11c98c,"\x0f\x84\x55\x03\x00\x00",6))goto finish;
    b[0x116]&=0xdf;b[0x1862dc]=0x74;b[0x1862dd]=0x16;
    memcpy(b+0x11c98c,"\x0f\x84\x55\x03\x00\x00",6);
    if(!CryptAcquireContextW(&provider,NULL,NULL,PROV_RSA_AES,CRYPT_VERIFYCONTEXT))goto finish;
    if(!CryptCreateHash(provider,CALG_SHA_256,0,0,&hash))goto finish;
    if(!CryptHashData(hash,b,size,0)||!CryptGetHashParam(hash,HP_HASHVAL,digest,&len,0))goto finish;
    for(i=0;i<32;i++){hex[i*2]=digits[digest[i]>>4];hex[i*2+1]=digits[digest[i]&15];}hex[64]=0;
    ok=!strcmp(hex,"69218fce876298c684a2140c7d3925a452c47bb10037ffd8c491f65c5c0c6e7a") || !strcmp(hex,"1b041ecf4b2d2a7306218efa1d7418fd87dc21dc4b2d00056cb5749084fe55a4");
finish:
    if(hash)CryptDestroyHash(hash);if(provider)CryptReleaseContext(provider,0);
    HeapFree(GetProcessHeap(),0,b);CloseHandle(file);return ok;
}
#include "crawl.c"
#include "startup.h"
#include "device-init.h"
#include "cpu-preference.h"
#include "welcome.h"
#include "timing.h"
#include "cab.h"
#include "signal.h"
#include "audio.h"
#include "movie.h"
#include "hud.h"
#include "tracks.h"
#include "window.h"
static DWORD WINAPI delayed_start(void *unused) {
    DWORD train=0,previous=0,head=0,body=0,owner=0,control=0; float now=0,first=0; int stable=0;
    WCHAR path[MAX_PATH];
    if(has_toolset(GetCommandLineA()))return 0;
    if(wcslen(root)+45>=MAX_PATH||!supported_image())return 0;
    read_config();
    if(!config_valid)return 0;
    if(!prevent_end&&!unlock_cameras&&!crawl_requested&&!cab_needles)return 0;
    /* Require five seconds of a valid driving scene with advancing simulation time.
       A paused load waits for resume; startup/menu configuration is never instrumented. */
    for(;;){
        Sleep(250);
        if(!read_memory(0x7c2ac0,&train,4)||!train||!read_memory(train+0x6a,&head,4)||!head||
           !read_memory(head+0x5c,&body,4)||!body||!read_memory(body+0x11d,&owner,4)||owner!=head||
           !read_memory(0x7b6440,&control,4)||!control||!read_memory(0x80acd4,&now,4)){
            stable=0;previous=0;continue;
        }
        if(train!=previous){previous=train;first=now;stable=0;}
        if(++stable>=20 && now>first+0.25f)break;
    }
    if(wcslen(root)+45>=MAX_PATH)return 0;
    if(!install_cab_hooks()){fail("Cab needle hook installation failed");write_status();return 0;}
    if(!start_native()){fail("Native hook installation failed");write_status();return 0;}
    /* No diagnostic worker or periodic file access when logging is disabled. */
    if(write_status_json)for(;;){Sleep(1000);write_status();}
    return 0;
}
static FARPROC resolve(const char *name) {
    WCHAR path[MAX_PATH]; HANDLE worker; WCHAR *slash;
    if(InterlockedCompareExchange(&initialized,1,0)==0){
        GetSystemDirectoryW(path,MAX_PATH);wcscat(path,L"\\dinput.dll");
        system_input=LoadLibraryW(path);
        if(GetModuleFileNameW(NULL,root,MAX_PATH)){
            slash=wcsrchr(root,L'\\');if(slash){slash[1]=0;worker=CreateThread(NULL,0,delayed_start,NULL,0,NULL);if(worker)CloseHandle(worker);}
        }
        InterlockedExchange(&initialized,2);
    }else while(initialized!=2)Sleep(0);
    return system_input?GetProcAddress(system_input,name):NULL;
}
typedef HRESULT (WINAPI *CreateFn)(HINSTANCE,DWORD,void**,void*);
typedef HRESULT (WINAPI *CreateExFn)(HINSTANCE,DWORD,const void*,void**,void*);
typedef HRESULT (WINAPI *ClassFn)(const void*,const void*,void**);
typedef HRESULT (WINAPI *VoidFn)(void);
__declspec(dllexport) HRESULT WINAPI DirectInputCreateA(HINSTANCE a,DWORD b,void** c,void* d){CreateFn f=(CreateFn)resolve("DirectInputCreateA");return f?f(a,b,c,d):E_FAIL;}
__declspec(dllexport) HRESULT WINAPI DirectInputCreateW(HINSTANCE a,DWORD b,void** c,void* d){CreateFn f=(CreateFn)resolve("DirectInputCreateW");return f?f(a,b,c,d):E_FAIL;}
__declspec(dllexport) HRESULT WINAPI DirectInputCreateEx(HINSTANCE a,DWORD b,const void* c,void** d,void* e){CreateExFn f=(CreateExFn)resolve("DirectInputCreateEx");return f?f(a,b,c,d,e):E_FAIL;}
__declspec(dllexport) HRESULT WINAPI DllGetClassObject(const void* a,const void* b,void** c){ClassFn f=(ClassFn)resolve("DllGetClassObject");return f?f(a,b,c):E_FAIL;}
__declspec(dllexport) HRESULT WINAPI DllCanUnloadNow(void){VoidFn f=(VoidFn)resolve("DllCanUnloadNow");return f?f():S_FALSE;}
__declspec(dllexport) HRESULT WINAPI DllRegisterServer(void){VoidFn f=(VoidFn)resolve("DllRegisterServer");return f?f():E_FAIL;}
__declspec(dllexport) HRESULT WINAPI DllUnregisterServer(void){VoidFn f=(VoidFn)resolve("DllUnregisterServer");return f?f():E_FAIL;}
BOOL WINAPI DllMain(HINSTANCE instance,DWORD reason,LPVOID reserved){if(reason==DLL_PROCESS_ATTACH)bootstrap_window_module();return TRUE;}
