#include <assert.h>
#include "../runtime/loader.c"
static void fixture(B *image){
 IMAGE_DOS_HEADER *dos=(void*)image;IMAGE_NT_HEADERS *nt=(void*)(image+128);IMAGE_SECTION_HEADER *section;
 memset(image,0,4096);dos->e_magic=IMAGE_DOS_SIGNATURE;dos->e_lfanew=128;
 nt->Signature=IMAGE_NT_SIGNATURE;nt->FileHeader.Machine=IMAGE_FILE_MACHINE_I386;
 nt->FileHeader.SizeOfOptionalHeader=sizeof(nt->OptionalHeader);nt->FileHeader.NumberOfSections=1;
 nt->OptionalHeader.Magic=0x10b;nt->OptionalHeader.SizeOfImage=4096;
 section=(void*)(nt+1);section->VirtualAddress=1024;section->Misc.VirtualSize=1024;section->Characteristics=IMAGE_SCN_MEM_EXECUTE;
 memcpy(image+1100,"\xb8\x00\x08\x00\x00\x39\x45\x90\x0f\x87\x40\x00\x00\x00\x39\x45\x8c\x0f\x87\x37\x00\x00\x00",23);
 memcpy(image+1200,"\xb8\x00\x08\x00\x00\x39\x85\x44\xff\xff\xff\x0f\x87\x40\x00\x00\x00\x39\x85\x40\xff\xff\xff\x0f\x87\x34\x00\x00\x00",29);
}
int main(int argc,char **argv){
 B *image=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);Hook patches[8];U count;int already;DWORD old;
 assert(image);fixture(image);
 assert(highres_plan(image,4096,patches,&count,&already)&&count==2&&!already);
 assert(VirtualProtect(image,4096,PAGE_EXECUTE_READ,&old));
 assert(prepare_hooks(patches,count)&&install_hooks(patches,count));
 assert(highres_plan(image,4096,patches,&count,&already)&&!count&&already==2);
 {MEMORY_BASIC_INFORMATION mi;assert(VirtualQuery(image,&mi,sizeof(mi)));assert(mi.Protect==PAGE_EXECUTE_READ);}
 assert(VirtualProtect(image,4096,PAGE_READWRITE,&old));fixture(image);claim_count=0;
 image[1219]=0x41;assert(!highres_plan(image,4096,patches,&count,&already));
 assert(!memcmp(image+1100,"\xb8\x00\x08\x00\x00",5));
 fixture(image);image[1119]++;assert(!highres_plan(image,4096,patches,&count,&already));
 fixture(image);memset(image+1101,255,4);assert(highres_plan(image,4096,patches,&count,&already)&&count==1&&already==1);
 fixture(image);((IMAGE_NT_HEADERS*)(image+128))->FileHeader.Machine=0x8664;assert(!highres_plan(image,4096,patches,&count,&already));
 fixture(image);assert(!highres_plan(image,100,patches,&count,&already));
 fixture(image);memcpy(image+1400,"\xb8\x00\x08\x00\x00\x39",6);assert(!highres_plan(image,4096,patches,&count,&already));
 VirtualFree(image,0,MEM_RELEASE);
 high_resolution=0;SetLastError(123);assert(apply_high_resolution()&&GetLastError()==123);
 {WCHAR temp[MAX_PATH],file[MAX_PATH];HANDLE h;
  assert(GetTempPathW(MAX_PATH,temp));assert(GetTempFileNameW(temp,L"NHR",0,root));assert(DeleteFileW(root));assert(CreateDirectoryW(root,NULL));
  wcscat(root,L"\\");wcscpy(file,root);wcscat(file,L"D3DIM700.dll");
  h=CreateFileW(file,GENERIC_WRITE,0,NULL,CREATE_NEW,0,NULL);assert(h!=INVALID_HANDLE_VALUE);CloseHandle(h);
  high_resolution=1;assert(highres_external());assert(apply_high_resolution());assert(strstr(high_resolution_state,"external"));
  assert(!high_resolution_module);DeleteFileW(file);root[wcslen(root)-1]=0;RemoveDirectoryW(root);root[0]=0;}
 if(argc>1 && !strcmp(argv[1],"--host-probe")){
  /* Only this disposable test process is patched; no game or disk edit. */
  GetModuleFileNameW(NULL,root,MAX_PATH);*wcsrchr(root,L'\\')=0;wcscat(root,L"\\");
  high_resolution=1;SetLastError(321);assert(apply_high_resolution());assert(GetLastError()==321);
  printf("HOST: %s\n",high_resolution_state);
  assert(apply_high_resolution());printf("HOST repeat: %s\n",high_resolution_state);
 }
 puts("PASS guarded high-resolution patch transaction, repeat/mixed state, malformed/ambiguous rejection and protection/error preservation.");return 0;
}
