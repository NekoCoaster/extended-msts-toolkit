/* DirectSound ABI subset. The silent secondary buffer keeps an idle device
   from repeatedly waking during the Route Editor's listener updates. */
typedef struct {WORD format,channels;DWORD rate,bytesPerSecond;WORD alignment,bits,extra;} EditorWave;
typedef struct {DWORD size,flags,bytes,reserved;EditorWave *format;GUID algorithm;} EditorSoundDesc;
typedef HRESULT (WINAPI *EditorSoundCreate)(void*,EditorSoundDesc*,void**,void*);
typedef HRESULT (WINAPI *EditorSoundLock)(void*,DWORD,DWORD,void**,DWORD*,void**,DWORD*,DWORD);
typedef HRESULT (WINAPI *EditorSoundUnlock)(void*,void*,DWORD,void*,DWORD);
typedef HRESULT (WINAPI *EditorSoundPlay)(void*,DWORD,DWORD,DWORD);
typedef HRESULT (WINAPI *EditorSoundStatus)(void*,DWORD*);
typedef ULONG (WINAPI *EditorSoundSimple)(void*);
static void *editor_sound_buffer,*editor_sound_device;
static DWORD editor_sound_retry;
#define EDITOR_SOUND_METHOD(p,n,type) ((type)(*(void***)(p))[n])
static void editor_sound_release(void){
 if(editor_sound_buffer){EDITOR_SOUND_METHOD(editor_sound_buffer,18,EditorSoundSimple)(editor_sound_buffer);EDITOR_SOUND_METHOD(editor_sound_buffer,2,EditorSoundSimple)(editor_sound_buffer);}
 editor_sound_buffer=NULL;editor_sound_device=NULL;
}
static int editor_sound_fill(void *buffer){
 void *p=NULL,*q=NULL;DWORD n=0,m=0;HRESULT hr;
 hr=EDITOR_SOUND_METHOD(buffer,11,EditorSoundLock)(buffer,0,44100,&p,&n,&q,&m,0);
 if(hr<0)return 0;
 if(n)memset(p,0,n);if(m)memset(q,0,m);
 return EDITOR_SOUND_METHOD(buffer,19,EditorSoundUnlock)(buffer,p,n,q,m)>=0;
}
static void editor_sound_tick(void *device){
 DWORD status=0;EditorWave format;EditorSoundDesc desc;void *buffer=NULL;
 if(device!=editor_sound_device)editor_sound_release();
 if(!device)return;
 if(editor_sound_buffer){
  if(EDITOR_SOUND_METHOD(editor_sound_buffer,9,EditorSoundStatus)(editor_sound_buffer,&status)<0)return;
  if(status&2){if((HRESULT)EDITOR_SOUND_METHOD(editor_sound_buffer,20,EditorSoundSimple)(editor_sound_buffer)<0||!editor_sound_fill(editor_sound_buffer))return;status=0;}
  if(!(status&1))EDITOR_SOUND_METHOD(editor_sound_buffer,12,EditorSoundPlay)(editor_sound_buffer,0,0,1);
  return;
 }
 if(editor_sound_retry&&(DWORD)(GetTickCount()-editor_sound_retry)<5000)return;
 editor_sound_retry=GetTickCount();
 memset(&format,0,sizeof(format));format.format=1;format.channels=1;format.rate=22050;format.bytesPerSecond=44100;format.alignment=2;format.bits=16;
 memset(&desc,0,sizeof(desc));desc.size=sizeof(desc);desc.flags=8;desc.bytes=44100;desc.format=&format;
 if(EDITOR_SOUND_METHOD(device,3,EditorSoundCreate)(device,&desc,&buffer,NULL)<0||!buffer)return;
 if(!editor_sound_fill(buffer)||EDITOR_SOUND_METHOD(buffer,12,EditorSoundPlay)(buffer,0,0,1)<0){EDITOR_SOUND_METHOD(buffer,2,EditorSoundSimple)(buffer);return;}
 editor_sound_device=device;editor_sound_buffer=buffer;
}
