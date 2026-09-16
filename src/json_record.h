/* Minimal, bounded JSON reader for an ownership record, not a substring search.
 * MIT License. The input remains owned by the caller. No allocations, no SDK.
 * It validates the complete document, rejects duplicate top-level keys, and
 * only returns typed, top-level values. Nested data is validated but skipped.
 */
#ifndef NEMT_JSON_RECORD_H
#define NEMT_JSON_RECORD_H
#include <string.h>
#include <stdlib.h>
#include <limits.h>

enum { J_STRING=1, J_NUMBER, J_TRUE, J_FALSE, J_NULL, J_OBJECT, J_ARRAY };
typedef struct { const char *p; size_t n; int type; } JsonValue;
typedef struct { char key[64]; JsonValue value; } JsonMember;
typedef struct { JsonMember member[64]; int count; } JsonRecord;

static void json_space(const char **p) {
    while (**p==' ' || **p=='\t' || **p=='\r' || **p=='\n') ++*p;
}
static int json_hex(char c) {
    if(c>='0' && c<='9') return c-'0';
    if(c>='a' && c<='f') return c-'a'+10;
    if(c>='A' && c<='F') return c-'A'+10;
    return -1;
}
static int json_scan_string(const char **cursor) {
    const unsigned char *p=(const unsigned char *)*cursor;
    if(*p++!='"') return 0;
    while(*p && *p!='"') {
        if(*p<32) return 0;
        if(*p=='\\') {
            ++p;
            if(!*p) return 0;
            if(*p=='u') {
                int i; ++p;
                for(i=0;i<4;++i,++p) if(json_hex((char)*p)<0) return 0;
                continue;
            }
            if(!strchr("\"\\/bfnrt",*p)) return 0;
        }
        ++p;
    }
    if(*p!='"') return 0;
    *cursor=(const char *)p+1;
    return 1;
}
static int json_decode(JsonValue v,char *out,size_t cap) {
    const char *p=v.p+1,*end=v.p+v.n-1;
    size_t n=0;
    if(v.type!=J_STRING || !cap) return 0;
    while(p<end) {
        unsigned char c=(unsigned char)*p++;
        if(c=='\\') {
            c=(unsigned char)*p++;
            if(c=='u') {
                int i,code=0;
                for(i=0;i<4;++i) code=code*16+json_hex(*p++);
                /* Ownership keys, runtime identifier and hashes are ASCII. */
                if(code==0 || code>127) return 0;
                c=(unsigned char)code;
            } else if(c=='b') c='\b';
            else if(c=='f') c='\f';
            else if(c=='n') c='\n';
            else if(c=='r') c='\r';
            else if(c=='t') c='\t';
        }
        if(n+1>=cap) return 0;
        out[n++]=(char)c;
    }
    out[n]=0;
    return 1;
}
static int json_value(const char **cursor,JsonValue *out,int depth) {
    const char *p=*cursor,*start;
    int type;
    if(depth>16) return 0;
    json_space(&p); start=p;
    if(*p=='"') {
        if(!json_scan_string(&p)) return 0;
        type=J_STRING;
    } else if(*p=='{' || *p=='[') {
        int object=*p=='{'; char close=object?'}':']';
        type=object?J_OBJECT:J_ARRAY;
        ++p; json_space(&p);
        if(*p!=close) for(;;) {
            JsonValue child;
            if(object) {
                if(!json_scan_string(&p)) return 0;
                json_space(&p); if(*p++!=':') return 0;
            }
            if(!json_value(&p,&child,depth+1)) return 0;
            json_space(&p);
            if(*p==close) break;
            if(*p++!=',') return 0;
            json_space(&p);
        }
        if(*p++!=close) return 0;
    } else if(!strncmp(p,"true",4)) { p+=4; type=J_TRUE; }
    else if(!strncmp(p,"false",5)) { p+=5; type=J_FALSE; }
    else if(!strncmp(p,"null",4)) { p+=4; type=J_NULL; }
    else {
        type=J_NUMBER;
        if(*p=='-') ++p;
        if(*p=='0') ++p;
        else {
            if(*p<'1' || *p>'9') return 0;
            do {++p;} while(*p>='0' && *p<='9');
        }
        if(*p=='.') {
            ++p; if(*p<'0' || *p>'9') return 0;
            do {++p;} while(*p>='0' && *p<='9');
        }
        if(*p=='e' || *p=='E') {
            ++p; if(*p=='+' || *p=='-') ++p;
            if(*p<'0' || *p>'9') return 0;
            do {++p;} while(*p>='0' && *p<='9');
        }
    }
    out->p=start; out->n=(size_t)(p-start); out->type=type;
    *cursor=p; return 1;
}
static int json_record_parse(const char *text,JsonRecord *doc) {
    const char *p=text;
    int i;
    memset(doc,0,sizeof(*doc));
    if((unsigned char)p[0]==0xef && (unsigned char)p[1]==0xbb && (unsigned char)p[2]==0xbf) p+=3;
    json_space(&p); if(*p++!='{') return 0;
    json_space(&p);
    if(*p!='}') for(;;) {
        JsonValue key;
        JsonMember *m;
        if(doc->count>=64) return 0;
        m=&doc->member[doc->count];
        key.p=p; key.type=J_STRING;
        if(!json_scan_string(&p)) return 0;
        key.n=(size_t)(p-key.p);
        if(!json_decode(key,m->key,sizeof(m->key))) return 0;
        for(i=0;i<doc->count;++i) if(!strcmp(doc->member[i].key,m->key)) return 0;
        json_space(&p); if(*p++!=':') return 0;
        if(!json_value(&p,&m->value,1)) return 0;
        ++doc->count; json_space(&p);
        if(*p=='}') break;
        if(*p++!=',') return 0;
        json_space(&p);
    }
    if(*p++!='}') return 0;
    json_space(&p);
    return *p==0;
}
static const JsonValue *json_member(const JsonRecord *doc,const char *key) {
    int i;
    for(i=0;i<doc->count;++i) if(!strcmp(doc->member[i].key,key)) return &doc->member[i].value;
    return NULL;
}
static int json_bool(const JsonRecord *doc,const char *key,int fallback) {
    const JsonValue *v=json_member(doc,key);
    if(!v || (v->type!=J_TRUE && v->type!=J_FALSE)) return fallback;
    return v->type==J_TRUE;
}
static int json_int(const JsonRecord *doc,const char *key,int fallback) {
    const JsonValue *v=json_member(doc,key);
    const char *p; size_t n; unsigned long value=0,limit;
    int neg=0;
    if(!v || v->type!=J_NUMBER || !v->n) return fallback;
    p=v->p; n=v->n;
    if(*p=='-') {neg=1; ++p; --n;}
    limit=neg?(unsigned long)INT_MAX+1UL:(unsigned long)INT_MAX;
    while(n--) {
        unsigned digit=(unsigned)(*p++-'0');
        if(digit>9 || value>(limit-digit)/10) return fallback;
        value=value*10+digit;
    }
    if(neg && value==(unsigned long)INT_MAX+1UL) return INT_MIN;
    return neg?-(int)value:(int)value;
}
static int json_text(const JsonRecord *doc,const char *key,char *out,size_t cap) {
    const JsonValue *v=json_member(doc,key);
    return v && json_decode(*v,out,cap);
}
#endif
