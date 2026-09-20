#include <assert.h>
#include <stdio.h>
#include "../runtime/loader.c"
static int present,buttons;
static int WINAPI fake_metrics(int index){SetLastError(123);return index==19?present:index==43?buttons:0;}
typedef HRESULT (WINAPI *MouseCreate)(HINSTANCE,DWORD,void**,void*);
typedef HRESULT (WINAPI *MouseDevice)(void*,const GUID*,void**,void*);
typedef ULONG (WINAPI *MouseRelease)(void*);
static HRESULT probe(HMODULE module){
 void *di=NULL,*mouse=NULL;HRESULT result;
 GUID guid={0x6f1d2b60,0xd5a0,0x11cf,{0xbf,0xc7,0x44,0x45,0x53,0x54,0,0}};
 MouseCreate create=(MouseCreate)GetProcAddress(module,"DirectInputCreateA");assert(create);
 result=create(GetModuleHandleA(NULL),0x700,&di,NULL);assert(!result&&di);
 result=((MouseDevice)(*(void***)di)[3])(di,&guid,&mouse,NULL);
 if(mouse)((MouseRelease)(*(void***)mouse)[2])(mouse);
 ((MouseRelease)(*(void***)di)[2])(di);return result;
}
int main(void){
 BYTE *image=VirtualAlloc(NULL,4096,MEM_RESERVE|MEM_COMMIT,PAGE_READWRITE);
 IMAGE_DOS_HEADER *dos=(void*)image;IMAGE_NT_HEADERS32 *nt=(void*)(image+128);
 IMAGE_IMPORT_DESCRIPTOR *desc=(void*)(image+512);DWORD old;WCHAR path[MAX_PATH];HMODULE module;HRESULT before,after;
 mouse_real_metrics=fake_metrics;
 assert(mouse_compatible_metrics(19)==1&&GetLastError()==123);
 assert(mouse_compatible_metrics(43)==3&&GetLastError()==123);
 assert(mouse_compatible_metrics(75)==0);
 present=1;buttons=5;assert(mouse_compatible_metrics(19)==1&&mouse_compatible_metrics(43)==5);
 buttons=0;assert(mouse_compatible_metrics(43)==0);
 mouse_real_metrics=GetSystemMetrics;
 assert(image);dos->e_magic=IMAGE_DOS_SIGNATURE;dos->e_lfanew=128;
 nt->Signature=IMAGE_NT_SIGNATURE;nt->FileHeader.Machine=IMAGE_FILE_MACHINE_I386;
 nt->OptionalHeader.Magic=0x10b;nt->OptionalHeader.SizeOfImage=4096;nt->OptionalHeader.NumberOfRvaAndSizes=16;
 nt->OptionalHeader.DataDirectory[1].VirtualAddress=512;nt->OptionalHeader.DataDirectory[1].Size=40;
 desc->Name=600;desc->OriginalFirstThunk=700;desc->FirstThunk=800;
 strcpy((char*)image+600,"USER32.dll");*(DWORD*)(image+700)=900;
 strcpy((char*)image+902,"GetSystemMetrics");*(DWORD*)(image+800)=(DWORD)GetProcAddress(GetModuleHandleA("user32.dll"),"GetSystemMetrics");
 assert(mouse_find_import((HMODULE)image)==(LONG*)(image+800));
 desc->FirstThunk=4095;assert(!mouse_find_import((HMODULE)image));desc->FirstThunk=800;
 *(DWORD*)(image+800)=123;assert(!mouse_find_import((HMODULE)image));*(DWORD*)(image+800)=(DWORD)GetSystemMetrics;
 assert(VirtualProtect(image,4096,PAGE_READONLY,&old));
 mouse_metric_slot=(LONG*)(image+800);
 assert(mouse_exchange(mouse_metric_slot,(LONG)GetSystemMetrics,(LONG)mouse_compatible_metrics));
 assert(restore_mouse_compatibility()&&*(DWORD*)(image+800)==(DWORD)GetSystemMetrics);
 {MEMORY_BASIC_INFORMATION mi;assert(VirtualQuery(image,&mi,sizeof(mi))&&mi.Protect==PAGE_READONLY);}
 VirtualFree(image,0,MEM_RELEASE);
 GetSystemDirectoryW(path,MAX_PATH);wcscat(path,L"\\dinput.dll");module=LoadLibraryW(path);assert(module);
 before=probe(module);assert(apply_mouse_compatibility());after=probe(module);
 printf("System mouse: present=%d before=%08lx after=%08lx\n",GetSystemMetrics(19),before,after);
 assert(!after);assert(apply_mouse_compatibility());assert(!probe(module));
 assert(install_mouse_compatibility());assert(mouse_metric_slot);assert(!probe(module));
 assert(install_mouse_compatibility());assert(!probe(module));
 assert(restore_mouse_compatibility());assert(probe(module)==before);
 puts("Mouse compatibility checks passed.");return 0;
}
