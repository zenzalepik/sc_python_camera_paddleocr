"""
Test script untuk mengecek LPR detection dengan gambar dummy
"""

import cv2
import numpy as np
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import os
    os.system('chcp 65001 > nul')

print("="*60)
print("LPR Detection Test")
print("="*60)

# Create a dummy license plate image
print("\nCreating dummy license plate image...")
plate_img = np.ones((100, 300, 3), dtype=np.uint8) * 200  # Light gray background

# Draw a rectangle for plate border
cv2.rectangle(plate_img, (5, 5), (295, 95), (0, 0, 0), 2)

# Add dummy plate text
cv2.putText(plate_img, "B 1234 XYZ", (30, 70), 
            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

# Save test image
cv2.imwrite("test_plate.jpg", plate_img)
print("[OK] Test image saved as test_plate.jpg")

# Test HyperLPR3
print("\n" + "-"*60)
print("Testing HyperLPR3...")
print("-"*60)
try:
    import hyperlpr3 as hpr
    print("[OK] HyperLPR3 imported")
    
    catcher = hpr.LicensePlateCatcher()
    print("[OK] LicensePlateCatcher created")
    
    # Test with dummy image
    results = catcher(plate_img)
    print(f"[INFO] Results: {results}")
    
    if results:
        print("[OK] Plates detected!")
        for i, result in enumerate(results):
            print(f"   Result {i+1}:")
            if isinstance(result, (list, tuple)) and len(result) >= 2:
                print(f"      - Text: {result[0]}")
                print(f"      - Confidence: {result[1]}")
                if len(result) > 2:
                    print(f"      - Bbox: {result[2]}")
    else:
        print("[WARN] No plates detected (may need real plate image)")
        
except ImportError as e:
    print(f"[ERROR] HyperLPR3 not installed: {e}")
except Exception as e:
    print(f"[ERROR] HyperLPR3 error: {e}")
    import traceback
    traceback.print_exc()

# Test PaddleOCR
print("\n" + "-"*60)
print("Testing PaddleOCR...")
print("-"*60)
try:
    from paddleocr import PaddleOCR
    print("[OK] PaddleOCR imported")
    
    ocr = PaddleOCR(lang='en')
    print("[OK] PaddleOCR initialized")
    
    # Test with dummy image
    result = ocr.ocr(plate_img)
    print(f"[INFO] OCR result type: {type(result)}")
    
    if result and result[0]:
        print("[OK] Text detected!")
        for res in result[0]:
            if isinstance(res, (list, tuple)) and len(res) >= 2:
                text_elem = res[1]
                if isinstance(text_elem, (list, tuple)) and len(text_elem) >= 2:
                    text = text_elem[0]
                    score = text_elem[1]
                    print(f"   - Text: {text}, Score: {score}")
    else:
        print("[WARN] No text detected (may need clearer text)")
        
except ImportError as e:
    print(f"[ERROR] PaddleOCR not installed: {e}")
except Exception as e:
    print(f"[ERROR] PaddleOCR error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test completed!")
print("="*60)

print("\nNext steps:")
print("1. If HyperLPR3 works: Use LPR_ENGINE=hyperlpr in .env")
print("2. If PaddleOCR works: Use LPR_ENGINE=paddleocr in .env")
print("3. Run main.py to test with real camera")
print("4. Enable DEBUG_MODE=True to see detailed logs")
