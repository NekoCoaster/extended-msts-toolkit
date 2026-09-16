@echo off
setlocal
cd /d "%~dp0"
call build.bat
if errorlevel 1 goto failed
echo.
echo Build successful. Starting NEMT...
start "" "build\NEMT.exe" %*
exit /b 0
:failed
echo.
pause
exit /b 1
