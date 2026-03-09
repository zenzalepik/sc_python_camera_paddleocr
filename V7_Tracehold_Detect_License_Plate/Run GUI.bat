@echo off
echo Starting ANPR Indonesian License Plate Detection GUI...
echo.
python gui.py
if errorlevel 1 (
    echo.
    echo Error: Failed to run GUI.
    echo Please ensure all dependencies are installed:
    echo   pip install -r requirements.txt
    pause
)
