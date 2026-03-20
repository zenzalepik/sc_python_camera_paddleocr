"""
PaddleOCR Multiple Widget Wrapper
Wrapper untuk multiple image OCR processing.

Usage:
    from paddleocr_multiple_widget import PaddleOCRMultipleWidget
    
    widget = PaddleOCRMultipleWidget(root=tkinter_root)
    widget.add_images(['img1.jpg', 'img2.jpg'])
    results = widget.process_all()
    widget.export_batch()
"""

import os
import sys
import json
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import threading
from dotenv import load_dotenv

# Load .env file
_widget_dir = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_widget_dir, '.env')
load_dotenv(_env_path)

# Import PaddleOCR
try:
    from paddleocr import PaddleOCR
    os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
except ImportError:
    print("PaddleOCR tidak terinstall!")
    print("Install: pip install paddlepaddle paddleocr")
    sys.exit(1)


class PaddleOCRMultipleWidget:
    """
    PaddleOCR Multiple Widget - Process multiple images dengan OCR.
    
    Features:
    - Add multiple images to queue
    - Batch process all images
    - Export results (TXT + JSON)
    - Per-image result tracking
    """

    def __init__(self, root=None, config=None):
        """
        Initialize widget.
        
        Args:
            root: Tkinter root (required for file dialogs)
            config: Configuration dict (optional)
        """
        self.root = root
        self.config = config or {}
        self.gui = None  # Store GUI reference if needed
        
        print("\n" + "="*60)
        print("PaddleOCR Multiple Widget initialized")
        print("="*60)

        # OCR Settings
        self.lang = self.config.get('OCR_LANG', os.getenv('OCR_LANG', 'id'))
        self.conf_threshold = float(self.config.get('CONF_THRESHOLD', os.getenv('CONF_THRESHOLD', '0.5')))
        self.delete_space = self.config.get('DELETE_SPACE', os.getenv('DELETE_SPACE', 'True')) == 'True'
        self.group_by_line = self.config.get('GROUP_BY_LINE', os.getenv('GROUP_BY_LINE', 'True')) == 'True'
        self.line_tolerance = int(self.config.get('LINE_TOLERANCE', os.getenv('LINE_TOLERANCE', '10')))
        self.detect_license_plate = self.config.get('DETECT_LICENSE_PLATE', os.getenv('DETECT_LICENSE_PLATE', 'True')) == 'True'
        self.output_dir = self.config.get('OUTPUT_DIR', os.getenv('OUTPUT_DIR', 'output'))

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # State variables
        self.images = []  # List of {path, filename, image, result, status, error, display_frame}
        self.ocr = None
        
        # Processing state
        self.processed_count = 0
        self.failed_count = 0
        
        # Initialize PaddleOCR
        self.init_ocr()

    def init_ocr(self):
        """Initialize PaddleOCR engine."""
        print("Initializing PaddleOCR v5 Mobile...")
        try:
            self.ocr = PaddleOCR(
                lang=self.lang,
                text_detection_model_name='PP-OCRv5_mobile_det',
                text_recognition_model_name='PP-OCRv5_mobile_rec',
            )
            print("[OK] PaddleOCR v5 Mobile initialized!")
            print(f"    - Language: {self.lang.upper()}")
            print(f"    - Delete Space: {'ON' if self.delete_space else 'OFF'}")
            print(f"    - Group by Line: {'ON' if self.group_by_line else 'OFF'}")
        except Exception as e:
            print(f"[ERROR] Error initializing PaddleOCR: {e}")
            raise

    def add_image(self, image_path):
        """Add single image to queue."""
        if not os.path.exists(image_path):
            print(f"[WARNING] File not found: {image_path}")
            return False
        
        image = cv2.imread(image_path)
        if image is None:
            print(f"[WARNING] Cannot read image: {image_path}")
            return False
        
        self.images.append({
            'path': image_path,
            'filename': os.path.basename(image_path),
            'image': image,
            'result': None,
            'status': 'pending',
            'error': None,
            'display_frame': None
        })
        
        print(f"[INFO] Added image: {os.path.basename(image_path)}")
        return True

    def add_images(self, image_paths):
        """Add multiple images to queue."""
        count = 0
        for path in image_paths:
            if self.add_image(path):
                count += 1
        print(f"[INFO] Added {count} images to queue")
        return count

    def clear_all(self):
        """Clear all images and results."""
        self.images = []
        self.processed_count = 0
        self.failed_count = 0
        print("[INFO] All data cleared")

    def process_all(self):
        """Process all images in queue."""
        if not self.images:
            print("[WARNING] No images to process")
            return []
        
        results = []
        self.processed_count = 0
        self.failed_count = 0
        
        print(f"\n{'='*60}")
        print(f"[BATCH] Processing {len(self.images)} images...")
        print(f"{'='*60}")
        
        for i, img_data in enumerate(self.images, 1):
            print(f"\n[{i}/{len(self.images)}] Processing: {img_data['filename']}")
            
            try:
                img_data['status'] = 'processing'
                
                # Run OCR
                result = self.ocr.predict(img_data['image'])
                
                # Parse result
                texts = []
                if result and len(result) > 0:
                    first_result = result[0]
                    if isinstance(first_result, dict):
                        rec_texts = first_result.get('rec_texts', [])
                        rec_scores = first_result.get('rec_scores', [])
                        rec_polys = first_result.get('rec_polys', [])
                        
                        for text, score, poly in zip(rec_texts, rec_scores, rec_polys):
                            if score >= self.conf_threshold:
                                processed_text = text.strip()
                                if self.delete_space:
                                    processed_text = processed_text.replace(' ', '')
                                
                                bbox = poly.tolist() if hasattr(poly, 'tolist') else poly
                                avg_y = sum([pt[1] for pt in bbox]) / 4 if len(bbox) == 4 else 0
                                x_min = min([pt[0] for pt in bbox]) if len(bbox) == 4 else 0
                                
                                texts.append({
                                    'text': processed_text,
                                    'confidence': float(score),
                                    'bbox': bbox,
                                    'original_text': text.strip(),
                                    'avg_y': avg_y,
                                    'x_min': x_min,
                                    'is_grouped': False
                                })
                
                # Group by line if enabled
                if self.group_by_line and len(texts) > 1:
                    texts = self._group_texts_by_line(texts)
                
                # Detect license plate if enabled
                plate = None
                if self.detect_license_plate:
                    plate = self._detect_license_plate(texts)
                
                # Create result dict
                result_dict = {
                    'texts': texts,
                    'total_texts': len(texts),
                    'total_lines': len(set(t['avg_y'] for t in texts)) if texts else 0,
                    'processing_time': 0.0,
                    'image_path': img_data['path'],
                    'image_filename': img_data['filename'],
                    'timestamp': datetime.now().isoformat(),
                    'plate': plate
                }
                
                # Draw bounding boxes
                frame_with_boxes = self._draw_boxes(img_data['image'], texts)
                
                # Update image data
                img_data['result'] = result_dict
                img_data['status'] = 'completed'
                img_data['display_frame'] = frame_with_boxes
                
                results.append(result_dict)
                self.processed_count += 1
                
                print(f"  [OK] Detected {len(texts)} texts")
                if plate:
                    print(f"  [PLATE] {plate}")
                
            except Exception as e:
                img_data['status'] = 'failed'
                img_data['error'] = str(e)
                self.failed_count += 1
                print(f"  [ERROR] {e}")
        
        print(f"\n{'='*60}")
        print(f"[BATCH] Complete! Success: {self.processed_count}, Failed: {self.failed_count}")
        print(f"{'='*60}")
        
        return results

    def _group_texts_by_line(self, texts):
        """Group texts by horizontal line."""
        sorted_texts = sorted(texts, key=lambda x: x['avg_y'])
        grouped = []
        current_line = [sorted_texts[0]]
        current_y = sorted_texts[0]['avg_y']
        
        for text in sorted_texts[1:]:
            if abs(text['avg_y'] - current_y) <= self.line_tolerance:
                current_line.append(text)
            else:
                current_line.sort(key=lambda x: x['x_min'])
                grouped.extend(current_line)
                current_line = [text]
                current_y = text['avg_y']
        
        current_line.sort(key=lambda x: x['x_min'])
        grouped.extend(current_line)
        
        for text in grouped:
            text['is_grouped'] = True
        
        return grouped

    def _detect_license_plate(self, texts):
        """Detect Indonesian license plate from texts."""
        if not texts:
            return None
        
        try:
            from .indonesia.plat_processor import IndonesianPlateProcessor
            processor = IndonesianPlateProcessor()
            combined = ' '.join([t['text'] for t in texts])
            return processor.detect_plate(combined)
        except:
            return None

    def _draw_boxes(self, image, texts):
        """Draw bounding boxes on image."""
        frame = image.copy()
        
        for text_data in texts:
            bbox = text_data['bbox']
            text = text_data['text']
            conf = text_data['confidence']
            
            pts = np.array(bbox, dtype=np.int32)
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
            
            label = f"{text} ({conf:.2f})"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            
            top_left = (pts[0][0], pts[0][1] - label_h - 5)
            bottom_right = (pts[0][0] + label_w, pts[0][1])
            
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), -1)
            cv2.putText(frame, label, (pts[0][0], pts[0][1] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return frame

    def export_batch(self, output_dir=None):
        """Export all results (TXT + JSON)."""
        if not output_dir:
            output_dir = self.output_dir
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export TXT
        txt_path = os.path.join(output_dir, f"batch_{timestamp}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("PaddleOCR Multiple Image Text Detection Result\n")
            f.write("="*60 + "\n\n")
            
            for i, img_data in enumerate(self.images, 1):
                if img_data.get('result'):
                    result = img_data['result']
                    f.write(f"Image {i}: {result.get('image_filename', 'N/A')}\n")
                    f.write(f"Timestamp: {result.get('timestamp', 'N/A')}\n")
                    f.write(f"Total Texts: {result.get('total_texts', 0)}\n")
                    if result.get('plate'):
                        f.write(f"Detected Plate: {result['plate']}\n")
                    f.write("="*60 + "\n\n")
                    
                    for j, text_data in enumerate(result.get('texts', []), 1):
                        f.write(f"[{j}] {text_data['text']}\n")
                        f.write(f"    Confidence: {text_data['confidence']:.4f}\n")
                    f.write("\n")
        
        # Export JSON
        json_path = os.path.join(output_dir, f"batch_{timestamp}.json")
        results = [img['result'] for img in self.images if img.get('result')]
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'batch_results': results,
                'total_images': len(results),
                'processed_count': self.processed_count,
                'failed_count': self.failed_count,
                'export_timestamp': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Exported to: {txt_path}, {json_path}")
        return txt_path, json_path


# Export
__all__ = ['PaddleOCRMultipleWidget']
