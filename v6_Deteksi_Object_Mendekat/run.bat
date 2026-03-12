@echo off
REM Object Distance Detection - Real-time Runner
cd /d %~dp0

echo ========================================
echo Object Distance Detection with YOLO
echo ========================================
echo.
echo Configuration: variables.py
echo.
echo Edit variables.py to change settings:
echo   - CLEAN_UI
echo   - CAMERA_WIDTH/HEIGHT
echo   - YOLO_SKIP_FRAMES
echo   - And more...
echo.
echo Controls:
echo   Q - Quit
echo   Y - Toggle YOLO (ON/OFF)
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
