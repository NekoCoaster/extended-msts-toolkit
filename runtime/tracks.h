/* MIT. Conservative text track-database preflight; no game files are changed. */
#include <stdlib.h>
#define TRACK_IDS 1048576
#define TRACK_MASK (TRACK_IDS/8)
typedef struct {char *p;int bad;char token[512];} TrackText;
static int track_token(TrackText *t){char *p=t->p;unsigned n=0;int quoted=0;
 while(*p&&((unsigned char)*p<=32))p++;
 if(!*p){t->p=p;return 0;}
 if(*p=='('||*p==')'){t->token[0]=*p++;t->token[1]=0;t->p=p;return 1;}
 if(*p=='"'){quoted=1;p++;}
 while(*p&&(quoted?*p!='"':((unsigned char)*p>32&&*p!='('&&*p!=')'))){if(n+1<sizeof(t->token))t->token[n++]=*p;else t->bad=1;p++;}
 if(quoted){if(*p!='"')t->bad=1;else p++;}t->token[n]=0;t->p=p;return 1;
}
static int track_skip(TrackText *t){int depth=1;while(depth&&track_token(t)){if(!strcmp(t->token,"("))depth++;else if(!strcmp(t->token,")"))depth--;if(depth>128)return 0;}return !depth&&!t->bad;}
static int track_next(TrackText *t){while(track_token(t)){if(!lstrcmpiA(t->token,"_Skip")||!lstrcmpiA(t->token,"_INFO")||!lstrcmpiA(t->token,"Comment")){if(!track_token(t)||strcmp(t->token,"(")||!track_skip(t)){t->bad=1;return 0;}continue;}return 1;}return 0;}
static int track_number(const char *s,unsigned *value){char *end;unsigned long v;if(*s<'0'||*s>'9')return 0;v=strtoul(s,&end,10);if(*end||v>=TRACK_IDS)return 0;*value=v;return 1;}
static void track_set(unsigned char *mask,unsigned id){mask[id>>3]|=1<<(id&7);}
static int track_has(const unsigned char *mask,unsigned id){return mask[id>>3]&(1<<(id&7));}
static char *track_read(const WCHAR *path){HANDLE f;DWORD n,got,i;unsigned char *raw;char *out=NULL;
 f=CreateFileW(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);if(f==INVALID_HANDLE_VALUE)return NULL;n=GetFileSize(f,NULL);
 if(n<32||n>32*1024*1024){CloseHandle(f);return NULL;}raw=HeapAlloc(GetProcessHeap(),0,n+2);if(!raw){CloseHandle(f);return NULL;}
 if(ReadFile(f,raw,n,&got,NULL)&&got==n){raw[n]=raw[n+1]=0;
  if(raw[0]==255&&raw[1]==254){if(n%2==0){out=HeapAlloc(GetProcessHeap(),0,n/2+1);if(out){for(i=2;i<n;i+=2)out[(i-2)/2]=raw[i+1]?'?':raw[i];out[(n-2)/2]=0;}}}
  else{out=(char*)raw;raw=NULL;}
 }CloseHandle(f);if(raw)HeapFree(GetProcessHeap(),0,raw);
 if(out&&(strncmp(out,"SIMISA@@@@@@@@@@",16)||!strstr(out,"______"))){HeapFree(GetProcessHeap(),0,out);out=NULL;}return out;
}
static int track_definitions(char *text,unsigned char *mask){TrackText t;unsigned id,count=0;memset(&t,0,sizeof(t));t.p=text;
 while(track_next(&t)){if(lstrcmpiA(t.token,"TrackSection"))continue;
  if(!track_next(&t)||strcmp(t.token,"(")||!track_next(&t))return 0;
  if(!lstrcmpiA(t.token,"SectionCurve")){if(!track_next(&t)||strcmp(t.token,"(")||!track_skip(&t)||!track_next(&t))return 0;}
  if(!track_number(t.token,&id))return 0;track_set(mask,id);count++;
 }return count&&!t.bad;
}
/* Return -1 for unsupported/malformed data, 0 for resolved, 1 for missing. */
static int track_missing(char *text,const unsigned char *global,const unsigned char *local,unsigned *missing){TrackText t;unsigned count,i,j,id=0,groups=0;int found=0;char *end;memset(&t,0,sizeof(t));t.p=text;
 while(track_next(&t)){if(lstrcmpiA(t.token,"TrVectorSections"))continue;groups++;
  if(!track_next(&t)||strcmp(t.token,"(")||!track_next(&t)||!track_number(t.token,&count))return -1;
  for(i=0;i<count;i++)for(j=0;j<16;j++){if(!track_next(&t))return -1;if(!j){if(!track_number(t.token,&id))return -1;if(!track_has(global,id)&&!track_has(local,id)&&!found){*missing=id;found=1;}}else{strtod(t.token,&end);if(end==t.token||*end)return -1;}}
  if(!track_next(&t)||strcmp(t.token,")"))return -1;
 }return t.bad||!groups?-1:found;
}
static int track_path(WCHAR *out,const WCHAR *base,const WCHAR *tail){if(wcslen(base)+wcslen(tail)>=MAX_PATH)return 0;wcscpy(out,base);wcscat(out,tail);return 1;}
static int track_preflight(const WCHAR *base,WCHAR *route,unsigned *missing){WCHAR path[MAX_PATH],directory[MAX_PATH],search[MAX_PATH];WIN32_FIND_DATAW rd,db;HANDLE routes,databases;unsigned char *global,*local;char *text;int result=0,local_ok;
 global=HeapAlloc(GetProcessHeap(),HEAP_ZERO_MEMORY,TRACK_MASK);local=HeapAlloc(GetProcessHeap(),HEAP_ZERO_MEMORY,TRACK_MASK);if(!global||!local)goto done;
 if(!track_path(path,base,L"GLOBAL\\tsection.dat")||!(text=track_read(path)))goto done;
 local_ok=track_definitions(text,global);HeapFree(GetProcessHeap(),0,text);if(!local_ok)goto done;
 if(!track_path(search,base,L"ROUTES\\*"))goto done;routes=FindFirstFileW(search,&rd);if(routes==INVALID_HANDLE_VALUE)goto done;
 do{if(!(rd.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)||rd.cFileName[0]=='.')continue;
  if(wcslen(base)+wcslen(rd.cFileName)+20>=MAX_PATH)continue;wcscpy(directory,base);wcscat(directory,L"ROUTES\\");wcscat(directory,rd.cFileName);wcscat(directory,L"\\");
  memset(local,0,TRACK_MASK);track_path(path,directory,L"tsection.dat");local_ok=1;
  if(GetFileAttributesW(path)!=INVALID_FILE_ATTRIBUTES){text=track_read(path);if(!text)local_ok=0;else{local_ok=track_definitions(text,local);HeapFree(GetProcessHeap(),0,text);}}
  if(!local_ok)continue;track_path(search,directory,L"*.tdb");databases=FindFirstFileW(search,&db);if(databases==INVALID_HANDLE_VALUE)continue;
  do{if(db.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)continue;if(!track_path(path,directory,db.cFileName))continue;text=track_read(path);if(!text)continue;
   result=track_missing(text,global,local,missing)==1;HeapFree(GetProcessHeap(),0,text);if(result){wcscpy(route,rd.cFileName);break;}
  }while(FindNextFileW(databases,&db));FindClose(databases);if(result)break;
 }while(FindNextFileW(routes,&rd));FindClose(routes);
 done:if(global)HeapFree(GetProcessHeap(),0,global);if(local)HeapFree(GetProcessHeap(),0,local);return result;
}
static void track_check_startup(const WCHAR *base){WCHAR route[MAX_PATH],message[1024];unsigned missing;
 if(!track_preflight(base,route,&missing))return;
 if(!lstrcmpiW(route,L"LGVMed"))swprintf(message,L"Xtracks is required for route %ls. Please refer to the route author's README and install the appropriate Xtracks version.\n\nThe installed track database is missing section %u required by this route. MSTS will now close.",route,missing);
 else swprintf(message,L"Route %ls requires track definitions missing from this installation (section %u).\n\nPlease refer to the route author's README and install its required track add-ons and compatible global tsection.dat. MSTS will now close.",route,missing);
 MessageBoxW(NULL,message,L"NEMT - Missing route track dependency",MB_OK|MB_ICONERROR|MB_SETFOREGROUND);ExitProcess(1);
}
