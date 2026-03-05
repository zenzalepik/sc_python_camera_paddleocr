"""
Test script untuk mengecek LPR engine (HyperLPR / PaddleOCR)
"""

import cv2
import numpy as np
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import os
    os.system('chcp 65001 > nul')

print("="*60)
print("LPR Engine Test Script")
print("="*60)

# Test 1: Check HyperLPR
print("\n[TEST 1] Checking HyperLPR3...")
try:
    import hyperlpr3 as hpr
    print("[OK] HyperLPR3 is installed")
    
    # Try to create catcher
    catcher = hpr.LicensePlateCatcher()
    print("[OK] LicensePlateCatcher created successfully")
    
    # Test with dummy image
    dummy_img = np.zeros((100, 300, 3), dtype=np.uint8)
    cv2.putText(dummy_img, "B 1234 XYZ", (20, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    results = catcher.recognize(dummy_img)
    print(f"[INFO] Test recognition result: {results}")
    
    if results:
        for r in results:
            print(f"   - Text: {r.text}, Confidence: {r.confidence}")
    else:
        print("   [WARN] No text detected (expected for dummy image)")
        
except ImportError as e:
    print(f"[ERROR] HyperLPR3 not installed: {e}")
    print("   [INFO] Install with: pip install hyperlpr3")
except Exception as e:
    print(f"[ERROR] HyperLPR3 error: {e}")

# Test 2: Check PaddleOCR
print("\n[TEST 2] Checking PaddleOCR...")
try:
    from paddleocr import PaddleOCR
    print("[OK] PaddleOCR is installed")
    
    # Initialize OCR
    ocr = PaddleOCR(lang='en', show_log=False)
    print("[OK] PaddleOCR initialized")
    
    # Test with dummy image
    dummy_img = np.zeros((100, 300, 3), dtype=np.uint8)
    cv2.putText(dummy_img, "HELLO WORLD", (20, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    result = ocr.ocr(dummy_img)
    print(f"[INFO] Test OCR result: {result is not None}")
    
    if result and result[0]:
        for res in result[0]:
            if isinstance(res, (list, tuple)) and len(res) >= 2:
                text_elem = res[1]
                if isinstance(text_elem, (list, tuple)) and len(text_elem) >= 2:
                    text = text_elem[0]
                    score = text_elem[1]
                    print(f"   - Text: {text}, Score: {score}")
    else:
        print("   [WARN] No text detected (expected for dummy image)")
        
except ImportError as e:
    print(f"[ERROR] PaddleOCR not installed: {e}")
    print("   [INFO] Install with: pip install paddlepaddle paddleocr")
except Exception as e:
    print(f"[ERROR] PaddleOCR error: {e}")

# Test 3: Check YOLO model
print("\n[TEST 3] Checking YOLO model...")
try:
    from ultralytics import YOLO
    print("[OK] Ultralytics YOLO is installed")
    
    model = YOLO('yolov8n.pt')
    print("[OK] YOLOv8n model loaded")
    
    # Test with dummy image
    dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
    results = model(dummy_img, verbose=False)
    
    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            detections.append(len(boxes))
        else:
            detections.append(0)
    
    print(f"[INFO] Test detection result: {detections}")
    print(f"   - Objects detected: {sum(detections)}")
    
except Exception as e:
    print(f"[ERROR] YOLO error: {e}")

print("\n" + "="*60)
print("Test completed!")
print("="*60)

print("\nSummary:")
print("   - If HyperLPR3 [OK] -> Use LPR_ENGINE=hyperlpr")
print("   - If PaddleOCR [OK] -> Use LPR_ENGINE=paddleocr")
print("   - If both [ERROR] -> Install at least one OCR engine")
print("\nRecommendation: Use HyperLPR3 for license plates (faster & more accurate)")
