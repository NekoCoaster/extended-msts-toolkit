#include <assert.h>
static unsigned char globals[0x1000];
#define G(a) ((U)globals+(a)-0x828000)
#include "../runtime/loader.c"
static U table[4],calls;static B widget[0x94];
static WCHAR *__fastcall original(U id){assert(id==308);return L"Original loading text";}
static U __fastcall set_text(U id,U message,const WCHAR *text){assert(id==1&&message==0x31&&text);calls++;return 17;}
int main(void){WCHAR *s=welcome_string(405);int area[4]={325,558,270,34},text[4]={0,0,270,34};B before[0x94];
 table[2]=(U)widget;*(U*)G(0x828108)=(U)table;welcome_set_original=set_text;welcome_original=original;
 memcpy(widget+0x20,area,16);memcpy(widget+0x38,text,16);memcpy(before,widget,sizeof(widget));
 assert(welcome_set_text(1,0x31,s)==17);assert(ru(widget+0x20)==260&&ru(widget+0x28)==530&&ru(widget+0x40)==530);
 welcome_set_text(1,0x31,s);assert(ru(widget+0x28)==530);
 welcome_set_text(1,0x31,L"Select your route");assert(!memcmp(before,widget,sizeof(widget)));assert(calls==3);
 area[0]=300;memcpy(widget+0x20,area,16);memcpy(before,widget,sizeof(widget));
 welcome_set_text(1,0x31,s);assert(!memcmp(before,widget,sizeof(widget)));
 assert(s==welcome_string(1683));assert(wcsstr(s,L"Simulator!\nNeko's Extended MSTS Toolkit is active."));
 assert(wcsstr(s,L"github repository linked in the patcher window. Enjoy!"));
 assert(!wcscmp(welcome_string(308),L"Original loading text"));
 puts("PASS welcome text, temporary footer expansion, repeated assignment, navigation restoration, custom skins and forwarding.");return 0;
}
