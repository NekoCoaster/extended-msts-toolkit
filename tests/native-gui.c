/* Windows/TinyCC regression harness. It uses a disposable TEMP directory and
 * synthetic files, never a real MSTS installation. No validation bypass is
 * added to the production frontend: tests call internal functions directly. */
#define WinMain NemtApplicationWinMain
#include "../src/nemt.c"
#undef WinMain
#include <assert.h>
static int checks,failures;
static int display_notices,display_width=2560;
static BOOL WINAPI fake_display_info(HMONITOR monitor,LPMONITORINFO info){
 memset(info,0,sizeof(*info));info->cbSize=sizeof(*info);info->rcMonitor.right=display_width;info->rcMonitor.bottom=1440;return TRUE;
}
static int WINAPI fake_display_notice(HWND owner,LPCSTR text,LPCSTR title,UINT flags){
 display_notices++;assert(strstr(text,"2048"));return IDOK;
}
static const char *test_phase="setup/installer";
#define CHECK(x) do {++checks;if(!(x)){++failures;printf("FAIL line %d [%s, layout DPI %d]: %s\n",__LINE__,test_phase,g_dpi,#x);}}while(0)
/* A fictitious work RECT does not enlarge Windows' real maximum track size.
 * Only synthetic layout tests opt into a larger *test-window* limit. The
 * production wndproc and normal desktop tests keep their normal limits. */
#define SYNTHETIC_DESKTOP_SIZE 4096
static int synthetic_layout;
static int erase_messages,child_paints;
static WNDPROC repaint_original;
static LRESULT CALLBACK test_wndproc(HWND w,UINT m,WPARAM wp,LPARAM lp) {
    if(m==WM_ERASEBKGND) ++erase_messages;
    if(m==WM_GETMINMAXINFO && synthetic_layout) {
        LRESULT result=wndproc(w,m,wp,lp);
        MINMAXINFO *limits=(MINMAXINFO *)lp;
        if(limits->ptMaxTrackSize.x<SYNTHETIC_DESKTOP_SIZE)
            limits->ptMaxTrackSize.x=SYNTHETIC_DESKTOP_SIZE;
        if(limits->ptMaxTrackSize.y<SYNTHETIC_DESKTOP_SIZE)
            limits->ptMaxTrackSize.y=SYNTHETIC_DESKTOP_SIZE;
        return result;
    }
    return wndproc(w,m,wp,lp);
}
static LRESULT CALLBACK repaint_probe(HWND w,UINT m,WPARAM wp,LPARAM lp) {
    if(m==WM_PAINT) ++child_paints;
    return CallWindowProcA(repaint_original,w,m,wp,lp);
}
/* SetWindowPos succeeding does not promise that the requested size survived
 * WM_GETMINMAXINFO. Check the actual size before asserting an exact fit. */
