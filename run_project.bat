@echo off
title YE Air - Flask project
cd /d "%~dp0"

rem ---- 1. Python environment: "venv" folder built with Python 3.10 (first run only) ----
if not exist "venv\installed.ok" (
    echo [1/3] Setting up the Python environment - first run only, this takes a few minutes...
    if not exist "venv\Scripts\python.exe" (
        if exist "C:\Program Files\Python310\python.exe" (
            "C:\Program Files\Python310\python.exe" -m venv venv
        ) else (
            py -3.10 -m venv venv
        )
    )
    if not exist "venv\Scripts\python.exe" goto :novenv
    "venv\Scripts\python.exe" -m pip install --upgrade pip
    "venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :pipfail
    echo ok> "venv\installed.ok"
)

rem ---- 2. MySQL database ----
echo [2/3] Checking the MySQL database...
"venv\Scripts\python.exe" check_setup.py
if errorlevel 1 goto :end

rem ---- 3. Start the website ----
echo [3/3] Starting the website at http://127.0.0.1:5000  - press Ctrl+C to stop
start "" /min cmd /c "timeout /t 8 /nobreak >nul & start http://127.0.0.1:5000"
"venv\Scripts\python.exe" app.py
goto :end

:novenv
echo Could not create the Python environment. Is Python 3.10 installed?
goto :end

:pipfail
echo Installing packages failed. Check your internet connection and run this file again.

:end
pause
