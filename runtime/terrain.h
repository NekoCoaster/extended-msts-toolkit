/* Native terrain progress is completed missing-buffer jobs / total jobs,
   rounded down to an integer percentage by MSTS before this call. */
static DWORD terrain_started,terrain_percent,terrain_updates,terrain_total,terrain_completed;
static int terrain_active;
static void (__fastcall *terrain_progress_original)(U,U)=(void*)0x4023e2;
static void terrain_format(char *out,unsigned int capacity,DWORD percent,DWORD elapsed,DWORD updates){
 char label[64];snprintf(label,sizeof(label),"Generating terrain buffers %lu/%lu",terrain_completed,terrain_total);
 if(percent>100)percent=100;
 if(percent==100){snprintf(out,capacity,"%s 100%%: 0m 00s remaining",label);return;}
 if(!percent||elapsed<2000||updates<2){snprintf(out,capacity,"%s %lu%%: estimating...",label,percent);return;}
 {double seconds=((double)elapsed/1000)*(100-percent)/percent;unsigned int remaining=(unsigned int)minimum(seconds,359999);
 snprintf(out,capacity,"%s %lu%%: ~%um %02us remaining",label,percent,remaining/60,remaining%60);}
}
static void __fastcall terrain_begin(U total,U percent){terrain_total=total;terrain_completed=0;terrain_started=GetTickCount();terrain_percent=0;terrain_updates=0;terrain_active=1;terrain_progress_original(53,percent);}
static void __fastcall terrain_progress(U completed,U percent){terrain_completed=completed;terrain_percent=percent>100?100:percent;terrain_updates++;terrain_progress_original(53,percent);}
