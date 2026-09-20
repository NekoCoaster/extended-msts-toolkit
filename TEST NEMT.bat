@echo off
setlocal
cd /d "%~dp0"
set "TCC=tools\tcc\tcc.exe"
if not exist "%TCC%" if exist "C:\Tools\tcc\tcc.exe" set "TCC=C:\Tools\tcc\tcc.exe"
if not exist "%TCC%" goto no_compiler
if not exist build mkdir build
if not exist build goto failed
"%TCC%" -o build\frontend-model-test.exe tests\frontend-model.c
if errorlevel 1 goto failed
build\frontend-model-test.exe
if errorlevel 1 goto failed
"%TCC%" -o build\viewport-model-test.exe tests\viewport-model.c
if errorlevel 1 goto failed
build\viewport-model-test.exe
if errorlevel 1 goto failed
"%TCC%" -DWINVER=0x0501 -D_WIN32_WINNT=0x0501 -o build\native-gui-test.exe tests\native-gui.c -luser32 -lgdi32 -lcomdlg32 -lcomctl32 -lshell32 -ladvapi32
if errorlevel 1 goto failed
copy /y src\NEMT.exe.manifest build\native-gui-test.exe.manifest >nul
if errorlevel 1 goto failed
build\native-gui-test.exe
if errorlevel 1 goto failed
"%TCC%" -DWINVER=0x0501 -D_WIN32_WINNT=0x0501 -o build\high-resolution-test.exe tests\high-resolution.c -ladvapi32 -luser32
if errorlevel 1 goto failed
build\high-resolution-test.exe
if errorlevel 1 goto failed
echo All native regression tests passed.
if /i not "%~1"=="--ci" pause
exit /b 0
:no_compiler
echo The bundled TinyCC compiler was not found. Restore tools\tcc from the source archive.
:failed
echo A native regression test or build failed. Capture this output for review.
if /i not "%~1"=="--ci" pause
exit /b 1
