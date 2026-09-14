#include <assert.h>
static unsigned char resolution_globals[0x100000];
#define G(a) ((U)resolution_globals+(a)-0x790000)
#define RESOLUTION_ADDR(a) G(a)
#include "../runtime/loader.c"
static U table[16],shown,closed,dispatches;static B widgets[8][512];
static U __fastcall find(const WCHAR *name){
 const WCHAR *names[]={L"",L"displayrescombo",L"combopopup9",L"condlgpopup",L"condlgcancel",L"condlginstruct",L"condlgcontrol"};U i;
 for(i=1;i<7;i++)if(!wcscmp(name,names[i]))return i;return 0;
}
static U __fastcall close_list(U id,U method,U value){closed++;return 123;}
static U __fastcall dispatch(U id,U method,U value){
 dispatches++;
 if(method==0x58){assert(id==3&&value==0x2b&&closed);shown++;}
 if(method==0x31&&id==5){assert(wcsstr((WCHAR*)value,L"msts-widescreen-patch.zip"));assert(wcsstr((WCHAR*)value,L"train.exe"));}
 return 456;
}
static void fixture(const char *path){
 FILE *f=fopen(path,"rb");B b[6];U sites[]={0x43b3e4,0x4648f2},targets[]={0x43b53f,0x464a1b};int i;assert(f);
 for(i=0;i<2;i++){fseek(f,sites[i]-0x400000,SEEK_SET);assert(fread(b,1,5,f)==5);assert(b[0]==0xe8&&sites[i]+5+ru(b+1)==targets[i]);}
 fseek(f,0x633b3,SEEK_SET);assert(fread(b,1,6,f)==6);assert(!memcmp(b,"\x0f\x85\xa4\0\0\0",6)||!memcmp(b,"\x0f\x85\0\0\0\0",6));fclose(f);
}
int main(int argc,char **argv){
 U i;int mode[10][4]={{1920,1080,32,1},{2048,2048,32,1},{2560,1600,32,0},{1080,2560,32,1}};
 int ba[]={16,82,288,50},bt[]={0,0,288,50},ta[]={16,58,288,25},tt[]={0,0,288,25};
 for(i=1;i<8;i++)table[i*2]=(U)widgets[i];*(U*)G(0x828108)=(U)table;
 memcpy((void*)G(0x79ca70),mode,sizeof(mode));
 memcpy(widgets[5]+0x20,ba,16);memcpy(widgets[5]+0x38,bt,16);memcpy(widgets[6]+0x20,ta,16);memcpy(widgets[6]+0x38,tt,16);
 resolution_find=find;resolution_dispatch=dispatch;resolution_close_original=close_list;
 *(U*)(widgets[1]+0x114)=0;assert(!resolution_selected_large());
 *(U*)(widgets[1]+0x114)=1;assert(!resolution_selected_large());
 *(U*)(widgets[1]+0x114)=2;assert(resolution_selected_large()); /* stock skips unavailable row */
 *(U*)(widgets[1]+0x114)=3;assert(!resolution_selected_large());
 resolution_all_modes=1;assert(resolution_selected_large()); /* widescreen includes unavailable row */
 *(U*)(widgets[1]+0x114)=2;
 assert(resolution_selection_closed(99,0x59,0)==123&&shown==0);
 assert(resolution_selection_closed(2,0x31,0)==123&&shown==0);
 assert(resolution_selection_closed(2,0x59,1)==123&&shown==0);
 assert(resolution_selection_closed(2,0x59,0)==123&&shown==1&&resolution_active);
 resolution_selection_closed(2,0x59,0);assert(shown==1); /* no reentrancy */
 *(U*)(widgets[5]+0x34)=0x12345678; /* never restore stale text pointers */
 assert(resolution_dialog_closed(3,0x59,0)==456&&!resolution_active);
 assert(!memcmp(widgets[5]+0x20,ba,16)&&!memcmp(widgets[5]+0x38,bt,16));assert(ru(widgets[5]+0x34)==0x12345678);
 assert(!memcmp(widgets[6]+0x20,ta,16)&&!memcmp(widgets[6]+0x38,tt,16));
 resolution_selection_closed(2,0x59,0);assert(shown==2);resolution_dialog_closed(3,0x59,0);
 *(U*)(widgets[1]+0x114)=1;resolution_selection_closed(2,0x59,0);assert(shown==2);
 *(U*)(widgets[1]+0x114)=10;assert(!resolution_selected_large());
 *(U*)(widgets[1]+0x114)=2;*(U*)(widgets[5]+0x20)=17;resolution_selection_closed(2,0x59,0);assert(shown==2); /* custom skin */
 for(i=1;i<(U)argc;i++)fixture(argv[i]);
 puts("PASS resolution selection, stock/widescreen indexing, threshold, other dropdowns, duplicate suppression, dialog restoration, custom skin and fixture call signatures.");return 0;
}
