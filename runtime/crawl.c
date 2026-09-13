/* MSTS native crawl V2. MIT. Included by loader.c after read_memory/root. */
#include <stdio.h>
#include "hooks.h"
#include "physics.h"
#ifndef G
#define G(a) (a)
#endif
enum {FRAME,EXIT,WHEEL,ROD,SPLIT,BODY,FORCE,DRAG,PITCH,VECTOR,CROSS,HOOK_COUNT};
#include "prologues.h"
typedef struct {U id,body,definition,engineDefinition,links[2];int engine,derailed,active;float mass,maxForce,maxPower,axis[3],velocity[3];double dp[3],dv[3];} Car;
typedef struct {U originalReturn,slot,bits,a,b,links[4],body;float filtered[3];int pitch;} Call;
typedef struct {U depth;Call calls[64];} ThreadCalls;
static DWORD tls_index=TLS_OUT_OF_INDEXES,simulation_thread;
static CRITICAL_SECTION state_lock;
static volatile LONG crawl_state_ready;
static double applied_dt;
static Car cars[256];static U car_count,train_id,frame_count,control_type,active_count;
static int enabled,blocked,strength=10,have_sim;
#include "config.h"
static float throttle,direction,last_sim;
static double friction_scale=1;
static const char *phase="waiting-for-activity",*last_error="";
static volatile LONG status_sequence;
static U wakes,drag_calls,pitch_calls,wheel_calls,rod_calls,impulses,graph_changes;
static void fail(const char *message){enabled=0;blocked=1;active_count=0;last_error=message;phase="fault";}
static U ru(const void *p){U v;memcpy(&v,p,4);return v;}
static float rf(const void *p){float v;memcpy(&v,p,4);return v;}
static void wf(U p,float v){memcpy((void*)p,&v,4);}
static int paused(void){return *(volatile U*)G(0x7be0f4)!=0;}
static Car *find_car(U id){U i;for(i=0;i<car_count;i++)if(cars[i].id==id)return &cars[i];return NULL;}
/* MSTS rotates integration buffers between the frame snapshot and collision
   callbacks. Ownership is stable; the cached body address is not. */
