/* Restart/size rotation, confined to the named startup log family. */
static void startup_log_name(WCHAR *path,int index){wcscpy(path,runtime_dir);if(index)swprintf(path+wcslen(path),L"startup.%d.log",index);else wcscat(path,L"startup.log");}
static int startup_open_log(void){WCHAR from[MAX_PATH],to[MAX_PATH];int i;DWORD error;
 if(startup_file!=INVALID_HANDLE_VALUE){CloseHandle(startup_file);startup_file=INVALID_HANDLE_VALUE;}
 /* Prune backups above the configured retention, including when retention is zero. */
 for(i=20;i>max_backup_logs;i--){startup_log_name(from,i);if(!DeleteFileW(from)){error=GetLastError();if(error!=ERROR_FILE_NOT_FOUND&&error!=ERROR_PATH_NOT_FOUND)return 0;}}
 if(max_backup_logs){
  startup_log_name(from,max_backup_logs);if(!DeleteFileW(from)){error=GetLastError();if(error!=ERROR_FILE_NOT_FOUND&&error!=ERROR_PATH_NOT_FOUND)return 0;}
  for(i=max_backup_logs-1;i>=0;i--){startup_log_name(from,i);startup_log_name(to,i+1);
   if(!MoveFileExW(from,to,MOVEFILE_REPLACE_EXISTING)){error=GetLastError();if(error!=ERROR_FILE_NOT_FOUND&&error!=ERROR_PATH_NOT_FOUND)return 0;}
  }
 }
 startup_log_name(from,0);startup_file=CreateFileW(from,GENERIC_WRITE,FILE_SHARE_READ,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);startup_bytes=0;return startup_file!=INVALID_HANDLE_VALUE;
}
