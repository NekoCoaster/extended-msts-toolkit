/*
 * Neko's Extended MSTS Toolkit (NEMT) native control panel.
 * MIT License.  Intentionally plain Win32/C for Windows XP SP3 and later.
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0501
#define WINVER 0x0501
#include <windows.h>
#include <commdlg.h>
#include <commctrl.h>
#include <stddef.h>
#include <limits.h>
#include <shellapi.h>
#include <tlhelp32.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#ifndef BCM_SETSHIELD
#define BCM_SETSHIELD 0x160C
#endif
#ifndef PROCESS_QUERY_LIMITED_INFORMATION
#define PROCESS_QUERY_LIMITED_INFORMATION 0x1000
#endif

#define APP_TITLE "Neko's Extended MSTS Toolkit"
#define TRAIN_SIZE 4091953L
#define MAX_TEXT 1024

/* UI ids */
enum {
 IDC_PATH=100, IDC_BROWSE, IDC_STATUS, IDC_RECOMMENDED, IDC_APPLY, IDC_UNINSTALL, IDC_CLOSE,
 IDC_PCORES=200, IDC_SKIPMOVIE, IDC_WINDOW, IDC_UNLOCKFPS, IDC_VSYNC, IDC_VERBOSE, IDC_CAB,
 IDC_BACKGROUND, IDC_REDSIGNAL, IDC_EDITORWINDOWS, IDC_EDITORTOOLS, IDC_EDITORAUDIO,
 IDC_EDITORKEYS, IDC_EDITORPAN, IDC_TIMEOUT, IDC_CAMERA, IDC_CRAWL, IDC_COUNTERTILT,
 IDC_STRENGTH, IDC_STRENGTHVALUE, IDC_HUDLEFT, IDC_LOGGING,
 IDC_TITLE=400, IDC_MESSAGE, IDC_CRAWLHINT, IDC_STRENGTHLABEL, IDC_ZERO, IDC_HUNDRED,
 IDC_ANCHORLABEL, IDC_SPACE, IDC_CREDIT, IDC_GITHUB, IDC_WIDENOTE, IDC_WIDEDOWNLOAD, IDC_WIDEGUIDE
};

typedef struct {
 uint32_t h[8]; uint64_t bits; unsigned char block[64]; unsigned used;
} SHA256;

typedef struct {
 char path[MAX_PATH];
 char version[96];
 char sha[65];
 int valid, widescreen, laa;
} MstsInfo;

#include "settings_model.h"

static HINSTANCE g_instance;
static HWND g_main, g_path, g_status, g_strength, g_message;
static char g_root[MAX_PATH], g_version[64]="dev";
static MstsInfo g_info;
static int g_loading, g_busy, g_cpu_supported;

/* ---------- SHA-256: compact public-domain style implementation ---------- */
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static const uint32_t K256[64]={
 0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
 0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
 0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
 0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
 0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
 0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
 0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
 0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static void sha_block(SHA256*s,const unsigned char*p){uint32_t w[64],a,b,c,d,e,f,g,h,t1,t2;int i;for(i=0;i<16;i++)w[i]=((uint32_t)p[i*4]<<24)|((uint32_t)p[i*4+1]<<16)|((uint32_t)p[i*4+2]<<8)|p[i*4+3];for(i=16;i<64;i++){uint32_t x=w[i-15],y=w[i-2];w[i]=(ROR(x,7)^ROR(x,18)^(x>>3))+w[i-16]+(ROR(y,17)^ROR(y,19)^(y>>10))+w[i-7];}a=s->h[0];b=s->h[1];c=s->h[2];d=s->h[3];e=s->h[4];f=s->h[5];g=s->h[6];h=s->h[7];for(i=0;i<64;i++){t1=h+(ROR(e,6)^ROR(e,11)^ROR(e,25))+((e&f)^((~e)&g))+K256[i]+w[i];t2=(ROR(a,2)^ROR(a,13)^ROR(a,22))+((a&b)^(a&c)^(b&c));h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;}s->h[0]+=a;s->h[1]+=b;s->h[2]+=c;s->h[3]+=d;s->h[4]+=e;s->h[5]+=f;s->h[6]+=g;s->h[7]+=h;}
static void sha_init(SHA256*s){static const uint32_t h[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};memcpy(s->h,h,sizeof(h));s->bits=0;s->used=0;}
static void sha_update(SHA256*s,const void*data,size_t n){const unsigned char*p=(const unsigned char*)data;s->bits+=(uint64_t)n*8;while(n){unsigned take=64-s->used;if(take>n)take=(unsigned)n;memcpy(s->block+s->used,p,take);s->used+=take;p+=take;n-=take;if(s->used==64){sha_block(s,s->block);s->used=0;}}}
static void sha_final(SHA256*s,unsigned char out[32]){uint64_t bits=s->bits;int i;s->block[s->used++]=0x80;if(s->used>56){while(s->used<64)s->block[s->used++]=0;sha_block(s,s->block);s->used=0;}while(s->used<56)s->block[s->used++]=0;for(i=7;i>=0;i--)s->block[s->used++]=(unsigned char)(bits>>(i*8));sha_block(s,s->block);for(i=0;i<8;i++){out[i*4]=(unsigned char)(s->h[i]>>24);out[i*4+1]=(unsigned char)(s->h[i]>>16);out[i*4+2]=(unsigned char)(s->h[i]>>8);out[i*4+3]=(unsigned char)s->h[i];}}
static void hex32(const unsigned char in[32],char out[65]){static const char*x="0123456789abcdef";int i;for(i=0;i<32;i++){out[i*2]=x[in[i]>>4];out[i*2+1]=x[in[i]&15];}out[64]=0;}
static int sha_bytes(const void*p,size_t n,char out[65]){SHA256 s;unsigned char h[32];sha_init(&s);sha_update(&s,p,n);sha_final(&s,h);hex32(h,out);return 1;}
static int sha_file(const char*path,char out[65]){FILE*f=fopen(path,"rb");unsigned char buf[32768],h[32];size_t n;SHA256 s;if(!f)return 0;sha_init(&s);while((n=fread(buf,1,sizeof(buf),f))>0)sha_update(&s,buf,n);if(ferror(f)){fclose(f);return 0;}fclose(f);sha_final(&s,h);hex32(h,out);return 1;}

/* ---------- small filesystem/string helpers ---------- */
static void set_error(char*err,size_t cap,const char*text){if(cap){lstrcpynA(err,text,(int)cap);err[cap-1]=0;}}
static int exists_file(const char*p){DWORD a=GetFileAttributesA(p);return a!=INVALID_FILE_ATTRIBUTES&&!(a&FILE_ATTRIBUTE_DIRECTORY);}
static int exists_dir(const char*p){DWORD a=GetFileAttributesA(p);return a!=INVALID_FILE_ATTRIBUTES&&(a&FILE_ATTRIBUTE_DIRECTORY);}
static void parent_dir(const char*path,char*out){char*s;lstrcpynA(out,path,MAX_PATH);s=strrchr(out,'\\');if(s)*s=0;else out[0]=0;}
static int join_path(char*out,const char*a,const char*b){size_t n=strlen(a),m=strlen(b);if(n+m+2>=MAX_PATH)return 0;strcpy(out,a);if(n&&out[n-1]!='\\'&&out[n-1]!='/')strcat(out,"\\");strcat(out,b);return 1;}
static int read_all(const char*path,unsigned char**data,DWORD*size){HANDLE h;DWORD total=0,n,z,high=0;unsigned char*p;h=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);if(h==INVALID_HANDLE_VALUE)return 0;z=GetFileSize(h,&high);if(z==INVALID_FILE_SIZE&&GetLastError()!=NO_ERROR){CloseHandle(h);return 0;}if(high!=0||z>0x7fffffffUL){CloseHandle(h);return 0;}p=(unsigned char*)malloc((size_t)z+1);if(!p){CloseHandle(h);return 0;}while(total<z){if(!ReadFile(h,p+total,z-total,&n,NULL)||!n){free(p);CloseHandle(h);return 0;}total+=n;}p[total]=0;CloseHandle(h);*data=p;*size=total;return 1;}
static int write_all(const char*path,const void*data,DWORD size){HANDLE h=CreateFileA(path,GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);DWORD off=0,n;if(h==INVALID_HANDLE_VALUE)return 0;while(off<size){if(!WriteFile(h,(const char*)data+off,size-off,&n,NULL)||!n){CloseHandle(h);return 0;}off+=n;}if(!FlushFileBuffers(h)){CloseHandle(h);return 0;}CloseHandle(h);return 1;}
static void trim(char*s){char*p=s,*e;while(*p==' '||*p=='\t'||*p=='\r'||*p=='\n')p++;if(p!=s)memmove(s,p,strlen(p)+1);e=s+strlen(s);while(e>s&&(e[-1]==' '||e[-1]=='\t'||e[-1]=='\r'||e[-1]=='\n'))*--e=0;}
static int true_text(const char*s){return !lstrcmpiA(s,"true")||!strcmp(s,"1");}
static int load_text(const char*path,char**text){unsigned char*d;DWORD n;if(!read_all(path,&d,&n))return 0;*text=(char*)d;return 1;}

