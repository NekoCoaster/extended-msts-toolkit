/* MIT. Shared restart-only movement tuning, used by frontend and runtime. */
#ifndef NEMT_WALKING_SETTINGS_H
#define NEMT_WALKING_SETTINGS_H
#include <stdlib.h>
enum { WALK_SPEED, FLY_SPEED, SPRINT_MULTIPLIER, SLOW_DIVISOR, WALK_TUNING_COUNT };
static const char *walk_tuning_names[]={"WalkSpeedMps","FlySpeedMps","SprintMultiplier","SlowDivisor"};
static const double walk_tuning_defaults[]={3,17,2,2};
static double walk_tuning_safe(double n,int i){
 /* Comparisons also reject NaN/infinity; divisors can never reach zero. */
 return n>=(i<2?0.01:1)&&n<=(i<2?1000:100)?n:walk_tuning_defaults[i];
}
static double walk_tuning_parse(const char *text,int i){
 char *end;double n=strtod(text,&end);
 while(*end==' '||*end=='\t')end++;
 return end==text||*end?walk_tuning_defaults[i]:walk_tuning_safe(n,i);
}
#endif
