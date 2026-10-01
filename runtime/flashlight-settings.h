/* MIT. Shared INI validation and bounded live flashlight adjustments. */
#ifndef NEMT_FLASHLIGHT_SETTINGS_H
#define NEMT_FLASHLIGHT_SETTINGS_H
#include <stdlib.h>
enum {FLASH_RANGE,FLASH_ANGLE,FLASH_BRIGHTNESS,FLASH_SETTING_COUNT};
static const char *flash_setting_names[]={"FlashlightRangeM","FlashlightAngleDeg","FlashlightBrightnessPct"};
static const double flash_defaults[]={45,70,100};
static const double flash_minimum[]={5,10,0},flash_maximum[]={1000,150,100};
static double flash_safe(double value,int setting){
 return value>=flash_minimum[setting]&&value<=flash_maximum[setting]?value:flash_defaults[setting];
}
static double flash_parse(const char *text,int setting){
 char *end;double n=strtod(text,&end);int empty=end==text;
 while(*end==' '||*end=='\t')end++;
 return empty||*end?flash_defaults[setting]:flash_safe(n,setting);
}
static double flash_adjust(double value,int setting,int direction){
 double next=flash_safe(value,setting)+(direction>0?5:-5);
 if(next<flash_minimum[setting])next=flash_minimum[setting];
 if(next>flash_maximum[setting])next=flash_maximum[setting];
 return next;
}
#endif
