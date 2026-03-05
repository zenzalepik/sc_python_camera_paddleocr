@echo off
REM PaddleOCR - Quick Test dengan Sample Image
cd /d %~dp0

echo ========================================
echo PaddleOCR - Sample Image Test
echo ========================================
echo.

REM Create sample image with Python
python -c "import cv2; import numpy as np; img = np.ones((300, 500, 3), dtype=np.uint8) * 255; cv2.putText(img, 'HELLO WORLD', (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3); cv2.imwrite('sample_image.jpg', img); print('Sample image created: sample_image.jpg')"

echo.
echo Running OCR on sample image...
echo.

python main.py sample_image.jpg

echo.
echo ========================================
echo Test completed!
echo ========================================
pause