/* ---------- executable validation ---------- */
static const unsigned char timeout_before[]={0x74,0x16}, timeout_after[]={0xeb,0x28};
static const unsigned char camera_before[]={0x0f,0x84,0x55,0x03,0,0}, camera_after[]={0x90,0x90,0x90,0x90,0x90,0x90};
static int bytes_eq(const unsigned char*p,const unsigned char*q,int n){return memcmp(p,q,(size_t)n)==0;}
static int inspect_msts(const char*path,MstsInfo*out,char*err,size_t errcap){unsigned char*b,*norm;DWORD n;char hash[65];int wide=0,laa;if(!path||!*path){set_error(err,errcap,"Choose a train.exe file first.");return 0;}{WIN32_FILE_ATTRIBUTE_DATA a; const char *ext=strrchr(path,'.');
 if(!ext || lstrcmpiA(ext,".exe")){set_error(err,errcap,"Choose one executable (.exe) file.");return 0;}
 if(!GetFileAttributesExA(path,GetFileExInfoStandard,&a)){set_error(err,errcap,"Could not read the selected executable.");return 0;}
 if(a.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY || a.nFileSizeHigh || a.nFileSizeLow!=TRAIN_SIZE){set_error(err,errcap,"Unsupported executable. NEMT supports the identified MSTS Bin 1.8.052113 builds only.");return 0;}}
 if(!read_all(path,&b,&n)){set_error(err,errcap,"Could not read the selected executable.");return 0;}if(n!=TRAIN_SIZE){free(b);set_error(err,errcap,"Unsupported executable. NEMT supports the identified MSTS Bin 1.8.052113 builds only.");return 0;}if(!(bytes_eq(b+0x1862dc,timeout_before,2))||!(bytes_eq(b+0x11c98c,camera_before,6))){if(bytes_eq(b+0x1862dc,timeout_after,2)||bytes_eq(b+0x11c98c,camera_after,6))set_error(err,errcap,"Previously modified executable. Restore it with its original patcher before installing NEMT.");else set_error(err,errcap,"Unsupported patch bytes. No changes were made.");free(b);return 0;}norm=(unsigned char*)malloc(n);if(!norm){free(b);set_error(err,errcap,"Not enough memory to inspect train.exe.");return 0;}memcpy(norm,b,n);norm[0x116]&=0xdf;sha_bytes(norm,n,hash);if(!strcmp(hash,"69218fce876298c684a2140c7d3925a452c47bb10037ffd8c491f65c5c0c6e7a"))wide=0;else if(!strcmp(hash,"1b041ecf4b2d2a7306218efa1d7418fd87dc21dc4b2d00056cb5749084fe55a4"))wide=1;else{free(norm);free(b);set_error(err,errcap,"Unrecognized executable or additional modifications. No changes were made.");return 0;}laa=(b[0x116]&0x20)!=0;memset(out,0,sizeof(*out));{DWORD len=GetFullPathNameA(path,MAX_PATH,out->path,NULL);if(!len||len>=MAX_PATH){free(norm);free(b);set_error(err,errcap,"The executable path is too long.");return 0;}}out->widescreen=wide;out->laa=laa;out->valid=1;sha_bytes(b,n,out->sha);lstrcpyA(out->version,"MSTS Bin 1.8.052113");if(wide)lstrcatA(out->version," Widescreen");if(laa)lstrcatA(out->version," + LAA");free(norm);free(b);return 1;}

/* ---------- OS capability / process checks ---------- */
typedef BOOL (WINAPI *CpuSetFn)(void*,ULONG,PULONG,HANDLE,ULONG);
static int hybrid_cpu_supported(void){HMODULE k=GetModuleHandleA("kernel32.dll");CpuSetFn fn;ULONG bytes=0,ret=0,off=0;unsigned char*buf;int found=0,min=255,max=0;if(!k)return 0;fn=(CpuSetFn)GetProcAddress(k,"GetSystemCpuSetInformation");if(!fn)return 0;fn(NULL,0,&bytes,NULL,0);if(!bytes||bytes>1024*1024)return 0;buf=(unsigned char*)malloc(bytes);if(!buf)return 0;if(!fn(buf,bytes,&ret,NULL,0)||ret>bytes){free(buf);return 0;}while(off+8<=ret){ULONG size=*(ULONG*)(buf+off),type=*(ULONG*)(buf+off+4);if(size<8||size>ret-off){free(buf);return 0;}if(type==0){if(size<32){free(buf);return 0;}USHORT group=*(USHORT*)(buf+off+12);BYTE logical=buf[off+14],eff=buf[off+18];if(group!=0||logical>=32){free(buf);return 0;}if(eff<min)min=eff;if(eff>max)max=eff;found=1;}off+=size;}free(buf);return off==ret&&found&&min!=max;}
typedef BOOL (WINAPI *QueryImageFn)(HANDLE,DWORD,LPSTR,PDWORD);
typedef DWORD (WINAPI *ModuleImageFn)(HANDLE,HMODULE,LPSTR,DWORD);
static int train_running(const char *selected) {
    HANDLE snap; PROCESSENTRY32 pe; const char *name=strrchr(selected,'\\');
    HMODULE kernel=GetModuleHandleA("kernel32.dll"),psapi=NULL;
    QueryImageFn query=kernel?(QueryImageFn)GetProcAddress(kernel,"QueryFullProcessImageNameA"):NULL;
    ModuleImageFn module=NULL;
    char lib[MAX_PATH]; int running=0;
    name=name?name+1:selected;
    /* Use an absolute system DLL path for the XP fallback. */
    if(GetSystemDirectoryA(lib,MAX_PATH)>0 && strlen(lib)+11<MAX_PATH) {
        strcat(lib,"\\psapi.dll");psapi=LoadLibraryA(lib);
        if(psapi) module=(ModuleImageFn)GetProcAddress(psapi,"GetModuleFileNameExA");
    }
    snap=CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS,0);
    if(snap==INVALID_HANDLE_VALUE) {if(psapi)FreeLibrary(psapi);return 1;}
    memset(&pe,0,sizeof(pe));pe.dwSize=sizeof(pe);
    if(!Process32First(snap,&pe)) running=GetLastError()!=ERROR_NO_MORE_FILES;
    else do {
        if(!lstrcmpiA(pe.szExeFile,name)) {
            HANDLE process=NULL; char path[MAX_PATH]="";DWORD count=MAX_PATH;int known=0;
            if(query) {
                process=OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION,FALSE,pe.th32ProcessID);
                if(process) {known=query(process,0,path,&count)!=0;CloseHandle(process);}
            }
            if(!known && module) {
                process=OpenProcess(PROCESS_QUERY_INFORMATION|PROCESS_VM_READ,FALSE,pe.th32ProcessID);
                if(process) {count=module(process,NULL,path,MAX_PATH);known=count>0 && count<MAX_PATH;CloseHandle(process);}
            }
            /* Inaccessible matching names block conservatively, like PS1. */
            if(!known || !lstrcmpiA(path,selected)) {running=1;break;}
        }
    } while(Process32Next(snap,&pe));
    if(!running && GetLastError()!=ERROR_NO_MORE_FILES) running=1;
    CloseHandle(snap);if(psapi)FreeLibrary(psapi);return running;
}

/* ---------- settings ---------- */

static void ini_get(const char*path,const char*sec,const char*key,const char*def,char*out,int cap){GetPrivateProfileStringA(sec,key,def,out,cap,path);trim(out);}
static const char*bt(int v);
static void load_settings(const char*path,Settings*s){char v[64];settings_defaults(s);if(!exists_file(path))return;
#define GB(sec,key,field) ini_get(path,sec,key,bt(s->field),v,sizeof(v));s->field=true_text(v)
 GB("Startup","PreferPCores",prefer_pcores);GB("Startup","SkipStartupMovie",skip_movie);GB("Startup","UnlockFPS",unlock_fps);GB("Startup","LimitToVSync",limit_vsync);GB("Startup","VerboseLoading",verbose_loading);GB("Startup","WriteLog",startup_log);
 GB("Window","Enabled",window_features);GB("Window","CenterWindowed",center_windowed);GB("Cab","CorrectNeedleAspect",cab_needles);GB("Audio","UnmuteInBackground",background_audio);GB("Activity","IgnoreRedSignal",ignore_red_signal);
 GB("Editors","ResizableViewports",editor_windows);GB("Editors","FreeToolWindows",editor_tools);GB("Editors","SmoothIdleAudio",editor_audio);GB("Editors","SwapArrowKeys",editor_keys);GB("Editors","UnlimitedMousePan",editor_pan);
 GB("Derailment","PreventActivityEnd",prevent_end);GB("Derailment","UnlockCameras",unlock_cameras);GB("Derailment","EnableCrawl",crawl);GB("Derailment","CounterTilt",counter_tilt);GB("Diagnostics","WriteStatusJson",write_status);
#undef GB
 ini_get(path,"Derailment","CrawlStrength","10",v,sizeof(v));s->strength=atoi(v);if(s->strength<0||s->strength>100)s->strength=10;
 ini_get(path,"Diagnostics","CrawlHUDAnchor","BottomLeft",v,sizeof(v));s->hud_left=lstrcmpiA(v,"BottomRight")!=0;
 ini_get(path,"Startup","MaxLogSizeKB","8192",v,sizeof(v));s->max_log_kb=atoi(v);if(s->max_log_kb<4||s->max_log_kb>65536)s->max_log_kb=8192;
 ini_get(path,"Startup","MaxBackupLogs","0",v,sizeof(v));s->max_backup_logs=atoi(v);if(s->max_backup_logs<0||s->max_backup_logs>20)s->max_backup_logs=0;
 ini_get(path,"Derailment","DerailKey","BACKSLASH",s->derail_key,sizeof(s->derail_key));
 ini_get(path,"Editors","RE_CAM_FORWARD","w",s->key_forward,sizeof(s->key_forward));ini_get(path,"Editors","RE_CAM_BACKWARD","s",s->key_backward,sizeof(s->key_backward));ini_get(path,"Editors","RE_CAM_LEFT","a",s->key_left,sizeof(s->key_left));ini_get(path,"Editors","RE_CAM_RIGHT","d",s->key_right,sizeof(s->key_right));ini_get(path,"Editors","RE_CAM_UP","e",s->key_up,sizeof(s->key_up));ini_get(path,"Editors","RE_CAM_DOWN","q",s->key_down,sizeof(s->key_down));
}
static const char*bt(int v){return v?"true":"false";}
static int write_settings(const char*path,const Settings*s){char b[8192];int n=_snprintf(b,sizeof(b),
 "[Startup]\r\nPreferPCores=%s\r\nVerboseLoading=%s\r\nWriteLog=%s\r\nLimitToVSync=%s\r\nUnlockFPS=%s\r\nSkipStartupMovie=%s\r\nRestoreMovieFocus=%s\r\nMaxLogSizeKB=%d\r\nMaxBackupLogs=%d\r\n\r\n"
 "[Window]\r\nEnabled=%s\r\nCenterWindowed=%s\r\n\r\n"
 "[Derailment]\r\nPreventActivityEnd=%s\r\nUnlockCameras=%s\r\nEnableCrawl=%s\r\nCrawlStrength=%d\r\nDerailKey=%s\r\nCounterTilt=%s\r\n\r\n"
 "[Diagnostics]\r\nWriteStatusJson=%s\r\nShowCrawlHUD=%s\r\nCrawlHUDAnchor=%s\r\n\r\n"
 "[Cab]\r\nCorrectNeedleAspect=%s\r\n\r\n[Audio]\r\nUnmuteInBackground=%s\r\n\r\n[Activity]\r\nIgnoreRedSignal=%s\r\n\r\n"
 "[Editors]\r\nResizableViewports=%s\r\nFreeToolWindows=%s\r\nSmoothIdleAudio=%s\r\nUnlimitedMousePan=%s\r\nSwapArrowKeys=%s\r\nRE_CAM_FORWARD=%s\r\nRE_CAM_BACKWARD=%s\r\nRE_CAM_LEFT=%s\r\nRE_CAM_RIGHT=%s\r\nRE_CAM_UP=%s\r\nRE_CAM_DOWN=%s\r\n",
 bt(s->prefer_pcores),bt(s->verbose_loading),bt(s->startup_log),bt(s->limit_vsync),bt(s->unlock_fps),bt(s->skip_movie),bt(s->skip_movie),s->max_log_kb,s->max_backup_logs,
 bt(s->window_features),bt(s->center_windowed),bt(s->prevent_end),bt(s->unlock_cameras),bt(s->crawl),s->strength,s->derail_key,bt(s->counter_tilt),bt(s->write_status),bt(s->crawl),s->hud_left?"BottomLeft":"BottomRight",bt(s->cab_needles),bt(s->background_audio),bt(s->ignore_red_signal),bt(s->editor_windows),bt(s->editor_tools),bt(s->editor_audio),bt(s->editor_pan),bt(s->editor_keys),s->key_forward,s->key_backward,s->key_left,s->key_right,s->key_up,s->key_down);
 if(n<0||n>=(int)sizeof(b))return 0;return write_all(path,b,(DWORD)n);}

