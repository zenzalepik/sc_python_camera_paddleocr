"""
Quick test untuk PaddleOCR
"""
import os
import cv2
import numpy as np

# Set environment variable
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR

print("="*60)
print("PaddleOCR Quick Test")
print("="*60)

print("\nInitializing PaddleOCR...")
ocr = PaddleOCR(
    lang='en',
    text_detection_model_name='PP-OCRv5_mobile_det',
    text_recognition_model_name='PP-OCRv5_mobile_rec',
)
print("OK - PaddleOCR initialized")

print("\nCreating test image...")
img = np.ones((200, 400, 3), dtype=np.uint8) * 255
cv2.putText(img, "HELLO WORLD", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
cv2.imwrite("test_image.jpg", img)
print("OK - Test image saved")

print("\nRunning OCR...")
result = ocr.predict(img)

if result and len(result) > 0:
    first_result = result[0]
    if isinstance(first_result, dict):
        rec_texts = first_result.get('rec_texts', [])
        rec_scores = first_result.get('rec_scores', [])
        
        print(f"OK - Detected {len(rec_texts)} text(s):")
        for text, score in zip(rec_texts, rec_scores):
            print(f"   - '{text}' (confidence: {score:.2f})")

print("\n" + "="*60)
print("Test completed!")
print("="*60)
print("\nNext: Run 'python app_gui.py' for desktop app")
