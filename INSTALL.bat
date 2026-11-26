@echo off
setlocal
cd /d "%~dp0"
title HOSE Global LSTM V3 - Installer
echo ==========================================
echo HOSE GLOBAL LSTM V3 - INSTALLATION
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
 echo Python Launcher not found. Install Python 3.12 64-bit.
 pause
 exit /b 1
)
py -3.12 --version
if errorlevel 1 (
 echo Python 3.12 is required.
 pause
 exit /b 1
)
if not exist ".venv\Scripts\python.exe" py -3.12 -m venv .venv
if errorlevel 1 goto :error
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 goto :error
pip install -r requirements.txt
if errorlevel 1 goto :error
if exist "scripts\generate_hose_simulation.py" (
 python "scripts\generate_hose_simulation.py"
 if errorlevel 1 goto :error
) else (
 echo Dataset generator is not delivered yet. Do not run the app until all files arrive.
)
echo Installation step completed.
pause
exit /b 0
:error
echo Installation failed. Please send a screenshot of this window.
pause
exit /b 1
