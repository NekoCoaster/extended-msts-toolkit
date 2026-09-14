/* DirectInput keyboard scan codes. Bindings describe physical keys, matching
   MSTS's IOM files. Keep parsing independent of the current Windows layout. */
static const WCHAR *editor_key_names[6]={L"RE_CAM_FORWARD",L"RE_CAM_BACKWARD",L"RE_CAM_LEFT",L"RE_CAM_RIGHT",L"RE_CAM_UP",L"RE_CAM_DOWN"};
static const WCHAR *editor_key_defaults[6]={L"w",L"s",L"a",L"d",L"e",L"q"};
static unsigned editor_keys[6]={0x11,0x1f,0x1e,0x20,0x12,0x10};
static unsigned editor_key_parse(const WCHAR *s){
 static const unsigned letters[26]={0x1e,0x30,0x2e,0x20,0x12,0x21,0x22,0x23,0x17,0x24,0x25,0x26,0x32,0x31,0x18,0x19,0x10,0x13,0x1f,0x14,0x16,0x2f,0x11,0x2d,0x15,0x2c};
 static const struct {const WCHAR *name;unsigned code;} names[]={
  {L"SPACE",0x39},{L"TAB",0x0f},{L"ENTER",0x1c},{L"BACKSPACE",0x0e},
  {L"HOME",0xc7},{L"END",0xcf},{L"PAGEUP",0xc9},{L"PAGEDOWN",0xd1},
  {L"INSERT",0xd2},{L"DELETE",0xd3},{L"MINUS",0x0c},{L"EQUALS",0x0d},
  {L"COMMA",0x33},{L"PERIOD",0x34},{L"SLASH",0x35},{L"SEMICOLON",0x27},
  {L"APOSTROPHE",0x28},{L"BACKQUOTE",0x29},{L"LBRACKET",0x1a},{L"RBRACKET",0x1b},{L"BACKSLASH",0x2b}};
 WCHAR c=s[0],*end;unsigned n,i;
 if(c>=L'a'&&c<=L'z')c-=32;
 if(!s[1]){if(c>=L'A'&&c<=L'Z')return letters[c-L'A'];if(c>=L'1'&&c<=L'9')return c-L'1'+2;if(c==L'0')return 0x0b;}
 if(c==L'F'){n=wcstoul(s+1,&end,10);if(end!=s+1&&!*end&&n>=1&&n<=12)return n<=10?0x3a+n:0x57+n-11;}
 if(s[0]==L'0'&&(s[1]==L'x'||s[1]==L'X')){n=wcstoul(s+2,&end,16);if(end!=s+2&&!*end&&n>0&&n<256)return n;}
 for(i=0;i<sizeof(names)/sizeof(names[0]);i++)if(!lstrcmpiW(s,names[i].name))return names[i].code;
 return 0;
}
static int editor_key_allowed(unsigned n){
 /* Arrow destinations and modifier keys cannot also be swap sources. Escape
    remains available to cancel tools and dialogs. Scan code zero is reserved. */
 return n&&n<256&&n!=1&&n!=0xc8&&n!=0xd0&&n!=0xcb&&n!=0xcd&&
  n!=0x1d&&n!=0x9d&&n!=0x2a&&n!=0x36&&n!=0x38&&n!=0xb8&&n!=0xdb&&n!=0xdc&&n!=0xdd;
}
/* Preserve Shift (native fast movement), Alt shortcuts and Ctrl+letter
   commands such as Save. Ctrl+Up/Down consumes Ctrl when recalling E/Q. */
static unsigned editor_key_swap(unsigned scan,unsigned modifiers,unsigned *consume_ctrl){
 unsigned i;*consume_ctrl=0;
 if(modifiers&3)return scan; /* Alt / Windows */
 if(scan==0xc8||scan==0xd0){
  i=(scan==0xd0);if(modifiers&4){i+=4;*consume_ctrl=1;}return editor_keys[i];
 }
 if(modifiers&4)return scan;
 if(scan==0xcb)return editor_keys[2];if(scan==0xcd)return editor_keys[3];
 for(i=0;i<6;i++)if(scan==editor_keys[i])return 0;
 return scan;
}
