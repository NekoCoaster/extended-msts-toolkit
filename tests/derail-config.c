#include <assert.h>
#include "../runtime/loader.c"
int main(int argc,char **argv){char full[MAX_PATH];WCHAR dir[MAX_PATH],ini[MAX_PATH];int i;
 const WCHAR *valid[]={L"\\",L"BACKSLASH",L"F12",L"k",L"0x56",L"NONE"};U expected[]={0x2b,0x2b,0x58,0x25,0x56,0};
 const WCHAR *bad[]={L"invalid",L"0xee",L"0x1d",L"0x01",L"Ctrl+K",L""};
 assert(argc==2&&GetFullPathNameA(argv[1],MAX_PATH,full,NULL));mbstowcs(root,full,MAX_PATH);wcscat(root,L"\\");
 wcscpy(dir,root);wcscat(dir,L"NEMT");assert(CreateDirectoryW(dir,NULL));wcscpy(ini,dir);wcscat(ini,L"\\settings.ini");
 read_config();assert(config_valid&&crawl_derail_scan==0x2b&&!strcmp(crawl_derail_name,"\\"));
 for(i=0;i<6;i++){assert(WritePrivateProfileStringW(L"Derailment",L"DerailKey",valid[i],ini));read_config();assert(config_valid&&crawl_derail_scan==expected[i]);}
 for(i=0;i<6;i++){assert(WritePrivateProfileStringW(L"Derailment",L"DerailKey",bad[i],ini));read_config();assert(!config_valid);}
 puts("PASS derail key defaults, named/letter/scan keys, disabled command and invalid/modifier rejection.");return 0;
}