/* ---------- installation ---------- */
/* Read and validate ownership before using either the GUI state or installer.
 * Return 0 for no record, 1 for an owned record, -1 for an invalid/unreadable one.
 */
static int read_record(const char *game,JsonRecord *doc,char **text,char *err,size_t cap) {
    char path[MAX_PATH],product[32];
    WIN32_FILE_ATTRIBUTE_DATA a;
    const JsonValue *enabled;
    *text=NULL;
    if(!join_path(path,game,"NEMT\\installation.json")) goto invalid;
    if(!GetFileAttributesExA(path,GetFileExInfoStandard,&a)) {
        DWORD code=GetLastError();
        if(code==ERROR_FILE_NOT_FOUND || code==ERROR_PATH_NOT_FOUND) return 0;
        goto invalid;
    }
    if((a.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) || a.nFileSizeHigh || a.nFileSizeLow>1048576) goto invalid;
    if(!load_text(path,text) || !json_record_parse(*text,doc)) goto invalid;
    if(!json_text(doc,"product",product,sizeof(product)) || strcmp(product,"NEMT") || json_int(doc,"schema",0)!=1) goto invalid;
    enabled=json_member(doc,"enabled");
    if(!enabled || (enabled->type!=J_TRUE && enabled->type!=J_FALSE)) goto invalid;
    return 1;
invalid:
    free(*text); *text=NULL;
    set_error(err,cap,"Unrecognized or unreadable NEMT ownership record. No changes made.");
    return -1;
}
static int is_hash(const char *value) {
    int i;
    if(strlen(value)!=64) return 0;
    for(i=0;i<64;++i) if(json_hex(value[i])<0) return 0;
    return 1;
}
static int expected_runtime_hash(char out[65]) {
    char p[MAX_PATH],*text=NULL;
    JsonRecord doc;
    int ok;
    if(!join_path(p,g_root,"runtime\\integrity.json") || !load_text(p,&text)) return 0;
    ok=json_record_parse(text,&doc) && json_text(&doc,"DINPUT.dll",out,65) && is_hash(out);
    free(text); return ok;
}
/* Preserve the PS1 split: manifest fields drive the main controls; the enabled
 * installation's INI supplies the fields that supported hand-editing. */
static int load_selection_settings(const MstsInfo *info,Settings *s,char *err,size_t cap) {
    char game[MAX_PATH],ini[MAX_PATH],*text=NULL;
    JsonRecord doc;
    Settings extra;
    int owned;
    parent_dir(info->path,game);
    owned=read_record(game,&doc,&text,err,cap);
    if(owned<0) return 0;
    settings_from_manifest(owned?&doc:NULL,s);
    if(owned && json_bool(&doc,"enabled",0) && join_path(ini,game,"NEMT\\settings.ini") && exists_file(ini)) {
        load_settings(ini,&extra);
        s->prefer_pcores=extra.prefer_pcores;
        s->skip_movie=extra.skip_movie;
        /* A missing key retains the manifest fallback, unlike a false key. */
        {char value[64];ini_get(ini,"Startup","LimitToVSync",bt(s->limit_vsync),value,sizeof(value));s->limit_vsync=true_text(value);}
        s->counter_tilt=extra.counter_tilt;
        s->cab_needles=info->widescreen && extra.cab_needles;
        s->background_audio=extra.background_audio; s->ignore_red_signal=extra.ignore_red_signal;
        s->editor_windows=extra.editor_windows; s->editor_tools=extra.editor_tools;
        s->editor_audio=extra.editor_audio; s->editor_keys=extra.editor_keys; s->editor_pan=extra.editor_pan;
    }
    free(text); return 1;
}
static int copy_verified(const char*src,const char*dst,const char*expected,char*err,size_t cap){char tmp[MAX_PATH],hash[65];if(_snprintf(tmp,sizeof(tmp),"%s.nemt.tmp",dst)<0){set_error(err,cap,"Path is too long.");return 0;}DeleteFileA(tmp);if(!CopyFileA(src,tmp,FALSE)){set_error(err,cap,"Could not copy the native runtime.");return 0;}if(!sha_file(tmp,hash)||lstrcmpiA(hash,expected)){DeleteFileA(tmp);set_error(err,cap,"Copied runtime verification failed.");return 0;}if(!MoveFileExA(tmp,dst,MOVEFILE_REPLACE_EXISTING|MOVEFILE_COPY_ALLOWED|MOVEFILE_WRITE_THROUGH)){DeleteFileA(tmp);set_error(err,cap,"Could not install DINPUT.dll.");return 0;}return 1;}
static int write_atomic(const char*path,const void*data,DWORD size){char tmp[MAX_PATH];if(_snprintf(tmp,sizeof(tmp),"%s.nemt.tmp",path)<0)return 0;DeleteFileA(tmp);if(!write_all(tmp,data,size)){DeleteFileA(tmp);return 0;}if(!MoveFileExA(tmp,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_COPY_ALLOWED|MOVEFILE_WRITE_THROUGH)){DeleteFileA(tmp);return 0;}return 1;}
static int ensure_dir(const char*p){if(exists_dir(p))return 1;return CreateDirectoryA(p,NULL)!=0;}
static int format_manifest(char*b,int cap,const Settings*s,int enabled,const char*proxy_hash){
 return _snprintf(b,cap,
  "{\r\n  \"schema\": 1,\r\n  \"product\": \"NEMT\",\r\n  \"version\": \"%s\",\r\n  \"runtime\": \"nemt-native\",\r\n  \"enabled\": %s,\r\n  \"strength\": %d,\r\n  \"preventEnd\": %s,\r\n  \"unlockCameras\": %s,\r\n  \"crawl\": %s,\r\n  \"preferPCores\": %s,\r\n  \"counterTilt\": %s,\r\n  \"windowFeatures\": %s,\r\n  \"editorWindows\": %s,\r\n  \"freeEditorTools\": %s,\r\n  \"smoothEditorAudio\": %s,\r\n  \"swapEditorKeys\": %s,\r\n  \"unlimitedEditorPan\": %s,\r\n  \"verboseLoading\": %s,\r\n  \"startupLog\": %s,\r\n  \"unlockFPS\": %s,\r\n  \"limitToVSync\": %s,\r\n  \"crawlHUD\": %s,\r\n  \"crawlHUDAnchor\": \"%s\",\r\n  \"proxyHash\": \"%s\",\r\n  \"files\": {}\r\n}\r\n",
  g_version,bt(enabled),s->strength,bt(s->prevent_end),bt(s->unlock_cameras),bt(s->crawl),bt(s->prefer_pcores),bt(s->counter_tilt),bt(s->window_features),
  bt(s->editor_windows),bt(s->editor_tools),bt(s->editor_audio),bt(s->editor_keys),bt(s->editor_pan),bt(s->verbose_loading),bt(s->startup_log),bt(s->unlock_fps),bt(s->limit_vsync),bt(s->crawl),s->hud_left?"BottomLeft":"BottomRight",proxy_hash?proxy_hash:"");
}
/* Multi-file save with rollback. Stage writes individually, and keep bounded
 * snapshots of the four owned files until the entire operation succeeds. */
