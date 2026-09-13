#include <windows.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>
#include "../runtime/editor_audio.h"
static void *device_vtable[10],*buffer_vtable[21];
static void **device=device_vtable,**buffer=buffer_vtable;
static unsigned char samples[44100];static int creates,plays,stops,releases,locks,restores;static DWORD state;static int fail_create;
static HRESULT WINAPI create(void *d,EditorSoundDesc *desc,void **out,void *outer){
 assert(d==&device&&!outer&&desc->size==36&&desc->flags==8&&desc->bytes==44100);
 assert(desc->format->format==1&&desc->format->channels==1&&desc->format->rate==22050&&desc->format->bits==16&&desc->format->extra==0);
 creates++;if(fail_create)return E_FAIL;*out=&buffer;memset(samples,0xff,sizeof(samples));return S_OK;
}
static HRESULT WINAPI lock(void *b,DWORD start,DWORD len,void **p,DWORD *n,void **q,DWORD *m,DWORD flags){assert(b==&buffer&&!start&&len==44100&&!flags);*p=samples;*n=22000;*q=samples+22000;*m=22100;locks++;return S_OK;}
static HRESULT WINAPI unlock(void *b,void *p,DWORD n,void *q,DWORD m){int i;assert(b==&buffer&&p==samples&&q==samples+22000&&n==22000&&m==22100);for(i=0;i<44100;i++)assert(samples[i]==0);return S_OK;}
static HRESULT WINAPI play(void *b,DWORD a,DWORD c,DWORD flags){assert(b==&buffer&&!a&&!c&&flags==1);state=1;plays++;return S_OK;}
static HRESULT WINAPI status(void *b,DWORD *out){assert(b==&buffer);*out=state;return S_OK;}
static ULONG WINAPI stop(void *b){assert(b==&buffer);stops++;state=0;return 0;}
static ULONG WINAPI release(void *b){assert(b==&buffer);releases++;return 0;}
static ULONG WINAPI restore(void *b){assert(b==&buffer);restores++;state=0;return 0;}
int main(void){
 device_vtable[3]=create;buffer_vtable[2]=release;buffer_vtable[9]=status;buffer_vtable[11]=lock;buffer_vtable[12]=play;buffer_vtable[18]=stop;buffer_vtable[19]=unlock;buffer_vtable[20]=restore;
 editor_sound_tick(NULL);assert(!creates);editor_sound_tick(&device);assert(creates==1&&plays==1&&locks==1);
 editor_sound_tick(&device);assert(creates==1&&plays==1);state=2;editor_sound_tick(&device);assert(restores==1&&locks==2&&plays==2);
 editor_sound_tick(NULL);assert(stops==1&&releases==1&&!editor_sound_buffer);editor_sound_release();assert(releases==1);
 editor_sound_retry=0;fail_create=1;editor_sound_tick(&device);assert(creates==2&&!editor_sound_buffer);editor_sound_tick(&device);assert(creates==2);
 puts("PASS silent buffer creation, zero-filled split locks, looping, loss recovery, teardown and failure backoff.");return 0;
}
