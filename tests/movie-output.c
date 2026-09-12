#include <assert.h>
#include "../runtime/loader.c"
static UINT id=7;static int queries,assignments;static DWORD rejection;static HWND assigned;
static LRESULT WINAPI output_message(HWND h,UINT m,WPARAM w,LPARAM l){assert(h==(HWND)123&&m==0x464&&!w&&!l);return id;}
static DWORD WINAPI command(UINT device,UINT message,DWORD_PTR flags,DWORD_PTR data){
 assert(device==7);
 if(message==0x814){MovieStatus *s=(MovieStatus*)data;assert(flags==0x100&&s->item==0x4001);s->result=(DWORD_PTR)assigned;queries++;return 0;}
 assert(message==0x841&&flags==0x10000);assert(((MovieTarget*)data)->window==(HWND)123);assignments++;if(!rejection)assigned=((MovieTarget*)data)->window;return rejection;
}
int main(void){
 movie_command=command;movie_send=output_message;
 movie_bind_output((HWND)123);assert(!queries&&!assignments);
 bind_movie_output=1;movie_bind_output((HWND)123);assert(queries==2&&assignments==1&&assigned==(HWND)123);
 rejection=274;movie_bind_output((HWND)123);assert(queries==3&&assignments==2);
 id=0;movie_bind_output((HWND)123);assert(queries==3&&assignments==2);
 puts("PASS decoder output binding: disabled bypass, query/assignment/verification, rejected command and missing device.");return 0;
}