typedef struct {
    char path[MAX_PATH];
    unsigned char *bytes;
    DWORD size;
    int existed,changed;
} FileSnapshot;
static int snapshot_file(FileSnapshot *s,const char *path) {
    WIN32_FILE_ATTRIBUTE_DATA a;
    memset(s,0,sizeof(*s)); lstrcpynA(s->path,path,MAX_PATH);
    if(!GetFileAttributesExA(path,GetFileExInfoStandard,&a)) {
        DWORD code=GetLastError();
        return code==ERROR_FILE_NOT_FOUND || code==ERROR_PATH_NOT_FOUND;
    }
    if((a.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY) || a.nFileSizeHigh || a.nFileSizeLow>8*1024*1024) return 0;
    s->existed=1;
    return read_all(path,&s->bytes,&s->size);
}
static int rollback_files(FileSnapshot *s,int count) {
    int i,ok=1;
    for(i=count-1;i>=0;--i) if(s[i].changed) {
        if(s[i].existed) { if(!write_atomic(s[i].path,s[i].bytes,s[i].size)) ok=0; }
        else if(exists_file(s[i].path) && !DeleteFileA(s[i].path)) ok=0;
    }
    return ok;
}
static int disable_record(const char *manifest,const JsonRecord *doc,const char *text) {
    const JsonValue *v=json_member(doc,"enabled");
    size_t before,after; char *updated; int ok;
    if(!v) return 0;
    before=(size_t)(v->p-text); after=strlen(v->p+v->n);
    updated=(char *)malloc(before+5+after+1);
    if(!updated) return 0;
    memcpy(updated,text,before); memcpy(updated+before,"false",5);
    memcpy(updated+before+5,v->p+v->n,after+1);
    ok=write_atomic(manifest,updated,(DWORD)(before+5+after));
    free(updated); return ok;
}
static int install_settings(const MstsInfo *info,const Settings *s,int remove,char *err,size_t cap) {
    char game[MAX_PATH],nemt[MAX_PATH],settings[MAX_PATH],manifest[MAX_PATH],status[MAX_PATH];
    char proxy[MAX_PATH],runtime[MAX_PATH],expected[65],current[65],old_proxy[65]="";
    char mbuf[4096],tmp[MAX_PATH]="",*record_text=NULL;
    JsonRecord record;
    FileSnapshot old[4];
    Settings safe=*s;
    int owned,mn,i,created=0,ok=0,changed=0;
    memset(old,0,sizeof(old));
    if(!info->valid || !sha_file(info->path,current) || lstrcmpiA(current,info->sha)) {
        set_error(err,cap,"The selected executable changed. Select it again."); return 0;
    }
    parent_dir(info->path,game);
    if(!join_path(nemt,game,"NEMT") || !join_path(settings,nemt,"settings.ini") ||
       !join_path(manifest,nemt,"installation.json") || !join_path(status,nemt,"status.json") ||
       !join_path(proxy,game,"DINPUT.dll") || strlen(manifest)+sizeof(".nemt.tmp")>MAX_PATH) {
        set_error(err,cap,"The selected installation path is too long."); return 0;
    }
    owned=read_record(game,&record,&record_text,err,cap);
    if(owned<0) return 0;
    if(train_running(info->path)) {set_error(err,cap,"The selected executable is running. Close MSTS before applying changes.");goto done;}
    if(owned) json_text(&record,"proxyHash",old_proxy,sizeof(old_proxy));
    if(exists_file(proxy) && (!owned || !is_hash(old_proxy) || !sha_file(proxy,current) || lstrcmpiA(current,old_proxy))) {
        set_error(err,cap,"Existing DINPUT.dll is unrelated or modified. It will not be changed.");goto done;
    }
    if(!remove && exists_dir(nemt) && !owned) {
        set_error(err,cap,"The existing NEMT folder is not owned by this installer.");goto done;
    }
    /* An uninstall with no ownership record must not delete an unrelated INI. */
    if(remove && !owned) {ok=1;goto done;}
    if(!remove) {
        if(safe.crawl) safe.prevent_end=1;
        if(!info->widescreen) safe.cab_needles=0;
        /* Unsupported CPU detection must NOT erase a saved preference. */
        if(!join_path(runtime,g_root,"runtime\\DINPUT.dll") || !expected_runtime_hash(expected) ||
           !sha_file(runtime,current) || lstrcmpiA(current,expected)) {
            set_error(err,cap,"Release DLL integrity mismatch or runtime/DINPUT.dll is missing.");goto done;
        }
    }
    if(!snapshot_file(&old[0],settings) || !snapshot_file(&old[1],proxy) ||
       !snapshot_file(&old[2],manifest) || !snapshot_file(&old[3],status)) {
        set_error(err,cap,"Could not snapshot the existing files (unreadable, locked or larger than 8 MB). No changes made.");goto done;
    }
    if(!sha_file(info->path,current) || lstrcmpiA(current,info->sha) || train_running(info->path)) {
        set_error(err,cap,"The executable changed or started during preparation. Select it again.");goto done;
    }
    if(remove) {
        if(old[1].existed) {
            if(!DeleteFileA(proxy)) {set_error(err,cap,"Could not remove DINPUT.dll.");goto rollback;}
            old[1].changed=1;
        }
        if(old[0].existed) {
            if(!DeleteFileA(settings)) {set_error(err,cap,"Could not remove settings.ini.");goto rollback;}
            old[0].changed=1;
        }
        if(!disable_record(manifest,&record,record_text)) {set_error(err,cap,"Could not update installation.json.");goto rollback;}
        old[2].changed=1;
        /* Preserve status/log diagnostics, as the PowerShell uninstaller did. */
    } else {
        if(!exists_dir(nemt)) {
            if(!ensure_dir(nemt)) {set_error(err,cap,"Could not create the NEMT folder. Check write permissions.");goto rollback;}
            created=1;
        }
        if(_snprintf(tmp,sizeof(tmp),"%s.nemt.tmp",settings)<0 || !write_settings(tmp,&safe)) {
            set_error(err,cap,"Could not write settings.ini. Check write permissions.");goto rollback;
        }
        if(!MoveFileExA(tmp,settings,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)) {
            set_error(err,cap,"Could not activate settings.ini.");goto rollback;
        }
        tmp[0]=0; old[0].changed=1;
        if(!copy_verified(runtime,proxy,expected,err,cap)) goto rollback;
        old[1].changed=1;
        mn=format_manifest(mbuf,sizeof(mbuf),&safe,1,expected);
        if(mn<=0 || mn>=(int)sizeof(mbuf) || !write_atomic(manifest,mbuf,(DWORD)mn)) {
            set_error(err,cap,"Could not write installation.json.");goto rollback;
        }
        old[2].changed=1;
        {const char *st="{\"runtime\":\"NEMT\",\"phase\":\"not-running\",\"note\":\"Installer snapshot; live diagnostics are optional.\"}";
         if(!write_atomic(status,st,(DWORD)strlen(st))) {set_error(err,cap,"Could not write status.json.");goto rollback;}}
        old[3].changed=1;
    }
    if(!sha_file(info->path,current) || lstrcmpiA(current,info->sha)) {
        set_error(err,cap,"The executable changed during installation.");goto rollback;
    }
    ok=1;goto done;
rollback:
    for(i=0;i<4;++i) changed|=old[i].changed;
    if(tmp[0]) DeleteFileA(tmp);
    if(!rollback_files(old,4)) {
        char problem[512];lstrcpynA(problem,err,sizeof(problem));
        _snprintf(err,cap,"%s Rollback also failed. Do not launch MSTS; restore the affected NEMT files from a backup.",problem);
        if(cap) err[cap-1]=0;
    } else {
        if(created) RemoveDirectoryA(nemt);
        if(changed && strlen(err)+27<cap) strcat(err," Changes were rolled back.");
    }
done:
    for(i=0;i<4;++i) free(old[i].bytes);
    free(record_text);return ok;
}

/* ---------- startup discovery ---------- */
static int registry_candidate(HKEY root,REGSAM view,const char *name,char *out) {
    HKEY k; DWORD type=0,n=MAX_PATH,len; char v[MAX_PATH],full[MAX_PATH];
    if(RegOpenKeyExA(root,"SOFTWARE\\Microsoft\\Microsoft Games\\Train Simulator\\1.0",0,KEY_QUERY_VALUE|view,&k)!=ERROR_SUCCESS) return 0;
    if(RegQueryValueExA(k,name,NULL,&type,(BYTE *)v,&n)!=ERROR_SUCCESS || !(type==REG_SZ || type==REG_EXPAND_SZ)) {RegCloseKey(k);return 0;}
    RegCloseKey(k);v[MAX_PATH-1]=0;
    if(type==REG_EXPAND_SZ) {
        char x[MAX_PATH];len=ExpandEnvironmentStringsA(v,x,MAX_PATH);
        if(!len || len>MAX_PATH) return 0;
        lstrcpynA(v,x,MAX_PATH);
    }
    trim(v);len=(DWORD)strlen(v);
    if(len>=2 && v[0]=='"' && v[len-1]=='"') {v[len-1]=0;memmove(v,v+1,len-1);trim(v);}
    if(!(v[0] && v[1]==':' && (v[2]=='\\' || v[2]=='/')) && !(v[0]=='\\' && v[1]=='\\')) return 0;
    len=(DWORD)strlen(v);
    if(len>=9 && !lstrcmpiA(v+len-9,"train.exe")) lstrcpynA(full,v,MAX_PATH);
    else if(!join_path(full,v,"train.exe")) return 0;
    len=GetFullPathNameA(full,MAX_PATH,out,NULL);
    return len>0 && len<MAX_PATH && exists_file(out);
}
static int find_msts(char *out) {
    HKEY hives[2]={HKEY_CURRENT_USER,HKEY_LOCAL_MACHINE};
    REGSAM views[3]={KEY_WOW64_32KEY,KEY_WOW64_64KEY,0};
    const char *names[2]={"EXE Path","Path"};
    char first[MAX_PATH]="",candidate[MAX_PATH],err[256];
    MstsInfo info;
    int h,v,n;
    for(h=0;h<2;++h) for(v=0;v<3;++v) for(n=0;n<2;++n) {
        /* XP x86 can reject explicit view flags; the ordinary view remains. */
        if(!registry_candidate(hives[h],views[v],names[n],candidate)) continue;
        if(!first[0]) lstrcpynA(first,candidate,MAX_PATH);
        if(inspect_msts(candidate,&info,err,sizeof(err))) {lstrcpynA(out,info.path,MAX_PATH);return 1;}
    }
    lstrcpynA(out,first,MAX_PATH);return first[0]!=0;
}

