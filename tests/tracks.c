#include <assert.h>
#include "../runtime/loader.c"
int main(int argc,char **argv){unsigned char a[TRACK_MASK]={0},b[TRACK_MASK]={0};unsigned missing=0;char *global,*local,*db;WCHAR path[MAX_PATH];
 assert(track_definitions("_Skip ( TrackSection ( 99 ) ) _INFO ( TrackSection from author ) TrackSection ( 1 SectionSize ( 2 ) )",a));assert(!track_has(a,99));
 assert(track_definitions("TrackSection ( SectionCurve ( 0 ) 40000 4.5 0 )",b));
 assert(track_missing("TrVectorSections ( 1 40000 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 )",a,b,&missing)==0);
 assert(track_missing("TrVectorSections ( 1 36013 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 )",a,b,&missing)==1&&missing==36013);
 assert(track_missing("TrVectorSections ( 1 36013 0 )",a,b,&missing)==-1);
 assert(track_missing("_Skip ( TrVectorSections ( 1 36013 ) )",a,b,&missing)==-1);
 if(argc==5){memset(a,0,sizeof(a));memset(b,0,sizeof(b));mbstowcs(path,argv[1],MAX_PATH);global=track_read(path);mbstowcs(path,argv[2],MAX_PATH);local=track_read(path);mbstowcs(path,argv[3],MAX_PATH);db=track_read(path);assert(global&&local&&db);assert(track_definitions(global,a)&&track_definitions(local,b));assert(track_missing(db,a,b,&missing)==atoi(argv[4]));printf("Real route comparison PASS; expected missing=%s, first missing=%u\n",argv[4],missing);}
 puts("PASS track dependency parsing, dynamic sections, skipped comments, malformed input and missing definitions.");return 0;
}
