@echo off
REM YOLOv8 Live Streaming Camera - Runner
cd /d %~dp0

echo ========================================
echo YOLOv8 Live Streaming Camera
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import ultralytics" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting YOLOv8 Live Stream...
echo.
python main.py
pause
