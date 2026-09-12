/* MIT. Experimental screen-relative cab dial rotation. Restart required.
   Four verified calls only; no persistent render scope and no texture edits. */
typedef float *(__fastcall *CabRotateFn)(float*,U,float);
static CabRotateFn cab_original=(void*)0x450e3e;
static int (*cab_mode)(void)=(void*)0x4b7dd8;
static float *cab_scales=(void*)0x79ca68;
static Hook cab_hooks[4];
static B *cab_entry;
static float *__fastcall cab_rotate(float *v,U unused,float angle){
 float sx=cab_scales[0],sy=cab_scales[1];
 if(cab_mode()!=1 || !(sx>0.0001f&&sx<1000&&sy>0.0001f&&sy<1000) || sx==sy)
  return cab_original(v,0,angle);
 v[0]/=sx;v[1]/=sy;
 cab_original(v,0,angle);
 v[0]*=sx;v[1]*=sy;
 return v;
}
/* At these calls EBP is the original quad-builder frame. Check its return
   before following its saved EBP to the renderer's original caller. Neither
   the vector register nor the stack argument is changed by this adapter. */
static void cab_adapter(B *p,void *corrected,void *original){
 B *a,*b,*fallback;
 emit8(&p,0x81);emit8(&p,0x7d);emit8(&p,4);emit32(&p,0x44fe46);
 emit8(&p,0x0f);emit8(&p,0x85);a=p;emit32(&p,0);
 emit8(&p,0x8b);emit8(&p,0x55);emit8(&p,0); /* mov edx,[ebp] */
 emit8(&p,0x81);emit8(&p,0x7a);emit8(&p,4);emit32(&p,0x41b771);
 emit8(&p,0x0f);emit8(&p,0x85);b=p;emit32(&p,0);
 branch(&p,0xe9,corrected);fallback=p;branch(&p,0xe9,original);
 *(U*)a=(U)fallback-(U)a-4;*(U*)b=(U)fallback-(U)b-4;
}
static int install_cab_hooks(void){
 static const U sites[]={0x44de2c,0x44de88,0x44dee1,0x44df3c};
 Hook check;DWORD old;U i;
 if(!cab_needles)return 1;
 /* Both frame layouts and the two connecting calls are required by adapter. */
 if(memcmp((void*)0x44dd35,"\x55\x8b\xec",3)||memcmp((void*)0x44fe01,"\x55\x8b\xec",3))return 0;
 startup_call(&check,0x44fe41,0x403c01,0);if(memcmp((void*)check.address,check.original,5))return 0;
 startup_call(&check,0x41b76c,0x40259f,0);if(memcmp((void*)check.address,check.original,5))return 0;
 cab_entry=VirtualAlloc(NULL,64,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);if(!cab_entry)return 0;
 cab_adapter(cab_entry,cab_rotate,cab_original);
 if(!VirtualProtect(cab_entry,64,PAGE_EXECUTE_READ,&old))goto failed;
 FlushInstructionCache(GetCurrentProcess(),cab_entry,64);
 for(i=0;i<4;i++)startup_call(&cab_hooks[i],sites[i],0x450e3e,(U)cab_entry);
 if(!prepare_hooks(cab_hooks,4))goto failed;
 for(i=0;i<200;i++){if(install_hooks(cab_hooks,4))return 1;Sleep(25);}
failed:VirtualFree(cab_entry,0,MEM_RELEASE);cab_entry=NULL;return 0;
}
