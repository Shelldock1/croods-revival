#!/bin/bash
# Wipes the game's data on the emulator (= new game), starts it and prints Lua errors.
A=~/Android/Sdk/platform-tools/adb
$A shell pm clear com.rovio.croods >/dev/null
$A logcat -c
$A shell monkey -p com.rovio.croods -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
echo "Game started. Lua errors (Ctrl+C to stop):"
$A logcat -v raw | grep --line-buffered -a 'LUAERR'
