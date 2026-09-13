#include <assert.h>
#include "../runtime/loader.c"
int main(int argc,char **argv){
 char full[MAX_PATH];WCHAR dir[MAX_PATH],ini[MAX_PATH];int bits;
 assert(argc==2);assert(GetFullPathNameA(argv[1],MAX_PATH,full,NULL));mbstowcs(root,full,MAX_PATH);wcscat(root,L"\\");
 wcscpy(dir,root);wcscat(dir,L"NEMT");assert(CreateDirectoryW(dir,NULL));wcscpy(ini,dir);wcscat(ini,L"\\settings.ini");
 read_config();assert(config_valid&&!editor_windows&&!editor_free_tools&&!editor_idle_audio);
 for(bits=0;bits<8;bits++){
  assert(WritePrivateProfileStringW(L"Editors",L"ResizableViewports",bits&1?L"true":L"false",ini));
  assert(WritePrivateProfileStringW(L"Editors",L"FreeToolWindows",bits&2?L"true":L"false",ini));
  assert(WritePrivateProfileStringW(L"Editors",L"SmoothIdleAudio",bits&4?L"true":L"false",ini));
  read_config();assert(config_valid&&editor_windows==!!(bits&1)&&editor_free_tools==!!(bits&2)&&editor_idle_audio==!!(bits&4));
 }
 assert(WritePrivateProfileStringW(L"Editors",L"ResizableViewports",L"invalid",ini));read_config();assert(!config_valid);
 puts("PASS editor configuration: missing options off, eight independent combinations, invalid value rejection.");return 0;
}
