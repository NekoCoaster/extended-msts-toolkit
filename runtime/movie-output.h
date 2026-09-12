/* MIT. Bind the decoder display explicitly after the movie window is final.
   Uses the existing system WinMM module; no driver registration or extra DLL. */
typedef DWORD (WINAPI *MovieCommandFn)(UINT,UINT,DWORD_PTR,DWORD_PTR);
typedef struct {DWORD_PTR callback,result;DWORD item,track;char *drive;DWORD reference;} MovieStatus;
typedef struct {DWORD_PTR callback;HWND window;UINT show;const char *text;} MovieTarget;
static MovieCommandFn movie_command;
static void movie_bind_output(HWND window){
 UINT device;DWORD error;MovieStatus status;MovieTarget target;
 if(!bind_movie_output)return;
 if(!movie_command)movie_command=(MovieCommandFn)GetProcAddress(GetModuleHandleW(L"winmm.dll"),"mciSendCommandA");
 if(!movie_command){movie_log("OUTPUT WinMM command unavailable",GetLastError());return;}
 device=(UINT)movie_send(window,0x464,0,0); /* MCIWNDM_GETDEVICEID */
 movie_log("OUTPUT device",device);if(!device)return;
 memset(&status,0,sizeof(status));status.item=0x4001; /* MCI_DGV_STATUS_HWND */
 error=movie_command(device,0x814,0x100,(DWORD_PTR)&status); /* MCI_STATUS, MCI_STATUS_ITEM */
 movie_log("OUTPUT target query error",error);if(!error)movie_log("OUTPUT target before",(U)status.result);
 memset(&target,0,sizeof(target));target.window=window;
 error=movie_command(device,0x841,0x10000,(DWORD_PTR)&target); /* MCI_WINDOW, MCI_DGV_WINDOW_HWND */
 movie_log("OUTPUT assignment error (0 means success)",error);movie_log("OUTPUT requested window",(U)window);
 if(error)return; /* Keep normal playback available if a driver rejects this command. */
 status.result=0;error=movie_command(device,0x814,0x100,(DWORD_PTR)&status);
 movie_log("OUTPUT verification error",error);if(!error)movie_log("OUTPUT target after",(U)status.result);
}
