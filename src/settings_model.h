/* GUI-independent settings/manifest model. MIT License. */
#ifndef NEMT_SETTINGS_MODEL_H
#define NEMT_SETTINGS_MODEL_H
#include <string.h>
#include "json_record.h"
typedef struct {
 int prefer_pcores, skip_movie, window_features, unlock_fps, limit_vsync, verbose_loading;
 int startup_log, cab_needles, background_audio, ignore_red_signal;
 int editor_windows, editor_tools, editor_audio, editor_keys, editor_pan;
 int prevent_end, unlock_cameras, crawl, counter_tilt, strength, hud_left;
 char derail_key[32];
 char key_forward[32], key_backward[32], key_left[32], key_right[32], key_up[32], key_down[32];
 int max_log_kb, max_backup_logs, center_windowed, write_status;
 char monitor[32];
} Settings;

static void settings_defaults(Settings*s){memset(s,0,sizeof(*s));s->window_features=1;s->strength=10;s->hud_left=1;s->max_log_kb=8192;s->center_windowed=1;strcpy(s->derail_key,"BACKSLASH");strcpy(s->key_forward,"w");strcpy(s->key_backward,"s");strcpy(s->key_left,"a");strcpy(s->key_right,"d");strcpy(s->key_up,"e");strcpy(s->key_down,"q");}
/* Match legacy/NEMT.ps1's manifest-driven controls. INI overrides are applied
 * separately, and only for an enabled, recognized installation. */
static void settings_from_manifest(const JsonRecord *doc,Settings *s) {
    char value[64];
    int active,native;
    settings_defaults(s);
    if(!doc) return;
    active=json_bool(doc,"enabled",0);
    native=json_text(doc,"runtime",value,sizeof(value)) && !strcmp(value,"nemt-native");
    s->strength=json_int(doc,"strength",0);
    if(s->strength<0) s->strength=0;
    if(s->strength>100) s->strength=100;
    s->hud_left=!(json_text(doc,"crawlHUDAnchor",value,sizeof(value)) && !strcmp(value,"BottomRight"));
    if(json_member(doc,"windowFeatures")) s->window_features=active && json_bool(doc,"windowFeatures",0);
    s->unlock_fps=active && json_bool(doc,"unlockFPS",0);
    s->verbose_loading=active && json_bool(doc,"verboseLoading",0);
    s->startup_log=active && json_bool(doc,"startupLog",0);
    s->limit_vsync=active && json_bool(doc,"limitToVSync",0);
    s->prevent_end=active && native && json_bool(doc,"preventEnd",0);
    s->unlock_cameras=active && native && json_bool(doc,"unlockCameras",0);
    s->crawl=active && (!native || json_bool(doc,"crawl",0));
}
static void settings_recommended(Settings *s,int widescreen,int cpu_supported) {
    if(cpu_supported) s->prefer_pcores=1;
    s->skip_movie=1; s->window_features=1; s->unlock_fps=1;
    s->limit_vsync=1; s->verbose_loading=1; s->startup_log=0;
    s->cab_needles=widescreen!=0; s->background_audio=1; s->ignore_red_signal=1;
    s->editor_windows=1; s->editor_tools=1; s->editor_audio=1;
    s->editor_keys=1; s->editor_pan=1; s->prevent_end=1;
    s->unlock_cameras=1; s->crawl=1; s->counter_tilt=1;
}
#endif
