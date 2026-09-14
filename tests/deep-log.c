#include <assert.h>
#include "../runtime/loader.c"
static int calls;
static HRESULT WINAPI sound(GUID *g,void **out,void *outer){assert(!g&&!outer&&GetLastError()==123);*out=(void*)456;calls++;SetLastError(87);return (HRESULT)0x88780078;}
static HRESULT WINAPI draw(GUID *g,void **out,const GUID *iid,void *outer){assert(!g&&!iid&&!outer&&GetLastError()==123);*out=(void*)789;calls++;SetLastError(5);return E_FAIL;}
static HMODULE WINAPI library(LPCSTR name){assert(!strcmp(name,"missing.dll")&&GetLastError()==123);calls++;SetLastError(126);return NULL;}
static int WINAPI message(HWND w,LPCSTR text,LPCSTR title,UINT flags){assert(!w&&!flags&&!strcmp(text,"failure")&&!strcmp(title,"MSTS")&&GetLastError()==123);calls++;SetLastError(99);return IDOK;}
static U __fastcall begin(U mode){return mode;}
static void end(void){}
int main(int argc,char **argv){
 WCHAR path[MAX_PATH];char data[16000]={0};DWORD n;HANDLE f;void *out=NULL;EXCEPTION_RECORD record;EXCEPTION_POINTERS exception;
 assert(argc==2);mbstowcs(runtime_dir,argv[1],MAX_PATH);wcscat(runtime_dir,L"\\");CreateDirectoryW(runtime_dir,NULL);InitializeCriticalSection(&startup_lock);startup_lock_ready=1;startup_log=1;max_log_bytes=65536;assert(startup_open_log());
 deep_sound_original=sound;deep_draw_original=draw;deep_library_original=library;deep_message_original=message;
 SetLastError(123);assert(deep_sound(NULL,&out,NULL)==(HRESULT)0x88780078&&out==(void*)456&&GetLastError()==87);
 SetLastError(123);assert(deep_draw(NULL,&out,NULL,NULL)==E_FAIL&&out==(void*)789&&GetLastError()==5);
 SetLastError(123);assert(!deep_library("missing.dll")&&GetLastError()==126);
 SetLastError(123);assert(deep_message(NULL,"failure","MSTS",0)==IDOK&&GetLastError()==99&&calls==4);
 startup_write("SANITIZE","first\nsecond\rthird",0);
 startup_active=1;startup_finish();assert(!startup_active&&startup_file!=INVALID_HANDLE_VALUE);
 verbose_loading=0;loading_begin_original=begin;loading_end_original=end;
 assert(loading_begin(1)==1&&startup_active&&activity_loading);startup_record("OPEN","test.eng");loading_end();assert(!startup_active&&!activity_loading&&startup_file!=INVALID_HANDLE_VALUE);
 assert(!loading_begin(0)&&!startup_active&&!activity_loading);
 memset(&record,0,sizeof(record));record.ExceptionCode=0xc0000005;record.ExceptionAddress=(void*)0x12345678;exception.ExceptionRecord=&record;exception.ContextRecord=NULL;
 SetLastError(234);assert(deep_exception(&exception)==EXCEPTION_CONTINUE_SEARCH&&GetLastError()==234);
 CloseHandle(startup_file);startup_file=INVALID_HANDLE_VALUE;startup_log_name(path,0);f=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);assert(f!=INVALID_HANDLE_VALUE);assert(ReadFile(f,data,sizeof(data)-1,&n,NULL));CloseHandle(f);
 assert(data[4]=='-'&&data[7]=='-'&&data[10]==' '&&data[13]=='-'&&data[16]=='-'&&data[19]=='.'&&data[23]==':');
 assert(strstr(data,"DirectSoundCreate HRESULT; result=0x88780078")&&strstr(data,"duration_ms=")&&strstr(data,"tid="));
 assert(strstr(data,"first second third"));
 assert(strstr(data,"ACTIVITY BEGIN")&&strstr(data,"ACTIVITY COMPLETE")&&strstr(data,"ACTIVITY FAILED")&&strstr(data,"EXCEPTION OBSERVED"));
 /* Production transaction installs exact IAT cells, then rejects overlap. */
 {U slots[4];U *page=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);int i;assert(page);
 for(i=0;i<4;i++)slots[i]=(U)&page[i];
 page[0]=(U)sound;page[1]=(U)draw;page[2]=(U)library;page[3]=(U)message;
 deep_prepare_slots(slots);assert(prepare_hooks(deep_hooks,4)&&install_hooks(deep_hooks,4)&&claim_count==4);
 assert(page[0]==(U)deep_sound&&page[1]==(U)deep_draw&&page[2]==(U)deep_library&&page[3]==(U)deep_message);}
 assert(!prepare_hooks(deep_hooks,4));
 puts("PASS deep log timestamps, API forwarding/LastError, log-only activity lifecycle, exception pass-through and shared IAT transaction.");return 0;
}
