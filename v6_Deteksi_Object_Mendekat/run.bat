@echo off
REM Object Distance Detection - Real-time Runner
cd /d %~dp0

REM Create .env file if it doesn't exist
if not exist .env (
    echo # CLEAN_UI Mode Configuration > .env
    echo # Set to "true" to hide all UI elements >> .env
    echo # Set to "false" to show full UI >> .env
    echo CLEAN_UI=false >> .env
    echo Created default .env file
)

REM Load environment variables from .env file if exists
if exist .env (
    for /f "delims=" %%a in ('findstr /r /c:"^CLEAN_UI=" .env') do set %%a
)

REM Default CLEAN_UI to false if not set
if "%CLEAN_UI%"=="" set CLEAN_UI=false

echo ========================================
echo Object Distance Detection with YOLO
echo ========================================
echo.
echo CLEAN_UI Mode: %CLEAN_UI%
echo.
echo To change mode, edit .env file:
echo   CLEAN_UI=true   - Hide all UI elements
echo   CLEAN_UI=false  - Show full UI
echo.
echo Controls:
echo   Q - Quit
echo   S - Save snapshot
echo   + - Increase threshold
echo   - - Decrease threshold
echo.
echo Status Colors:
echo   RED   = Object MENDEKAT
echo   GREEN = Object TETAP
echo   BLUE  = Object MENJAUH
echo.

set CLEAN_UI=%CLEAN_UI%
python main.py

pause
