"""
PaddleOCR Widget Wrapper
Wrapper untuk menggunakan PaddleOCR sebagai widget reusable.

Semua sistem, flow, fitur, dan UI dari main.py tetap sama, hanya di-refactor jadi class.
"""

import os
import sys
import json
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import threading
import re
from dotenv import load_dotenv

# Load .env file from widget directory (SAMA PERSIS dengan main.py non_widget)
_widget_dir = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_widget_dir, '.env')
load_dotenv(_env_path)

# Debug: verify .env loaded
print(f"\n[ENV] Loading .env from: {_env_path}")
print(f"[ENV] DELETE_SPACE from .env: {os.getenv('DELETE_SPACE', 'NOT SET')}")

# Import PaddleOCR
try:
    from paddleocr import PaddleOCR
    # Disable model source check
    os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
except ImportError:
    print("PaddleOCR tidak terinstall!")
    print("Install dengan: pip install paddlepaddle paddleocr")
    sys.exit(1)


class PaddleOCRWidget:
    """
    PaddleOCR Widget - Reusable component untuk OCR Text Detection.
    
    Fitur (SAMA PERSIS dengan main.py):
    - OCR dengan PaddleOCR v5 Mobile
    - Support multi-language
    - Bounding box detection
    - Confidence score
    - Group by line
    - Delete space option
    - Export ke TXT/JSON
    - Copy to clipboard
    
    Usage:
        widget = PaddleOCRWidget(lang='id', conf_threshold=0.5)
        result = widget.process_image('path/to/image.jpg')
        texts = widget.get_result()
        widget.export_to_txt('output.txt')
    """

    def __init__(self, config=None):
        """
        Initialize PaddleOCR Widget.

        Args:
            config: Configuration dict (optional)
        """
        self.config = config or {}

        # Load config from .env (SAMA PERSIS dengan main.py non_widget)
        # Config dict overrides .env if provided
        
        # OCR Settings
        self.lang = self.config.get('OCR_LANG', os.getenv('OCR_LANG', 'id'))
        self.conf_threshold = float(self.config.get('CONF_THRESHOLD', os.getenv('CONF_THRESHOLD', '0.5')))
        
        # Text Processing Settings - load from .env
        self.delete_space = self.config.get('DELETE_SPACE', os.getenv('DELETE_SPACE', 'True')) == 'True'
        self.group_by_line = self.config.get('GROUP_BY_LINE', os.getenv('GROUP_BY_LINE', 'True')) == 'True'
        self.line_tolerance = int(self.config.get('LINE_TOLERANCE', os.getenv('LINE_TOLERANCE', '10')))
        
        # License Plate Detection
        self.detect_license_plate = self.config.get('DETECT_LICENSE_PLATE', os.getenv('DETECT_LICENSE_PLATE', 'True')) == 'True'
        
        # Debug: print settings
        print(f"\n[CONFIG] DELETE_SPACE: {self.delete_space} (from .env: {os.getenv('DELETE_SPACE')})")
        print(f"[CONFIG] GROUP_BY_LINE: {self.group_by_line}")
        print(f"[CONFIG] LINE_TOLERANCE: {self.line_tolerance}")
        print(f"[CONFIG] DETECT_LICENSE_PLATE: {self.detect_license_plate}\n")
        
        # Error Handling
        self.hide_popup_unknown_exception = self.config.get(
            'HIDE_POPUP_UNKNOWN_EXCEPTION',
            os.getenv('HIDE_POPUP_UNKNOWN_EXCEPTION', 'False')
        ) == 'True'
        
        # Output Settings
        self.output_dir = self.config.get('OUTPUT_DIR', os.getenv('OUTPUT_DIR', 'output'))

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # State variables
        self.current_image = None
        self.current_image_path = None
        self.current_result = None
        self.detected_plate = None  # Store detected license plate
        
        # Initialize PaddleOCR
        self.ocr = None
        self.init_ocr()

    def init_ocr(self):
        """Initialize PaddleOCR engine."""
        print("Initializing PaddleOCR v5 Mobile...")
        try:
            # PaddleOCR v5 new API - use mobile models
            self.ocr = PaddleOCR(
                lang=self.lang,
                text_detection_model_name='PP-OCRv5_mobile_det',
                text_recognition_model_name='PP-OCRv5_mobile_rec',
            )
            print("[OK] PaddleOCR v5 Mobile initialized!")
            print(f"    - Language: {self.lang.upper()}")
            print(f"    - Delete Space: {'ON' if self.delete_space else 'OFF'}")
            print(f"    - Group by Line: {'ON' if self.group_by_line else 'OFF'}")
            if self.group_by_line:
                print(f"    - Line Tolerance: {self.line_tolerance}px")
        except Exception as e:
            print(f"[ERROR] Error initializing PaddleOCR: {e}")
            raise

    def process_image(self, image_path):
        """
        Process image dengan OCR.
        
        Args:
            image_path: Path to image file atau numpy array
            
        Returns:
            dict: OCR result
        """
        try:
            # Load image jika path
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
                if image is None:
                    raise ValueError(f"Cannot read image: {image_path}")
                self.current_image = image
                self.current_image_path = image_path
            else:
                # Assume numpy array
                self.current_image = image_path
                self.current_image_path = None
            
            start_time = datetime.now()
            print(f"[{start_time.strftime('%H:%M:%S')}] [OCR] Running PaddleOCR prediction...")
            
            # Run PaddleOCR
            result = self.ocr.predict(self.current_image)
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [OCR] Completed in {elapsed:.2f}s")
            
            # RE-CREATE model setelah predict (biar state fresh untuk predict berikutnya)
            # Ini penting karena PaddleOCR model tidak thread-safe
            print("[INFO] Re-creating PaddleOCR model for fresh state...")
            self.ocr = PaddleOCR(
                lang=self.lang,
                text_detection_model_name='PP-OCRv5_mobile_det',
                text_recognition_model_name='PP-OCRv5_mobile_rec',
            )
            print("[OK] PaddleOCR model re-created")
            
            # Parse result
            texts = []
            if result and len(result) > 0:
                first_result = result[0]
                if isinstance(first_result, dict):
                    rec_texts = first_result.get('rec_texts', [])
                    rec_scores = first_result.get('rec_scores', [])
                    rec_polys = first_result.get('rec_polys', [])
                    
                    for i, (text, score, poly) in enumerate(zip(rec_texts, rec_scores, rec_polys)):
                        if score >= self.conf_threshold:
                            processed_text = text.strip()
                            
                            # Debug: check delete_space
                            print(f"  [DEBUG] Original text: '{text}'")
                            print(f"  [DEBUG] delete_space={self.delete_space}")
                            
                            if self.delete_space:
                                processed_text = processed_text.replace(' ', '')
                                print(f"  [DEBUG] After delete_space: '{processed_text}'")

                            bbox = poly.tolist() if hasattr(poly, 'tolist') else poly
                            avg_y = sum([pt[1] for pt in bbox]) / 4 if len(bbox) == 4 else 0
                            x_min = min([pt[0] for pt in bbox]) if len(bbox) == 4 else 0

                            texts.append({
                                'text': processed_text,
                                'confidence': float(score),
                                'bbox': bbox,
                                'original_text': text.strip(),
                                'avg_y': avg_y,
                                'x_min': x_min
                            })
                    
                    if self.group_by_line:
                        texts = self.group_texts_by_line(texts)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.current_result = {
                'texts': texts,
                'total_texts': len(texts),
                'total_lines': len([t for t in texts if t.get('is_grouped', False)]) if self.group_by_line else 0,
                'processing_time': processing_time,
                'image_path': self.current_image_path,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Found {len(texts)} text(s)")
            if texts:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [SUCCESS] Detection successful!")
                for i, item in enumerate(texts, 1):
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [RESULT]   [{i}] '{item['text']}' (conf: {item['confidence']:.2f})")
            
            return self.current_result
            
        except Exception as e:
            print(f"[ERROR] OCR failed: {e}")
            raise

    def process_frame(self, frame):
        """
        Process frame (numpy array) dengan OCR.

        Args:
            frame: OpenCV frame (numpy array)

        Returns:
            tuple: (frame_with_boxes, result_dict)
        """
        result = self.process_image(frame)
        frame_with_boxes = self.draw_result(frame)
        
        # Detect license plate if enabled
        if self.detect_license_plate:
            self.detected_plate = self.detect_license_plate_from_result()
        
        return frame_with_boxes, result

    def detect_license_plate_from_result(self):
        """
        Detect license plate from OCR result.
        
        Logic:
        - Cari teks yang mengandung 3 atau 4 angka berturut-turut
        - Tidak boleh ada huruf di antara angka
        - Boleh ada huruf sebelum dan setelah rangkaian angka
        - Return SELURUH teks plat nomor (bukan cuma angka)
        
        Returns:
            str or None: Full license plate text if found, None otherwise
        """
        if self.current_result is None:
            return None
        
        texts = self.current_result.get('texts', [])
        
        print(f"\n[PLATE DETECTION] Checking {len(texts)} text(s)...")
        
        for item in texts:
            text = item.get('text', '')
            
            print(f"  Checking: '{text}'")
            
            # Skip if text too short
            if len(text) < 3:
                print(f"    → Skip (too short)")
                continue
            
            # Remove spasi untuk checking pattern
            text_no_space = text.replace(' ', '')
            
            # Regex pattern: optional letters, then 3-4 digits, then optional letters
            # No letters allowed BETWEEN the digits
            import re
            
            # Pattern: [A-Z]*[0-9]{3,4}[A-Z]*
            pattern = r'[A-Z]*[0-9]{3,4}[A-Z]*'
            
            # Convert to uppercase for matching
            text_upper = text_no_space.upper()
            
            # Find all matches
            matches = re.findall(pattern, text_upper)
            
            print(f"    Text (no space): '{text_no_space}' → '{text_upper}'")
            print(f"    Pattern: '{pattern}'")
            print(f"    Matches: {matches}")
            
            for match in matches:
                # Verify the match has 3-4 consecutive digits
                digits = re.search(r'[0-9]{3,4}', match)
                if digits:
                    # FOUND! Return the ORIGINAL text (with spaces)
                    print(f"    → FOUND PLATE: '{text}' (matched: '{match}')")
                    return text  # Return original text, not just the match
                else:
                    print(f"    → No 3-4 digits in '{match}'")
        
        print(f"  No plate found\n")
        return None

    def get_result(self):
        """
        Get OCR result.
        
        Returns:
            dict: OCR result dengan keys:
                - texts: list of detected texts
                - total_texts: jumlah teks terdeteksi
                - total_lines: jumlah lines (jika group_by_line)
                - processing_time: waktu proses
                - image_path: path gambar
                - timestamp: timestamp
        """
        return self.current_result

    def get_texts(self):
        """
        Get list of detected texts.
        
        Returns:
            list: List of text strings
        """
        if self.current_result is None:
            return []
        return [t['text'] for t in self.current_result.get('texts', [])]

    def get_detected_plate(self):
        """
        Get detected license plate number.
        
        Returns:
            str or None: License plate number if found, None otherwise
        """
        return self.detected_plate

    def draw_result(self, image=None):
        """
        Draw bounding boxes pada image.
        
        Args:
            image: Image untuk draw (default: current_image)
            
        Returns:
            numpy array: Image dengan bounding boxes
        """
        if image is None:
            image = self.current_image
        
        if image is None or self.current_result is None:
            return image
        
        # Copy image
        result_image = image.copy()
        
        # Draw bounding boxes
        for item in self.current_result.get('texts', []):
            bbox = item['bbox']
            text = item['text']
            conf = item['confidence']
            
            # Convert bbox to points
            if len(bbox) == 4:
                pts = np.array(bbox, dtype=np.int32)
                
                # Draw box
                cv2.polylines(result_image, [pts], True, (0, 255, 0), 2)
                
                # Draw label
                label = f"{text} ({conf:.2f})"
                (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                
                # Background untuk label
                cv2.rectangle(result_image, 
                            (pts[0][0], pts[0][1] - label_h - 10),
                            (pts[0][0] + label_w, pts[0][1]),
                            (0, 255, 0), -1)
                
                # Text label
                cv2.putText(result_image, label,
                           (pts[0][0], pts[0][1] - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return result_image

    def group_texts_by_line(self, texts):
        """
        Group texts yang berada pada line yang sama.
        
        Args:
            texts: List of detected texts dengan bbox dan avg_y
            
        Returns:
            list: List of grouped texts
        """
        if not texts:
            return []
        
        # Sort by y-coordinate
        texts_sorted = sorted(texts, key=lambda x: x['avg_y'])
        
        grouped = []
        current_line = [texts_sorted[0]]
        
        for i in range(1, len(texts_sorted)):
            current = texts_sorted[i]
            prev_avg_y = current_line[-1]['avg_y']
            
            # Check if same line
            if abs(current['avg_y'] - prev_avg_y) <= self.line_tolerance:
                current_line.append(current)
            else:
                # Finalize current line
                if len(current_line) > 1:
                    merged = self.merge_line_texts(current_line)
                    grouped.append(merged)
                else:
                    grouped.append(current_line[0])
                current_line = [current]
        
        # Last line
        if len(current_line) > 1:
            merged = self.merge_line_texts(current_line)
            grouped.append(merged)
        else:
            grouped.append(current_line[0])
        
        # Sort by y (top to bottom)
        grouped.sort(key=lambda x: x['avg_y'])
        
        return grouped

    def merge_line_texts(self, texts):
        """
        Merge multiple texts pada line yang sama.

        Args:
            texts: List of texts pada line yang sama

        Returns:
            dict: Merged text
        """
        # Sort by x_min (left to right)
        texts_sorted = sorted(texts, key=lambda x: x['x_min'])

        # Merge texts - use space if delete_space is False, otherwise join without space
        if self.delete_space:
            merged_text = ''.join([t['text'] for t in texts_sorted])
        else:
            merged_text = ' '.join([t['text'] for t in texts_sorted])

        # Merge bbox
        all_pts = []
        for t in texts_sorted:
            all_pts.extend(t['bbox'])

        # Calculate merged bbox
        x_min = min([pt[0] for pt in all_pts])
        x_max = max([pt[0] for pt in all_pts])
        y_min = min([pt[1] for pt in all_pts])
        y_max = max([pt[1] for pt in all_pts])

        merged_bbox = [
            [x_min, y_min],
            [x_max, y_min],
            [x_max, y_max],
            [x_min, y_max]
        ]

        # Average confidence
        avg_conf = sum([t['confidence'] for t in texts_sorted]) / len(texts_sorted)

        return {
            'text': merged_text,
            'confidence': avg_conf,
            'bbox': merged_bbox,
            'original_text': merged_text,
            'avg_y': texts_sorted[0]['avg_y'],
            'x_min': x_min,
            'is_grouped': True
        }

    def export_to_txt(self, output_path=None):
        """
        Export hasil ke TXT file.
        
        Args:
            output_path: Path ke output file (default: output_dir/timestamp.txt)
            
        Returns:
            str: Path ke file yang disimpan
        """
        if self.current_result is None:
            raise ValueError("No result to export. Run process_image first.")
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.output_dir, f"{timestamp}.txt")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in self.current_result.get('texts', []):
                f.write(f"{item['text']} (conf: {item['confidence']:.2f})\n")
        
        print(f"[OK] Exported to {output_path}")
        return output_path

    def export_to_json(self, output_path=None):
        """
        Export hasil ke JSON file.
        
        Args:
            output_path: Path ke output file (default: output_dir/timestamp.json)
            
        Returns:
            str: Path ke file yang disimpan
        """
        if self.current_result is None:
            raise ValueError("No result to export. Run process_image first.")
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.output_dir, f"{timestamp}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.current_result, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Exported to {output_path}")
        return output_path

    def copy_to_clipboard(self):
        """
        Copy hasil ke clipboard.
        
        Returns:
            str: Text yang di-copy
        """
        if self.current_result is None:
            raise ValueError("No result to copy. Run process_image first.")
        
        text = '\n'.join([t['text'] for t in self.current_result.get('texts', [])])
        
        # Copy to clipboard (cross-platform)
        try:
            import pyperclip
            pyperclip.copy(text)
            print(f"[OK] Copied {len(text)} characters to clipboard")
        except ImportError:
            # Fallback: print text
            print("[WARNING] pyperclip not installed. Text:")
            print(text)
        
        return text

    def set_config(self, key, value):
        """
        Set configuration value.
        
        Args:
            key: Config key
            value: Config value
        """
        self.config[key] = value
        
        # Update instance variables
        if key == 'OCR_LANG':
            self.lang = value
            self.init_ocr()  # Re-initialize OCR
        elif key == 'CONF_THRESHOLD':
            self.conf_threshold = float(value)
        elif key == 'DELETE_SPACE':
            self.delete_space = value == 'True'
        elif key == 'GROUP_BY_LINE':
            self.group_by_line = value == 'True'
        elif key == 'LINE_TOLERANCE':
            self.line_tolerance = int(value)
        elif key == 'OUTPUT_DIR':
            self.output_dir = value
            os.makedirs(self.output_dir, exist_ok=True)

    def clear_result(self):
        """Clear current result."""
        self.current_image = None
        self.current_image_path = None
        self.current_result = None
        print("[OK] Result cleared")


__all__ = ['PaddleOCRWidget']
