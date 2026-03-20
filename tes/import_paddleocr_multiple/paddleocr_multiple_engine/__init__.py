"""
PaddleOCR Multiple Engine - CORE LOGIC COPY dari import_paddleocr

SEMUA LOGIC DI-COPY 100% DARI:
  D:\Github\sc_python_camera_paddleocr\tes\import_paddleocr\paddleocr_widget\widget_wrapper.py

CARA KERJA:
1. Create instance dari PaddleOCRWidget (dari engine yang di-copy)
2. LOOPING untuk setiap image
3. Panggil method yang SAMA PERSIS: process_frame(), get_result(), dll
4. Kumpulkan semua hasil

SEMUA FITUR SAMA:
- ✅ OCR dengan PaddleOCR v5 Mobile
- ✅ Delete space
- ✅ Group by line (horizontal grouping)
- ✅ License plate detection (indonesia/plat_processor.py)
- ✅ Bounding box visualization
- ✅ Export TXT/JSON
- ✅ Copy to clipboard
"""

import os
import sys
import cv2
import numpy as np
from datetime import datetime
import threading

# Import dari engine yang di-copy (100% SAME LOGIC!)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "paddleocr_engine"))
from paddleocr_engine import PaddleOCRWidget


class PaddleOCRMultipleCoreEngine:
    """
    Multiple Image Engine - CORE LOGIC COPY.
    
    CARA KERJA:
    1. Initialize SINGLE widget (dengan semua logic dari referensi)
    2. Add multiple images ke queue
    3. process_all() -> LOOPING call widget.process_frame() untuk setiap image
    4. Return semua hasil
    
    SEMUA LOGIC SAMA PERSIS dengan import_paddleocr!
    """

    def __init__(self, config=None):
        """
        Initialize Multiple Engine dengan CORE LOGIC yang sama.
        
        Args:
            config: Configuration dict (sama dengan single image)
        """
        self.config = config or {}
        
        # Create SINGLE widget instance (PAKAI CORE LOGIC YANG SAMA!)
        print(f"\n{'='*80}")
        print(f"  PADDLEOCR MULTIPLE ENGINE - CORE LOGIC COPY")
        print(f"{'='*80}")
        print(f"\n[INIT] Creating PaddleOCRWidget dengan logic dari import_paddleocr...")
        
        self.widget = PaddleOCRWidget(config=self.config)
        
        # Multiple image state
        self.images = []  # List of {path, filename, image, result, status, error, display_frame}
        self.processed_count = 0
        self.failed_count = 0
        
        print(f"\n[INFO] Multiple Engine initialized")
        print(f"[INFO] Using 100% SAME core logic as import_paddleocr")
        print(f"[INFO] Features:")
        print(f"  - OCR: PaddleOCR v5 Mobile")
        print(f"  - Delete Space: {self.widget.delete_space}")
        print(f"  - Group by Line: {self.widget.group_by_line}")
        print(f"  - Line Tolerance: {self.widget.line_tolerance}px")
        print(f"  - License Plate Detection: {self.widget.detect_license_plate}")
        print(f"{'='*80}\n")

    def add_image(self, image_path):
        """
        Add single image to queue.
        
        Args:
            image_path: Path to image file
            
        Returns:
            bool: True if success
        """
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
        """
        Add multiple images to queue.
        
        Args:
            image_paths: List of image paths
            
        Returns:
            int: Number of images added
        """
        count = 0
        for path in image_paths:
            if self.add_image(path):
                count += 1
        print(f"[INFO] Added {count} images to queue")
        return count

    def process_image(self, index):
        """
        Process single image by index - MENGGUNAKAN CORE LOGIC YANG SAMA!
        
        LOGIC (COPY 100% dari import_paddleocr):
        1. Load image
        2. Run PaddleOCR prediction
        3. Parse result (rec_texts, rec_scores, rec_polys)
        4. Apply delete_space (if enabled)
        5. Apply group_by_line (if enabled)
        6. Detect license plate (if enabled)
        7. Draw bounding boxes
        8. Return result dict
        
        Args:
            index: Index of image to process
            
        Returns:
            dict: OCR result or None if failed
        """
        if index < 0 or index >= len(self.images):
            print(f"[ERROR] Invalid image index: {index}")
            return None
        
        img_data = self.images[index]
        img_data['status'] = 'processing'
        
        print(f"\n{'='*80}")
        print(f"[PROCESS] Image {index + 1}/{len(self.images)}")
        print(f"  - File: {img_data['filename']}")
        print(f"{'='*80}")
        
        try:
            # PAKAI CORE LOGIC YANG SAMA PERSIS!
            image = img_data['image']
            
            # Call widget.process_frame() - INI CORE LOGIC YANG SAMA!
            # Di dalamnya ada:
            # 1. OCR prediction
            # 2. Parse results
            # 3. Delete space
            # 4. Group by line
            # 5. Plate detection
            # 6. Draw boxes
            frame_with_boxes, result = self.widget.process_frame(image)
            
            # Get results - SAME LOGIC!
            texts = self.widget.get_texts()
            plate = self.widget.get_detected_plate()
            
            # Update image data
            img_data['result'] = self.widget.current_result
            img_data['display_frame'] = frame_with_boxes
            img_data['status'] = 'completed'
            
            self.processed_count += 1
            
            print(f"\n[SUCCESS] Detected {len(texts)} text(s)")
            if plate:
                print(f"[PLATE] Detected: {plate}")
            
            return self.widget.current_result
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            
            img_data['status'] = 'failed'
            img_data['error'] = error_msg
            
            self.failed_count += 1
            
            print(f"\n[ERROR] Processing failed!")
            print(f"  - Error: {error_msg}")
            print(f"  - Traceback: {error_traceback}")
            
            return None

    def process_all(self):
        """
        Process all images in queue - LOOPING dengan core logic yang sama.
        
        CARA KERJA:
        1. Loop melalui semua images di queue
        2. Untuk setiap image, call process_image(index)
        3. process_image() call widget.process_frame() - CORE LOGIC SAMA!
        4. Kumpulkan semua results
        5. Return list of results
        
        Returns:
            list: List of OCR results
        """
        if not self.images:
            print("[WARNING] No images in queue!")
            return []
        
        results = []
        self.processed_count = 0
        self.failed_count = 0
        
        print(f"\n{'='*80}")
        print(f"[BATCH] Starting batch processing")
        print(f"  - Total images: {len(self.images)}")
        print(f"  - Delete Space: {self.widget.delete_space}")
        print(f"  - Group by Line: {self.widget.group_by_line}")
        print(f"  - Line Tolerance: {self.widget.line_tolerance}px")
        print(f"  - Detect License Plate: {self.widget.detect_license_plate}")
        print(f"{'='*80}")
        
        # LOOPING - Pakai core logic yang sama untuk setiap image!
        for i, img_data in enumerate(self.images):
            print(f"\n[BATCH] Image {i+1}/{len(self.images)}")
            result = self.process_image(i)
            if result:
                results.append(result)
        
        print(f"\n{'='*80}")
        print(f"[BATCH] Processing complete!")
        print(f"  - Total: {len(self.images)}")
        print(f"  - Success: {self.processed_count}")
        print(f"  - Failed: {self.failed_count}")
        print(f"{'='*80}\n")
        
        return results

    def process_all_threaded(self, callback=None):
        """
        Process all images in background thread.
        
        Args:
            callback: Optional callback function(result, index, total)
        """
        def worker():
            for i, img_data in enumerate(self.images):
                result = self.process_image(i)
                if callback:
                    callback(result, i, len(self.images))
        
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        return thread

    def get_result(self, index=None):
        """
        Get OCR result.
        
        Args:
            index: Image index (optional). If None, returns all results.
            
        Returns:
            dict or list: OCR result(s)
        """
        if index is not None:
            if 0 <= index < len(self.images):
                return self.images[index]['result']
            return None
        return [img['result'] for img in self.images if img.get('result')]

    def get_texts(self, index=None):
        """
        Get detected texts.
        
        Args:
            index: Image index (optional). If None, returns all texts from all images.
            
        Returns:
            list: List of text strings
        """
        if index is not None:
            result = self.get_result(index)
            if result:
                return [t['text'] for t in result.get('texts', [])]
            return []
        
        # All texts from all images
        all_texts = []
        for img in self.images:
            if img.get('result'):
                all_texts.extend([t['text'] for t in img['result'].get('texts', [])])
        return all_texts

    def export_to_txt(self, index=None, output_path=None):
        """
        Export result to TXT file - SAME LOGIC as import_paddleocr!
        
        Args:
            index: Image index (optional). If None, export all results.
            output_path: Output file path (optional)
            
        Returns:
            str: Output file path
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if index is not None:
                filename = f"result_{timestamp}_img{index}.txt"
            else:
                filename = f"batch_result_{timestamp}.txt"
            output_path = os.path.join(self.widget.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("PaddleOCR Multiple Image Text Detection Result\n")
            f.write("="*60 + "\n\n")
            
            if index is not None:
                # Export single image - PAKAI METHOD YANG SAMA!
                result = self.get_result(index)
                if result:
                    self._write_result_to_file(f, result, index + 1)
            else:
                # Export all images - LOOPING dengan method yang sama
                for i, result in enumerate(self.get_result(), 1):
                    self._write_result_to_file(f, result, i)
        
        print(f"[EXPORT] TXT exported to: {output_path}")
        return output_path

    def _write_result_to_file(self, f, result, index):
        """Write single result to file - SAME LOGIC as import_paddleocr!"""
        f.write(f"Image {index}: {result.get('image_filename', 'N/A')}\n")
        f.write(f"Timestamp: {result.get('timestamp', 'N/A')}\n")
        f.write(f"Processing Time: {result.get('processing_time', 0):.2f}s\n")
        f.write(f"Total Texts: {result.get('total_texts', 0)}\n")
        if result.get('plate'):
            f.write(f"Detected Plate: {result['plate']}\n")
        f.write("="*60 + "\n\n")
        
        for i, text_data in enumerate(result.get('texts', []), 1):
            f.write(f"[{i}] {text_data['text']}\n")
            f.write(f"    Confidence: {text_data['confidence']:.4f}\n")
        
        f.write("\n")

    def export_to_json(self, index=None, output_path=None):
        """
        Export result to JSON file - SAME LOGIC as import_paddleocr!
        
        Args:
            index: Image index (optional). If None, export all results.
            output_path: Output file path (optional)
            
        Returns:
            str: Output file path
        """
        import json
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if index is not None:
                filename = f"result_{timestamp}_img{index}.json"
            else:
                filename = f"batch_result_{timestamp}.json"
            output_path = os.path.join(self.widget.output_dir, filename)
        
        if index is not None:
            data = self.get_result(index)
        else:
            data = {
                'batch_results': self.get_result(),
                'total_images': len(self.images),
                'processed_count': self.processed_count,
                'failed_count': self.failed_count,
                'export_timestamp': datetime.now().isoformat()
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[EXPORT] JSON exported to: {output_path}")
        return output_path

    def export_batch(self, output_dir=None):
        """
        Export all results (TXT + JSON) - SAME LOGIC as import_paddleocr!
        
        Args:
            output_dir: Output directory (optional)
            
        Returns:
            tuple: (txt_path, json_path)
        """
        txt_path = self.export_to_txt(output_path=os.path.join(
            output_dir or self.widget.output_dir,
            f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        ))
        
        json_path = self.export_to_json(output_path=os.path.join(
            output_dir or self.widget.output_dir,
            f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        ))
        
        return txt_path, json_path

    def copy_to_clipboard(self, index=None):
        """
        Copy texts to clipboard - SAME LOGIC as import_paddleocr!
        
        Args:
            index: Image index (optional). If None, copy all texts.
        """
        try:
            import pyperclip
            
            if index is not None:
                texts = self.get_texts(index)
            else:
                texts = self.get_texts()
            
            text = '\n'.join(texts)
            pyperclip.copy(text)
            print(f"[CLIPBOARD] Copied {len(texts)} text(s)")
            return text
        except ImportError:
            print("[WARNING] pyperclip not installed. Cannot copy to clipboard.")
            return None

    def clear_all(self):
        """Clear all images and results."""
        self.images = []
        self.processed_count = 0
        self.failed_count = 0
        self.widget.clear_result()
        print("[INFO] All data cleared")


# Export
__all__ = ['PaddleOCRMultipleCoreEngine']
