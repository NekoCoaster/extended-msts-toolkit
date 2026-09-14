/* Main-game menu text only. Installed at the verified CRT bootstrap stage. */
static Hook welcome_hooks[3];
static U welcome_widget_id;
static WCHAR welcome_text[]=L"Welcome to Microsoft Train Simulator!\nNeko's Extended MSTS Toolkit is active. For help or feedback, visit the github repository linked in the patcher window. Enjoy!";
static U (__fastcall *welcome_set_original)(U,U,const WCHAR*)=(void*)0x44d2f4;
#include "resolution-note.h"
static void welcome_layout(U id,int expanded){
 U table,widget;int area[4],text[4];
 static const int stock_area[4]={325,558,270,34},stock_text[4]={0,0,270,34};
 static const int wide_area[4]={260,558,530,34},wide_text[4]={0,0,530,34};
 const int *from_area=expanded?stock_area:wide_area,*from_text=expanded?stock_text:wide_text;
 if(!id||id>65535||!read_memory(G(0x828108),&table,4)||!table||
    !read_memory(table+id*8,&widget,4)||!widget||!read_memory(widget+0x20,area,16)||!read_memory(widget+0x38,text,16))return;
 /* Widen only while the welcome message is assigned. Restore before hover
    help or another screen: route selection has a Start button in this space.
    Exact geometry checks preserve custom skins and make repeated calls safe. */
 if(memcmp(area,from_area,16)||memcmp(text,from_text,16))return;
 memcpy((void*)(widget+0x20),expanded?wide_area:stock_area,16);
 memcpy((void*)(widget+0x38),expanded?wide_text:stock_text,16);
}
static U __fastcall welcome_set_text(U id,U message,const WCHAR *text){
 if(message==0x31){
  text=resolution_note(id,text);
  if(text==welcome_text){welcome_widget_id=id;welcome_layout(id,1);}
  else if(id==welcome_widget_id)welcome_layout(id,0);
 }
 return welcome_set_original(id,message,text);
}
static WCHAR *(__fastcall *welcome_original)(U)=(void*)0x402590;
static WCHAR *__fastcall welcome_string(U resource){
 if(resource==405||resource==1683)return welcome_text;
 return welcome_original(resource);
}
static int install_welcome_hooks(void){
 startup_call(&welcome_hooks[0],0x457e9e,0x402590,(U)welcome_string);
 startup_call(&welcome_hooks[1],0x4582f7,0x402590,(U)welcome_string);
 startup_call(&welcome_hooks[2],0x44c59c,0x44d2f4,(U)welcome_set_text);
 return prepare_hooks(welcome_hooks,3)&&install_hooks(welcome_hooks,3);
}
