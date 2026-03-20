"""
PaddleOCR Multiple Engine Wrapper
Wrapper untuk multiple image processing menggunakan ENGINE yang sama persis dengan single image version.

SEMUA FITUR dari import_paddleocr/widget_wrapper.py DI-COPY UTUH:
- ✅ License plate detection (plat nomor Indonesia)
- ✅ O/0, B/8, I/1 handling
- ✅ Delete space option
- ✅ Group by line
- ✅ Confidence threshold
- ✅ Export TXT/JSON
- ✅ Copy to clipboard
"""

import os
import sys
import json
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import threading

# Import dari engine yang di-copy (SAMA PERSIS!)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "paddleocr_engine"))
from paddleocr_engine import PaddleOCRWidget


class PaddleOCRMultipleEngine:
    """
    Multiple Image Engine - Menggunakan logic yang sama persis dengan single image.
    
    CARA KERJA:
    1. Create instance dari PaddleOCRWidget (dari engine yang di-copy)
    2. Loop untuk setiap image
    3. Panggil method yang sama: process_image(), get_result(), dll
    
    SEMUA FITUR SAMA:
    - License plate detection
    - O/0, B/8, I/1 correction
    - Delete space
    - Group by line
    - Export TXT/JSON
    - Copy to clipboard
    """

    def __init__(self, config=None):
        """
        Initialize Multiple Engine.
        
        Args:
            config: Configuration dict (sama dengan single image)
        """
        self.config = config or {}
        
        # Create SINGLE widget instance (PAKAI ENGINE YANG SAMA!)
        self.widget = PaddleOCRWidget(config=self.config)
        
        # Multiple image state
        self.images = []  # List of {path, filename, image, result, status, error, display_frame}
        self.processed_count = 0
        self.failed_count = 0
        
        print(f"\n[INFO] PaddleOCR Multiple Engine initialized")
        print(f"[INFO] Using SAME engine as single image version")
        print(f"[INFO] All features preserved:")
        print(f"  - License plate detection: {self.widget.detect_license_plate}")
        print(f"  - Delete space: {self.widget.delete_space}")
        print(f"  - Group by line: {self.widget.group_by_line}")
        print(f"  - Line tolerance: {self.widget.line_tolerance}px")

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
        Process single image by index - MENGGUNAKAN ENGINE YANG SAMA!
        
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
        
        print(f"\n{'='*60}")
        print(f"[PROCESS] Processing image {index + 1}/{len(self.images)}")
        print(f"  - File: {img_data['filename']}")
        print(f"{'='*60}")
        
        try:
            # PAKAI ENGINE YANG SAMA PERSIS!
            image = img_data['image']
            
            # Process dengan widget (ENGINE SAMA!)
            frame_with_boxes, result = self.widget.process_frame(image)
            
            # Get results (ENGINE SAMA!)
            texts = self.widget.get_texts()
            plate = self.widget.get_detected_plate()
            
            # Update image data
            img_data['result'] = self.widget.current_result
            img_data['display_frame'] = frame_with_boxes
            img_data['status'] = 'completed'
            
            self.processed_count += 1
            
            print(f"[SUCCESS] Detected {len(texts)} text(s)")
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
            
            print(f"[ERROR] Processing failed!")
            print(f"  - Error: {error_msg}")
            print(f"  - Traceback: {error_traceback}")
            
            return None

    def process_all(self):
        """
        Process all images in queue - LOOPING dengan engine yang sama.
        
        Returns:
            list: List of OCR results
        """
        if not self.images:
            print("[WARNING] No images in queue!")
            return []
        
        results = []
        self.processed_count = 0
        self.failed_count = 0
        
        print(f"\n{'='*60}")
        print(f"[BATCH] Starting batch processing")
        print(f"  - Total images: {len(self.images)}")
        print(f"{'='*60}")
        
        # LOOPING - Pakai engine yang sama untuk setiap image!
        for i, img_data in enumerate(self.images):
            print(f"\n[BATCH] Image {i+1}/{len(self.images)}")
            result = self.process_image(i)
            if result:
                results.append(result)
        
        print(f"\n{'='*60}")
        print(f"[BATCH] Processing complete!")
        print(f"  - Total: {len(self.images)}")
        print(f"  - Success: {self.processed_count}")
        print(f"  - Failed: {self.failed_count}")
        print(f"{'='*60}")
        
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
        Export result to TXT file - MENGGUNAKAN ENGINE EXPORT YANG SAMA!
        
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
        """Write single result to file - SAMA PERSIS dengan engine."""
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
        Export result to JSON file - MENGGUNAKAN ENGINE EXPORT YANG SAMA!
        
        Args:
            index: Image index (optional). If None, export all results.
            output_path: Output file path (optional)
            
        Returns:
            str: Output file path
        """
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
        Export all results (TXT + JSON) - MENGGUNAKAN METHOD YANG SAMA!
        
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
        Copy texts to clipboard - MENGGUNAKAN METHOD YANG SAMA!
        
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
__all__ = ['PaddleOCRMultipleEngine']