/* ---------- GUI: conventional controls, no framework or polling loop ---------- */
typedef struct {
    HWND hwnd;
    int id,x,y,width,height;
    WNDPROC original;
} UiControl;
static UiControl g_controls[64];
static int g_control_count,g_control_failed,g_dpi=96,g_scroll_x,g_scroll_y,g_layout_active,g_ui_ready;
static HFONT g_font,g_bold,g_title_font,g_link_font;
static HWND g_tooltip,g_last_focus;
static const char *g_instructions="Select train.exe and choose features, then Apply. Settings take effect after restarting MSTS.";
#define CONTENT_WIDTH 760
#define CONTENT_HEIGHT 840
#define STARTUP_EXTRA_WIDTH 24
#define STARTUP_EXTRA_HEIGHT 24
#define MAIN_WINDOW_STYLE (WS_OVERLAPPEDWINDOW|WS_CLIPCHILDREN)
#define MAIN_WINDOW_EX_STYLE WS_EX_CONTROLPARENT
#include "viewport_model.h"
static int dip(int value) {return MulDiv(value,g_dpi,96);}
static void layout_controls(void);
static void ensure_focus_visible(HWND hwnd);
static int is_link(int id) {return id==IDC_GITHUB || id==IDC_WIDEDOWNLOAD || id==IDC_WIDEGUIDE;}
static UiControl *ui_control(HWND hwnd) {
    int i;for(i=0;i<g_control_count;++i) if(g_controls[i].hwnd==hwnd) return &g_controls[i];
    return NULL;
}
static void scroll_to(int x,int y) {
    g_scroll_x=x;g_scroll_y=y;layout_controls();
}
static LRESULT CALLBACK child_proc(HWND w,UINT m,WPARAM wp,LPARAM lp) {
    UiControl *c=ui_control(w);
    if(!c || !c->original) return DefWindowProcA(w,m,wp,lp);
    if(m==WM_SETFOCUS) {
        LRESULT result=CallWindowProcA(c->original,w,m,wp,lp);
        g_last_focus=w;ensure_focus_visible(w);return result;
    }
    if(m==WM_MOUSEWHEEL) {
        if(c->id!=IDC_HUDLEFT || !SendMessageA(w,CB_GETDROPPEDSTATE,0,0)) {
            SendMessageA(g_main,m,wp,lp);return 0;
        }
    }
    if(m==WM_DROPFILES) {SendMessageA(g_main,m,wp,lp);return 0;}
    if(is_link(c->id)) {
        if(m==WM_SETCURSOR) {SetCursor(LoadCursor(NULL,IDC_HAND));return TRUE;}
        if(m==WM_GETDLGCODE && lp) {
            MSG *msg=(MSG *)lp;
            if(msg->wParam==VK_RETURN || msg->wParam==VK_SPACE) return DLGC_WANTALLKEYS;
        }
        if(m==WM_KEYDOWN && (wp==VK_RETURN || wp==VK_SPACE)) {
            SendMessageA(g_main,WM_COMMAND,MAKEWPARAM(c->id,STN_CLICKED),(LPARAM)w);return 0;
        }
    }
    return CallWindowProcA(c->original,w,m,wp,lp);
}
static HWND add_control(const char *cls,const char *text,DWORD style,int x,int y,int width,int height,int id) {
    UiControl *c;
    HWND hwnd;
    if(g_control_count>=(int)(sizeof(g_controls)/sizeof(g_controls[0]))) return NULL;
    hwnd=CreateWindowExA(0,cls,text,WS_CHILD|WS_VISIBLE|style,dip(x),dip(y),dip(width),dip(height),g_main,(HMENU)(INT_PTR)id,g_instance,NULL);
    if(!hwnd) {g_control_failed=1;return NULL;}
    c=&g_controls[g_control_count++];c->hwnd=hwnd;c->id=id;
    c->x=x;c->y=y;c->width=width;c->height=height;
    SendMessageA(hwnd,WM_SETFONT,(WPARAM)g_font,TRUE);
    c->original=(WNDPROC)(LONG_PTR)SetWindowLongA(hwnd,GWL_WNDPROC,(LONG)(LONG_PTR)child_proc);
    DragAcceptFiles(hwnd,TRUE);
    return hwnd;
}
static void check_set(int id,int on) {SendDlgItemMessageA(g_main,id,BM_SETCHECK,on?BST_CHECKED:BST_UNCHECKED,0);}
static int check_get(int id) {return SendDlgItemMessageA(g_main,id,BM_GETCHECK,0,0)==BST_CHECKED;}
static void enable(int id,int on) {EnableWindow(GetDlgItem(g_main,id),on);}
static void show_control(int id,int on) {ShowWindow(GetDlgItem(g_main,id),on?SW_SHOW:SW_HIDE);}
static void colored_text(HWND hwnd,const char *text,int state) {
    SetWindowLongA(hwnd,GWL_USERDATA,state);SetWindowTextA(hwnd,text);InvalidateRect(hwnd,NULL,TRUE);
}
static void status_text(const char *text,int state) {colored_text(g_status,text,state);}
static void message_text(const char *text,int state) {colored_text(g_message,text,state);}
static int strength_value(void) {return (int)SendMessageA(g_strength,TBM_GETPOS,0,0);}
static void update_strength(void) {
    int n=strength_value();char text[24];
    if(n==0) strcpy(text,"Disabled");else wsprintfA(text,"%dx",n);
    SetDlgItemTextA(g_main,IDC_STRENGTHVALUE,text);
    SendDlgItemMessageA(g_main,IDC_STRENGTHVALUE,WM_SETFONT,(WPARAM)(n?g_font:g_bold),TRUE);
}
static void refresh_crawl(void) {
    const int ids[]={IDC_CRAWLHINT,IDC_STRENGTHLABEL,IDC_STRENGTHVALUE,IDC_STRENGTH,IDC_ZERO,IDC_HUNDRED,IDC_ANCHORLABEL,IDC_HUDLEFT};
    int on=g_info.valid && check_get(IDC_CRAWL),i;
    for(i=0;i<(int)(sizeof(ids)/sizeof(ids[0]));++i) show_control(ids[i],on);
    enable(IDC_COUNTERTILT,on && !g_busy);
    enable(IDC_STRENGTH,on && !g_busy);enable(IDC_HUDLEFT,on && !g_busy);
    update_strength();
}
static void set_valid_controls(int on) {
    const int ids[]={IDC_RECOMMENDED,IDC_APPLY,IDC_UNINSTALL,IDC_SKIPMOVIE,IDC_WINDOW,IDC_UNLOCKFPS,IDC_VERBOSE,IDC_LOGGING,IDC_BACKGROUND,IDC_REDSIGNAL,IDC_EDITORWINDOWS,IDC_EDITORTOOLS,IDC_EDITORAUDIO,IDC_EDITORKEYS,IDC_EDITORPAN,IDC_TIMEOUT,IDC_CAMERA,IDC_CRAWL};
    int i;on=on && !g_busy;
    for(i=0;i<(int)(sizeof(ids)/sizeof(ids[0]));++i) enable(ids[i],on);
    enable(IDC_PCORES,on && g_cpu_supported);enable(IDC_CAB,on && g_info.widescreen);
    enable(IDC_VSYNC,on && check_get(IDC_UNLOCKFPS));
    enable(IDC_BROWSE,!g_busy);enable(IDC_CLOSE,!g_busy);
    refresh_crawl();
}
static void settings_to_ui(const Settings *s) {
    g_loading=1;
    check_set(IDC_PCORES,s->prefer_pcores);check_set(IDC_SKIPMOVIE,s->skip_movie);
    check_set(IDC_WINDOW,s->window_features);check_set(IDC_UNLOCKFPS,s->unlock_fps);
    check_set(IDC_VSYNC,s->limit_vsync);check_set(IDC_VERBOSE,s->verbose_loading);
    check_set(IDC_LOGGING,s->startup_log);check_set(IDC_CAB,s->cab_needles);
    check_set(IDC_BACKGROUND,s->background_audio);check_set(IDC_REDSIGNAL,s->ignore_red_signal);
    check_set(IDC_EDITORWINDOWS,s->editor_windows);check_set(IDC_EDITORTOOLS,s->editor_tools);
    check_set(IDC_EDITORAUDIO,s->editor_audio);check_set(IDC_EDITORKEYS,s->editor_keys);
    check_set(IDC_EDITORPAN,s->editor_pan);check_set(IDC_TIMEOUT,s->prevent_end);
    check_set(IDC_CAMERA,s->unlock_cameras);check_set(IDC_CRAWL,s->crawl);
    check_set(IDC_COUNTERTILT,s->counter_tilt);
    SendMessageA(g_strength,TBM_SETPOS,TRUE,s->strength);
    SendDlgItemMessageA(g_main,IDC_HUDLEFT,CB_SETCURSEL,s->hud_left?1:0,0);
    g_loading=0;set_valid_controls(g_info.valid);
}
static void ui_to_settings(Settings *s) {
    char game[MAX_PATH],ini[MAX_PATH];
    parent_dir(g_info.path,game);
    if(join_path(ini,game,"NEMT\\settings.ini")) load_settings(ini,s);else settings_defaults(s);
    /* Preserve manually configured, non-GUI options. A disabled P-core box
     * must not silently turn an existing preference off on another machine. */
    if(g_cpu_supported) s->prefer_pcores=check_get(IDC_PCORES);
    s->skip_movie=check_get(IDC_SKIPMOVIE);s->window_features=check_get(IDC_WINDOW);
    s->unlock_fps=check_get(IDC_UNLOCKFPS);s->limit_vsync=s->unlock_fps && check_get(IDC_VSYNC);
    s->verbose_loading=check_get(IDC_VERBOSE);s->startup_log=check_get(IDC_LOGGING);
    s->cab_needles=g_info.widescreen && check_get(IDC_CAB);
    s->background_audio=check_get(IDC_BACKGROUND);s->ignore_red_signal=check_get(IDC_REDSIGNAL);
    s->editor_windows=check_get(IDC_EDITORWINDOWS);s->editor_tools=check_get(IDC_EDITORTOOLS);
    s->editor_audio=check_get(IDC_EDITORAUDIO);s->editor_keys=check_get(IDC_EDITORKEYS);
    s->editor_pan=check_get(IDC_EDITORPAN);s->prevent_end=check_get(IDC_TIMEOUT);
    s->unlock_cameras=check_get(IDC_CAMERA);s->crawl=check_get(IDC_CRAWL);
    if(s->crawl) s->prevent_end=1;
    /* Like PS1, keep the optional preference even when crawl is off. */
    s->counter_tilt=check_get(IDC_COUNTERTILT);s->strength=strength_value();
    s->hud_left=SendDlgItemMessageA(g_main,IDC_HUDLEFT,CB_GETCURSEL,0,0)!=0;
}
static void load_selection(const char *path) {
    char selected[MAX_PATH],err[512],text[256];
    Settings s;MstsInfo info;
    /* The caller may pass g_info.path. Copy BEFORE clearing g_info. */
    lstrcpynA(selected,path?path:"",MAX_PATH);
    memset(&g_info,0,sizeof(g_info));
    settings_defaults(&s);s.window_features=0;settings_to_ui(&s);
    SetWindowTextA(g_path,selected);
    show_control(IDC_WIDENOTE,0);show_control(IDC_WIDEDOWNLOAD,0);show_control(IDC_WIDEGUIDE,0);
    if(!inspect_msts(selected,&info,err,sizeof(err)) || !load_selection_settings(&info,&s,err,sizeof(err))) {
        status_text("Unsupported executable or installation selected.",0);
        message_text(err,0);set_valid_controls(0);return;
    }
    g_info=info;settings_to_ui(&s);
    wsprintfA(text,"Valid train.exe version: %s",g_info.version);status_text(text,1);
    SetWindowTextA(g_path,g_info.path);
    show_control(IDC_WIDENOTE,!g_info.widescreen);show_control(IDC_WIDEDOWNLOAD,!g_info.widescreen);show_control(IDC_WIDEGUIDE,!g_info.widescreen);
    message_text(g_instructions,-1);set_valid_controls(1);
}
static void browse_train(void) {
    OPENFILENAMEA o;char p[MAX_PATH]="";
    memset(&o,0,sizeof(o));o.lStructSize=sizeof(o);o.hwndOwner=g_main;
    o.lpstrFilter="Train executable (*.exe)\0*.exe\0\0";o.lpstrFile=p;o.nMaxFile=MAX_PATH;
    o.Flags=OFN_FILEMUSTEXIST|OFN_PATHMUSTEXIST|OFN_HIDEREADONLY|OFN_NOCHANGEDIR;
    o.lpstrTitle="Select MSTS train.exe";
    if(GetOpenFileNameA(&o)) load_selection(p);
    else if(CommDlgExtendedError()) message_text("The file selection dialog could not be opened.",0);
}
static void recommended(void) {
    Settings s;if(!g_info.valid || g_busy) return;
    ui_to_settings(&s);settings_recommended(&s,g_info.widescreen,g_cpu_supported);settings_to_ui(&s);
}
static int any_feature_enabled(const Settings *s) {
    return s->prefer_pcores||s->skip_movie||s->window_features||s->unlock_fps||s->verbose_loading||s->startup_log||s->cab_needles||s->background_audio||s->ignore_red_signal||s->editor_windows||s->editor_tools||s->editor_audio||s->editor_keys||s->editor_pan||s->prevent_end||s->unlock_cameras||s->crawl;
}
static void do_save(int remove) {
    Settings s,effective;char err[512],selected[MAX_PATH];int ok;
    if(!g_info.valid || g_busy) return;
    lstrcpynA(selected,g_info.path,MAX_PATH);ui_to_settings(&s);
    effective=s;if(!g_cpu_supported) effective.prefer_pcores=0;
    if(!remove && !any_feature_enabled(&effective)) remove=1;
    g_busy=1;set_valid_controls(0);SetCursor(LoadCursor(NULL,IDC_WAIT));
    message_text(remove?"Removing toolkit...":"Saving settings...",-1);UpdateWindow(g_main);
    ok=install_settings(&g_info,&s,remove,err,sizeof(err));
    g_busy=0;SetCursor(LoadCursor(NULL,IDC_ARROW));
    if(ok) {
        load_selection(selected);
        /* Reload FIRST; otherwise the success message is immediately lost. */
        if(g_info.valid) message_text(remove?"Toolkit removed. Widescreen and LAA were preserved.":"Settings saved. Restart MSTS to apply changes. Windowed mode is used unless fullscreen is requested.",1);
    } else message_text(err,0);
    set_valid_controls(g_info.valid);
    ensure_focus_visible(g_message);
}
static void layout_controls(void) {
    RECT client;SCROLLINFO si;ViewportLayout view;HDWP batch;
    DWORD style;int i,width,height,moved=0;
    const UINT move_flags=SWP_NOZORDER|SWP_NOACTIVATE|SWP_NOREDRAW|SWP_NOCOPYBITS;
    if(!g_ui_ready || !g_main || g_layout_active || IsIconic(g_main)) return;
    g_layout_active=1;
    GetClientRect(g_main,&client);style=(DWORD)GetWindowLongA(g_main,GWL_STYLE);
    /* Recover the area WITHOUT scrollbars before deciding which are needed.
     * Starting from the already-reduced client area can leave two unnecessary
     * bars keeping each other alive when the user enlarges the window. */
    width=client.right+((style&WS_VSCROLL)?GetSystemMetrics(SM_CXVSCROLL):0);
    height=client.bottom+((style&WS_HSCROLL)?GetSystemMetrics(SM_CYHSCROLL):0);
    viewport_layout(&view,width,height,dip(CONTENT_WIDTH),dip(CONTENT_HEIGHT),
        GetSystemMetrics(SM_CXVSCROLL),GetSystemMetrics(SM_CYHSCROLL),g_scroll_x,g_scroll_y);
    g_scroll_x=view.x;g_scroll_y=view.y;
    memset(&si,0,sizeof(si));si.cbSize=sizeof(si);si.fMask=SIF_RANGE|SIF_PAGE|SIF_POS;
    si.nMax=dip(CONTENT_WIDTH)-1;si.nPage=view.width;si.nPos=g_scroll_x;
    SetScrollInfo(g_main,SB_HORZ,&si,TRUE);
    si.nMax=dip(CONTENT_HEIGHT)-1;si.nPage=view.height;si.nPos=g_scroll_y;
    SetScrollInfo(g_main,SB_VERT,&si,TRUE);

    /* Move every control together, including those outside the viewport.
     * Never copy saved window pixels during a move: partially clipped controls
     * and transparent labels otherwise carry old pixels into the new frame. */
    batch=BeginDeferWindowPos(g_control_count);
    for(i=0;batch && i<g_control_count;++i) {
        UiControl *c=&g_controls[i];
        batch=DeferWindowPos(batch,c->hwnd,NULL,dip(c->x)-g_scroll_x,dip(c->y)-g_scroll_y,
            dip(c->width),dip(c->height),move_flags);
    }
    if(batch) moved=EndDeferWindowPos(batch);
    if(!moved) {
        /* Allocation can fail on a low-memory machine. Keep the same no-copy,
         * no-redraw policy and repaint only once after the fallback moves. */
        for(i=0;i<g_control_count;++i) {
            UiControl *c=&g_controls[i];
            SetWindowPos(c->hwnd,NULL,dip(c->x)-g_scroll_x,dip(c->y)-g_scroll_y,
                dip(c->width),dip(c->height),move_flags);
        }
    }
    /* WS_CLIPCHILDREN means invalidating just the parent is insufficient.
     * Erase the exposed background and repaint all children/nonclient edges
     * before returning, rather than leaving trails until a later WM_PAINT. */
    RedrawWindow(g_main,NULL,NULL,RDW_INVALIDATE|RDW_ERASE|RDW_FRAME|RDW_ALLCHILDREN|RDW_UPDATENOW);
    g_layout_active=0;
}
static void ensure_focus_visible(HWND hwnd) {
    RECT r,client;int x=g_scroll_x,y=g_scroll_y;
    if(!g_ui_ready || !hwnd || !IsWindowVisible(hwnd)) return;
    GetWindowRect(hwnd,&r);MapWindowPoints(NULL,g_main,(POINT *)&r,2);GetClientRect(g_main,&client);
    if(r.top<0) y+=r.top-dip(8);else if(r.bottom>client.bottom) y+=r.bottom-client.bottom+dip(8);
    if(r.left<0) x+=r.left-dip(8);else if(r.right>client.right) x+=r.right-client.right+dip(8);
    if(x!=g_scroll_x || y!=g_scroll_y) scroll_to(x,y);
}
static void handle_scroll(UINT m,WPARAM wp) {
    SCROLLINFO si;int bar=m==WM_VSCROLL?SB_VERT:SB_HORZ,value;
    memset(&si,0,sizeof(si));si.cbSize=sizeof(si);si.fMask=SIF_ALL;GetScrollInfo(g_main,bar,&si);value=si.nPos;
    switch(LOWORD(wp)) {
    case SB_LINEUP:value-=dip(22);break;case SB_LINEDOWN:value+=dip(22);break;
    case SB_PAGEUP:value-=(int)si.nPage;break;case SB_PAGEDOWN:value+=(int)si.nPage;break;
    case SB_THUMBTRACK:case SB_THUMBPOSITION:value=si.nTrackPos;break;
    case SB_TOP:value=0;break;case SB_BOTTOM:value=si.nMax;break;default:return;
    }
    scroll_to(bar==SB_HORZ?value:g_scroll_x,bar==SB_VERT?value:g_scroll_y);
}
static void open_link(int id) {
    const char *url=id==IDC_GITHUB?"https://github.com/NekoCoaster/extended-msts-toolkit":
        id==IDC_WIDEDOWNLOAD?"https://digital-rails.com/wordpress/2018/06/23/running-msts-at-high-resolution/":
        "https://youtu.be/nkWh1HAuRKQ?t=556";
    if((INT_PTR)ShellExecuteA(g_main,"open",url,NULL,NULL,SW_SHOWNORMAL)<=32) message_text("Could not open the documentation link in your browser.",0);
}
static LRESULT CALLBACK wndproc(HWND w,UINT m,WPARAM wp,LPARAM lp) {
    switch(m) {
    case WM_CREATE:return 0;
    case WM_SIZE:layout_controls();return 0;
    case WM_GETMINMAXINFO: {
        MINMAXINFO *mm=(MINMAXINFO *)lp;mm->ptMinTrackSize.x=dip(400);mm->ptMinTrackSize.y=dip(260);return 0;
    }
    case WM_ACTIVATE:if(LOWORD(wp)==WA_INACTIVE) g_last_focus=GetFocus();break;
    case WM_SETFOCUS:
        if(g_last_focus && IsWindowEnabled(g_last_focus) && IsWindowVisible(g_last_focus)) SetFocus(g_last_focus);
        else if(g_ui_ready) SetFocus(GetDlgItem(w,IDC_BROWSE));return 0;
    case DM_GETDEFID:return MAKELONG(g_info.valid?IDC_APPLY:IDC_BROWSE,DC_HASDEFID);
    case DM_SETDEFID:return 0;
    case WM_SETCURSOR:if(g_busy) {SetCursor(LoadCursor(NULL,IDC_WAIT));return TRUE;}break;
    case WM_CTLCOLORSTATIC: {
        HDC dc=(HDC)wp;HWND child=(HWND)lp;int id=GetDlgCtrlID(child),state=(int)GetWindowLongA(child,GWL_USERDATA);
        if(child==g_status || child==g_message) SetTextColor(dc,state>0?RGB(0,140,0):(state==0?RGB(180,0,0):RGB(90,90,90)));
        else if(is_link(id)) SetTextColor(dc,RGB(0,70,180));
        else if(id==IDC_SPACE || id==IDC_CREDIT || id==IDC_CRAWLHINT || id==IDC_WIDENOTE) SetTextColor(dc,RGB(90,90,90));
        else SetTextColor(dc,GetSysColor(COLOR_WINDOWTEXT));
        SetBkMode(dc,TRANSPARENT);return (LRESULT)GetStockObject(WHITE_BRUSH);
    }
    case WM_HSCROLL:if((HWND)lp==g_strength) {update_strength();return 0;} /* fall through */
    case WM_VSCROLL:handle_scroll(m,wp);return 0;
    case WM_MOUSEWHEEL: {
        static int remainder;UINT lines=3;int steps;
        remainder+=(short)HIWORD(wp);steps=remainder/WHEEL_DELTA;remainder%=WHEEL_DELTA;
        SystemParametersInfoA(SPI_GETWHEELSCROLLLINES,0,&lines,0);
        if(steps) {RECT r;GetClientRect(w,&r);scroll_to(g_scroll_x,g_scroll_y-steps*(lines==WHEEL_PAGESCROLL?r.bottom:dip(22)*(int)lines));}
        return 0;
    }
    case WM_DROPFILES: {
        HDROP drop=(HDROP)wp;char path[MAX_PATH];
        if(!g_busy) {
            if(DragQueryFileA(drop,0xFFFFFFFF,NULL,0)!=1) message_text("Drop one executable at a time.",0);
            else if(DragQueryFileA(drop,0,NULL,0)>=MAX_PATH) message_text("The dropped executable path is too long.",0);
            else if(DragQueryFileA(drop,0,path,MAX_PATH)) load_selection(path);
        }
        DragFinish(drop);return 0;
    }
    case WM_COMMAND: {
        int id=LOWORD(wp),code=HIWORD(wp);
        if(g_busy) return 0;
        if(is_link(id) && code==STN_CLICKED) {open_link(id);return 0;}
        if(code!=BN_CLICKED) return 0;
        if(id==IDC_BROWSE) browse_train();else if(id==IDC_RECOMMENDED) recommended();
        else if(id==IDC_APPLY || id==IDOK) do_save(0);else if(id==IDC_UNINSTALL) do_save(1);
        else if(id==IDC_CLOSE || id==IDCANCEL) DestroyWindow(w);
        else if(id==IDC_CRAWL) {if(check_get(IDC_CRAWL) && !g_loading) check_set(IDC_TIMEOUT,1);refresh_crawl();}
        else if(id==IDC_TIMEOUT && !check_get(IDC_TIMEOUT) && !g_loading) {check_set(IDC_CRAWL,0);refresh_crawl();}
        else if(id==IDC_UNLOCKFPS) enable(IDC_VSYNC,g_info.valid && check_get(IDC_UNLOCKFPS));
        return 0;
    }
    case WM_CLOSE:if(!g_busy) DestroyWindow(w);return 0;
    case WM_DESTROY:PostQuitMessage(0);return 0;
    }
    return DefWindowProcA(w,m,wp,lp);
}
static void add_tip(HWND target,const char *text) {
    TOOLINFOA ti;
    if(!g_tooltip) return;
    memset(&ti,0,sizeof(ti));ti.cbSize=sizeof(ti);ti.uFlags=TTF_IDISHWND|TTF_SUBCLASS;
    ti.hwnd=g_main;ti.uId=(UINT_PTR)target;ti.lpszText=(LPSTR)text;
    SendMessageA(g_tooltip,TTM_ADDTOOLA,0,(LPARAM)&ti);
}
static int create_ui(void) {
    HWND c;int y=118,i;
    char text[512],runtime[MAX_PATH];WIN32_FILE_ATTRIBUTE_DATA data;
    INITCOMMONCONTROLSEX controls;
    const int ids[]={IDC_PCORES,IDC_SKIPMOVIE,IDC_WINDOW,IDC_UNLOCKFPS,IDC_VERBOSE,IDC_CAB,IDC_BACKGROUND,IDC_REDSIGNAL,IDC_EDITORWINDOWS,IDC_EDITORTOOLS,IDC_EDITORAUDIO,IDC_EDITORKEYS,IDC_EDITORPAN,IDC_TIMEOUT,IDC_CAMERA,IDC_CRAWL,IDC_COUNTERTILT};
    const char *labels[]={
        "Prefer P-cores (Only applicable to CPUs with hybrid architecture, e.g. Intel P && E cores)",
        "Skip startup movie (fixes keyboard control issue when loading into simulator)",
        "Enable borderless windowed mode for the main game",
        "Unlock FPS limit (corrected timing; potentially unstable)",
        "Show verbose startup and activity loading details",
        "Fix cabview dials for widescreen displays",
        "Unmute while in background",
        "Continue after passing a red signal (Resume after failure message)",
        "Resizable editor windows and fullscreen (Alt+Enter)",
        "Move Route Editor tool windows freely",
        "Fix Route Editor slowdown without nearby sounds",
        "Swap arrow keys with WASDEQ controls in route editor",
        "Remove Route Editor mouse-panning limit",
        "Remove derailment activity-end message",
        "Unlock camera modes during derailment",
        "Allow connected engines to crawl after derailment",
        "Enable counter-tilt filter while crawling (optional)"};
    controls.dwSize=sizeof(controls);controls.dwICC=ICC_BAR_CLASSES;
    if(!InitCommonControlsEx(&controls)) return 0;
#define ADD(cls,text,style,x,yy,ww,hh,id) add_control(cls,text,style,x,yy,ww,hh,id)
    wsprintfA(text,"Neko's Extended MSTS Toolkit Patcher v%s",g_version);
    c=ADD("STATIC",text,SS_LEFT|SS_NOPREFIX,24,8,712,36,IDC_TITLE);SendMessageA(c,WM_SETFONT,(WPARAM)g_title_font,TRUE);
    g_path=ADD("EDIT","",ES_AUTOHSCROLL|ES_READONLY|WS_BORDER|WS_TABSTOP,24,48,550,26,IDC_PATH);
    ADD("BUTTON","&Browse...",BS_PUSHBUTTON|WS_TABSTOP,585,45,125,32,IDC_BROWSE);
    g_status=ADD("STATIC","Choose or drop your train.exe.",SS_LEFT|SS_NOPREFIX,24,82,712,34,IDC_STATUS);
    SendMessageA(g_status,WM_SETFONT,(WPARAM)g_bold,TRUE);SetWindowLongA(g_status,GWL_USERDATA,-1);
    for(i=0;i<(int)(sizeof(ids)/sizeof(ids[0]));++i,y+=22) {
        int width=ids[i]==IDC_UNLOCKFPS?510:(ids[i]==IDC_CAB?308:712);
        ADD("BUTTON",labels[i],BS_AUTOCHECKBOX|WS_TABSTOP,24,y,width,22,ids[i]);
        if(ids[i]==IDC_UNLOCKFPS) ADD("BUTTON","Limit FPS to vsync",BS_AUTOCHECKBOX|WS_TABSTOP,544,y,192,22,IDC_VSYNC);
        if(ids[i]==IDC_CAB) {
            ADD("STATIC","Widescreen patch required.",SS_LEFT|SS_NOPREFIX,340,y+2,175,20,IDC_WIDENOTE);
            c=ADD("STATIC","Download",SS_NOTIFY|WS_TABSTOP,518,y+2,73,20,IDC_WIDEDOWNLOAD);SendMessageA(c,WM_SETFONT,(WPARAM)g_link_font,TRUE);
            c=ADD("STATIC","Install guide",SS_NOTIFY|WS_TABSTOP,602,y+2,100,20,IDC_WIDEGUIDE);SendMessageA(c,WM_SETFONT,(WPARAM)g_link_font,TRUE);
        }
    }
    ADD("STATIC","Use throttle for speed & reverser for direction",SS_LEFT|SS_NOPREFIX,24,494,712,18,IDC_CRAWLHINT);
    ADD("STATIC","Crawling thrust momentum:",SS_LEFT|SS_NOPREFIX,24,516,213,20,IDC_STRENGTHLABEL);
    ADD("STATIC","10x",SS_LEFT,240,516,160,20,IDC_STRENGTHVALUE);
    ADD("STATIC","0",SS_LEFT,24,542,18,20,IDC_ZERO);
    g_strength=ADD(TRACKBAR_CLASSA,"",TBS_AUTOTICKS|TBS_HORZ|WS_TABSTOP,44,536,660,30,IDC_STRENGTH);
    SendMessageA(g_strength,TBM_SETRANGE,TRUE,MAKELONG(0,100));SendMessageA(g_strength,TBM_SETPOS,TRUE,10);
    SendMessageA(g_strength,TBM_SETTICFREQ,10,0);SendMessageA(g_strength,TBM_SETPAGESIZE,0,10);
    ADD("STATIC","100",SS_LEFT,710,542,30,20,IDC_HUNDRED);
    ADD("STATIC","Extended F5 HUD location for crawling statistics",SS_LEFT|SS_NOPREFIX,24,574,390,24,IDC_ANCHORLABEL);
    c=ADD("COMBOBOX","",CBS_DROPDOWNLIST|WS_TABSTOP|WS_VSCROLL,424,570,170,120,IDC_HUDLEFT);
    SendMessageA(c,CB_ADDSTRING,0,(LPARAM)"Bottom right");SendMessageA(c,CB_ADDSTRING,0,(LPARAM)"Bottom left");SendMessageA(c,CB_SETCURSEL,1,0);
    ADD("BUTTON","Enable deep logging (Optional; HIGH DISK USAGE! Use only for bug reporting or troubleshooting issues)",BS_AUTOCHECKBOX|BS_MULTILINE|WS_TABSTOP,24,606,712,40,IDC_LOGGING);
    if(join_path(runtime,g_root,"runtime\\DINPUT.dll") && GetFileAttributesExA(runtime,GetFileExInfoStandard,&data))
        wsprintfA(text,"An additional ~%lu KB is required for this patch (DINPUT.dll, settings.ini, installation.json & status.json). Optional startup.log size may vary.",(data.nFileSizeLow+2048+1023)/1024);
    else lstrcpyA(text,"Keep runtime\\DINPUT.dll and runtime\\integrity.json alongside the toolkit. Optional startup.log size may vary.");
    ADD("STATIC",text,SS_LEFT|SS_NOPREFIX,24,650,712,36,IDC_SPACE);
    g_message=ADD("STATIC",g_instructions,SS_LEFT|SS_NOPREFIX,24,690,712,38,IDC_MESSAGE);SetWindowLongA(g_message,GWL_USERDATA,-1);
    ADD("BUTTON","Use &Recommended",BS_PUSHBUTTON|WS_TABSTOP,180,736,158,32,IDC_RECOMMENDED);
    ADD("BUTTON","&Apply",BS_DEFPUSHBUTTON|WS_TABSTOP,346,736,100,32,IDC_APPLY);
    ADD("BUTTON","&Uninstall",BS_PUSHBUTTON|WS_TABSTOP,454,736,106,32,IDC_UNINSTALL);
    ADD("BUTTON","&Close",BS_PUSHBUTTON|WS_TABSTOP,568,736,108,32,IDC_CLOSE);
    ADD("STATIC","Developed and Tested by NekoCoaster with Astra | MIT License",SS_LEFT|SS_NOPREFIX,24,782,712,20,IDC_CREDIT);
    c=ADD("STATIC","NekoCoaster/extended-msts-toolkit",SS_NOTIFY|WS_TABSTOP,24,806,500,22,IDC_GITHUB);SendMessageA(c,WM_SETFONT,(WPARAM)g_link_font,TRUE);
#undef ADD
    for(i=0;i<g_control_count;++i) if(!g_controls[i].hwnd) return 0;
    if(g_control_failed || !g_strength || !g_path || !g_status || !g_message || !GetDlgItem(g_main,IDC_HUDLEFT)) return 0;
    g_tooltip=CreateWindowExA(WS_EX_TOPMOST,TOOLTIPS_CLASSA,NULL,WS_POPUP|TTS_ALWAYSTIP,CW_USEDEFAULT,CW_USEDEFAULT,CW_USEDEFAULT,CW_USEDEFAULT,g_main,NULL,g_instance,NULL);
    if(g_tooltip) SendMessageA(g_tooltip,TTM_SETMAXTIPWIDTH,0,dip(400));
    add_tip(GetDlgItem(g_main,IDC_VSYNC),"Caps FPS to the current display refresh rate. Does not force tear-free presentation; driver VSync settings still apply.");
    add_tip(GetDlgItem(g_main,IDC_PCORES),"Available only when the OS exposes supported hybrid CPU topology. An unavailable API leaves saved preferences unchanged.");
    DragAcceptFiles(g_main,TRUE);g_ui_ready=1;
    show_control(IDC_WIDENOTE,0);show_control(IDC_WIDEDOWNLOAD,0);show_control(IDC_WIDEGUIDE,0);
    set_valid_controls(0);layout_controls();return 1;
}
static void init_fonts(void) {
    NONCLIENTMETRICSA metrics;LOGFONTA lf;HDC dc=GetDC(NULL);
    g_dpi=GetDeviceCaps(dc,LOGPIXELSY);ReleaseDC(NULL,dc);if(g_dpi<=0) g_dpi=96;
    memset(&metrics,0,sizeof(metrics));metrics.cbSize=sizeof(metrics);
    if(SystemParametersInfoA(SPI_GETNONCLIENTMETRICS,sizeof(metrics),&metrics,0)) lf=metrics.lfMessageFont;
    else {memset(&lf,0,sizeof(lf));lstrcpyA(lf.lfFaceName,"Tahoma");lf.lfCharSet=DEFAULT_CHARSET;}
    lf.lfHeight=-MulDiv(10,g_dpi,72);lf.lfWeight=FW_NORMAL;g_font=CreateFontIndirectA(&lf);
    lf.lfUnderline=TRUE;g_link_font=CreateFontIndirectA(&lf);lf.lfUnderline=FALSE;
    lf.lfWeight=FW_BOLD;g_bold=CreateFontIndirectA(&lf);lf.lfHeight=-MulDiv(17,g_dpi,72);g_title_font=CreateFontIndirectA(&lf);
}

