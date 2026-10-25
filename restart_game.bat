@echo off
rem Wipes The Croods data on the emulator (= new game), starts it and saves the log to logcat.txt after 40 s.
set "ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
set "OUT=%~dp0logcat.txt"
"%ADB%" shell pm clear com.rovio.croods
"%ADB%" logcat -c
"%ADB%" shell monkey -p com.rovio.croods -c android.intent.category.LAUNCHER 1 >nul 2>&1
echo Game started, waiting 40 seconds...
timeout /t 40 /nobreak >nul
"%ADB%" logcat -d -v time > "%OUT%" 2>&1
echo Log saved to %OUT%
timeout /t 3 >nul
