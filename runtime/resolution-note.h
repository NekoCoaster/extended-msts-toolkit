/* Native resolution selection alert. Bootstrap/main game only.
   Hook the dropdown selection's final close call, not text population. */
#ifndef RESOLUTION_ADDR
#define RESOLUTION_ADDR(a) G(a)
#endif
static Hook resolution_hooks[2];
static int resolution_all_modes;
static U (__fastcall *resolution_find)(const WCHAR*)=(void*)0x40164f;
static U (__fastcall *resolution_dispatch)(U,U,U)=(void*)0x464a1b;
static U (__fastcall *resolution_close_original)(U,U,U)=(void*)0x43b53f;
static U resolution_active,resolution_body,resolution_title;
static B resolution_saved_body[32],resolution_saved_title[32];
static const WCHAR resolution_message[]=L"Before using a resolution above 2048 pixels, close MSTS and copy D3DIM700.DLL from your original msts-widescreen-patch.zip into the folder containing train.exe.\n\nWithout it, MSTS may revert to 1280 x 720 or crash.";
static U resolution_widget(U id){
 U table,widget;
 if(!id||id>65535||!read_memory(G(0x828108),&table,4)||!table||
 !read_memory(table+id*8,&widget,4)||!widget)return 0;
 return widget;
}
static void resolution_restore(void){
 U widget;
 if(!resolution_active)return;
 widget=resolution_widget(resolution_body);if(widget){memcpy((void*)(widget+0x20),resolution_saved_body,16);memcpy((void*)(widget+0x38),resolution_saved_body+16,16);}
 widget=resolution_widget(resolution_title);if(widget){memcpy((void*)(widget+0x20),resolution_saved_title,16);memcpy((void*)(widget+0x38),resolution_saved_title+16,16);}
 resolution_active=0;
}
static int resolution_selected_large(void){
 U widget,index,i;int mode[4];
 widget=resolution_widget(resolution_find(L"displayrescombo"));
 if(!widget||!read_memory(widget+0x114,&index,4)||index>=10)return 0;
 for(i=0;i<10;i++){
  if(!read_memory(RESOLUTION_ADDR(0x79ca70)+i*16,mode,16))return 0;
  if(!resolution_all_modes&&mode[3]!=1)continue;
  if(!index)return mode[0]>2048||mode[1]>2048;
  index--;
 }
 return 0;
}
static void resolution_show(void){
 U popup,button,body,title;
 static const int body_area[4]={16,82,288,50},body_text[4]={0,0,288,50};
 static const int title_area[4]={16,58,288,25},title_text[4]={0,0,288,25};
 static const int expanded_body[4]={16,52,312,150},expanded_text[4]={0,0,312,150};
 static const int expanded_title[4]={16,22,312,25},expanded_title_text[4]={0,0,312,25};
 if(resolution_active)return;
 popup=resolution_find(L"condlgpopup");button=resolution_find(L"condlgcancel");
 resolution_body=resolution_find(L"condlginstruct");resolution_title=resolution_find(L"condlgcontrol");
 body=resolution_widget(resolution_body);title=resolution_widget(resolution_title);
 if(!popup||!button||!body||!title)return;
 /* Only the stock dialog is resized. Preserve all intervening fields. */
 if(!read_memory(body+0x20,resolution_saved_body,16)||!read_memory(body+0x38,resolution_saved_body+16,16)||!read_memory(title+0x20,resolution_saved_title,16)||!read_memory(title+0x38,resolution_saved_title+16,16))return;
 if(memcmp((void*)(body+0x20),body_area,16)||memcmp((void*)(body+0x38),body_text,16)||
 memcmp((void*)(title+0x20),title_area,16)||memcmp((void*)(title+0x38),title_text,16))return;
 memcpy((void*)(body+0x20),expanded_body,16);memcpy((void*)(body+0x38),expanded_text,16);
 memcpy((void*)(title+0x20),expanded_title,16);memcpy((void*)(title+0x38),expanded_title_text,16);
 resolution_active=1;
 resolution_dispatch(button,0x31,(U)L"OK");
 resolution_dispatch(resolution_title,0x31,(U)L"High resolution warning");
 resolution_dispatch(resolution_body,0x31,(U)resolution_message);
 resolution_dispatch(popup,0x58,0x2b);
}
static U __fastcall resolution_selection_closed(U id,U method,U value){
 U result=resolution_close_original(id,method,value);
 /* This call site is reached only after committing a list item. Other
    dropdowns, list population and hover never show this warning. */
 if(method==0x59&&!value&&id==resolution_find(L"combopopup9")&&resolution_selected_large())resolution_show();
 return result;
}
static U __fastcall resolution_dialog_closed(U id,U method,U value){
 U result=resolution_dispatch(id,method,value);
 if(method==0x59&&!value)resolution_restore();
 return result;
}
static int install_resolution_hooks(void){
 B branch_bytes[6];
 if(!read_memory(0x4633b3,branch_bytes,6))return 0;
 if(!memcmp(branch_bytes,"\x0f\x85\x00\x00\x00\x00",6))resolution_all_modes=1;
 else if(!memcmp(branch_bytes,"\x0f\x85\xa4\x00\x00\x00",6))resolution_all_modes=0;
 else return 0;
 startup_call(&resolution_hooks[0],0x43b3e4,0x43b53f,(U)resolution_selection_closed);
 startup_call(&resolution_hooks[1],0x4648f2,0x464a1b,(U)resolution_dialog_closed);
 return prepare_hooks(resolution_hooks,2)&&install_hooks(resolution_hooks,2);
}