static void check_outer_size(int width,int height) {
    RECT actual;BOOL ok=GetWindowRect(g_main,&actual);
    CHECK(ok);if(!ok) return;
    if(actual.right-actual.left!=width || actual.bottom-actual.top!=height)
        printf("  requested outer %d x %d; actual %ld x %ld; system max-track %d x %d\n",
            width,height,actual.right-actual.left,actual.bottom-actual.top,
            GetSystemMetrics(SM_CXMAXTRACK),GetSystemMetrics(SM_CYMAXTRACK));
    CHECK(actual.right-actual.left==width);
    CHECK(actual.bottom-actual.top==height);
}
static void check_test_limits(int enabled) {
    MINMAXINFO limits;
    memset(&limits,0,sizeof(limits));
    limits.ptMaxTrackSize.x=800;limits.ptMaxTrackSize.y=600;
    test_wndproc(g_main,WM_GETMINMAXINFO,0,(LPARAM)&limits);
    CHECK(limits.ptMinTrackSize.x==dip(400));
    CHECK(limits.ptMinTrackSize.y==dip(260));
    CHECK(limits.ptMaxTrackSize.x==(enabled?SYNTHETIC_DESKTOP_SIZE:800));
    CHECK(limits.ptMaxTrackSize.y==(enabled?SYNTHETIC_DESKTOP_SIZE:600));
}
static void desktop_startup_checks(void) {
    RECT work,outer,actual,client,borders;
    ViewportLayout expected;DWORD style;int width,height;BOOL ok;
    test_phase="real desktop startup";
    CHECK(!synthetic_layout);
    check_test_limits(0);
    ok=SystemParametersInfoA(SPI_GETWORKAREA,0,&work,0);CHECK(ok);if(!ok) return;
    ok=initial_window_rect(&work,&outer);CHECK(ok);if(!ok) return;
    printf("layout desktop: %ld x %ld work area, %d DPI; max-track %d x %d\n",
        work.right-work.left,work.bottom-work.top,g_dpi,
        GetSystemMetrics(SM_CXMAXTRACK),GetSystemMetrics(SM_CYMAXTRACK));
    CHECK(SetWindowPos(g_main,NULL,outer.left,outer.top,outer.right-outer.left,outer.bottom-outer.top,
        SWP_NOZORDER|SWP_NOACTIVATE));layout_controls();
    check_outer_size(outer.right-outer.left,outer.bottom-outer.top);
    ok=GetWindowRect(g_main,&actual);CHECK(ok);if(!ok) return;
    CHECK(actual.left>=work.left && actual.top>=work.top && actual.right<=work.right && actual.bottom<=work.bottom);
    /* Predict the viewport from the requested, work-area-bounded frame, not
     * from the result being tested. Small real desktops may need scrollbars. */
    SetRect(&borders,0,0,0,0);
    ok=AdjustWindowRectEx(&borders,MAIN_WINDOW_STYLE,FALSE,MAIN_WINDOW_EX_STYLE);CHECK(ok);if(!ok) return;
    width=(outer.right-outer.left)-(borders.right-borders.left);
    height=(outer.bottom-outer.top)-(borders.bottom-borders.top);
    viewport_layout(&expected,width,height,dip(CONTENT_WIDTH),dip(CONTENT_HEIGHT),
        GetSystemMetrics(SM_CXVSCROLL),GetSystemMetrics(SM_CYHSCROLL),0,0);
    ok=GetClientRect(g_main,&client);CHECK(ok);if(!ok) return;
    style=(DWORD)GetWindowLongA(g_main,GWL_STYLE);
    CHECK(client.right==expected.width && client.bottom==expected.height);
    CHECK(!!(style&WS_HSCROLL)==expected.horizontal);
    CHECK(!!(style&WS_VSCROLL)==expected.vertical);
    CHECK(g_scroll_x==0 && g_scroll_y==0);
}
static void resize_client_without_bars(int width,int height) {
    RECT frame;
    SetRect(&frame,0,0,width,height);
    CHECK(AdjustWindowRectEx(&frame,MAIN_WINDOW_STYLE,FALSE,MAIN_WINDOW_EX_STYLE));
    CHECK(SetWindowPos(g_main,NULL,0,0,frame.right-frame.left,frame.bottom-frame.top,
        SWP_NOMOVE|SWP_NOZORDER|SWP_NOACTIVATE));
    layout_controls();
    if(synthetic_layout) check_outer_size(frame.right-frame.left,frame.bottom-frame.top);
}
static void cosmetic_gui_checks(void) {
    RECT work,outer,client,restore,control_rect;DWORD style;
    int i,saved_dpi=g_dpi;const int dpis[]={96,120,144,192};
    HWND probe=GetDlgItem(g_main,IDC_SKIPMOVIE);
    CHECK(GetWindowRect(g_main,&restore));
    desktop_startup_checks();
    test_phase="synthetic layout";
    synthetic_layout=1;check_test_limits(1);
    for(i=0;i<4;++i) {
        g_dpi=dpis[i];SetRect(&work,0,0,SYNTHETIC_DESKTOP_SIZE,SYNTHETIC_DESKTOP_SIZE);
        printf("layout synthetic: %d DPI, preferred client %d x %d; test-window limit %d x %d\n",
            g_dpi,dip(CONTENT_WIDTH+STARTUP_EXTRA_WIDTH),dip(CONTENT_HEIGHT+STARTUP_EXTRA_HEIGHT),
            SYNTHETIC_DESKTOP_SIZE,SYNTHETIC_DESKTOP_SIZE);
        CHECK(initial_window_rect(&work,&outer));
        CHECK(outer.left>=work.left && outer.top>=work.top && outer.right<=work.right && outer.bottom<=work.bottom);
        CHECK(SetWindowPos(g_main,NULL,0,0,outer.right-outer.left,outer.bottom-outer.top,
            SWP_NOMOVE|SWP_NOZORDER|SWP_NOACTIVATE));layout_controls();
        check_outer_size(outer.right-outer.left,outer.bottom-outer.top);
        CHECK(GetClientRect(g_main,&client));
        CHECK(client.right>=dip(CONTENT_WIDTH+STARTUP_EXTRA_WIDTH));
        CHECK(client.bottom>=dip(CONTENT_HEIGHT+STARTUP_EXTRA_HEIGHT));
        CHECK(!(GetWindowLongA(g_main,GWL_STYLE)&(WS_HSCROLL|WS_VSCROLL)));
        /* A small viewport requires both bars. Growing to the EXACT content
         * size must remove both in one layout pass, regardless of old state. */
        resize_client_without_bars(dip(600),dip(500));
        style=(DWORD)GetWindowLongA(g_main,GWL_STYLE);
        CHECK((style&(WS_HSCROLL|WS_VSCROLL))==(WS_HSCROLL|WS_VSCROLL));
        scroll_to(100000,100000);CHECK(g_scroll_x>0 && g_scroll_y>0);
        resize_client_without_bars(dip(CONTENT_WIDTH),dip(CONTENT_HEIGHT));
        CHECK(!(GetWindowLongA(g_main,GWL_STYLE)&(WS_HSCROLL|WS_VSCROLL)));
        CHECK(g_scroll_x==0 && g_scroll_y==0);
        /* Work-area constraints win on a small screen (including offsets). */
        SetRect(&work,20,30,820,590);CHECK(initial_window_rect(&work,&outer));
        CHECK(outer.left>=work.left && outer.top>=work.top && outer.right<=work.right && outer.bottom<=work.bottom);
    }
    synthetic_layout=0;g_dpi=saved_dpi;test_phase="real desktop repaint";
    check_test_limits(0);
    resize_client_without_bars(dip(600),dip(500));scroll_to(0,0);
    repaint_original=(WNDPROC)(LONG_PTR)SetWindowLongA(probe,GWL_WNDPROC,(LONG)(LONG_PTR)repaint_probe);
    CHECK(repaint_original!=NULL);
    erase_messages=child_paints=0;
    scroll_to(dip(10),dip(22));
    CHECK(erase_messages>0);CHECK(child_paints>0);
    CHECK(!GetUpdateRect(g_main,NULL,FALSE));CHECK(!GetUpdateRect(probe,NULL,FALSE));
    /* Top and bottom controls cross the clip boundary and return. Repeating
     * this must not accumulate position drift or leave pending repaint work. */
    for(i=0;i<20;++i) {
        scroll_to(100000,100000);scroll_to(0,0);
        GetWindowRect(probe,&control_rect);MapWindowPoints(NULL,g_main,(POINT *)&control_rect,2);
        CHECK(control_rect.left==dip(ui_control(probe)->x));
        CHECK(control_rect.top==dip(ui_control(probe)->y));
        CHECK(!GetUpdateRect(probe,NULL,FALSE));
    }
    SetWindowLongA(probe,GWL_WNDPROC,(LONG)(LONG_PTR)repaint_original);
    CHECK(SetWindowPos(g_main,NULL,restore.left,restore.top,restore.right-restore.left,restore.bottom-restore.top,
        SWP_NOZORDER|SWP_NOACTIVATE));layout_controls();
    test_phase="controls/installer";
}
static void get_text(int id,char *out,int cap) {GetDlgItemTextA(g_main,id,out,cap);}
static void remove_fixture(const char *dir) {
    char p[MAX_PATH];const char *files[]={"NEMT\\settings.ini","NEMT\\installation.json","NEMT\\status.json","DINPUT.dll","fixture.exe"};int i;
    for(i=0;i<5;++i) {join_path(p,dir,files[i]);DeleteFileA(p);}
    join_path(p,dir,"NEMT");RemoveDirectoryA(p);RemoveDirectoryA(dir);
}
int main(void) {
    char temp[MAX_PATH],fixture[MAX_PATH],ini[MAX_PATH],manifest[MAX_PATH],status[MAX_PATH],proxy[MAX_PATH];
    char err[512],before[4][65],after[65],text[1024],*record_text=NULL;
    const char *paths[4];Settings s,loaded;MstsInfo info;JsonRecord record;WNDCLASSA wc;RECT a,b;
    HANDLE lock;int i;MSG msg;
    g_instance=GetModuleHandleA(NULL);GetCurrentDirectoryA(MAX_PATH,g_root);
    CHECK(GetTempPathA(MAX_PATH,temp)>0);CHECK(GetTempFileNameA(temp,"NMT",0,fixture)!=0);
    CHECK(DeleteFileA(fixture));CHECK(CreateDirectoryA(fixture,NULL));
    memset(&info,0,sizeof(info));join_path(info.path,fixture,"fixture.exe");
    CHECK(write_all(info.path,"synthetic fixture - not a game executable",(DWORD)strlen("synthetic fixture - not a game executable")));CHECK(sha_file(info.path,info.sha));
    info.valid=1;info.widescreen=1;strcpy(info.version,"synthetic test fixture");
    join_path(ini,fixture,"NEMT\\settings.ini");join_path(manifest,fixture,"NEMT\\installation.json");
    join_path(status,fixture,"NEMT\\status.json");join_path(proxy,fixture,"DINPUT.dll");
    settings_defaults(&s);s.prefer_pcores=1;s.crawl=1;s.prevent_end=1;s.counter_tilt=1;s.strength=77;s.hud_left=0;
    strcpy(s.monitor,"\\\\.\\DISPLAY99");
    s.high_resolution=1;
    CHECK(install_settings(&info,&s,0,err,sizeof(err)));
    CHECK(load_selection_settings(&info,&loaded,err,sizeof(err)));
    CHECK(loaded.prefer_pcores && loaded.crawl && loaded.strength==77 && !loaded.hud_left);
    CHECK(!strcmp(loaded.monitor,s.monitor));
    CHECK(loaded.high_resolution);
    /* A partial old INI must not clear CenterWindowed's true default. */
    CHECK(write_all(ini,"[Startup]\r\nPreferPCores=true\r\n[Derailment]\r\nDerailKey=F8\r\nCounterTilt=true\r\n[Editors]\r\nRE_CAM_FORWARD=i\r\n",(DWORD)strlen("[Startup]\r\nPreferPCores=true\r\n[Derailment]\r\nDerailKey=F8\r\nCounterTilt=true\r\n[Editors]\r\nRE_CAM_FORWARD=i\r\n")));
    load_settings(ini,&loaded);CHECK(loaded.center_windowed && loaded.window_features);
    CHECK(!strcmp(loaded.derail_key,"F8") && !strcmp(loaded.key_forward,"i"));
    /* Lock only the manifest against replacement. Earlier commits must roll
     * back rather than leaving the user's INI/DLL changed after this failure. */
    paths[0]=ini;paths[1]=proxy;paths[2]=manifest;paths[3]=status;
    for(i=0;i<4;++i) CHECK(sha_file(paths[i],before[i]));
    lock=CreateFileA(manifest,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,0,NULL);CHECK(lock!=INVALID_HANDLE_VALUE);
    s.strength=99;CHECK(!install_settings(&info,&s,0,err,sizeof(err)));if(lock!=INVALID_HANDLE_VALUE)CloseHandle(lock);
    for(i=0;i<4;++i) {CHECK(sha_file(paths[i],after));CHECK(!strcmp(before[i],after));}
    CHECK(strstr(err,"rolled back")!=NULL);
    /* Interactive controls are tested through native window messages. */
    init_fonts();memset(&wc,0,sizeof(wc));wc.lpfnWndProc=test_wndproc;wc.hInstance=g_instance;wc.lpszClassName="NEMTRegressionWindow";
    wc.hbrBackground=(HBRUSH)GetStockObject(WHITE_BRUSH);CHECK(RegisterClassA(&wc));
    g_main=CreateWindowExA(WS_EX_CONTROLPARENT,wc.lpszClassName,"NEMT regression tests",MAIN_WINDOW_STYLE,0,0,780,580,NULL,NULL,g_instance,NULL);
    CHECK(g_main!=NULL);CHECK(create_ui());ShowWindow(g_main,SW_SHOWNORMAL);UpdateWindow(g_main);SetActiveWindow(g_main);g_info=info;g_cpu_supported=0;
    cosmetic_gui_checks();
    settings_defaults(&s);settings_to_ui(&s);
    CHECK(g_monitor_count>=2);
    CHECK(!check_get(IDC_HIGHRES));
    SendDlgItemMessageA(g_main,IDC_HIGHRES,BM_CLICK,0,0);ui_to_settings(&loaded);CHECK(loaded.high_resolution);
    CHECK(nemt_large_display(2560,1440) && nemt_large_display(1080,2560));
    CHECK(!nemt_large_display(2048,2048) && !nemt_large_display(1920,1080));
    CHECK(panel_graphics_file()==0);
    panel_monitor_info=fake_display_info;panel_display_notice=fake_display_notice;
    check_set(IDC_HIGHRES,0);display_width=2048;refresh_display_guidance(1);CHECK(display_notices==0);
    get_text(IDC_HIGHRES,text,sizeof(text));CHECK(!strcmp(text,"Enable High-res support (Optional)"));
    CHECK(IsWindowEnabled(GetDlgItem(g_main,IDC_HIGHRES)));
    display_width=2560;refresh_display_guidance(1);CHECK(display_notices==1);
    get_text(IDC_HIGHRES,text,sizeof(text));CHECK(!strcmp(text,"Enable High-res support (Recommended)"));
    refresh_display_guidance(1);CHECK(display_notices==1);
    check_set(IDC_HIGHRES,1);display_width=3840;refresh_display_guidance(1);CHECK(display_notices==1);
    check_set(IDC_HIGHRES,0);refresh_display_guidance(1);CHECK(display_notices==2);
    {char graphics[MAX_PATH];join_path(graphics,fixture,"D3DIM700.dll");
     CHECK(write_all(graphics,"unknown",7));CHECK(panel_graphics_file()==2);
     refresh_display_guidance(1);CHECK(display_notices==3);
     get_text(IDC_HIGHRES,text,sizeof(text));CHECK(!strcmp(text,"Enable high-res support (Existing D3D wrapper detected. e.g dgVoodoo2, D3DIM700.DLL, etc)"));
     CHECK(!IsWindowEnabled(GetDlgItem(g_main,IDC_HIGHRES)));
     set_valid_controls(1);CHECK(!IsWindowEnabled(GetDlgItem(g_main,IDC_HIGHRES)));
     display_width=1920;refresh_display_guidance(0);CHECK(!IsWindowEnabled(GetDlgItem(g_main,IDC_HIGHRES)));
     DeleteFileA(graphics);refresh_display_guidance(0);CHECK(IsWindowEnabled(GetDlgItem(g_main,IDC_HIGHRES)));
     join_path(graphics,fixture,"ddraw.dll");CHECK(write_all(graphics,"wrapper",7));CHECK(panel_graphics_file()==2);DeleteFileA(graphics);}
    panel_monitor_info=GetMonitorInfoA;panel_display_notice=MessageBoxA;
    CHECK(!strcmp(panel_selected_monitor(),""));
    strcpy(s.monitor,"\\\\.\\DISPLAY99");settings_to_ui(&s);
    CHECK(!strcmp(panel_selected_monitor(),s.monitor));
    CHECK(nemt_selected_monitor(s.monitor)==nemt_selected_monitor(""));
    SendMessageA(g_main,WM_DISPLAYCHANGE,0,0);CHECK(!strcmp(panel_selected_monitor(),s.monitor));
    SendDlgItemMessageA(g_main,IDC_WINDOW,BM_CLICK,0,0);CHECK(!IsWindowEnabled(GetDlgItem(g_main,IDC_MONITOR)));
    SendDlgItemMessageA(g_main,IDC_WINDOW,BM_CLICK,0,0);CHECK(IsWindowEnabled(GetDlgItem(g_main,IDC_MONITOR)));
    ui_to_settings(&loaded);CHECK(!strcmp(loaded.monitor,s.monitor));
    GetWindowRect(GetDlgItem(g_main,IDC_WINDOW),&a);GetWindowRect(GetDlgItem(g_main,IDC_MONITOR),&b);CHECK(a.right<=b.left);
    CHECK(GetWindowLongA(GetDlgItem(g_main,IDC_BROWSE),GWL_STYLE)&WS_TABSTOP);
    CHECK(LOWORD(SendMessageA(g_main,DM_GETDEFID,0,0))==IDC_APPLY);
    GetWindowRect(GetDlgItem(g_main,IDC_UNLOCKFPS),&a);GetWindowRect(GetDlgItem(g_main,IDC_VSYNC),&b);CHECK(a.right<=b.left);
    SendDlgItemMessageA(g_main,IDC_RECOMMENDED,BM_CLICK,0,0);
    CHECK(check_get(IDC_VERBOSE) && check_get(IDC_VSYNC) && check_get(IDC_COUNTERTILT) && !check_get(IDC_LOGGING));
    CHECK(check_get(IDC_CRAWL) && check_get(IDC_TIMEOUT));
    SendDlgItemMessageA(g_main,IDC_UNLOCKFPS,BM_CLICK,0,0);CHECK(!IsWindowEnabled(GetDlgItem(g_main,IDC_VSYNC)) && check_get(IDC_VSYNC));
    SendDlgItemMessageA(g_main,IDC_UNLOCKFPS,BM_CLICK,0,0);CHECK(IsWindowEnabled(GetDlgItem(g_main,IDC_VSYNC)) && check_get(IDC_VSYNC));
    SendDlgItemMessageA(g_main,IDC_CRAWL,BM_CLICK,0,0);CHECK(!IsWindowEnabled(GetDlgItem(g_main,IDC_COUNTERTILT)) && check_get(IDC_COUNTERTILT));
    ui_to_settings(&loaded);CHECK(loaded.prefer_pcores && loaded.counter_tilt && !loaded.crawl);
    CHECK(!strcmp(loaded.derail_key,"F8") && !strcmp(loaded.key_forward,"i"));
    SendDlgItemMessageA(g_main,IDC_CRAWL,BM_CLICK,0,0);CHECK(check_get(IDC_TIMEOUT));
    SendDlgItemMessageA(g_main,IDC_TIMEOUT,BM_CLICK,0,0);CHECK(!check_get(IDC_CRAWL));
    SendMessageA(g_strength,TBM_SETPOS,TRUE,0);SendMessageA(g_main,WM_HSCROLL,0,(LPARAM)g_strength);
    get_text(IDC_STRENGTHVALUE,text,sizeof(text));CHECK(!strcmp(text,"Disabled"));
    CHECK(SendMessageA(g_strength,TBM_GETRANGEMAX,0,0)==100);
    CHECK(SendDlgItemMessageA(g_main,IDC_HUDLEFT,CB_GETCOUNT,0,0)==2);
    scroll_to(0,0);SendMessageA(g_main,WM_MOUSEWHEEL,MAKEWPARAM(0,(WORD)-WHEEL_DELTA),0);CHECK(g_scroll_y>0);
    g_dpi=144;layout_controls();GetWindowRect(GetDlgItem(g_main,IDC_UNLOCKFPS),&a);GetWindowRect(GetDlgItem(g_main,IDC_VSYNC),&b);CHECK(a.right<=b.left);g_dpi=96;
    /* The alias regression: clearing g_info must not erase the input path. */
    strcpy(g_info.path,"C:\\NEMT-does-not-exist\\missing.exe");load_selection(g_info.path);
    get_text(IDC_MESSAGE,text,sizeof(text));CHECK(strstr(text,"Choose a train.exe file first")==NULL);
    CHECK(!g_info.valid && !IsWindowEnabled(GetDlgItem(g_main,IDC_COUNTERTILT)));
    get_text(IDC_PATH,text,sizeof(text));CHECK(!strcmp(text,"C:\\NEMT-does-not-exist\\missing.exe"));
    /* Disabled manifest: preserve strength/anchor, not stale checked features. */
    CHECK(install_settings(&info,&s,1,err,sizeof(err)));
    CHECK(!exists_file(proxy) && !exists_file(ini) && exists_file(status));
    CHECK(load_selection_settings(&info,&loaded,err,sizeof(err)));CHECK(!loaded.window_features && !loaded.crawl && loaded.strength==77 && !loaded.hud_left);
    CHECK(read_record(fixture,&record,&record_text,err,sizeof(err))==1);CHECK(!json_bool(&record,"enabled",1));free(record_text);record_text=NULL;
    /* Never delete an unowned config on Uninstall. */
    DeleteFileA(manifest);CHECK(write_all(ini,"unrelated config",(DWORD)strlen("unrelated config")));CHECK(install_settings(&info,&s,1,err,sizeof(err)));CHECK(exists_file(ini));
    /* Reject changed executable and spoofed/wrong-schema ownership. */
    CHECK(write_all(info.path,"changed",(DWORD)strlen("changed")));CHECK(!install_settings(&info,&s,0,err,sizeof(err)));
    CHECK(write_all(manifest,"{\"product\":\"OTHER\",\"schema\":1,\"enabled\":true,\"note\":\"NEMT\"}",(DWORD)strlen("{\"product\":\"OTHER\",\"schema\":1,\"enabled\":true,\"note\":\"NEMT\"}")));
    CHECK(read_record(fixture,&record,&record_text,err,sizeof(err))==-1);
    DestroyWindow(g_main);while(PeekMessageA(&msg,NULL,0,0,PM_REMOVE)) {}
    if(g_font)DeleteObject(g_font);if(g_bold)DeleteObject(g_bold);if(g_title_font)DeleteObject(g_title_font);if(g_link_font)DeleteObject(g_link_font);
    remove_fixture(fixture);
    printf("native GUI/installer: %d checks, %d failures\n",checks,failures);return failures?1:0;
}
