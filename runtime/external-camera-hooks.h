/* Shared walking frame/window dispatch avoids overlapping detours. */
static Hook external_hooks[3];static B *external_code;
static int install_external_hooks(void){
 B *p;DWORD old;U count=1;
 if(!external_requested)return 1;
 external_code=VirtualAlloc(NULL,128,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
 if(!external_code)return 0;p=external_code;
 external_original=(void*)p;
 p=walking_detour(&external_hooks[0],p,0x51a69a,(B*)"\x55\x8b\xec\x81\xec\xa4\x00\x00\x00",9,external_orbit);
 if(!walking_requested){
  external_frame_original=(void*)p;
  p=walking_detour(&external_hooks[count++],p,0x51cfd5,(B*)"\x55\x8b\xec\x83\xec\x44",6,external_frame);
  external_proc_original=(WNDPROC)p;
  p=walking_detour(&external_hooks[count++],p,0x696c00,(B*)"\xa1\x54\x99\x82\x00",5,external_proc);
 }
 if(!VirtualProtect(external_code,128,PAGE_EXECUTE_READ,&old))return 0;
 FlushInstructionCache(GetCurrentProcess(),external_code,128);
 if(!prepare_hooks(external_hooks,count)||!install_hooks(external_hooks,count))return 0;
 external_ready=1;return 1;
}
