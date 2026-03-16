@echo off
REM PaddleOCR Mobile - Desktop App Runner
cd /d %~dp0

echo ========================================
echo PaddleOCR Mobile - Text Detection
echo ========================================
echo.
echo Starting GUI Application...
echo.
echo Instructions:
echo   1. Click "Open Image" to select image
echo   2. Click "Detect Text" to detect text
echo   3. Copy or Save results
echo.
echo Keyboard Shortcuts:
echo   Ctrl+O - Open Image
echo   Ctrl+D - Detect Text
echo   Ctrl+C - Copy Results
echo   Ctrl+S - Save Results
echo   Delete - Clear All
echo.

python main.py
pause
