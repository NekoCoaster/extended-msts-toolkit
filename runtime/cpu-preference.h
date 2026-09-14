/* Optional process-default CPU Sets preference; no global or hard affinity writes. */
typedef BOOL (WINAPI *CpuQueryFn)(void*,ULONG,ULONG*,HANDLE,ULONG);
typedef BOOL (WINAPI *CpuDefaultsFn)(HANDLE,ULONG*,ULONG,ULONG*);
typedef BOOL (WINAPI *CpuApplyFn)(HANDLE,const ULONG*,ULONG);
/* SYSTEM_CPU_SET_INFORMATION is variable-sized. Read its stable documented prefix. */
static int cpu_select(const B *data,U bytes,DWORD mask,const ULONG *existing,U existing_count,ULONG *chosen,U *count){
 U offset=0,n=0,min=255,max=0,i,j;int found=0;*count=0;
 while(offset<bytes){
  U size,type;WORD group;B logical,eff;if(bytes-offset<8)return -1;memcpy(&size,data+offset,4);memcpy(&type,data+offset+4,4);
  if(size<8||size>bytes-offset)return -1;
  if(type==0){
   if(size<32)return -1;memcpy(&group,data+offset+12,2);logical=data[offset+14];eff=data[offset+18];
   /* Avoid ambiguous x86 affinity mappings on larger/multi-group machines. */
   if(group||logical>=32)return -2;
   if(eff<min)min=eff;if(eff>max)max=eff;found=1;
  }offset+=size;
 }
 if(!found||min==max)return 0;
 offset=0;
 while(offset<bytes){
  U size,type,id;B flags,logical;int allowed;memcpy(&size,data+offset,4);memcpy(&type,data+offset+4,4);
  if(type==0){
   memcpy(&id,data+offset+8,4);flags=data[offset+19];logical=data[offset+14];allowed=!existing_count;
   for(j=0;j<existing_count;j++)if(existing[j]==id)allowed=1;
   if(data[offset+18]==max&&(mask&(1UL<<logical))&&(!(flags&2)||(flags&4))&&allowed){
    for(i=0;i<n;i++)if(chosen[i]==id)return -1;
    if(n==32)return -1;chosen[n++]=id;
   }
  }offset+=size;
 }
 *count=n;return n?1:-3;
}
static void apply_cpu_preference(void){
 HMODULE kernel;CpuQueryFn query;CpuDefaultsFn defaults;CpuApplyFn apply;ULONG bytes=0,returned=0,existing[256],existing_count=0,chosen[32];U count=0;B *data;DWORD_PTR process_mask,system_mask;int result;char line[180];
 if(!prefer_pcores){startup_write("CPU PREFERENCE","Disabled; Windows scheduling unchanged",0);return;}
 kernel=GetModuleHandleA("kernel32.dll");query=(CpuQueryFn)GetProcAddress(kernel,"GetSystemCpuSetInformation");defaults=(CpuDefaultsFn)GetProcAddress(kernel,"GetProcessDefaultCpuSets");apply=(CpuApplyFn)GetProcAddress(kernel,"SetProcessDefaultCpuSets");
 if(!query||!defaults||!apply){startup_write("CPU PREFERENCE","Unsupported Windows APIs; unchanged",0);return;}
 if(!GetProcessAffinityMask(GetCurrentProcess(),&process_mask,&system_mask)||!defaults(GetCurrentProcess(),existing,256,&existing_count)||existing_count>256){startup_write("CPU PREFERENCE","Cannot safely read existing restrictions; unchanged",0);return;}
 query(NULL,0,&bytes,GetCurrentProcess(),0);
 if(!bytes||bytes>1024*1024){startup_write("CPU PREFERENCE","CPU topology unavailable or too large; unchanged",0);return;}
 data=HeapAlloc(GetProcessHeap(),0,bytes);if(!data)return;
 if(!query(data,bytes,&returned,GetCurrentProcess(),0)||returned>bytes){HeapFree(GetProcessHeap(),0,data);startup_write("CPU PREFERENCE","CPU topology changed or unavailable; unchanged",0);return;}
 result=cpu_select(data,returned,(DWORD)(process_mask&system_mask),existing,existing_count,chosen,&count);HeapFree(GetProcessHeap(),0,data);
 if(result==1){
  if(apply(GetCurrentProcess(),chosen,count)){U i;startup_write("CPU PREFERENCE","Applied highest-performance CPU class; thread-specific selections and hard affinity still take precedence",count);for(i=0;i<count;i++){snprintf(line,sizeof(line),"selected CPU Set ID=%lu",chosen[i]);startup_write("CPU SET",line,i);}}
  else{snprintf(line,sizeof(line),"Windows rejected preference; error=%lu",GetLastError());startup_write("CPU PREFERENCE",line,0);}
 }else startup_write("CPU PREFERENCE",result==0?"No distinct performance classes reported; unchanged":result==-2?"Unsupported multi-group or >32-logical topology for this x86 preference; unchanged":result==-3?"No eligible performance cores within existing restrictions; unchanged":"Malformed topology; unchanged",0);
}
