@echo off
setlocal
cd /d "%~dp0"
title HOSE Global LSTM V3

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Chua tim thay moi truong .venv.
    echo Hay chay INSTALL.bat truoc.
    echo.
    pause
    exit /b 1
)

if not exist "app.py" (
    echo [ERROR] Khong tim thay app.py trong thu muc goc.
    echo Hay dat app.py cung cap voi RUN_APP.bat.
    echo.
    pause
    exit /b 1
)

echo ================================================
echo       HOSE GLOBAL LSTM V3 - STARTING APP
echo ================================================
echo.
".venv\Scripts\python.exe" -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Ung dung dung do loi. Hay chup man hinh loi gui lai de kiem tra.
    pause
)
endlocal
