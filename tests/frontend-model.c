/* Portable regression tests: gcc -std=c99 tests/frontend-model.c -o model-test */
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "../src/settings_model.h"
static int checks;
#define CHECK(x) do {++checks; if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);return 1;}} while(0)
int main(void) {
    JsonRecord doc;Settings s;char value[65];int i;
    const char *bad[]={"", "{", "[]", "{\"a\":}", "{\"a\":true,}","{\"a\":tru}",
        "{\"a\":1} trailing", "{\"a\":1,\"a\":2}", "{\"enabled\":true,\"enabled\":false}",
        "{\"x\":\"bad\\q\"}","{\"x\":\"bad\ntext\"}","{\"x\":01}","{\"x\":1.}","{\"x\":1e}",
        "{\"x\":[1,]}","{\"x\":{\"a\":1,}}","{\"x\":\"\\u123\"}"};
    for(i=0;i<(int)(sizeof(bad)/sizeof(bad[0]));++i) CHECK(!json_record_parse(bad[i],&doc));
    CHECK(json_record_parse("{\"schema\":1,\"product\":\"NEMT\",\"enabled\": true,\"files\":{\"x\":[1,true,null,\"escaped \\\" quote\"]}}",&doc));
    CHECK(json_int(&doc,"schema",0)==1);CHECK(json_bool(&doc,"enabled",0)==1);
    CHECK(json_text(&doc,"product",value,sizeof(value)) && !strcmp(value,"NEMT"));
    CHECK(!json_member(&doc,"x"));
    CHECK(json_record_parse("{\"notes\":{\"product\":\"NEMT\"},\"product\":\"OTHER\",\"schema\":2,\"enabled\":\"true\"}",&doc));
    CHECK(json_bool(&doc,"enabled",0)==0);CHECK(json_int(&doc,"schema",0)==2);
    CHECK(json_text(&doc,"product",value,sizeof(value)) && !strcmp(value,"OTHER"));
    CHECK(json_record_parse("{\"small\":-2147483648,\"large\":2147483647,\"overflow\":99999999999999999999999,\"fraction\":1.5}",&doc));
    CHECK(json_int(&doc,"small",0)==INT_MIN);CHECK(json_int(&doc,"large",0)==INT_MAX);
    CHECK(json_int(&doc,"overflow",17)==17);CHECK(json_int(&doc,"fraction",17)==17);
    CHECK(json_record_parse("{\"product\":\"NEM\\u0054\"}",&doc));
    CHECK(json_text(&doc,"product",value,sizeof(value)) && !strcmp(value,"NEMT"));
    settings_from_manifest(NULL,&s);
    CHECK(s.window_features && s.center_windowed && s.strength==10 && s.hud_left);
    CHECK(!s.crawl && !s.prefer_pcores && !s.startup_log && s.max_log_kb==8192);
    CHECK(json_record_parse("{\"enabled\":true,\"runtime\":\"nemt-native\",\"windowFeatures\":false,\"unlockFPS\":true,\"limitToVSync\":true,\"verboseLoading\":true,\"startupLog\":false,\"preventEnd\":true,\"unlockCameras\":true,\"crawl\":true,\"strength\":77,\"crawlHUDAnchor\":\"BottomRight\"}",&doc));
    settings_from_manifest(&doc,&s);
    CHECK(!s.window_features && s.unlock_fps && s.limit_vsync && s.verbose_loading);
    CHECK(s.prevent_end && s.unlock_cameras && s.crawl && s.strength==77 && !s.hud_left);
    CHECK(json_record_parse("{\"enabled\":false,\"runtime\":\"nemt-native\",\"windowFeatures\":true,\"unlockFPS\":true,\"verboseLoading\":true,\"preventEnd\":true,\"crawl\":true,\"strength\":73,\"crawlHUDAnchor\":\"BottomRight\"}",&doc));
    settings_from_manifest(&doc,&s);
    CHECK(!s.window_features && !s.unlock_fps && !s.verbose_loading && !s.prevent_end && !s.crawl);
    CHECK(s.strength==73 && !s.hud_left);
    CHECK(json_record_parse("{\"enabled\":true,\"runtime\":\"nemt-native\",\"strength\":999}",&doc));
    settings_from_manifest(&doc,&s);CHECK(s.strength==100);
    CHECK(json_record_parse("{\"enabled\":true,\"runtime\":\"nemt-native\",\"strength\":-2}",&doc));
    settings_from_manifest(&doc,&s);CHECK(s.strength==0);
    settings_defaults(&s);s.startup_log=1;s.strength=31;s.hud_left=0;
    settings_recommended(&s,1,1);
    CHECK(s.prefer_pcores && s.skip_movie && s.window_features && s.unlock_fps);
    CHECK(s.limit_vsync && s.verbose_loading && s.cab_needles && s.background_audio);
    CHECK(s.ignore_red_signal && s.editor_windows && s.editor_tools && s.editor_audio);
    CHECK(s.editor_keys && s.editor_pan && s.prevent_end && s.unlock_cameras && s.crawl && s.counter_tilt);
    CHECK(!s.startup_log && s.strength==31 && !s.hud_left);
    settings_defaults(&s);settings_recommended(&s,0,0);CHECK(!s.prefer_pcores && !s.cab_needles);
    s.prefer_pcores=1;settings_recommended(&s,0,0);CHECK(s.prefer_pcores);
    printf("frontend model: %d checks passed\n",checks);return 0;
}
