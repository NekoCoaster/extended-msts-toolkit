#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../runtime/window_math.h"
static void check(const char *in,const char *expected,int mode){char out[1024];assert(normalize_vm(in,NULL)==mode);assert(normalize_vm(in,out)==mode);assert(!strcmp(out,expected));}
int main(void){int x,y;char launch[256];
 normalize_launch("train.exe",launch,1);assert(!strcmp(launch,"train.exe -vm:w -noclamp"));
 normalize_launch("train.exe -vm:w,1280,720,32",launch,1);assert(!strcmp(launch,"train.exe -vm:w,1280,720,32 -noclamp"));
 normalize_launch("train.exe \"-NOCLAMP\"",launch,1);assert(!strcmp(launch,"train.exe \"-NOCLAMP\" -vm:w"));
 normalize_launch("train.exe -vm:1920,1080,32",launch,0);assert(!strcmp(launch,"train.exe -vm:1920,1080,32"));
 assert(!has_noclamp("train.exe -noclampX")&&!has_noclamp("\"C:\\-noclamp\\train.exe\""));
 check("\"C:\\MSTS Games\\train.exe\" -vm:w,1280,720,32 -noclamp","\"C:\\MSTS Games\\train.exe\" -vm:w,1280,720,32 -noclamp",1);
 check("train.exe \"-VM:W,s,800,600,16\"","train.exe \"-VM:W,s,800,600,16\"",1);
 check("train.exe -vm:w -vm:800,600,32","train.exe  -vm:800,600,32",3);
 check("train.exe -vm:800,600,32 -vm:w","train.exe -vm:800,600,32 ",3);
 check("train.exe -vm:s,800,600,16","train.exe -vm:s,800,600,16",3);
 check("train.exe -vm:bw","train.exe -vm:bw",0); /* Not a supported alias. */
 check("train.exe","train.exe",0);
 centered_position(0,0,1920,1080,1280,720,&x,&y);assert(x==320&&y==180);
 centered_position(-1920,0,0,1080,1280,720,&x,&y);assert(x==-1600&&y==180);
 puts("PASS native window/fullscreen arguments, fullscreen precedence, default windowing, resolution preservation and centering.");return 0;
}
