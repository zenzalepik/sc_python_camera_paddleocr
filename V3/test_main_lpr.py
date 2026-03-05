"""
Quick test untuk mengecek apakah LPR detection berjalan
"""
import cv2
import numpy as np
import os
import sys

# Set environment variables
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
os.environ['SUPPRESS_DEPRECATION_WARNINGS'] = '1'

from dotenv import load_dotenv
load_dotenv()

print("="*60)
print("Quick LPR Test - Main Module")
print("="*60)

# Import main module
from main import LPREngine

# Create LPR engine
print("\nInitializing LPR engine...")
lpr = LPREngine(engine=os.getenv('LPR_ENGINE', 'paddleocr'), country='id')

if lpr.initialize():
    print("[OK] LPR engine initialized")
else:
    print("[ERROR] LPR engine failed to initialize")
    sys.exit(1)

# Create test image (white board with text)
print("\nCreating test image...")
test_img = np.ones((200, 400, 3), dtype=np.uint8) * 255
cv2.putText(test_img, "B 1234 XYZ", (50, 120), 
            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
cv2.rectangle(test_img, (30, 50), (370, 150), (0, 0, 255), 2)

# Save test image
cv2.imwrite("test_ocr.jpg", test_img)
print("[OK] Test image saved as test_ocr.jpg")

# Test recognition
print("\nRunning OCR on test image...")
result = lpr.recognize(test_img)

if result[0]:
    print(f"[OK] Text detected: {result[0]}")
    print(f"     Confidence: {result[1]:.2f}")
else:
    print("[WARN] No text detected")

print("\n" + "="*60)
print("Test completed!")
print("="*60)