static void init_root(void){char*p;GetModuleFileNameA(NULL,g_root,MAX_PATH);p=strrchr(g_root,'\\');if(p)*p=0;{char probe[MAX_PATH];if(join_path(probe,g_root,"runtime\\DINPUT.dll")&&!exists_file(probe)){char parent[MAX_PATH];parent_dir(g_root,parent);if(join_path(probe,parent,"runtime\\DINPUT.dll")&&exists_file(probe))lstrcpynA(g_root,parent,MAX_PATH);}}{char v[MAX_PATH];FILE*f;if(join_path(v,g_root,"VERSION")&&(f=fopen(v,"rb"))!=NULL){if(fgets(g_version,sizeof(g_version),f)){trim(g_version);}fclose(f);}}}

/* The preferred size is a CLIENT area, not an outer window size. Start
 * without scrollbar styles; layout_controls adds them only when necessary. */
static int initial_window_rect(const RECT *work,RECT *window) {
    RECT frame;int width,height;
    SetRect(&frame,0,0,dip(CONTENT_WIDTH+STARTUP_EXTRA_WIDTH),dip(CONTENT_HEIGHT+STARTUP_EXTRA_HEIGHT));
    if(!AdjustWindowRectEx(&frame,MAIN_WINDOW_STYLE,FALSE,MAIN_WINDOW_EX_STYLE)) return 0;
    width=frame.right-frame.left;height=frame.bottom-frame.top;
    if(width>work->right-work->left) width=work->right-work->left;
    if(height>work->bottom-work->top) height=work->bottom-work->top;
    if(width<=0 || height<=0) return 0;
    window->left=work->left+(work->right-work->left-width)/2;
    window->top=work->top+(work->bottom-work->top-height)/2;
    window->right=window->left+width;window->bottom=window->top+height;
    return 1;
}

