@echo off
rem Fake Rovio server for The Croods. Keep this window open while playing.
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0server"

rem --- find a real Python (the "python" command may point to an empty Microsoft Store stub) ---
set "PYEXE="
for /d %%d in ("%LOCALAPPDATA%\Python\pythoncore-3*" "%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%~d\python.exe" set "PYEXE=%%~d\python.exe"
)
if not defined PYEXE (
    py -3 --version >nul 2>nul && set "PYEXE=py"
)
if not defined PYEXE set "PYEXE=python"
echo Python: %PYEXE%

rem --- install the only dependency once ---
"%PYEXE%" -c "import cryptography" >nul 2>nul
if errorlevel 1 (
    echo Installing cryptography...
    "%PYEXE%" -m pip install cryptography
)

"%PYEXE%" fake_rovio.py
pause
