"""Source-level parity invariants; actual Windows control tests are in native-gui.c.

These checks do NOT claim to prove GUI behavior from source text alone.
Run TEST NEMT.bat on Windows to execute the native behavioral tests.
"""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
src=(root/'src/nemt.c').read_text(encoding='utf-8')
model=(root/'src/settings_model.h').read_text(encoding='utf-8')
build=(root/'build.bat').read_text(encoding='utf-8')
checks=0

def check(value,description):
    global checks
    assert value, description
    checks+=1

check('#define _WIN32_WINNT 0x0501' in src,'XP API baseline')
check('GetProcAddress(k,"GetSystemCpuSetInformation")' in src,'dynamic topology lookup')
check(not re.search(r'\bGetSystemCpuSetInformation\s*\(',src),'no mandatory CPU-set import')
check('System.Windows.Forms' not in src,'no WinForms dependency')
check('-mwindows' in build and '-lcomctl32' in build,'native GUI and standard trackbar linkage')
check('IsDialogMessageA(g_main,&msg)' in src and 'WS_TABSTOP' in src,'dialog keyboard path')
check('case WM_VSCROLL:' in src and 'case WM_MOUSEWHEEL:' in src,'small-display scrolling path')
check('TBM_SETRANGE' in src and 'MAKELONG(0,100)' in src and '"Disabled"' in src,'crawl slider range/label')
check('CBS_DROPDOWNLIST' in src and '"Bottom right"' in src and '"Bottom left"' in src,'HUD dropdown')
load=src[src.index('static void load_selection('):src.index('static void browse_train(')]
check(load.index('lstrcpynA(selected,')<load.index('memset(&g_info'),'copy aliased path before clearing state')
save=src[src.index('static void do_save('):src.index('static void layout_controls(void) {')]
check(save.index('load_selection(selected);')<save.index('Settings saved.'),'reload before success message')
check('s->limit_vsync=1; s->verbose_loading=1; s->startup_log=0;' in model,'recommended choices match PS1')
check('s->crawl=1; s->counter_tilt=1;' in model,'recommended counter-tilt')
check('if(g_cpu_supported) s->prefer_pcores=check_get(IDC_PCORES);' in src,'preserve unsupported P-core setting')
check('s->counter_tilt=check_get(IDC_COUNTERTILT);' in src,'preserve inactive counter-tilt preference')
check('rollback_files(old,4)' in src and 'disable_record(manifest,' in src,'transaction/uninstall safeguards')
check('KEY_WOW64_32KEY,KEY_WOW64_64KEY,0' in src,'both registry views and XP fallback')
check('build\\NEMT.pending.exe' in build and 'move /y' in build,'staged build output')
check(not (root/'NEMT.vbs').exists(),'no script launcher at repository root')
check('STARTUP_EXTRA_WIDTH 24' in src and 'STARTUP_EXTRA_HEIGHT 24' in src,'larger default client area')
check('#define MAIN_WINDOW_STYLE (WS_OVERLAPPEDWINDOW|WS_CLIPCHILDREN)' in src,'do not force initial scrollbars')
check('initial_window_rect(&work,&frame)' in src,'work-area bounded startup sizing')
layout=src[src.index('static void layout_controls(void) {'):src.index('static void ensure_focus_visible(HWND hwnd) {')]
check('viewport_layout(&view' in layout and 'style&WS_VSCROLL' in layout,'solve scrollbars using area without bars')
check('BeginDeferWindowPos' in layout and 'EndDeferWindowPos' in layout,'batch control movement')
check('SWP_NOREDRAW|SWP_NOCOPYBITS' in layout,'discard stale pixels before repaint')
check('if(!moved)' in layout and 'SetWindowPos(c->hwnd' in layout,'low-memory positioning fallback')
check('RDW_INVALIDATE|RDW_ERASE|RDW_FRAME|RDW_ALLCHILDREN|RDW_UPDATENOW' in layout,'erase and repaint parent plus children')
check('MoveWindow(' not in layout and 'ScrollWindowEx(' not in layout,'no individual repaint or pixel-scrolling path')
print(f'native frontend source invariants: {checks} checks passed (not a live GUI test)')
