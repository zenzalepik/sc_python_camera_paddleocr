"""
Test script untuk demonstrate DELETE_SPACE feature
"""
import os
import cv2
import numpy as np

# Set environment variable
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR

print("="*60)
print("DELETE_SPACE Feature Test")
print("="*60)

# Initialize PaddleOCR
print("\nInitializing PaddleOCR...")
ocr = PaddleOCR(
    lang='en',
    text_detection_model_name='PP-OCRv5_mobile_det',
    text_recognition_model_name='PP-OCRv5_mobile_rec',
)
print("[OK] PaddleOCR initialized")

# Create test image with spaced text
print("\nCreating test image with text: 'ABC 123 XYZ'")
img = np.ones((200, 500, 3), dtype=np.uint8) * 255
cv2.putText(img, "ABC 123 XYZ", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
cv2.imwrite("test_space.jpg", img)
print("[OK] Test image saved")

# Run OCR
print("\nRunning OCR...")
result = ocr.predict(img)

if result and len(result) > 0:
    first_result = result[0]
    if isinstance(first_result, dict):
        rec_texts = first_result.get('rec_texts', [])
        rec_scores = first_result.get('rec_scores', [])
        
        print(f"\nDetected {len(rec_texts)} text(s):")
        print("\nWITH SPACE (DELETE_SPACE=False):")
        for text, score in zip(rec_texts, rec_scores):
            print(f"   - '{text}' (confidence: {score:.2f})")
        
        print("\nWITHOUT SPACE (DELETE_SPACE=True):")
        for text, score in zip(rec_texts, rec_scores):
            processed = text.replace(' ', '')
            print(f"   - '{processed}' (confidence: {score:.2f})")

print("\n" + "="*60)
print("Test completed!")
print("="*60)
print("\nTo use DELETE_SPACE feature:")
print("1. Edit .env file")
print("2. Set DELETE_SPACE=True")
print("3. Run: python main.py")
