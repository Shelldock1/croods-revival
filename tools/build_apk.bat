@echo off
rem Rebuild and sign croods_offline.apk from the original APK (Windows, Android Studio installed).
setlocal
set "D=%~dp0.."
set "BT=%LOCALAPPDATA%\Android\Sdk\build-tools\36.0.0"
if not exist "%BT%\zipalign.exe" for /d %%b in ("%LOCALAPPDATA%\Android\Sdk\build-tools\*") do set "BT=%%~b"
set "JAVA_HOME=%ProgramFiles%\Android\Android Studio\jbr"
set "PATH=%JAVA_HOME%\bin;%PATH%"
set "PYEXE="
for /d %%d in ("%LOCALAPPDATA%\Python\pythoncore-3*" "%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%~d\python.exe" set "PYEXE=%%~d\python.exe"
)
if not defined PYEXE set "PYEXE=python"
if not exist "%D%\original\the_croods_1.3.1.apk" (
    echo Put your own The Croods 1.3.1 APK into original\the_croods_1.3.1.apk first.
    goto :fail
)
set "TMPD=%TEMP%\croods_build"
if exist "%TMPD%" rmdir /s /q "%TMPD%"
mkdir "%TMPD%"
"%PYEXE%" -I "%D%\tools\patch_apk.py" "%D%\original\the_croods_1.3.1.apk" "%TMPD%\unsigned.apk" || goto :fail
"%BT%\zipalign.exe" -f -p 4 "%TMPD%\unsigned.apk" "%TMPD%\aligned.apk" || goto :fail
call "%BT%\apksigner.bat" sign --ks "%D%\debug.keystore" --ks-pass pass:android --out "%D%\croods_offline.apk" "%TMPD%\aligned.apk" || goto :fail
rmdir /s /q "%TMPD%"
echo built %D%\croods_offline.apk
exit /b 0
:fail
echo BUILD FAILED
exit /b 1
