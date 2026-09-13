"""Execute the actual loader readiness loop against deterministic scene samples."""
import subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
source = (root/'runtime/loader.c').read_text()
start = source.index('static DWORD WINAPI delayed_start(')
end = source.index('static FARPROC resolve(', start)
loop = source[start:end]
scratch = root/'work/readiness-regression'
scratch.mkdir(parents=True, exist_ok=True)
harness = r'''
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>
static WCHAR root[MAX_PATH]=L"C:\\fixture\\";
static int config_valid=1,prevent_end=1,unlock_cameras=1,crawl_requested=1,cab_needles=0,write_status_json=0;
static int polls,scenario,installed,toolset;
static void die(const char *s){fprintf(stderr,"FAIL %s (scenario %d poll %d)\n",s,scenario,polls);exit(1);}
static int has_toolset(const char *s){return toolset;}
static int supported_image(void){return 1;}
static void read_config(void){}
static void write_status(void){}
static void fail(const char *s){die(s);}
static int install_cab_hooks(void){installed++;return 1;}
static int start_native(void){installed++;return 1;}
static void test_sleep(DWORD ms){if(ms!=250||++polls>200)die("wait bound");}
#define Sleep test_sleep
static int read_memory(DWORD address,void *out,SIZE_T size){
 DWORD value=0;float now=(float)polls*.25f;
 if(address==0x7c2ac0)value=(scenario==1&&polls<=10)?0:0x1000;
 else if(address==0x106a)value=0x2000;
 else if(address==0x205c)value=0x3000;
 else if(address==0x311d)value=(scenario==2&&polls<=10)?0x9999:0x2000;
 else if(address==0x7b6440)value=(scenario==3&&polls<=10)?0:0x4000;
 else if(address==0x80acd4){
  if(scenario==4&&polls<=30)now=0;
  memcpy(out,&now,4);return 1;
 }else die("unexpected scene field");
 memcpy(out,&value,4);return 1;
}
'''
harness += loop
harness += r'''
int main(void){
 for(scenario=0;scenario<=4;scenario++){
  polls=installed=0;delayed_start(NULL);
  if(installed!=2)die("missing installation");
  if(polls!=(scenario==0?20:scenario==4?31:30))die("premature readiness");
 }
 toolset=1;polls=installed=0;delayed_start(NULL);if(polls||installed)die("toolset entered driving gate");
 toolset=0;config_valid=0;polls=installed=0;delayed_start(NULL);if(polls||installed)die("invalid config entered gate");
 puts("PASS actual native readiness loop: delayed driving scene, ownership/control validity, paused clock, minimum stable samples, toolset/config exclusion.");return 0;
}
'''
c = scratch/'readiness.c'
c.write_text(harness)
exe = scratch/'readiness.exe'
subprocess.run([sys.argv[1], '-o', str(exe), str(c)], check=True)
subprocess.run([str(exe)], check=True)
