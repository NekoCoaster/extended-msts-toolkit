/* The simulation-thread frame hook calls MSTS's derail routine.
   Check its entry before calling, and require an acyclic
   reciprocal consist because the native code traverses both link directions. */
static void (__fastcall *crawl_derail_native)(U)=(void*)0x62e017;
static void crawl_manual_event(Registers *r){
 U *stack=(U*)(r->esp+4),*event=(U*)stack[6],*device=(U*)stack[9],mode;int allowed;
 if(!event||!device||!device[1]||*((B*)device[1]+0x2d)!=1||event[0]!=0x1002b||event[1]>1)return;
 allowed=!(stack[10]&15)&&!paused()&&crawl_control_focus()&&read_memory(G(0x829980),&mode,4)&&!mode;
 if(crawl_derail_edge(event[1]?CRAWL_DERAIL:0,allowed))crawl_derail_pending=1;
}
static int crawl_derail_consist(void){
 B entry[6];U i,links=0;
 if(!crawl_requested||!prevent_end||!car_count||paused())return 0;
 for(i=0;i<car_count;i++){
  Car *previous=find_car(cars[i].links[0]),*next=find_car(cars[i].links[1]);
  if((cars[i].links[0]&&(!previous||previous->links[1]!=cars[i].id))||
     (cars[i].links[1]&&(!next||next->links[0]!=cars[i].id))){fail("Invalid directed consist for manual derailment");return 0;}
  links+=!!cars[i].links[0]+!!cars[i].links[1];
 }
 if(links!=2*(car_count-1)||!read_memory((U)crawl_derail_native,entry,6)||
    memcmp(entry,"\x55\x8b\xec\x83\xec\x10",6)){fail("Native derail routine or consist validation failed");return 0;}
 for(i=0;i<car_count;i++)if(!cars[i].derailed){
  crawl_derail_native(cars[i].id);
  /* Native collision derailment expects a moving body. Wake a stationary one
     as well so the deliberate command works with the throttle closed. */
  *((B*)ru((B*)cars[i].id+0x5c)+0xf2)&=~8;
 }
 return 1;
}
