@echo off
rem Saves the Android emulator log to logcat.txt next to this file (for debugging The Croods).
set "ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
set "OUT=%~dp0logcat.txt"
echo ==== packages > "%OUT%"
"%ADB%" shell pm list packages -f com.rovio >> "%OUT%" 2>&1
"%ADB%" shell dumpsys package com.rovio.croods | findstr /i "versionName lastUpdateTime firstInstallTime" >> "%OUT%" 2>&1
echo ==== logcat >> "%OUT%"
"%ADB%" logcat -d -v time >> "%OUT%" 2>&1
