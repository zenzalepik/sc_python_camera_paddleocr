"""
Test script untuk bug fix: DELETE_SPACE + GROUP_BY_LINE
"""
import os
import cv2
import numpy as np

# Set environment variable
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR

print("="*60)
print("DELETE_SPACE + GROUP_BY_LINE Bug Fix Test")
print("="*60)

# Initialize PaddleOCR
print("\nInitializing PaddleOCR...")
ocr = PaddleOCR(
    lang='en',
    text_detection_model_name='PP-OCRv5_mobile_det',
    text_recognition_model_name='PP-OCRv5_mobile_rec',
)
print("[OK] PaddleOCR initialized")

# Create test image similar to user's case
print("\nCreating test image (similar to user's case):")
print("  Line 1: ER TIGA")
print("  Line 2: B 2156 TOR")
print("  Line 3: 09.27")

img = np.ones((300, 400, 3), dtype=np.uint8) * 255

# Line 1
cv2.putText(img, "ER", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "TIGA", (120, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

# Line 2
cv2.putText(img, "B", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "2156", (100, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "TOR", (200, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

# Line 3
cv2.putText(img, "09.27", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

cv2.imwrite("test_bug_fix.jpg", img)
print("[OK] Test image saved")

# Run OCR
print("\nRunning OCR...")
result = ocr.predict(img)

if result and len(result) > 0:
    first_result = result[0]
    if isinstance(first_result, dict):
        rec_texts = first_result.get('rec_texts', [])
        rec_scores = first_result.get('rec_scores', [])
        rec_polys = first_result.get('rec_polys', [])
        
        print(f"\n{'='*60}")
        print("CASE 1: GROUP_BY_LINE=True + DELETE_SPACE=True")
        print(f"{'='*60}")
        
        # Simulate grouping + delete space
        texts_with_y = []
        for i, (text, score, poly) in enumerate(zip(rec_texts, rec_scores, rec_polys)):
            bbox = poly.tolist() if hasattr(poly, 'tolist') else poly
            avg_y = sum([pt[1] for pt in bbox]) / 4 if len(bbox) == 4 else 0
            x_min = min([pt[0] for pt in bbox]) if len(bbox) == 4 else 0
            texts_with_y.append({
                'text': text.strip(),
                'original': text.strip(),
                'score': score,
                'avg_y': avg_y,
                'x_min': x_min
            })
        
        # Sort by y
        texts_sorted = sorted(texts_with_y, key=lambda x: x['avg_y'])
        
        # Group by line (tolerance=10px)
        lines = []
        current_line = [texts_sorted[0]]
        
        for i in range(1, len(texts_sorted)):
            current = texts_sorted[i]
            prev_avg_y = current_line[-1]['avg_y']
            
            if abs(current['avg_y'] - prev_avg_y) <= 10:
                current_line.append(current)
            else:
                # Sort current line by x and merge
                current_line.sort(key=lambda x: x['x_min'])
                merged = ' '.join([t['text'] for t in current_line])
                # Apply DELETE_SPACE
                merged_no_space = merged.replace(' ', '')
                lines.append({
                    'merged': merged,
                    'no_space': merged_no_space
                })
                current_line = [current]
        
        # Last line
        current_line.sort(key=lambda x: x['x_min'])
        merged = ' '.join([t['text'] for t in current_line])
        merged_no_space = merged.replace(' ', '')
        lines.append({
            'merged': merged,
            'no_space': merged_no_space
        })
        
        # Display results
        for i, line in enumerate(lines, 1):
            print(f"  Line {i}:")
            print(f"    With spaces:    '{line['merged']}'")
            print(f"    Without spaces: '{line['no_space']}'")

print(f"\n{'='*60}")
print("Expected output with GROUP_BY_LINE=True + DELETE_SPACE=True:")
print(f"{'='*60}")
print("  Line 1: 'ERTIGA'")
print("  Line 2: 'B2156TOR'")
print("  Line 3: '09.27'")
print(f"\n{'='*60}")
print("Test completed!")
print(f"{'='*60}")
