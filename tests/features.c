#include <assert.h>
#include <stdlib.h>
static unsigned char *globals,*patches;
#define G(a) ((a)==0x5862dc?(unsigned int)patches:((a)==0x51c98c?(unsigned int)patches+16:(unsigned int)globals+(a)-0x7b0000))
#include "../runtime/loader.c"
int main(int argc,char **argv){
 char full[MAX_PATH],config[512];WCHAR dir[MAX_PATH],ini[MAX_PATH];HANDLE f;DWORD n;int bits,i,ok;
 assert(argc==3);bits=atoi(argv[2]);assert(GetFullPathNameA(argv[1],MAX_PATH,full,NULL));mbstowcs(root,full,MAX_PATH);wcscat(root,L"\\");
 wcscpy(dir,root);wcscat(dir,L"NEMT");assert(CreateDirectoryW(dir,NULL));wcscpy(ini,dir);wcscat(ini,L"\\native.ini");
 snprintf(config,sizeof(config),"[Derailment]\r\nPreventActivityEnd=%s\r\nUnlockCameras=%s\r\nEnableCrawl=%s\r\nCrawlStrength=10\r\n[Diagnostics]\r\nWriteStatusJson=false\r\n",bits&1?"true":"false",bits&2?"true":"false",bits&4?"true":"false");
 if(bits==8)strcpy(config,"[Derailment]\r\nPreventActivityEnd=invalid\r\n");
 if(bits==9)strcpy(config,"[Derailment]\r\nCrawlStrength=101\r\n");
 if(bits==10)strcpy(config,"[Derailment]\r\nCrawlStrength=not-a-number\r\n");
 f=CreateFileW(ini,GENERIC_WRITE,0,NULL,CREATE_ALWAYS,0,NULL);assert(f!=INVALID_HANDLE_VALUE);assert(WriteFile(f,config,strlen(config),&n,NULL));CloseHandle(f);
 globals=VirtualAlloc(NULL,0x80000,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);patches=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_EXECUTE_READWRITE);assert(globals&&patches);
 memcpy(patches,"\x74\x16",2);memcpy(patches+16,"\x0f\x84\x55\x03\x00\x00",6);
 for(i=0;i<HOOK_COUNT;i++){B *fake=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_EXECUTE_READWRITE);assert(fake);memcpy(fake,hooks[i].original,hooks[i].length);hooks[i].address=(U)fake;}
 ok=start_native();
 if(bits>=8||((bits&4)&&!(bits&1))){assert(!ok&&!config_valid);assert(!memcmp(patches,"\x74\x16",2));assert(!memcmp(patches+16,"\x0f\x84\x55\x03\x00\x00",6));}
 else{assert(ok&&config_valid);assert(!memcmp(patches,bits&1?"\xeb\x28":"\x74\x16",2));assert(!memcmp(patches+16,bits&2?"\x90\x90\x90\x90\x90\x90":"\x0f\x84\x55\x03\x00\x00",6));}
 wcscpy(ini,runtime_dir);wcscat(ini,L"status.json");for(i=0;i<10000;i++)write_status();assert(GetFileAttributesW(ini)==INVALID_FILE_ATTRIBUTES);
 printf("PASS feature configuration %d: selected in-memory changes, dependency validation, disabled logging.\n",bits);return 0;
}
