/* Execute MSTS's real derail routine from supported EXE fixtures. Only the
   camera notification and unrelated wake helper are replaced with observers. */
#include <assert.h>
#include "../runtime/loader.c"
static B native_fixture_space[0x450000];
#undef assert
#define assert(x) do{if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static int camera_calls,wake_calls;
static void __fastcall camera(void){camera_calls++;}
static void __fastcall wake(U car){assert(car);wake_calls++;}
static B *obj(void){B *p=VirtualAlloc(NULL,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);assert(p);return p;}
static void put(B *p,U n){memcpy(p,&n,4);}
static B *load_native(const char *path){
 FILE *f=fopen(path,"rb");B *file,*page=NULL;long size;U pe,table,i,j,rva,raw,bytes;DWORD old;
 U sites[3]={0x62e0a7,0x62e0bf,0x62e206};
 assert(f);fseek(f,0,SEEK_END);size=ftell(f);rewind(f);file=malloc(size);assert(file&&fread(file,1,size,f)==size);fclose(f);
 pe=ru(file+60);table=pe+24+*(unsigned short*)(file+pe+20);
 for(i=0;i<*(unsigned short*)(file+pe+6);i++){
  B *s=file+table+i*40;rva=ru(s+12);bytes=ru(s+16);raw=ru(s+20);
  if(rva<=0x22e017&&0x22e50a<=rva+bytes){
   page=obj();memcpy(page,file+raw+0x22e017-rva,0x4f3);
   assert(!memcmp(page,"\x55\x8b\xec\x83\xec\x10",6)&&page[0x4f2]==0xc3);
   for(j=0;j<3;j++){
    B *p=page+sites[j]-0x62e017;
    assert(*p==0xe8&&sites[j]+5+ru(p+1)==(j?0x40415b:0x402f90));
    put(p+1,(U)(j?wake:camera)-(U)p-5);
   }
   assert(VirtualProtect(page,4096,PAGE_EXECUTE_READ,&old));FlushInstructionCache(GetCurrentProcess(),page,4096);break;
  }
 }
 free(file);assert(page);crawl_derail_native=(void*)page;return page;
}
int main(int argc,char **argv){
 B *train,*car[3],*body[3],*def[3],*code;int i,total;DWORD old;
 assert(argc==2&&(U)native_fixture_space<0x7b0000&&(U)(native_fixture_space+sizeof(native_fixture_space))>=0x830000);
 code=load_native(argv[1]);train=obj();*(U*)0x7c2ac0=(U)train;*(U*)0x7ba04c=0;*(U*)0x7be0f4=0;
 for(i=0;i<3;i++){
  car[i]=obj();body[i]=obj();def[i]=obj();put(car[i]+0x5c,(U)body[i]);put(car[i]+0x94,(U)def[i]);put(car[i]+0x98,(U)train);
  body[i][0xf2]=8;def[i][0x88]=i!=1;cars[i].id=(U)car[i];cars[i].body=(U)body[i];
 }
 for(i=0;i<3;i++){
  if(i){put(car[i]+0xa0,(U)car[i-1]);cars[i].links[0]=(U)car[i-1];}
  if(i<2){put(car[i]+0xa8,(U)car[i+1]);cars[i].links[1]=(U)car[i+1];}
 }
 car_count=3;crawl_requested=prevent_end=1;
 assert(crawl_derail_consist());assert(camera_calls==3&&wake_calls==9&&(*(B*)(train+0x5c)&2)&&*(U*)0x80a9ac==1);
 for(i=0;i<3;i++){assert((body[i][0xf2]&12)==4&&(ru(car[i]+0x84)&8));cars[i].derailed=1;}
 assert((ru(car[0]+0x296)&0x204)==0x204&&(ru(car[2]+0x296)&0x204)==0x204&&!ru(car[1]+0x296));
 assert(crawl_derail_consist()&&camera_calls==3); /* already derailed */
 crawl_requested=0;assert(!crawl_derail_consist());crawl_requested=1;prevent_end=0;assert(!crawl_derail_consist());prevent_end=1;
 *(U*)0x7be0f4=1;assert(!crawl_derail_consist());*(U*)0x7be0f4=0;
 cars[0].links[0]=(U)car[2];cars[2].links[1]=(U)car[0];assert(!crawl_derail_consist()&&blocked&&camera_calls==3);
 cars[0].links[0]=cars[2].links[1]=0;blocked=0;
 car_count=2;cars[1].links[0]=0;cars[1].links[1]=(U)car[0];assert(!crawl_derail_consist()&&blocked&&camera_calls==3);
 car_count=3;cars[1].links[0]=(U)car[0];cars[1].links[1]=(U)car[2];blocked=0;
 assert(VirtualProtect(code,4096,PAGE_READWRITE,&old));code[0]=0xcc;assert(!crawl_derail_consist()&&blocked&&camera_calls==3);
 crawl_derail_down=1;assert(!crawl_derail_edge(CRAWL_DERAIL,1));assert(!crawl_derail_edge(0,1));
 total=0;for(i=0;i<100;i++)total+=crawl_derail_edge(CRAWL_DERAIL,1);assert(total==1);
 assert(!crawl_derail_edge(0,0));assert(!crawl_derail_edge(CRAWL_DERAIL,1));assert(!crawl_derail_edge(0,1));assert(crawl_derail_edge(CRAWL_DERAIL,1));
 puts("PASS real native derail routine: whole consist, engine/train flags, stopped-body wake, already-derailed skip, signature/cycle rejection, feature/pause gates and one-shot/release/focus edges.");return 0;
}
