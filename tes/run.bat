@echo off
echo ========================================
echo  Selamat Datang - Parent Application
echo  Object Distance Detection System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak terinstall!
    echo Download dan install Python dari https://python.org
    pause
    exit /b 1
)

echo [OK] Python terdeteksi
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import ultralytics" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Gagal install dependencies!
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies terinstall
)

echo.
echo ========================================
echo  Starting Application...
echo ========================================
echo.

REM Run the application
python welcome_app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Aplikasi berhenti dengan error!
    pause
)
