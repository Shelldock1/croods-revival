@echo off
rem Starts The Croods (keeps progress) and writes the emulator log to logcat.txt while you play.
rem Lua errors appear in the log as lines with LUAERR. Close this window to stop logging.
set "ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
"%ADB%" wait-for-device
"%ADB%" logcat -c
"%ADB%" shell monkey -p com.rovio.croods -c android.intent.category.LAUNCHER 1 >nul 2>&1
echo Logging to %~dp0logcat.txt ... close this window to stop.
"%ADB%" logcat -v time > "%~dp0logcat.txt"
