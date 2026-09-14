/* Pure argument/placement helpers. Keep the original command line immutable. */
static int ascii_lower(int c){return c>='A'&&c<='Z'?c+32:c;}
/* 1 = windowed, 3 = native fullscreen resolution. No private bw alias. */
static int vm_mode(const char *s,unsigned int n){
 static const char prefix[]="-vm:";unsigned int i;
 if(n<5)return 0;for(i=0;i<4;i++)if(ascii_lower(s[i])!=prefix[i])return 0;
 if(ascii_lower(s[4])=='w'&&(n==5||s[5]==','))return 1;
 if((s[4]>='0'&&s[4]<='9')||(ascii_lower(s[4])=='s'&&(n==5||s[5]==',')))return 3;
 return 0;
}
static unsigned int vm_token(const char *src,unsigned int *position,int *mode,int token){
 unsigned int begin=*position,end,j,slashes=0;int quote=0;
 while(src[*position]){char c=src[*position];if(c=='"'&&!(slashes&1))quote=!quote;if(!quote&&(c==' '||c=='\t'))break;slashes=c=='\\'?slashes+1:0;(*position)++;}
 end=*position;j=begin;if(src[j]=='"'&&end>j+1&&src[end-1]=='"'){j++;end--;}
 *mode=token?vm_mode(src+j,end-j):0;return begin;
}
static int normalize_vm(const char *src,char *dst){
 unsigned int i=0,out=0,begin,j;int token=0,m,mode=0,fullscreen=0;
 while(src[i]){if(src[i]==' '||src[i]=='\t'){i++;continue;}vm_token(src,&i,&m,token++);if(m==3)fullscreen=1;if(m)mode=m;}
 i=0;token=0;
 while(src[i]){if(src[i]==' '||src[i]=='\t'){if(dst)dst[out]=src[i];out++;i++;continue;}
  begin=vm_token(src,&i,&m,token++);if(fullscreen&&m==1)continue;
  for(j=begin;j<i;j++){if(dst)dst[out]=src[j];out++;}
 }
 if(dst)dst[out]=0;return fullscreen?3:mode;
}
static void centered_position(int left,int top,int right,int bottom,int width,int height,int *x,int *y){
 *x=left+(right-left-width)/2;*y=top+(bottom-top-height)/2;
}
static int has_launch_option(const char *s,const char *option){
 unsigned int i=0,begin,end,k,token=0,slashes,n=(unsigned int)strlen(option);int quote,match;
 while(s[i]){
  while(s[i]==' '||s[i]=='\t')i++;if(!s[i])break;begin=i;quote=0;slashes=0;
  while(s[i]){if(s[i]=='"'&&!(slashes&1))quote=!quote;if(!quote&&(s[i]==' '||s[i]=='\t'))break;slashes=s[i]=='\\'?slashes+1:0;i++;}
  end=i;if(s[begin]=='"'&&end>begin+1&&s[end-1]=='"'){begin++;end--;}
  match=token&&end-begin==n;for(k=0;match&&k<n;k++)if(ascii_lower(s[begin+k])!=option[k])match=0;
  if(match)return 1;token++;
 }return 0;
}
static int has_noclamp(const char *s){return has_launch_option(s,"-noclamp");}
static int has_toolset(const char *s){return has_launch_option(s,"-toolset");}
/* Caller allocates input length + 32 bytes for the two optional tokens. */
static void normalize_launch(const char *src,char *dst,int fps){
 int mode;if(has_toolset(src)){strcpy(dst,src);return;}mode=normalize_vm(src,dst);
 if(!mode)strcat(dst," -vm:w");
 if(fps&&!has_noclamp(dst))strcat(dst," -noclamp");
}
