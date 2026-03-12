@echo off
REM Object Distance Detection - Real-time Runner
cd /d %~dp0

echo ========================================
echo Object Distance Detection with YOLO
echo ========================================
echo.
echo Starting real-time detection...
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

python main.py

pause
