#include <assert.h>
#include "../runtime/loader.c"
static void contents(const WCHAR *path,const char *expected){char b[64]={0};DWORD n;HANDLE f=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);assert(f!=INVALID_HANDLE_VALUE);assert(ReadFile(f,b,63,&n,NULL));CloseHandle(f);assert(!strcmp(b,expected));}
int main(int argc,char **argv){WCHAR path[MAX_PATH];DWORD n;int i;assert(argc==2);mbstowcs(runtime_dir,argv[1],MAX_PATH);wcscat(runtime_dir,L"\\");CreateDirectoryW(runtime_dir,NULL);max_backup_logs=2;max_log_bytes=4096;
 assert(startup_open_log());assert(WriteFile(startup_file,"first",5,&n,NULL));assert(startup_open_log());assert(WriteFile(startup_file,"second",6,&n,NULL));assert(startup_open_log());
 startup_log_name(path,2);contents(path,"first");startup_log_name(path,1);contents(path,"second");
 for(i=0;i<400;i++)startup_write("TEST","rotation evidence",i);
 assert(startup_bytes<=4096);CloseHandle(startup_file);startup_file=INVALID_HANDLE_VALUE;
 for(i=0;i<=2;i++){HANDLE f;startup_log_name(path,i);f=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);assert(f!=INVALID_HANDLE_VALUE&&GetFileSize(f,NULL)<=4096);CloseHandle(f);}
 max_backup_logs=0;assert(startup_open_log());CloseHandle(startup_file);startup_file=INVALID_HANDLE_VALUE;startup_log_name(path,1);assert(GetFileAttributesW(path)==INVALID_FILE_ATTRIBUTES);startup_log_name(path,2);assert(GetFileAttributesW(path)==INVALID_FILE_ATTRIBUTES);startup_log_name(path,0);contents(path,"");
 puts("PASS launch and size rotation, bounded log size, retention and zero-backup truncation.");return 0;
}
