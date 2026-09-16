@echo off
cd /d "%~dp0"
for %%F in (NEMT.exe NEMT.pending.exe NEMT.exe.manifest frontend-model-test.exe viewport-model-test.exe native-gui-test.exe native-gui-test.exe.manifest) do if exist "build\%%F" del /q "build\%%F"
if exist build rmdir build 2>nul
echo NEMT native build output cleaned.
