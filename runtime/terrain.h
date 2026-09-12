/* Native terrain progress is completed missing-buffer jobs / total jobs,
   rounded down to an integer percentage by MSTS before this call. */
static DWORD terrain_started,terrain_percent,terrain_updates;
static int terrain_active;
static void (__fastcall *terrain_progress_original)(U,U)=(void*)0x4023e2;
static void terrain_format(char *out,unsigned int capacity,DWORD percent,DWORD elapsed,DWORD updates){
 if(percent>100)percent=100;
 if(percent==100){snprintf(out,capacity,"Generating terrain buffers 100.0%%: 0m 00s remaining");return;}
 if(!percent||elapsed<2000||updates<2){snprintf(out,capacity,"Generating terrain buffers %lu.0%%: estimating...",percent);return;}
 {double seconds=((double)elapsed/1000)*(100-percent)/percent;unsigned int remaining=(unsigned int)minimum(seconds,359999);
 snprintf(out,capacity,"Generating terrain buffers %lu.0%%: ~%um %02us remaining",percent,remaining/60,remaining%60);}
}
static void __fastcall terrain_begin(U resource,U percent){terrain_started=GetTickCount();terrain_percent=0;terrain_updates=0;terrain_active=1;terrain_progress_original(resource,percent);}
static void __fastcall terrain_progress(U resource,U percent){terrain_percent=percent>100?100:percent;terrain_updates++;terrain_progress_original(resource,percent);}
