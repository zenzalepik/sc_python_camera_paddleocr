"""
Test script untuk demonstrate GROUP_BY_LINE feature
"""
import os
import cv2
import numpy as np

# Set environment variable
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR

print("="*60)
print("GROUP_BY_LINE Feature Test")
print("="*60)

# Initialize PaddleOCR
print("\nInitializing PaddleOCR...")
ocr = PaddleOCR(
    lang='en',
    text_detection_model_name='PP-OCRv5_mobile_det',
    text_recognition_model_name='PP-OCRv5_mobile_rec',
)
print("[OK] PaddleOCR initialized")

# Create test image with multiple lines
print("\nCreating test image with multiple lines:")
print("  Line 1: HELLO WORLD")
print("  Line 2: ABC 123 XYZ")
print("  Line 3: TEST TEXT")

img = np.ones((400, 600, 3), dtype=np.uint8) * 255

# Line 1
cv2.putText(img, "HELLO", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "WORLD", (180, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

# Line 2
cv2.putText(img, "ABC", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "123", (130, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "XYZ", (210, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

# Line 3
cv2.putText(img, "TEST", (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
cv2.putText(img, "TEXT", (150, 280), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)

cv2.imwrite("test_lines.jpg", img)
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
        print("WITHOUT GROUPING (GROUP_BY_LINE=False):")
        print(f"{'='*60}")
        for i, (text, score) in enumerate(zip(rec_texts, rec_scores), 1):
            print(f"  [{i}] '{text}' (conf: {score:.2f})")
        
        # Simulate grouping
        print(f"\n{'='*60}")
        print("WITH GROUPING (GROUP_BY_LINE=True):")
        print(f"{'='*60}")
        
        # Group by y-coordinate
        texts_with_y = []
        for i, (text, score, poly) in enumerate(zip(rec_texts, rec_scores, rec_polys)):
            bbox = poly.tolist() if hasattr(poly, 'tolist') else poly
            avg_y = sum([pt[1] for pt in bbox]) / 4 if len(bbox) == 4 else 0
            x_min = min([pt[0] for pt in bbox]) if len(bbox) == 4 else 0
            texts_with_y.append({
                'text': text,
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
                lines.append(merged)
                current_line = [current]
        
        # Last line
        current_line.sort(key=lambda x: x['x_min'])
        merged = ' '.join([t['text'] for t in current_line])
        lines.append(merged)
        
        # Display grouped lines
        for i, line in enumerate(lines, 1):
            print(f"  [Line {i}] '{line}'")

print(f"\n{'='*60}")
print("Test completed!")
print(f"{'='*60}")
print("\nTo use GROUP_BY_LINE feature:")
print("1. Edit .env file")
print("2. Set GROUP_BY_LINE=True")
print("3. Adjust LINE_TOLERANCE if needed (default: 10)")
print("4. Run: python main.py")
