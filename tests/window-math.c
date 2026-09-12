#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../runtime/window_math.h"
static void check(const char *in,const char *expected,int mode){char out[1024];assert(normalize_vm(in,NULL)==mode);assert(normalize_vm(in,out)==mode);assert(!strcmp(out,expected));}
int main(void){int x,y;
 check("train.exe -vm:bw","train.exe -vm:w",2);
 check("\"C:\\MSTS Games\\train.exe\" -vm:bw,1280,720,32 -noclamp","\"C:\\MSTS Games\\train.exe\" -vm:w,1280,720,32 -noclamp",2);
 check("train.exe \"-VM:BW,s,800,600,16\"","train.exe \"-VM:W,s,800,600,16\"",2);
 check("train.exe\t-vm:w,1024,768,32","train.exe\t-vm:w,1024,768,32",1);
 check("train.exe -vm:bwindow -other=\"-vm:bw\"","train.exe -vm:bwindow -other=\"-vm:bw\"",0);
 check("train.exe -vm:bw -vm:w","train.exe -vm:w -vm:w",1);
 check("train.exe -vm:w -vm:bw","train.exe -vm:w -vm:w",2);
 check("-vm:bw","-vm:bw",0);
 check("train.exe","train.exe",0);
 check("","",0);
 centered_position(0,0,1920,1080,1280,720,&x,&y);assert(x==320&&y==180);
 centered_position(-1920,0,0,1080,1280,720,&x,&y);assert(x==-1600&&y==180);
 centered_position(0,40,1920,1080,800,600,&x,&y);assert(x==560&&y==260);
 puts("PASS window arguments, preserved resolutions and monitor centering.");return 0;
}