static int eligible(U body){Car *c;if(!body||*((B*)body+0xf0)!=1||!(*((B*)body+0xf2)&4))return 0;c=find_car(ru((B*)body+0x11d));return c&&c->derailed;}
static void clear_activity(void){enabled=blocked=have_sim=0;car_count=active_count=train_id=0;throttle=direction=0;friction_scale=1;last_error="";phase="waiting-for-activity";}
static int read_car(U id,Car *c){
 B header[0xac],body[0x124],engine[0x116];B flag;U i;
 memset(c,0,sizeof(*c));c->id=id;
 if(!read_memory(id,header,sizeof(header)))return 0;
 c->body=ru(header+0x5c);c->definition=ru(header+0x94);c->links[0]=ru(header+0xa0);c->links[1]=ru(header+0xa8);
 if(!c->body||!c->definition||!read_memory(c->body,body,sizeof(body))||ru(body+0x11d)!=id||!read_memory(c->definition+0x88,&flag,1))return 0;
 c->engine=flag==1;c->derailed=(body[0xf2]&4)!=0;c->mass=1.0/rf(body+0xc8);
 for(i=0;i<3;i++){c->axis[i]=rf(body+0x24+i*4);c->velocity[i]=rf(body+0x88+i*4);}
 if(c->engine){if(!read_memory(id+0x29a,&c->engineDefinition,4)||!c->engineDefinition||!read_memory(c->engineDefinition,engine,sizeof(engine)))return 0;c->maxForce=rf(engine+0x102);c->maxPower=rf(engine+0xfe);}
 return 1;
}
/* Bounded breadth-first graph; one snapshot per car, then reciprocal-link check. */
static int snapshot(void){
 U train,head,ctl,type,pending[256],n=1,index=0,i,j;Car next[256];float t,d;
 if(!read_memory(G(0x7c2ac0),&train,4)||!train)return 0;
 if(!read_memory(train+0x6a,&head,4)||!head||!read_memory(G(0x7b6440),&ctl,4)||!ctl||!read_memory(G(0x7b6438),&type,4)||type<1||type>3||!read_memory(ctl+(type==1?0x54:0x8c),&t,4)||!read_memory(ctl+(type==1?0x8c:0xc8),&d,4)||!finite_number(t)||!finite_number(d))return 0;
 pending[0]=head;
 while(index<n){
  if(!read_car(pending[index],&next[index]))return 0;
  for(i=0;i<2;i++){U link=next[index].links[i];if(!link)continue;for(j=0;j<n&&pending[j]!=link;j++);if(j==n){if(n==256)return 0;pending[n++]=link;}}
  index++;
 }
 for(index=0;index<n;index++)for(i=0;i<2;i++){U link=next[index].links[i];if(!link)continue;for(j=0;j<n&&next[j].id!=link;j++);if(j==n||(next[j].links[0]!=next[index].id&&next[j].links[1]!=next[index].id))return 0;}
 for(index=0;index<n;index++){Car *old=find_car(next[index].id);next[index].active=old&&old->active&&train_id==train;}
 if(train_id!=train){have_sim=0;train_id=train;}
 memcpy(cars,next,n*sizeof(Car));car_count=n;throttle=t;direction=d;control_type=type;friction_scale=1-clamp_throttle(t);return 1;
}
static void update_frame(void){
 U i,j,derailed=0;float sim,dt;frame_count++;
 if(blocked)return;
 if(!*(volatile U*)G(0x7c2ac0)){clear_activity();return;}
 if(!enabled&&frame_count%6)return;
 if(!snapshot()){fail("Invalid train, controls or connection graph");return;}
 for(i=0;i<car_count;i++)if(cars[i].derailed)derailed=1;
 if(!derailed){enabled=0;have_sim=0;active_count=0;phase="waiting-for-derailment";return;}
 enabled=1;phase="crawling";
 if(paused()){active_count=0;for(i=0;i<car_count;i++)cars[i].active=0;return;}
 sim=*(float*)G(0x80acd4);dt=*(float*)G(0x828fb4);
 if(!finite_number(sim)){fail("Invalid simulation clock");return;}
 if(have_sim&&sim==last_sim)return;
 have_sim=1;last_sim=sim;active_count=0;
 /* Validate every planned write before applying any propulsion. */
 for(i=0;i<car_count;i++){Car *c=&cars[i];c->active=0;if(!c->engine||!c->derailed)continue;
  if(!calc_impulse(c->axis,c->velocity,c->mass,c->maxForce,c->maxPower,throttle,direction,dt,strength,c->dp,c->dv)){fail("Invalid propulsion parameters");return;}
  for(j=0;j<3;j++){double p=rf((B*)c->body+0x4c+j*4)+c->dp[j],v=c->velocity[j]+c->dv[j];if(!finite_number(p)||fabs(p)>3.4e38||!finite_number(v)||fabs(v)>3.4e38){fail("Invalid momentum");return;}}
 }
 applied_dt=minimum(dt,.25);
 for(i=0;i<car_count;i++){Car *c=&cars[i];if(!c->engine||!c->derailed||!(c->dp[0]||c->dp[1]||c->dp[2]))continue;
  *((B*)c->body+0xf2)&=~8;
  for(j=0;j<3;j++){wf(c->body+0x4c+j*4,rf((B*)c->body+0x4c+j*4)+c->dp[j]);wf(c->body+0x88+j*4,c->velocity[j]+c->dv[j]);}
  c->active=1;active_count++;impulses++;
 }
}
static ThreadCalls *thread_calls(void){ThreadCalls *t=TlsGetValue(tls_index);if(!t){t=HeapAlloc(GetProcessHeap(),HEAP_ZERO_MEMORY,sizeof(*t));if(t&&!TlsSetValue(tls_index,t)){HeapFree(GetProcessHeap(),0,t);t=NULL;}}return t;}
static Call *push_call(U id,Registers *r){
 ThreadCalls *t=thread_calls();Call *c;U *stack=(U*)(r+1);
 if(!t||t->depth==64){fail("Native callback nesting limit");return NULL;}
 c=&t->calls[t->depth++];memset(c,0,sizeof(*c));c->originalReturn=stack[0];stack[0]=(U)hooks[id].leave;return c;
}
static void wake_body(U b,int force){Car *c;if(!eligible(b))return;c=find_car(ru((B*)b+0x11d));if((!force&&c->active)||friction_scale<1){*((B*)b+0xf2)&=~8;wakes++;}}
static void enter_effect(U id,Registers *r){
 U *s=(U*)(r+1),body=0,offset=0,i;Call *call;ThreadCalls *t;Car *c;double speed,rate;float factor,omega[3],forward[3];
 if(id==PITCH){
  /* Push even an ineligible nested derivative to mask an outer pitch context. */
  call=push_call(id,r);if(!call)return;body=s[2];if(!eligible(body))return;
  for(i=0;i<3;i++){omega[i]=rf((B*)body+0x94+i*4);forward[i]=rf((B*)body+0x24+i*4);}
  if(!calc_pitch(omega,forward,friction_scale,call->filtered)){fail("Invalid pitch input");return;}
  call->pitch=1;call->body=body;return;
 }
 if(id==VECTOR||id==CROSS){
  if(s[0]!=(id==VECTOR?0x5f8796:0x5f8876))return;
  t=TlsGetValue(tls_index);if(!t||!t->depth)return;call=&t->calls[t->depth-1];if(!call->pitch)return;
  if(r->ecx!=call->body+0x94){fail("Unexpected orientation input");return;}r->ecx=(U)call->filtered;pitch_calls++;return;
 }
 if(id==SPLIT){call=push_call(id,r);if(!call)return;call->a=r->ecx;call->b=r->edx;if(!call->a||!call->b){call->a=0;return;}call->links[0]=ru((B*)call->a+0xa0);call->links[1]=ru((B*)call->a+0xa8);call->links[2]=ru((B*)call->b+0xa0);call->links[3]=ru((B*)call->b+0xa8);return;}
 if(id==BODY){wake_body(r->ecx,0);return;}if(id==FORCE){wake_body(s[2],1);return;}
 if(id==DRAG){
  switch(s[0]){case 0x62b18a:case 0x62b30e:case 0x62b45a:offset=0x88;break;case 0x62b207:case 0x62b38d:case 0x62b4d6:offset=0x94;break;default:return;}
  body=r->ecx-offset;if(!eligible(body))return;factor=rf(&s[2]);if(!finite_number(factor)||factor>0){fail("Unexpected drag coefficient");return;}wf((U)&s[2],factor*friction_scale);drag_calls++;return;
 }
 if(id==WHEEL||id==ROD){
  U car=id==WHEEL?ru((B*)s[4]+4):r->ecx;c=find_car(car);if(!c||!c->derailed)return;
  body=ru((B*)car+0x5c);if(!eligible(body)||ru((B*)body+0x11d)!=car)return;
  for(i=0;i<3;i++){omega[i]=rf((B*)body+0x88+i*4);forward[i]=rf((B*)body+0x24+i*4);}
  if(!calc_wheel(omega,forward,throttle,strength,&speed)){fail("Invalid wheel input");return;}
  if(id==WHEEL){factor=rf((B*)c->definition+0x4a0);if(!finite_number(factor)||factor<=0||factor>100){fail("Invalid wheel factor");return;}rate=speed*factor;offset=0x1b0;}
  else{if(!c->engine)return;factor=rf((B*)c->engineDefinition+0x112);if(!finite_number(factor)||factor<=0||factor>10){fail("Invalid driving radius");return;}rate=speed/(2*3.14159*factor);offset=0x2b2;}
  if(!finite_number(rate)||fabs(rate)>3.4e38){fail("Invalid visual rate");return;}
  call=push_call(id,r);if(!call)return;call->slot=car+offset;call->bits=ru((void*)call->slot);wf(call->slot,rate);if(id==WHEEL)wheel_calls++;else rod_calls++;
 }
}
static void hook_enter(U id,Registers *r){
 DWORD tid=GetCurrentThreadId();
 EnterCriticalSection(&state_lock);
 if(id==FRAME){if(!simulation_thread)simulation_thread=tid;if(tid==simulation_thread){InterlockedIncrement(&status_sequence);update_frame();InterlockedIncrement(&status_sequence);}}
 else if(id==EXIT){InterlockedIncrement(&status_sequence);clear_activity();InterlockedIncrement(&status_sequence);}
 else if(enabled&&!paused())enter_effect(id,r);
 LeaveCriticalSection(&state_lock);
}
static void hook_leave(U id,Registers *r){
 ThreadCalls *t=TlsGetValue(tls_index);Call *c;U links[4];
 EnterCriticalSection(&state_lock);
 /* Every leave is paired with push_call on this thread, even after a fault. */
 if(!t||!t->depth){TerminateProcess(GetCurrentProcess(),0xE0000002);return;}
 c=&t->calls[t->depth-1];*((U*)(r+1))=c->originalReturn;
 if(c->slot)memcpy((void*)c->slot,&c->bits,4);
 if(id==SPLIT&&c->a&&enabled){
  links[0]=ru((B*)c->a+0xa0);links[1]=ru((B*)c->a+0xa8);links[2]=ru((B*)c->b+0xa0);links[3]=ru((B*)c->b+0xa8);
  if(memcmp(links,c->links,sizeof(links))){graph_changes++;if(!snapshot())fail("Invalid graph after uncoupling");}
 }
 t->depth--;
 LeaveCriticalSection(&state_lock);
}
static void write_status(void){
 WCHAR path[MAX_PATH];char text[768];DWORD written;HANDLE f;LONG before;U attempts=0;int length;
 if(!write_status_json)return;
 do{before=status_sequence;if(before&1)continue;
  length=snprintf(text,sizeof(text),"{\"version\":2,\"runtime\":\"native\",\"phase\":\"%s\",\"enabled\":%s,\"strength\":%d,\"error\":\"%s\",\"frame\":%u,\"connected\":%u,\"activeEngines\":%u,\"controlType\":%u,\"throttle\":%.6f,\"impulses\":%u,\"wakes\":%u,\"dragCalls\":%u,\"pitchCalls\":%u,\"wheelCalls\":%u,\"rodCalls\":%u,\"graphChanges\":%u}\n",phase,enabled?"true":"false",strength,last_error,frame_count,car_count,paused()?0:active_count,control_type,throttle,impulses,wakes,drag_calls,pitch_calls,wheel_calls,rod_calls,graph_changes);
  if(before==status_sequence)break;
 }while(++attempts<4);
 if(attempts==4||length<=0||length>=sizeof(text))return;
 wcscpy(path,runtime_dir);wcscat(path,L"status.json");
 f=CreateFileW(path,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);if(f==INVALID_HANDLE_VALUE)return;
 WriteFile(f,text,length,&written,NULL);CloseHandle(f);
}
static int start_native(void){
 U tries,count=0;Hook *h;
 static const U drag_sites[]={0x62b18a,0x62b207,0x62b30e,0x62b38d,0x62b45a,0x62b4d6};
 static const U vector_site[]={0x5f8796},cross_site[]={0x5f8876};
 read_config();if(!config_valid)return 0;
 if(crawl_requested){
  tls_index=TlsAlloc();if(tls_index==TLS_OUT_OF_INDEXES)return 0;
  InitializeCriticalSection(&state_lock);
  InterlockedExchange(&crawl_state_ready,1);
  for(tries=WHEEL;tries<HOOK_COUNT;tries++){hooks[tries].gate=(U)&enabled;hooks[tries].pause=G(0x7be0f4);}
  hooks[DRAG].sites=drag_sites;hooks[DRAG].site_count=6;
  hooks[VECTOR].sites=vector_site;hooks[VECTOR].site_count=1;
  hooks[CROSS].sites=cross_site;hooks[CROSS].site_count=1;
  count=HOOK_COUNT;
 }
 if(prevent_end){h=&hooks[count++];memset(h,0,sizeof(*h));h->address=G(0x5862dc);h->length=2;h->raw=1;memcpy(h->original,"\x74\x16",2);memcpy(h->replacement,"\xeb\x28",2);}
 if(unlock_cameras){h=&hooks[count++];memset(h,0,sizeof(*h));h->address=G(0x51c98c);h->length=6;h->raw=1;memcpy(h->original,"\x0f\x84\x55\x03\x00\x00",6);memset(h->replacement,0x90,6);}
 if(!count){phase="disabled";return 1;}
 if(!prepare_hooks(hooks,count))return 0;
 for(tries=0;tries<200;tries++){if(install_hooks(hooks,count)){phase="ready";return 1;}Sleep(25);}return 0;
}
