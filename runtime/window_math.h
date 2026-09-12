/* Pure argument/placement helpers. Keep the original command line immutable. */
static int ascii_lower(int c){return c>='A'&&c<='Z'?c+32:c;}
static int vm_mode(const char *s,unsigned int n){
 static const char prefix[]="-vm:";unsigned int i;
 if(n<5)return 0;for(i=0;i<4;i++)if(ascii_lower(s[i])!=prefix[i])return 0;
 if(ascii_lower(s[4])=='w'&&(n==5||s[5]==','))return 1;
 if(n>=6&&ascii_lower(s[4])=='b'&&ascii_lower(s[5])=='w'&&(n==6||s[6]==','))return 2;
 return 0;
}
static int normalize_vm(const char *src,char *dst){
 unsigned int i=0,out=0,begin,end,j,token=0,slashes;int quote,mode=0,m;
 while(src[i]){
  if(src[i]==' '||src[i]=='\t'){if(dst)dst[out]=src[i];out++;i++;continue;}
  begin=i;quote=0;slashes=0;
  while(src[i]){
   if(src[i]=='"'&&!(slashes&1))quote=!quote;
   if(!quote&&(src[i]==' '||src[i]=='\t'))break;
   slashes=src[i]=='\\'?slashes+1:0;i++;
  }
  end=i;j=begin;
  if(src[j]=='"'&&end>j+1&&src[end-1]=='"'){j++;end--;}
  m=token?vm_mode(src+j,end-j):0;if(m)mode=m;
  for(;begin<i;begin++){if(m==2&&begin==j+4)continue;if(dst)dst[out]=src[begin];out++;}
  token++;
 }
 if(dst)dst[out]=0;return mode;
}
static void centered_position(int left,int top,int right,int bottom,int width,int height,int *x,int *y){
 *x=left+(right-left-width)/2;*y=top+(bottom-top-height)/2;
}
static int has_noclamp(const char *s){
 unsigned int i=0,begin,end,k,token=0,slashes;int quote,match;static const char option[]="-noclamp";
 while(s[i]){
  while(s[i]==' '||s[i]=='\t')i++;if(!s[i])break;begin=i;quote=0;slashes=0;
  while(s[i]){if(s[i]=='"'&&!(slashes&1))quote=!quote;if(!quote&&(s[i]==' '||s[i]=='\t'))break;slashes=s[i]=='\\'?slashes+1:0;i++;}
  end=i;if(s[begin]=='"'&&end>begin+1&&s[end-1]=='"'){begin++;end--;}
  match=token&&end-begin==8;for(k=0;match&&k<8;k++)if(ascii_lower(s[begin+k])!=option[k])match=0;
  if(match)return 1;token++;
 }return 0;
}
/* Caller allocates input length + 12 bytes. */
static void normalize_launch(const char *src,char *dst,int fps){
 normalize_vm(src,dst);if(fps&&!has_noclamp(dst)){unsigned int n=0,k;while(dst[n])n++;for(k=0;k<10;k++)dst[n+k]=" -noclamp"[k];}
}
