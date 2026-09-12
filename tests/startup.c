#include <assert.h>
#include "../runtime/loader.c"
static int forwarded;
static HANDLE WINAPI fake_open(LPCSTR a,DWORD b,DWORD c,LPSECURITY_ATTRIBUTES d,DWORD e,DWORD f,HANDLE g){assert(GetLastError()==123);forwarded++;SetLastError(2);return INVALID_HANDLE_VALUE;}
static WCHAR *__fastcall fake_string(U id){assert(id==308);return L"Original";}
static U __fastcall fake_begin(U mode){assert(mode==1);return 123;}
static void fake_end(void){}
static U __fastcall failed_begin(U mode){return 0;}
int main(void){WCHAR before[96];char long_path[850];DWORD id;char eta[96];
 InitializeCriticalSection(&startup_lock);startup_active=1;verbose_loading=1;startup_open_original=fake_open;startup_string_original=fake_string;
 SetLastError(123);assert(startup_open("TRAINS\\TRAINSET\\test.eng",1,2,NULL,3,4,NULL)==INVALID_HANDLE_VALUE);assert(GetLastError()==2&&forwarded==1);
 assert(wcsstr(startup_loading_string(308),L"test.eng"));
 memset(long_path,'x',sizeof(long_path));long_path[sizeof(long_path)-1]=0;startup_record("SCAN",long_path);assert(wcslen(startup_text)<96);
 wcscpy(before,startup_text);startup_finish();assert(!startup_active);assert(!wcscmp(startup_loading_string(308),L"Original"));id=startup_sequence;startup_record("OPEN","after-startup");assert(startup_sequence==id&&!wcscmp(before,startup_text));
 loading_begin_original=fake_begin;loading_end_original=fake_end;
 assert(loading_begin(1)==123&&startup_active&&activity_loading);startup_record("OPEN","ROUTES\\test\\tile.t");assert(wcsstr(startup_text,L"tile.t"));loading_end();assert(!startup_active&&!activity_loading);
 assert(loading_begin(1)==123&&startup_active);loading_end();assert(!startup_active);
 loading_begin_original=failed_begin;assert(!loading_begin(1)&&!startup_active&&!activity_loading);
 terrain_format(eta,sizeof(eta),0,0,0);assert(strstr(eta,"estimating")); terrain_format(eta,sizeof(eta),25,200000,3);assert(strstr(eta,"25.0%")&&strstr(eta,"~10m 00s")); terrain_format(eta,sizeof(eta),100,800000,8);assert(strstr(eta,"0m 00s")); terrain_format(eta,sizeof(eta),5,1000,1);assert(strstr(eta,"estimating"));
 puts("PASS startup API forwarding, LastError preservation, bounded display text and completion bypass.");return 0;
}
