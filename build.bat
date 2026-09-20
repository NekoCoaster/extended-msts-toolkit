@echo off
setlocal
cd /d "%~dp0"
title NEMT Native Builder

echo.
echo ========================================
echo  Neko's Extended MSTS Toolkit - Builder
echo ========================================
echo.
set "TCC=tools\tcc\tcc.exe"
if not exist "%TCC%" if exist "C:\Tools\tcc\tcc.exe" set "TCC=C:\Tools\tcc\tcc.exe"
if not exist "%TCC%" goto no_compiler
if not exist build mkdir build
if not exist build goto failed

echo Building NEMT.exe...
if exist build\NEMT.pending.exe del /q build\NEMT.pending.exe
"%TCC%" -DWINVER=0x0501 -D_WIN32_WINNT=0x0501 -mwindows -o build\NEMT.pending.exe src\nemt.c -luser32 -lgdi32 -lcomdlg32 -lcomctl32 -lshell32 -ladvapi32
if errorlevel 1 goto failed
copy /y "src\NEMT.exe.manifest" "build\NEMT.exe.manifest" >nul
if errorlevel 1 goto failed
move /y "build\NEMT.pending.exe" "build\NEMT.exe" >nul
if errorlevel 1 goto in_use
echo [OK] build\NEMT.exe
exit /b 0

:no_compiler
echo TinyCC 0.9.27 x86 was not found in tools\tcc.
echo Keep the bundled compiler, required WinAPI headers and libraries together.
exit /b 2

:in_use
echo Close any running NEMT window before rebuilding.
:failed
if exist build\NEMT.pending.exe del /q build\NEMT.pending.exe
echo.
echo NEMT could not be built. The existing NEMT.exe was not replaced.
echo Keep the reviewed TinyCC subset and required WinAPI headers in tools\tcc.
exit /b 1
