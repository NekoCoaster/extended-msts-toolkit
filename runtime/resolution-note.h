/* Reuse the validated native text-dispatch hook; no GUI file changes.
   Exact stock widget geometry prevents altering custom layouts. */
static U resolution_heading;
static WCHAR resolution_title[128],resolution_warning[320];
static int resolution_large;
static int resolution_above_limit(const WCHAR *text){
 WCHAR copy[64],*end;unsigned long width,height;int i;
 if(!text)return 0;
 for(i=0;i<63;i++){if(!read_memory((U)(text+i),copy+i,2))return 0;if(!copy[i])break;}copy[63]=0;
 width=wcstoul(copy,&end,10);if(end==copy)return 0;
 while(*end==L' ')end++;if(*end!=L'x'&&*end!=L'X'&&*end!=0xd7)return 0;end++;
 {WCHAR *start=end;height=wcstoul(start,&end,10);if(end==start)return 0;}
 return width>2048||height>2048;
}
static U resolution_widget(U id,int area[4],int text[4]){
 U table,widget;
 if(!id||id>65535||!read_memory(G(0x828108),&table,4)||!table||!read_memory(table+id*8,&widget,4)||!widget||
    !read_memory(widget+0x20,area,16)||!read_memory(widget+0x38,text,16))return 0;
 return widget;
}
static const WCHAR *resolution_heading_text(U id){
 int area[4],text[4];U widget=resolution_widget(id,area,text);
 static const int normal[4]={80,176,225,30},expanded[4]={80,176,650,114};
 static const int normal_text[4]={0,0,225,30},expanded_text[4]={0,0,650,114};
 if(!widget||!resolution_title[0]||
    ((memcmp(area,normal,16)||memcmp(text,normal_text,16))&&(memcmp(area,expanded,16)||memcmp(text,expanded_text,16))))return NULL;
 memcpy((void*)(widget+0x20),resolution_large?expanded:normal,16);
 memcpy((void*)(widget+0x38),resolution_large?expanded_text:normal_text,16);
 if(!resolution_large)return resolution_title;
 wcscpy(resolution_warning,resolution_title);
 wcscat(resolution_warning,L"\n\n\nAbove 2048 pixels may require D3DIM700.DLL. See the widescreen guide linked in NEMT.");
 return resolution_warning;
}
static const WCHAR *resolution_note(U id,const WCHAR *value){
 int area[4],text[4];U widget=resolution_widget(id,area,text);const WCHAR *heading;
 static const int selector[4]={88,209,197,15};
 if(!widget||!value)return value;
 if(area[0]==80&&area[1]==176&&((area[2]==225&&area[3]==30)||(id==resolution_heading&&area[2]==650&&area[3]==114))){
  resolution_heading=id;wcsncpy(resolution_title,value,127);resolution_title[127]=0;
  heading=resolution_heading_text(id);return heading?heading:value;
 }
 if(!memcmp(area,selector,16)&&text[0]==10&&text[1]==0&&text[2]==160&&text[3]==15){
  resolution_large=resolution_above_limit(value);
  heading=resolution_heading_text(resolution_heading);
  if(heading)welcome_set_original(resolution_heading,0x31,heading);
 }
 return value;
}