int WINAPI WinMain(HINSTANCE h,HINSTANCE prev,LPSTR cmd,int show) {
    WNDCLASSA wc;MSG msg;RECT work,frame;char startup[MAX_PATH]="",title[128];
    int result=0;
    (void)prev;g_instance=h;init_root();init_fonts();g_cpu_supported=hybrid_cpu_supported();
    memset(&wc,0,sizeof(wc));wc.lpfnWndProc=wndproc;wc.hInstance=h;
    wc.hCursor=LoadCursor(NULL,IDC_ARROW);wc.hIcon=LoadIcon(NULL,IDI_APPLICATION);
    wc.hbrBackground=(HBRUSH)GetStockObject(WHITE_BRUSH);wc.lpszClassName="NEMTNativeWindow";
    if(!RegisterClassA(&wc)) return 1;
    if(!SystemParametersInfoA(SPI_GETWORKAREA,0,&work,0)) SetRect(&work,0,0,GetSystemMetrics(SM_CXSCREEN),GetSystemMetrics(SM_CYSCREEN));
    if(!initial_window_rect(&work,&frame)) return 1;
    wsprintfA(title,"NEMT %s",g_version);
    g_main=CreateWindowExA(MAIN_WINDOW_EX_STYLE,wc.lpszClassName,title,MAIN_WINDOW_STYLE,
        frame.left,frame.top,frame.right-frame.left,frame.bottom-frame.top,NULL,NULL,h,NULL);
    if(!g_main || !create_ui()) {MessageBoxA(NULL,"Could not create the NEMT form.",APP_TITLE,MB_ICONERROR|MB_OK);return 1;}
    ShowWindow(g_main,show);UpdateWindow(g_main);SetFocus(GetDlgItem(g_main,IDC_BROWSE));
    if(cmd && *cmd) {
        const char *end;size_t n;
        while(*cmd==' ' || *cmd=='\t') ++cmd;
        if(*cmd=='"') {++cmd;end=strchr(cmd,'"');if(!end) end=cmd+strlen(cmd);}
        else {end=cmd;while(*end && *end!=' ' && *end!='\t') ++end;}
        n=(size_t)(end-cmd);
        if(n>=MAX_PATH) message_text("The command-line executable path is too long.",0);
        else {memcpy(startup,cmd,n);startup[n]=0;}
    }
    if(!startup[0] && (!cmd || !*cmd)) find_msts(startup);
    if(startup[0]) load_selection(startup);
    /* Standard dialog navigation also works for a conventional Win32 window. */
    while((result=GetMessageA(&msg,NULL,0,0))>0) {
        if(!IsDialogMessageA(g_main,&msg)) {TranslateMessage(&msg);DispatchMessageA(&msg);}
    }
    if(g_font)DeleteObject(g_font);if(g_bold)DeleteObject(g_bold);
    if(g_title_font)DeleteObject(g_title_font);if(g_link_font)DeleteObject(g_link_font);
    return result<0?1:(int)msg.wParam;
}
