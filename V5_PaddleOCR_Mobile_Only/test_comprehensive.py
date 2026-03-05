"""
Comprehensive test untuk DELETE_SPACE (grouping & non-grouping)
"""
import os
import cv2
import numpy as np

os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR

print("="*60)
print("DELETE_SPACE Comprehensive Test")
print("="*60)

ocr = PaddleOCR(
    lang='en',
    text_detection_model_name='PP-OCRv5_mobile_det',
    text_recognition_model_name='PP-OCRv5_mobile_rec',
)
print("\n[OK] PaddleOCR initialized")

# Create test image
print("\nCreating test image:")
print("  Line 1: HELLO WORLD")
print("  Line 2: ABC 123")
print("  Line 3: TEST")

img = np.ones((300, 500, 3), dtype=np.uint8) * 255
cv2.putText(img, "HELLO", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "WORLD", (180, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "ABC", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "123", (130, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "TEST", (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.imwrite("test_comprehensive.jpg", img)
print("[OK] Test image saved")

result = ocr.predict(img)

if result and len(result) > 0:
    first_result = result[0]
    if isinstance(first_result, dict):
        rec_texts = first_result.get('rec_texts', [])
        rec_scores = first_result.get('rec_scores', [])
        
        print(f"\n{'='*60}")
        print("CASE 1: DELETE_SPACE=True (NO GROUPING)")
        print(f"{'='*60}")
        for i, (text, score) in enumerate(zip(rec_texts, rec_scores), 1):
            processed = text.strip().replace(' ', '')
            print(f"  [{i}] '{text}' -> '{processed}'")
        
        print(f"\n{'='*60}")
        print("CASE 2: DELETE_SPACE=True + GROUP_BY_LINE=True")
        print(f"{'='*60}")
        
        # Simulate grouping
        rec_polys = first_result.get('rec_polys', [])
        texts_with_y = []
        for i, (text, score, poly) in enumerate(zip(rec_texts, rec_scores, rec_polys)):
            bbox = poly.tolist() if hasattr(poly, 'tolist') else poly
            avg_y = sum([pt[1] for pt in bbox]) / 4 if len(bbox) == 4 else 0
            x_min = min([pt[0] for pt in bbox]) if len(bbox) == 4 else 0
            texts_with_y.append({
                'text': text.strip().replace(' ', ''),  # Apply DELETE_SPACE
                'score': score,
                'avg_y': avg_y,
                'x_min': x_min
            })
        
        texts_sorted = sorted(texts_with_y, key=lambda x: x['avg_y'])
        lines = []
        current_line = [texts_sorted[0]]
        
        for i in range(1, len(texts_sorted)):
            current = texts_sorted[i]
            if abs(current['avg_y'] - current_line[-1]['avg_y']) <= 10:
                current_line.append(current)
            else:
                current_line.sort(key=lambda x: x['x_min'])
                merged = ' '.join([t['text'] for t in current_line])
                merged_no_space = merged.replace(' ', '')  # Apply DELETE_SPACE again
                lines.append(merged_no_space)
                current_line = [current]
        
        current_line.sort(key=lambda x: x['x_min'])
        merged = ' '.join([t['text'] for t in current_line])
        merged_no_space = merged.replace(' ', '')
        lines.append(merged_no_space)
        
        for i, line in enumerate(lines, 1):
            print(f"  [Line {i}] '{line}'")

print(f"\n{'='*60}")
print("Expected:")
print(f"{'='*60}")
print("  NO GROUPING + DELETE_SPACE:")
print("    Individual texts without spaces")
print("  GROUPING + DELETE_SPACE:")
print("    Line 1: 'HELLOWORLD'")
print("    Line 2: 'ABC123'")
print("    Line 3: 'TEST'")
print(f"\n{'='*60}")
