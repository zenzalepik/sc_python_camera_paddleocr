"""
Aplikasi Python dengan Layout Responsive - 2 Frame Kiri-Kanan
- Frame kiri: Teks "Selamat Datang" + 4 tombol
- Frame kanan: PaddleOCR Widget (OCR Text Detection)
- UI elements scale otomatis saat window resize
"""

import cv2
import numpy as np
import sys
import os
import tkinter as tk
from tkinter import filedialog
import time
import threading

# Import PaddleOCR widget
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "paddleocr_widget"))
from paddleocr_widget import PaddleOCRWidget


class Button:
    """Reusable Button component."""

    def __init__(self, text, color=(0, 120, 255), text_color=(255, 255, 255)):
        self.text = text
        self.color = color
        self.text_color = text_color
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

    def draw(self, frame, x, y, width, height, font_scale=None):
        """Draw button on frame."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Button background
        cv2.rectangle(frame, (x, y), (x + width, y + height), self.color, -1)
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 255), 2)

        # Button text
        if font_scale is None:
            font_scale = min(frame.shape[1], frame.shape[0]) / 1500

        (text_w, text_h), _ = cv2.getTextSize(
            self.text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1
        )
        text_x = x + (width - text_w) // 2
        text_y = y + (height + text_h) // 2

        cv2.putText(frame, self.text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, self.text_color, 1)

    def is_clicked(self, mouse_x, mouse_y):
        """Check if button is clicked."""
        return (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height)


class ResponsiveApp:
    """Aplikasi dengan UI responsive yang scale otomatis."""

    def __init__(self, window_width=1280, window_height=700):
        self.window_width = window_width
        self.window_height = window_height
        self.window_name = "Aplikasi Python - PaddleOCR Widget"

        # Initialize buttons
        self.buttons = [
            Button("Open", color=(0, 120, 255)),
            Button("Detect", color=(0, 180, 0)),
            Button("Export", color=(255, 100, 0)),
            Button("Clear", color=(200, 0, 200)),
        ]

        # Initialize PaddleOCR widget
        self.widget = PaddleOCRWidget()

        # Current image
        self.current_image = None
        self.current_image_path = None

        # Mouse callback
        self.mouse_callback = None

        # Loading state
        self.is_loading = False
        self.loading_start_time = 0
        self.ocr_result = None
        self.ocr_error = None
        self.ocr_thread = None
        
        # STATE FLAGS - untuk tracking progress
        self.widget_initialized = True  # Widget sudah init di __init__
        self.image_loaded = False
        self.ocr_processing = False
        self.ocr_complete = False
        self.cooldown_complete = True  # Ready dari awal
        
        # Export success message flag
        self.show_export_message = False
        self.export_message_time = 0

    def draw_left_frame(self, frame, width, height):
        """Draw frame kiri dengan teks 'Selamat Datang' + 4 tombol + hasil deteksi."""
        # Background putih
        cv2.rectangle(frame, (0, 0), (width, height), (255, 255, 255), -1)

        # Teks "Selamat Datang"
        text = "Selamat Datang"
        font_scale = min(width, height) / 500
        thickness = max(1, int(font_scale * 2))

        (text_w, text_h), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )

        text_x = (width - text_w) // 2
        text_y = height // 8

        cv2.putText(frame, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)

        # Draw export success message (below "Selamat Datang")
        if self.show_export_message:
            # Check if 2 seconds have passed
            if time.time() - self.export_message_time > 2:
                self.show_export_message = False
            else:
                # Draw success message
                msg = "✓ Export Berhasil!"
                msg_font_scale = min(width, height) / 600
                msg_thickness = max(1, int(msg_font_scale * 2))
                
                (msg_w, msg_h), _ = cv2.getTextSize(
                    msg, cv2.FONT_HERSHEY_SIMPLEX, msg_font_scale, msg_thickness
                )
                msg_x = (width - msg_w) // 2
                msg_y = text_y + 50  # Below "Selamat Datang"
                
                # Draw background rectangle for message
                cv2.rectangle(frame, 
                             (msg_x - 20, msg_y - msg_h - 10),
                             (msg_x + msg_w + 20, msg_y + 10),
                             (76, 175, 80),  # Green background
                             -1)
                
                cv2.putText(frame, msg, (msg_x, msg_y),
                           cv2.FONT_HERSHEY_SIMPLEX, msg_font_scale, (255, 255, 255), msg_thickness)

        # Draw buttons horizontal
        button_width = width // 6
        button_height = height // 12
        button_spacing = width // 40
        total_buttons_width = len(self.buttons) * button_width + (len(self.buttons) - 1) * button_spacing
        start_x = (width - total_buttons_width) // 2
        start_y = height // 4

        font_scale_btn = min(width, height) / 1800

        for i, button in enumerate(self.buttons):
            btn_x = start_x + i * (button_width + button_spacing)
            btn_y = start_y
            button.draw(frame, btn_x, btn_y, button_width, button_height, font_scale_btn)

        # Draw plat nomor panel (jika ada)
        self.draw_plate_panel(frame, width, height, start_y + button_height)

        # Draw hasil deteksi panel di bawah tombol
        self.draw_result_panel(frame, width, height, start_y + button_height)

    def draw_plate_panel(self, frame, width, height, y_start):
        """Draw panel plat nomor terdeteksi - WITH CLEAR CHECK."""
        # Check jika data sudah di-clear
        if not self.image_loaded or self.ocr_result is None:
            return  # Don't draw if cleared
        
        # Get detected plate from ocr_result
        plate = None
        if self.ocr_result and 'plate' in self.ocr_result:
            plate = self.ocr_result['plate']

        if plate is None:
            return  # Don't draw if no plate detected

        panel_y = y_start + 20
        margin = 10
        panel_height = 70

        # Draw panel background (green gradient)
        cv2.rectangle(frame, (margin, panel_y),
                     (width - margin, panel_y + panel_height), (0, 100, 0), -1)
        cv2.rectangle(frame, (margin, panel_y),
                     (width - margin, panel_y + panel_height), (0, 255, 0), 2)

        # Draw title (top line)
        title = "Plat Nomor Terdeteksi:"
        cv2.putText(frame, title, (margin + 15, panel_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Draw plate number (large, bold, centered) - second line
        plate_text = plate.upper()
        (plate_w, plate_h), _ = cv2.getTextSize(plate_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)
        plate_x = (width - plate_w) // 2
        cv2.putText(frame, plate_text, (plate_x, panel_y + 58),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)

    def draw_result_panel(self, frame, width, height, y_start):
        """Draw panel hasil deteksi di bawah tombol."""
        # Panel area - start lower to make room for plate panel
        panel_y = y_start + 100  # Increased from 30 to 100 to push down
        panel_height = height - panel_y - 30
        margin = 10
        
        # Draw panel background
        cv2.rectangle(frame, (margin, panel_y), 
                     (width - margin, height - 20), (240, 240, 240), -1)
        cv2.rectangle(frame, (margin, panel_y), 
                     (width - margin, height - 20), (128, 128, 128), 2)
        
        # Title
        title = "Hasil Deteksi:"
        cv2.putText(frame, title, (margin + 10, panel_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Check loading state
        if self.is_loading:
            # Draw loading indicator
            self.draw_loading_indicator(frame, width, panel_y, panel_height, margin)
            return
        
        # Check error
        if self.ocr_error:
            error_text = f"Error: {self.ocr_error}"
            cv2.putText(frame, error_text, (margin + 10, panel_y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            return
        
        # Check ada result
        if self.ocr_result is None and self.widget.current_result is None:
            info = "Belum ada hasil deteksi"
            cv2.putText(frame, info, (margin + 10, panel_y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 1)
            return
        
        # Get texts dari OCR result atau widget
        if self.ocr_result:
            texts = self.ocr_result['texts']
            total = self.ocr_result['count']
        else:
            texts = self.widget.get_texts()
            total = len(texts)
        
        # Show count
        count_info = f"Total: {total} teks"
        cv2.putText(frame, count_info, (width - margin - 120, panel_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 128, 0), 1)
        
        # Draw texts (max 10 yang ditampilkan)
        max_display = 10
        start_idx = 0
        line_height = 28
        max_lines = (panel_height - 80) // line_height
        
        # Scroll jika lebih dari max_lines
        if total > max_lines:
            # Show last max_lines
            start_idx = total - max_lines
        
        display_texts = texts[start_idx:start_idx + max_display]
        
        for i, text_item in enumerate(display_texts, start_idx):
            if isinstance(text_item, dict):
                text = text_item['text']
                conf = text_item['confidence']
            else:
                text = str(text_item)
                conf = 0.0
            
            # Truncate text jika terlalu panjang
            max_chars = (width - 60) // 10
            if len(text) > max_chars:
                text = text[:max_chars-3] + "..."
            
            # Draw text line
            y_pos = panel_y + 65 + (i - start_idx) * line_height
            
            # Background selang-seling
            color = (255, 255, 255) if i % 2 == 0 else (230, 230, 230)
            cv2.rectangle(frame, (margin + 5, y_pos - 20),
                         (width - margin - 5, y_pos + 8), color, -1)
            
            # Text
            label = f"{i+1}. {text}"
            cv2.putText(frame, label, (margin + 10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            # Confidence (kanan)
            conf_label = f"({conf:.2f})"
            (conf_w, conf_h), _ = cv2.getTextSize(conf_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.putText(frame, conf_label, (width - margin - conf_w - 15, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 128, 0), 1)
        
        # Info jika ada lebih banyak teks
        if total > max_display:
            info = f"... dan {total - max_display} teks lainnya"
            cv2.putText(frame, info, (margin + 10, height - 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (128, 128, 128), 1)

    def draw_loading_indicator(self, frame, width, panel_y, panel_height, margin):
        """Draw loading indicator saat OCR processing."""
        # Calculate elapsed time
        elapsed = time.time() - self.loading_start_time
        
        # Center positions
        center_x = width // 2
        start_y = panel_y + 80
        
        # Draw loading message
        loading_text = "⏳ Processing OCR..."
        (text_w, text_h), _ = cv2.getTextSize(loading_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        text_x = center_x - text_w // 2
        cv2.putText(frame, loading_text, (text_x, start_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Draw elapsed time
        time_text = f"⏱️  Elapsed: {elapsed:.1f}s"
        (time_w, time_h), _ = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        time_x = center_x - time_w // 2
        cv2.putText(frame, time_text, (time_x, start_y + 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
        
        # Draw animated loading bar
        bar_width = 400
        bar_height = 25
        bar_x = center_x - bar_width // 2
        bar_y = start_y + 80
        
        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + bar_height), (200, 200, 200), -1)
        cv2.rectangle(frame, (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), 2)
        
        # Animated fill (pulsing effect)
        fill_width = int((elapsed * 40) % (bar_width + 100)) - 50
        if fill_width < 10:
            fill_width = 10
        if fill_width > bar_width:
            fill_width = bar_width
        
        # Pulsing color (blue ↔ cyan ↔ green)
        pulse = int(elapsed * 3) % 3
        if pulse == 0:
            color = (255, 0, 0)  # Blue
        elif pulse == 1:
            color = (255, 255, 0)  # Cyan
        else:
            color = (0, 255, 0)  # Green
        
        cv2.rectangle(frame, (bar_x + 2, bar_y + 2), 
                     (bar_x + fill_width - 2, bar_y + bar_height - 2), color, -1)
        
        # Draw percentage
        percent = int((fill_width / bar_width) * 100)
        percent_text = f"{percent}%"
        (pct_w, pct_h), _ = cv2.getTextSize(percent_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        pct_x = center_x - pct_w // 2
        cv2.putText(frame, percent_text, (pct_x, bar_y + bar_height + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 128, 0), 2)
        
        # Draw spinner dots
        dot_count = 5
        dot_spacing = 40
        dots_start_x = center_x - (dot_count * dot_spacing) // 2
        dots_y = bar_y + bar_height + 60
        
        for i in range(dot_count):
            dot_x = dots_start_x + i * dot_spacing
            dot_y = dots_y
            
            # Animate dots - wave effect
            dot_phase = (int(elapsed * 10) + i * 2) % (dot_count * 2)
            if dot_phase < dot_count:
                dot_active = True
                dot_radius = 8
                dot_color = (0, 255, 0)  # Green
            else:
                dot_active = False
                dot_radius = 5
                dot_color = (200, 200, 200)  # Gray
            
            cv2.circle(frame, (dot_x, dot_y), dot_radius, dot_color, -1)
            cv2.circle(frame, (dot_x, dot_y), dot_radius, (100, 100, 100), 1)
        
        # Draw please wait message
        wait_text = "Please wait..."
        (wait_w, wait_h), _ = cv2.getTextSize(wait_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        wait_x = center_x - wait_w // 2
        cv2.putText(frame, wait_text, (wait_x, dots_y + 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)

    def draw_right_frame(self, frame, start_x, width, height, ocr_frame=None):
        """Draw frame kanan dengan PaddleOCR widget."""
        if ocr_frame is not None:
            # Resize OCR frame to fit right frame
            ocr_resized = cv2.resize(ocr_frame, (width, height))

            # Copy to main frame
            frame[:height, start_x:start_x + width] = ocr_resized
        else:
            # Fallback
            cv2.rectangle(frame, (start_x, 0), (start_x + width, height), (128, 128, 128), -1)
            text = "No Image Loaded"
            cv2.putText(frame, text, (start_x + 10, height // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    def draw(self, frame, ocr_frame=None):
        """Draw semua UI elements."""
        height, width = frame.shape[:2]
        half_width = width // 2

        self.draw_left_frame(frame[:, :half_width], half_width, height)
        self.draw_right_frame(frame, half_width, half_width, height, ocr_frame)

        # Divider line
        cv2.line(frame, (half_width, 0), (half_width, height), (255, 255, 255), 2)

    def open_image(self):
        """Open file dialog untuk pilih gambar."""
        # Gunakan tkinter untuk file dialog
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("All files", "*.*")
        ]

        filepath = filedialog.askopenfilename(
            title="Select Image",
            filetypes=filetypes
        )

        root.destroy()

        if filepath:
            self.current_image = cv2.imread(filepath)
            self.current_image_path = filepath
            self.image_loaded = True  # Set flag
            print(f"[OK] Loaded: {filepath}")
            return True

        return False

    def detect_text(self):
        """Detect text dengan STATE MACHINE - proper sequencing + DETAILED LOGS."""
        
        print(f"\n{'='*60}")
        print(f"[DETECT] Click detected at {time.strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # === FASE 1: Check image loaded ===
        print(f"[FASE 1] Checking image loaded...")
        if self.current_image is None:
            print(f"[FASE 1] ❌ FAILED - No image loaded!")
            print("[WARNING] No image loaded. Open image first.")
            return
        print(f"[FASE 1] ✓ PASSED - Image loaded: {self.current_image.shape}")
        
        # === FASE 2: Check thread tidak sedang jalan ===
        print(f"[FASE 2] Checking OCR thread status...")
        if self.ocr_thread and self.ocr_thread.is_alive():
            print(f"[FASE 2] ❌ FAILED - Thread still alive!")
            print("[WARNING] OCR already running! Please wait until complete...")
            print("[INFO] Click ignored to prevent race condition.")
            return
        print(f"[FASE 2] ✓ PASSED - Thread not running")
        
        # === FASE 3: Check cooldown sudah selesai ===
        print(f"[FASE 3] Checking cooldown status...")
        if not self.cooldown_complete:
            print(f"[FASE 3] ❌ FAILED - Cooldown not complete!")
            print("[WARNING] Cooldown not complete yet. Please wait...")
            return
        print(f"[FASE 3] ✓ PASSED - Cooldown complete")
        
        # === FASE 4: Clear state ===
        print(f"[FASE 4] Clearing previous state...")
        print(f"  - ocr_result: {self.ocr_result is not None}")
        print(f"  - ocr_error: {self.ocr_error is not None}")
        self.ocr_result = None
        self.ocr_error = None
        self.widget.clear_result()
        print(f"[FASE 4] ✓ State cleared")
        
        # === FASE 5: Set state flags ===
        print(f"[FASE 5] Setting state flags...")
        self.ocr_processing = True
        self.ocr_complete = False
        self.cooldown_complete = False
        self.is_loading = True
        self.loading_start_time = time.time()
        print(f"  - ocr_processing: {self.ocr_processing}")
        print(f"  - ocr_complete: {self.ocr_complete}")
        print(f"  - cooldown_complete: {self.cooldown_complete}")
        print(f"  - is_loading: {self.is_loading}")
        print(f"[FASE 5] ✓ Flags set")
        
        print(f"\n{'='*60}")
        print("Running OCR...")
        print(f"{'='*60}")
        
        # === FASE 6: Start OCR thread ===
        print(f"[FASE 6] Starting OCR thread...")
        self.ocr_thread = threading.Thread(target=self._ocr_worker)
        self.ocr_thread.daemon = True
        self.ocr_thread.start()
        print(f"[FASE 6] ✓ Thread started (ID: {self.ocr_thread.ident})")

    def _ocr_worker(self):
        """OCR worker thread dengan DETAILED LOGS."""
        thread_id = threading.current_thread().ident
        print(f"\n{'='*60}")
        print(f"[THREAD {thread_id}] Started at {time.strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        try:
            # === FASE 1: Process OCR ===
            print(f"[THREAD {thread_id}] [FASE 1] Starting OCR processing...")
            print(f"[THREAD {thread_id}]   - Image shape: {self.current_image.shape}")
            print(f"[THREAD {thread_id}]   - Image dtype: {self.current_image.dtype}")
            
            frame_with_boxes, result = self.widget.process_frame(self.current_image)
            
            print(f"[THREAD {thread_id}] [FASE 1] ✓ OCR processing complete")
            print(f"[THREAD {thread_id}]   - Result type: {type(result)}")
            print(f"[THREAD {thread_id}]   - Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")

            # === FASE 2: Get results ===
            print(f"[THREAD {thread_id}] [FASE 2] Getting results...")
            texts = self.widget.get_texts()
            plate = self.widget.get_detected_plate()
            
            print(f"[THREAD {thread_id}] [FASE 2] ✓ Results retrieved")
            print(f"[THREAD {thread_id}]   - Text count: {len(texts)}")
            print(f"[THREAD {thread_id}]   - Plate: {plate}")

            # === FASE 3: Save results ===
            print(f"[THREAD {thread_id}] [FASE 3] Saving results...")
            self.ocr_result = {
                'texts': texts,
                'count': len(texts),
                'plate': plate,
                'display_frame': frame_with_boxes
            }
            print(f"[THREAD {thread_id}] [FASE 3] ✓ Results saved")
            print(f"[THREAD {thread_id}]   - ocr_result keys: {self.ocr_result.keys()}")

            print(f"\n[SUCCESS] Detected {len(texts)} text(s):")
            for i, text in enumerate(texts, 1):
                print(f"  [{i}] {text}")

            if plate:
                print(f"\n[🚗 PLATE DETECTED] {plate}")

            print("\n" + "="*60)
            
            # === FASE 4: Set OCR complete flag ===
            print(f"[THREAD {thread_id}] [FASE 4] Setting ocr_complete=True...")
            self.ocr_complete = True
            print(f"[THREAD {thread_id}] [FASE 4] ✓ Flag set")

        except Exception as e:
            import traceback
            self.ocr_error = str(e)
            error_traceback = traceback.format_exc()
            print(f"\n{'='*60}")
            print(f"[THREAD {thread_id}] [ERROR] OCR failed!")
            print(f"[THREAD {thread_id}]   - Error type: {type(e).__name__}")
            print(f"[THREAD {thread_id}]   - Error message: {e}")
            print(f"[THREAD {thread_id}]   - Traceback:\n{error_traceback}")
            print(f"{'='*60}")
        finally:
            # === FASE 5: Clear processing flag ===
            elapsed = time.time() - self.loading_start_time
            self.is_loading = False
            self.ocr_processing = False
            
            print(f"\n{'='*60}")
            print(f"[THREAD {thread_id}] [FASE 5] Clearing processing flags...")
            print(f"[THREAD {thread_id}]   - Elapsed time: {elapsed:.2f}s")
            print(f"[THREAD {thread_id}]   - ocr_processing: {self.ocr_processing}")
            print(f"[THREAD {thread_id}]   - is_loading: {self.is_loading}")
            print(f"[THREAD {thread_id}] [FASE 5] ✓ Flags cleared")
            
            # === FASE 6: Set cooldown complete flag (NO DELAY!) ===
            print(f"[THREAD {thread_id}] [FASE 6] Setting cooldown_complete=True...")
            self.cooldown_complete = True
            print(f"[THREAD {thread_id}] [FASE 6] ✓ Flag set")
            print(f"[THREAD {thread_id}] Cooldown complete - ready for next detection")
            print(f"{'='*60}")

    def export_result(self):
        """Export hasil OCR - FULL EXPORT."""
        print("\n" + "="*60)
        print("[EXPORT] === EXPORT BUTTON CLICKED ===")
        print("="*60)
        
        # Check if we have results
        if self.widget.current_result is None:
            print("[WARNING] No result to export. Please click 'Detect' first.")
            print("[EXPORT] Export cancelled - no data available")
            return

        if len(self.widget.current_result.get('texts', [])) == 0:
            print("[WARNING] No text detected. Nothing to export.")
            print("[EXPORT] Export cancelled - empty result")
            return

        # Get result info for logging
        texts_count = len(self.widget.current_result.get('texts', []))
        plate = self.widget.current_result.get('plate', 'N/A')
        print(f"[EXPORT] Data available:")
        print(f"  - Total texts: {texts_count}")
        print(f"  - Detected plate: {plate}")
        print(f"  - Processing time: {self.widget.current_result.get('processing_time', 'N/A')}s")
        print()

        # Export ke TXT
        print("[EXPORT] Exporting to TXT...")
        try:
            txt_path = self.widget.export_to_txt()
            print(f"[EXPORT] ✓ TXT exported to: {txt_path}")
        except Exception as e:
            print(f"[EXPORT] ✗ TXT export failed: {e}")

        # Export ke JSON
        print("[EXPORT] Exporting to JSON...")
        try:
            json_path = self.widget.export_to_json()
            print(f"[EXPORT] ✓ JSON exported to: {json_path}")
        except Exception as e:
            print(f"[EXPORT] ✗ JSON export failed: {e}")

        # Copy to clipboard
        print("[EXPORT] Copying to clipboard...")
        try:
            self.widget.copy_to_clipboard()
            print(f"[EXPORT] ✓ Copied to clipboard")
        except Exception as e:
            print(f"[EXPORT] ✗ Clipboard copy failed: {e}")

        print()
        print("[EXPORT] ✓ All exports completed successfully")
        print("="*60)

        # Show success message for 2 seconds (below "Selamat Datang")
        self.show_export_message = True
        self.export_message_time = time.time()

    def clear_all(self):
        """Clear semua - FULL RESET."""
        print("\n[CLEAR] Clearing all data...")
        
        # Clear app state
        self.current_image = None
        self.current_image_path = None
        self.ocr_result = None
        self.ocr_error = None
        self.is_loading = False
        
        # Clear state flags
        self.image_loaded = False
        self.ocr_processing = False
        self.ocr_complete = False
        self.cooldown_complete = True  # Ready untuk detect berikutnya
        
        # Clear widget state
        self.widget.clear_result()
        
        print("[CLEAR] ✓ All data cleared")
        print("[INFO] Ready for new image")

    def on_mouse_click(self, event, x, y, flags, param):
        """Handle mouse click events."""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check button clicks (hanya di frame kiri)
            half_width = self.window_width // 2
            if x < half_width:
                for i, button in enumerate(self.buttons):
                    if button.is_clicked(x, y):
                        print(f"\n[CLICK] Button {i+1}: {button.text}")
                        if i == 0:  # Open
                            self.open_image()
                        elif i == 1:  # Detect
                            self.detect_text()
                        elif i == 2:  # Export
                            self.export_result()
                        elif i == 3:  # Clear
                            self.clear_all()
                        break

    def run(self):
        """Run aplikasi."""
        print("\n" + "="*60)
        print("Aplikasi Python - PaddleOCR Widget")
        print("="*60)
        print("\nLayout:")
        print("  - Frame Kiri: Teks 'Selamat Datang' + 4 Tombol")
        print("  - Frame Kanan: PaddleOCR Widget (OCR Text Detection)")
        print("\nFeatures:")
        print("  - OpenCV-based display")
        print("  - PaddleOCR v5 Mobile")
        print("  - Bounding box visualization")
        print("  - Export to TXT/JSON")
        print("\nControls:")
        print("  - Click tombol di frame kiri untuk aksi")
        print("  - 'o': Open image")
        print("  - 'd': Detect text")
        print("  - 'e': Export result")
        print("  - 'c': Clear all")
        print("  - 'q' / ESC: Quit")
        print("="*60 + "\n")

        # Create Tkinter root untuk file dialogs
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()  # Hide main tkinter window

        # Create OpenCV window dengan mouse callback dan custom cursor
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.window_width, self.window_height)
        cv2.setMouseCallback(self.window_name, self.on_mouse_click)
        
        # Set custom cursor (default arrow cursor, bukan +)
        try:
            cv2.setWindowTitle(self.window_name, self.window_name)
        except:
            pass

        # Button click state
        button_clicked = [False] * len(self.buttons)

        try:
            while True:
                # Create frame
                frame = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)

                # Draw UI - PRIORITAS: display_frame (dengan bounding box) jika ada
                if self.ocr_result and 'display_frame' in self.ocr_result:
                    # Tampilkan frame dengan bounding box (dari hasil OCR terakhir)
                    ocr_frame = self.ocr_result['display_frame']
                elif self.current_image is not None:
                    # Tampilkan image asli (tanpa bounding box)
                    ocr_frame = self.current_image
                else:
                    ocr_frame = None

                self.draw(frame, ocr_frame)

                # Show
                cv2.imshow(self.window_name, frame)

                # Handle keyboard - ESC disabled, only 'q' can close
                key = cv2.waitKey(10) & 0xFF
                if key == ord('q'):  # Only 'q' closes app, ESC (key 27) disabled
                    break
                elif key == ord('o'):
                    self.open_image()
                elif key == ord('d'):
                    self.detect_text()
                elif key == ord('e'):
                    self.export_result()
                elif key == ord('c'):
                    self.clear_all()

        except Exception as e:
            print(f"\n[ERROR] {e}")
        finally:
            self.widget.clear_result()
            self.tk_root.destroy()
            cv2.destroyAllWindows()
            print("\n[OK] Application closed")


def main():
    """Main function."""
    app = ResponsiveApp(window_width=1280, window_height=700)
    app.run()


if __name__ == "__main__":
    main()
