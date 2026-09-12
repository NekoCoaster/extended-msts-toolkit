/* MIT. Request DSBCAPS_GLOBALFOCUS on MSTS's secondary sound buffers.
   Preserve its existing volume/frequency/3D flags and focus/input handling. */
static Hook audio_hook;
static int install_audio_hook(void){
 if(!background_audio)return 1;
 memset(&audio_hook,0,sizeof(audio_hook));audio_hook.address=0x538302;audio_hook.length=6;audio_hook.raw=1;
 memcpy(audio_hook.original,"\x81\xca\xa0\x00\x00\x00",6);
 memcpy(audio_hook.replacement,"\x81\xca\xa0\x80\x00\x00",6);
 return prepare_hooks(&audio_hook,1)&&install_hooks(&audio_hook,1);
}
