#include <assert.h>
#include "../runtime/loader.c"
static void item(B *p,U id,B logical,B efficiency,B flags){memset(p,0,32);*(U*)p=32;*(U*)(p+8)=id;p[14]=logical;p[18]=efficiency;p[19]=flags;}
int main(int argc,char **argv){B data[128];ULONG chosen[32],existing[2]={103,101};U count;int i;
 for(i=0;i<4;i++)item(data+32*i,100+i,i,i%2?8:0,0);
 assert(cpu_select(data,128,15,NULL,0,chosen,&count)==1&&count==2&&chosen[0]==101&&chosen[1]==103);
 assert(cpu_select(data,128,3,NULL,0,chosen,&count)==1&&count==1&&chosen[0]==101);
 assert(cpu_select(data,128,15,existing,1,chosen,&count)==1&&count==1&&chosen[0]==103);
 data[32+19]=2;assert(cpu_select(data,128,15,NULL,0,chosen,&count)==1&&count==1&&chosen[0]==103);
 data[32+19]=6;assert(cpu_select(data,128,15,NULL,0,chosen,&count)==1&&count==2);
 assert(cpu_select(data,128,5,NULL,0,chosen,&count)==-3&&count==0);
 data[12]=1;assert(cpu_select(data,128,15,NULL,0,chosen,&count)==-2);data[12]=0;
 data[14]=32;assert(cpu_select(data,128,15,NULL,0,chosen,&count)==-2);data[14]=0;
 assert(cpu_select(data,127,15,NULL,0,chosen,&count)==-1);data[0]=0;assert(cpu_select(data,128,15,NULL,0,chosen,&count)==-1);data[0]=32;
 for(i=0;i<4;i++)data[i*32+18]=0;assert(cpu_select(data,128,15,NULL,0,chosen,&count)==0&&count==0);
 prefer_pcores=0;apply_cpu_preference();
 if(argc==2){mbstowcs(runtime_dir,argv[1],MAX_PATH);wcscat(runtime_dir,L"\\");CreateDirectoryW(runtime_dir,NULL);InitializeCriticalSection(&startup_lock);startup_lock_ready=1;assert(startup_open_log());deep_environment();prefer_pcores=1;apply_cpu_preference();CloseHandle(startup_file);startup_file=INVALID_HANDLE_VALUE;}

 puts("PASS CPU class selection, masks, existing CPU Sets, reservations, homogeneous/malformed/unsupported topology and disabled path.");return 0;
}
