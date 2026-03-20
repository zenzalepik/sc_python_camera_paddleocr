"""
Aplikasi Python dengan Layout Responsive - Multiple Image Detection
- Frame kiri: Teks "Selamat Datang" + 4 tombol + Image Queue Info
- Frame kanan: PaddleOCR Widget (OCR Text Detection Multiple Images)
- UI elements scale otomatis saat window resize
- SUPPORT MULTIPLE IMAGE SELECTION!
"""

import cv2
import numpy as np
import sys
import os
import tkinter as tk
from tkinter import filedialog
import time
import threading

# Import PaddleOCR Multiple Widget
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "paddleocr_multiple_widget"))
from paddleocr_multiple_widget import PaddleOCRMultipleWidget


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
    """Aplikasi dengan UI responsive yang scale otomatis untuk Multiple Images."""

    def __init__(self, window_width=1280, window_height=700):
        self.window_width = window_width
        self.window_height = window_height
        self.window_name = "Aplikasi Python - Multiple Image OCR"

        # Initialize buttons
        self.buttons = [
            Button("Open", color=(0, 120, 255)),
            Button("Detect All", color=(0, 180, 0)),  # Changed to "Detect All"
            Button("Export", color=(255, 100, 0)),
            Button("Clear", color=(200, 0, 200)),
        ]

        # Initialize Tkinter root (required for Multiple Widget)
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()

        # Initialize PaddleOCR Multiple Widget
        self.widget = PaddleOCRMultipleWidget(root=self.tk_root)

        # Current image (preview) - PERBAIKAN: ensure always int, not numpy array
        self.current_image = None
        self.current_image_path = None
        self.current_index = int(-1)  # Force int, not numpy array

        # Navigation for multiple images
        self.showing_image_index = int(-1)  # Which image we're currently viewing (always int)

        # Mouse callback
        self.mouse_callback = None

        # Loading state
        self.is_loading = False
        self.loading_start_time = 0
        self.ocr_result = None
        self.ocr_error = None
        self.ocr_thread = None

        # STATE FLAGS
        self.widget_initialized = True
        self.images_loaded = False
        self.ocr_processing = False
        self.ocr_complete = False
        self.cooldown_complete = True

        # Export success message flag
        self.show_export_message = False
        self.export_message_time = 0

    def draw_left_frame(self, frame, width, height):
        """Draw frame kiri dengan teks 'Selamat Datang' + 4 tombol + queue info + hasil."""
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
            if time.time() - self.export_message_time > 2:
                self.show_export_message = False
            else:
                msg = "✓ Export Berhasil!"
                msg_font_scale = min(width, height) / 600
                msg_thickness = max(1, int(msg_font_scale * 2))

                (msg_w, msg_h), _ = cv2.getTextSize(
                    msg, cv2.FONT_HERSHEY_SIMPLEX, msg_font_scale, msg_thickness
                )
                msg_x = (width - msg_w) // 2
                msg_y = text_y + 50

                cv2.rectangle(frame,
                             (msg_x - 20, msg_y - msg_h - 10),
                             (msg_x + msg_w + 20, msg_y + 10),
                             (76, 175, 80), -1)

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

        # Draw image queue info
        self.draw_queue_info(frame, width, height, start_y + button_height + 20)

        # Draw hasil deteksi panel
        self.draw_result_panel(frame, width, height, start_y + button_height + 60)

    def draw_queue_info(self, frame, width, height, y_start):
        """Draw image queue info dengan list semua gambar."""
        margin = 10
        
        # Get queue info from widget - PERBAIKAN: gunakan widget.images
        if self.widget:
            images = self.widget.images
            total = len(images)
            completed = sum(1 for img in images if img.get('status') == 'completed')
            pending = sum(1 for img in images if img.get('status') == 'pending')
            failed = sum(1 for img in images if img.get('status') == 'failed')
            
            # Draw header
            info_text = f"Queue: {total} images | ✓: {completed} | ⏳: {pending} | ✗: {failed}"
            
            cv2.rectangle(frame, (margin, y_start),
                         (width - margin, y_start + 35), (240, 240, 240), -1)
            cv2.rectangle(frame, (margin, y_start),
                         (width - margin, y_start + 35), (128, 128, 128), 2)
            
            cv2.putText(frame, info_text, (margin + 10, y_start + 23),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 100, 255), 1)
            
            # Draw image list jika ada gambar
            if total > 0:
                list_y = y_start + 45
                item_height = 28
                max_items = 6  # Max items to display
                
                # Draw background for list
                list_height = min(total, max_items) * item_height + 10
                cv2.rectangle(frame, (margin, list_y),
                             (width - margin, list_y + list_height), (250, 250, 250), -1)
                cv2.rectangle(frame, (margin, list_y),
                             (width - margin, list_y + list_height), (180, 180, 180), 1)
                
                # Draw each image item
                for i in range(min(total, max_items)):
                    img_data = images[i]
                    y_pos = list_y + 8 + (i * item_height)
                    
                    # Status icon
                    status = img_data.get('status', 'pending')
                    if status == 'completed':
                        status_icon = "✓"
                        status_color = (0, 200, 0)
                    elif status == 'processing':
                        status_icon = "⏳"
                        status_color = (0, 165, 255)
                    elif status == 'failed':
                        status_icon = "✗"
                        status_color = (0, 0, 255)
                    else:
                        status_icon = "○"
                        status_color = (128, 128, 128)
                    
                    # Highlight current showing image
                    if i == self.showing_image_index:
                        cv2.rectangle(frame, (margin + 3, y_pos - 18),
                                     (width - margin - 3, y_pos + 8), (200, 230, 255), -1)
                    
                    # Draw status
                    cv2.putText(frame, status_icon, (margin + 8, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)
                    
                    # Draw filename (truncated)
                    filename = img_data.get('filename', 'Unknown')
                    max_chars = (width - 80) // 8
                    if len(filename) > max_chars:
                        filename = filename[:max_chars-3] + "..."
                    
                    cv2.putText(frame, f"{i+1}. {filename}", (margin + 28, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                    
                    # Draw texts count if completed
                    if status == 'completed' and img_data.get('result'):
                        texts_count = img_data['result'].get('total_texts', 0)
                        texts_text = f"{texts_count} texts"
                        (texts_w, _), _ = cv2.getTextSize(texts_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                        cv2.putText(frame, texts_text, (width - margin - texts_w - 10, y_pos),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 128, 0), 1)
                
                # Show "and more" if needed
                if total > max_items:
                    more_text = f"... and {total - max_items} more"
                    cv2.putText(frame, more_text, (margin + 10, list_y + list_height + 18),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (128, 128, 128), 1)

    def draw_result_panel(self, frame, width, height, y_start):
        """Draw panel hasil deteksi - menampilkan hasil dari gambar yang dipilih."""
        panel_y = y_start
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
            self.draw_loading_indicator(frame, width, panel_y, panel_height, margin)
            return

        # Check error
        if self.ocr_error:
            error_text = f"Error: {self.ocr_error}"
            cv2.putText(frame, error_text, (margin + 10, panel_y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            return

        # Check result - PERBAIKAN: gunakan widget.images dan showing_image_index
        if not self.widget or not self.widget.images or len(self.widget.images) == 0:
            info = "Belum ada gambar. Klik 'Open' untuk menambah."
            cv2.putText(frame, info, (margin + 10, panel_y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
            return

        # Get current image to display - PERBAIKAN: check dengan int()
        try:
            showing_idx = int(self.showing_image_index) if self.showing_image_index is not None else -1
        except (TypeError, ValueError):
            showing_idx = -1
        
        if showing_idx < 0 or showing_idx >= len(self.widget.images):
            info = "Pilih gambar dari list untuk melihat hasil"
            cv2.putText(frame, info, (margin + 10, panel_y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
            return

        img_data = self.widget.images[showing_idx]
        
        # Check if image has result
        if not img_data.get('result'):
            if img_data['status'] == 'pending':
                info = "Image belum diproses. Klik 'Detect All'."
            elif img_data['status'] == 'processing':
                info = "Sedang memproses..."
            elif img_data['status'] == 'failed':
                info = f"Failed: {img_data.get('error', 'Unknown error')}"
            else:
                info = "No result available"
            
            cv2.putText(frame, info, (margin + 10, panel_y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
            return

        # Get result
        result = img_data['result']
        texts = result.get('texts', [])
        total = len(texts)
        plate = result.get('plate', None)

        # Show image info
        img_filename = result.get('image_filename', img_data.get('filename', 'N/A'))
        img_info = f"Image {self.showing_image_index + 1}: {img_filename} | Total: {total} teks"
        if plate:
            img_info += f" | Plate: {plate}"
        
        cv2.putText(frame, img_info, (margin + 10, panel_y + 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 100, 255), 1)

        # Draw texts
        max_display = 15
        line_height = 25
        start_idx = 0

        if total > max_display:
            start_idx = total - max_display

        display_texts = texts[start_idx:start_idx + max_display]

        for i, text_item in enumerate(display_texts, start_idx):
            if isinstance(text_item, dict):
                text = text_item['text']
                conf = text_item['confidence']
            else:
                text = str(text_item)
                conf = 0.0

            max_chars = (width - 60) // 9
            if len(text) > max_chars:
                text = text[:max_chars-3] + "..."

            y_pos = panel_y + 85 + ((i - start_idx) * line_height)

            color = (255, 255, 255) if i % 2 == 0 else (230, 230, 230)
            cv2.rectangle(frame, (margin + 5, y_pos - 18),
                         (width - margin - 5, y_pos + 5), color, -1)

            label = f"{i+1}. {text}"
            cv2.putText(frame, label, (margin + 10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

            conf_label = f"({conf:.2f})"
            (conf_w, _), _ = cv2.getTextSize(conf_label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.putText(frame, conf_label, (width - margin - conf_w - 15, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 128, 0), 1)

    def draw_loading_indicator(self, frame, width, panel_y, panel_height, margin):
        """Draw loading indicator."""
        elapsed = time.time() - self.loading_start_time
        center_x = width // 2
        start_y = panel_y + 80

        # Get progress from widget
        if self.widget.gui:
            processed = sum(1 for img in self.widget.gui.images if img.get('status') in ['completed', 'failed'])
            total = len(self.widget.gui.images)
            progress_text = f"⏳ Processing... ({processed}/{total})"
        else:
            progress_text = "⏳ Processing..."

        (text_w, text_h), _ = cv2.getTextSize(progress_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        text_x = center_x - text_w // 2
        cv2.putText(frame, progress_text, (text_x, start_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        time_text = f"⏱️  Elapsed: {elapsed:.1f}s"
        (time_w, _), _ = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        time_x = center_x - time_w // 2
        cv2.putText(frame, time_text, (time_x, start_y + 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)

        # Progress bar
        bar_width = 400
        bar_height = 25
        bar_x = center_x - bar_width // 2
        bar_y = start_y + 70

        cv2.rectangle(frame, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height), (200, 200, 200), -1)
        cv2.rectangle(frame, (bar_x, bar_y),
                     (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), 2)

        if self.widget.gui and len(self.widget.gui.images) > 0:
            processed = sum(1 for img in self.widget.gui.images if img.get('status') in ['completed', 'failed'])
            progress = processed / len(self.widget.gui.images)
            fill_width = int(bar_width * progress)
            cv2.rectangle(frame, (bar_x + 2, bar_y + 2),
                         (bar_x + fill_width - 2, bar_y + bar_height - 2), (0, 255, 0), -1)

            percent_text = f"{int(progress * 100)}%"
            (pct_w, _), _ = cv2.getTextSize(percent_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            pct_x = center_x - pct_w // 2
            cv2.putText(frame, percent_text, (pct_x, bar_y + bar_height + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 128, 0), 2)

    def draw_right_frame(self, frame, start_x, width, height, ocr_frame=None):
        """Draw frame kanan dengan preview image."""
        if ocr_frame is not None:
            try:
                ocr_resized = cv2.resize(ocr_frame, (width, height))
                frame[:height, start_x:start_x + width] = ocr_resized
            except Exception as e:
                print(f"[WARNING] Cannot resize preview: {e}")
                cv2.rectangle(frame, (start_x, 0), (start_x + width, height), (128, 128, 128), -1)
                text = "Preview Error"
                cv2.putText(frame, text, (start_x + 10, height // 2),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            cv2.rectangle(frame, (start_x, 0), (start_x + width, height), (128, 128, 128), -1)
            text = "No Image Preview"
            cv2.putText(frame, text, (start_x + 10, height // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    def draw(self, frame, ocr_frame=None):
        """Draw semua UI elements."""
        height, width = frame.shape[:2]
        half_width = width // 2

        self.draw_left_frame(frame[:, :half_width], half_width, height)
        self.draw_right_frame(frame, half_width, half_width, height, ocr_frame)

        cv2.line(frame, (half_width, 0), (half_width, height), (255, 255, 255), 2)

    def open_image(self):
        """Open file dialog untuk pilih MULTIPLE images - DENGAN LENGKAP LOG."""
        print("\n" + "="*70)
        print("  [OPEN] OPEN BUTTON CLICKED")
        print("="*70)
        print(f"[OPEN] Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[OPEN] Current queue size: {len(self.widget.images) if self.widget.gui else 0}")
        
        # Use existing tk_root
        print("[OPEN] Preparing file dialog...")
        self.tk_root.update()
        self.tk_root.focus_force()
        self.tk_root.attributes('-topmost', True)
        self.tk_root.after(100, lambda: self.tk_root.attributes('-topmost', False))
        
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("All files", "*.*")
        ]

        print("[OPEN] Showing file dialog...")
        print("[OPEN] Supported formats: JPG, JPEG, PNG, BMP, TIFF, WEBP")
        
        filepaths = filedialog.askopenfilenames(
            title="Select Multiple Images",
            filetypes=filetypes,
            parent=self.tk_root
        )

        print(f"[OPEN] Files selected: {len(filepaths) if filepaths else 0}")
        
        if filepaths:
            print("\n[OPEN] File list:")
            for i, path in enumerate(filepaths, 1):
                filename = os.path.basename(path)
                size = os.path.getsize(path) / 1024  # KB
                print(f"  [{i}] {filename} ({size:.1f} KB)")
                print(f"      Path: {path}")
            
            # Add multiple images to widget queue
            print(f"\n[OPEN] Adding {len(filepaths)} images to queue...")
            count = self.widget.add_images(list(filepaths))
            self.images_loaded = True

            # Set first image as current preview
            if count > 0 and self.current_index < 0:
                self.current_index = 0
                self.show_preview_image()
                print(f"[OPEN] Set preview to image #{self.current_index + 1}")

            print(f"\n[OK] Added {count} images to queue")
            print(f"[OK] New queue size: {len(self.widget.images)}")
            print(f"[OK] Queue status: {sum(1 for img in self.widget.images if img['status'] == 'pending')} pending")
            print("="*70)
            return True
        else:
            print("[OPEN] No files selected (user canceled)")
            print("="*70)

        return False

    def show_preview_image(self):
        """Show preview of current selected image - PERBAIKAN."""
        # Update showing_image_index to match current_index - ensure int
        try:
            current_idx = int(self.current_index) if self.current_index is not None else -1
        except (TypeError, ValueError):
            current_idx = -1
        
        if current_idx >= 0 and self.widget and current_idx < len(self.widget.images):
            self.showing_image_index = current_idx  # Already int
            img_data = self.widget.images[current_idx]
            if img_data and 'image' in img_data:
                self.current_image = img_data['image']
                self.current_image_path = img_data['path']
                print(f"[INFO] Preview: {img_data['filename']}")

    def detect_text(self):
        """Detect text dari SEMUA images dalam queue - DENGAN LENGKAP LOG."""
        print("\n" + "="*70)
        print("  [DETECT] DETECT ALL BUTTON CLICKED")
        print("="*70)
        print(f"[DETECT] Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check queue - PERBAIKAN: cek widget.images bukan widget.gui.images
        if not self.widget or not self.widget.images:
            print("[WARNING] No images in queue!")
            print("[WARNING] Please click 'Open' first to add images")
            print("="*70)
            return
        
        # Check if already processing
        if self.ocr_thread and self.ocr_thread.is_alive():
            print("[WARNING] OCR already running!")
            print("[WARNING] Please wait for current processing to complete")
            print("="*70)
            return
        
        # Show queue info - PERBAIKAN: gunakan widget.images
        queue = self.widget.images
        total = len(queue)
        pending = sum(1 for img in queue if img['status'] == 'pending')
        completed = sum(1 for img in queue if img['status'] == 'completed')
        failed = sum(1 for img in queue if img['status'] == 'failed')
        
        print(f"[DETECT] Queue information:")
        print(f"  - Total images: {total}")
        print(f"  - Pending: {pending}")
        print(f"  - Completed: {completed}")
        print(f"  - Failed: {failed}")
        
        # Clear previous results
        print(f"\n[DETECT] Clearing previous results...")
        self.ocr_result = None
        self.ocr_error = None
        print(f"[DETECT] Previous results cleared")
        
        # Set state flags
        print(f"\n[DETECT] Setting state flags...")
        self.ocr_processing = True
        self.ocr_complete = False
        self.cooldown_complete = False
        self.is_loading = True
        self.loading_start_time = time.time()
        print(f"  - ocr_processing: True")
        print(f"  - ocr_complete: False")
        print(f"  - is_loading: True")
        
        print(f"\n[DETECT] Starting batch processing...")
        print(f"  - Images to process: {total}")
        print(f"  - Estimated time: ~{total * 5} seconds ({total} images × ~5s each)")
        
        # Start OCR thread
        self.ocr_thread = threading.Thread(target=self._ocr_worker)
        self.ocr_thread.daemon = True
        self.ocr_thread.start()
        
        print(f"\n[OK] OCR thread started (ID: {self.ocr_thread.ident})")
        print(f"[OK] Processing in background...")
        print("="*70)

    def _ocr_worker(self):
        """OCR worker thread untuk batch processing - DENGAN LENGKAP LOG."""
        thread_id = threading.current_thread().ident
        
        print("\n" + "="*70)
        print(f"  [THREAD {thread_id}] OCR PROCESSING STARTED")
        print("="*70)
        print(f"[THREAD] Thread ID: {thread_id}")
        print(f"[THREAD] Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[THREAD] Images to process: {len(self.widget.images) if self.widget else 0}")
        print("="*70)

        try:
            # Process all images - PERBAIKAN: gunakan widget.images
            print(f"\n[THREAD] Calling widget.process_all()...")
            results = self.widget.process_all()
            
            print(f"\n[THREAD] Processing complete!")
            print(f"[THREAD] Total results: {len(results)}")

            # Set first completed image as current result for preview - PERBAIKAN
            print(f"\n[THREAD] Setting preview to first completed image...")
            for i, img_data in enumerate(self.widget.images):
                if img_data['status'] == 'completed' and img_data.get('result'):
                    self.current_index = i
                    self.ocr_result = img_data['result']
                    self.show_preview_image()
                    print(f"[THREAD] Set preview to image #{i+1}: {img_data['filename']}")
                    break

            # Show detailed results - PERBAIKAN: gunakan widget.images
            print(f"\n{'='*70}")
            print(f"[THREAD] BATCH PROCESSING RESULTS")
            print(f"{'='*70}")
            
            completed_count = sum(1 for img in self.widget.images if img['status'] == 'completed')
            failed_count = sum(1 for img in self.widget.images if img['status'] == 'failed')
            
            print(f"\n[SUMMARY] Processing Summary:")
            print(f"  - Total images: {len(self.widget.images)}")
            print(f"  - Completed: {completed_count} ✓")
            print(f"  - Failed: {failed_count} ✗")
            print(f"  - Success rate: {(completed_count/len(self.widget.images)*100):.1f}%")
            
            # Show per-image results
            print(f"\n[RESULTS] Per-image Results:")
            for i, img_data in enumerate(self.widget.images, 1):
                status_icon = "✓" if img_data['status'] == 'completed' else "✗" if img_data['status'] == 'failed' else "○"
                if img_data['status'] == 'completed' and img_data.get('result'):
                    result = img_data['result']
                    texts_count = result.get('total_texts', 0)
                    plate = result.get('plate', 'N/A')
                    print(f"  [{i}] {img_data['filename']} {status_icon}")
                    print(f"      - Texts detected: {texts_count}")
                    if plate != 'N/A':
                        print(f"      - Plate detected: {plate}")
                else:
                    print(f"  [{i}] {img_data['filename']} {status_icon}")
                    if img_data.get('error'):
                        print(f"      - Error: {img_data['error'][:50]}...")

            print(f"\n[SUCCESS] Batch processing complete!")
            print(f"{'='*70}")

        except Exception as e:
            import traceback
            self.ocr_error = str(e)
            error_traceback = traceback.format_exc()
            
            print(f"\n{'='*70}")
            print(f"[THREAD {thread_id}] [ERROR] OCR FAILED!")
            print(f"{'='*70}")
            print(f"[ERROR] Error type: {type(e).__name__}")
            print(f"[ERROR] Error message: {e}")
            print(f"[ERROR] Traceback:\n{error_traceback}")
            print(f"{'='*70}")
            
        finally:
            elapsed = time.time() - self.loading_start_time
            self.is_loading = False
            self.ocr_processing = False
            self.cooldown_complete = True

            print(f"\n{'='*70}")
            print(f"[THREAD {thread_id}] CLEANUP")
            print(f"{'='*70}")
            print(f"[THREAD] Elapsed time: {elapsed:.2f}s")
            print(f"[THREAD] Setting flags:")
            print(f"  - is_loading: False")
            print(f"  - ocr_processing: False")
            print(f"  - cooldown_complete: True")
            print(f"[THREAD] Ready for next operation")
            print(f"{'='*70}")

    def export_result(self):
        """Export hasil OCR dari semua images - DENGAN LENGKAP LOG."""
        print("\n" + "="*70)
        print("  [EXPORT] EXPORT BUTTON CLICKED")
        print("="*70)
        print(f"[EXPORT] Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if there are results - PERBAIKAN: gunakan widget.images
        if not self.widget:
            print("[WARNING] Widget not initialized!")
            print("[EXPORT] Export cancelled")
            print("="*70)
            return
        
        # Check for results
        results = [img for img in self.widget.images if img.get('result')]
        
        if not results:
            print("[WARNING] No results to export!")
            print("[WARNING] Please click 'Detect All' first")
            print("[EXPORT] Export cancelled")
            print("="*70)
            return
        
        # Get batch info
        print(f"\n[EXPORT] Analyzing data...")
        total_images = len(results)
        total_texts = sum(len(r['result'].get('texts', [])) for r in results if r.get('result'))
        total_plates = sum(1 for r in results if r.get('result') and r['result'].get('plate'))
        
        print(f"[EXPORT] Data available:")
        print(f"  - Total images processed: {total_images}")
        print(f"  - Total texts detected: {total_texts}")
        print(f"  - License plates detected: {total_plates}")
        
        # Show per-image summary
        print(f"\n[EXPORT] Images to export:")
        for i, img_data in enumerate(results, 1):
            if img_data.get('result'):
                result = img_data['result']
                filename = result.get('image_filename', 'N/A')
                texts = result.get('total_texts', 0)
                plate = result.get('plate', 'N/A')
                print(f"  [{i}] {filename}")
                print(f"      - Texts: {texts}")
                if plate != 'N/A':
                    print(f"      - Plate: {plate}")
        
        # Export batch
        print(f"\n[EXPORT] Exporting batch results...")
        print(f"[EXPORT] Formats: TXT + JSON")
        
        try:
            txt_path, json_path = self.widget.export_batch()
            
            # Get file sizes
            txt_size = os.path.getsize(txt_path)
            json_size = os.path.getsize(json_path)
            
            print(f"\n[OK] Export successful!")
            print(f"[OK] Files created:")
            print(f"  ✓ TXT: {txt_path}")
            print(f"      Size: {txt_size:,} bytes ({txt_size/1024:.1f} KB)")
            print(f"  ✓ JSON: {json_path}")
            print(f"      Size: {json_size:,} bytes ({json_size/1024:.1f} KB)")
            
        except Exception as e:
            print(f"\n[ERROR] Export failed!")
            print(f"[ERROR] Error: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            print("="*70)
            return

        print(f"\n[EXPORT] Export completed successfully")
        print(f"[EXPORT] Files saved to: output/")
        print("="*70)

        # Show success message
        self.show_export_message = True
        self.export_message_time = time.time()

    def clear_all(self):
        """Clear semua data - DENGAN LENGKAP LOG."""
        print("\n" + "="*70)
        print("  [CLEAR] CLEAR BUTTON CLICKED")
        print("="*70)
        print(f"[CLEAR] Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show current state - PERBAIKAN: gunakan widget.images
        if self.widget:
            queue_size = len(self.widget.images)
            completed = sum(1 for img in self.widget.images if img.get('status') == 'completed')
            pending = sum(1 for img in self.widget.images if img.get('status') == 'pending')

            print(f"[CLEAR] Current state:")
            print(f"  - Images in queue: {queue_size}")
            print(f"  - Completed: {completed}")
            print(f"  - Pending: {pending}")

            # Check ocr_result safely
            if self.ocr_result is not None and isinstance(self.ocr_result, dict):
                texts = self.ocr_result.get('total_texts', 0)
                print(f"  - Current result texts: {texts}")
        
        print(f"\n[CLEAR] Clearing all data...")
        
        # Clear widget data
        print(f"[CLEAR] Clearing widget queue...")
        self.widget.clear_all()
        
        # Clear app state
        print(f"[CLEAR] Clearing app state...")
        self.current_image = None
        self.current_image_path = None
        self.current_index = -1
        self.ocr_result = None
        self.ocr_error = None
        self.is_loading = False
        
        # Clear flags
        print(f"[CLEAR] Resetting flags...")
        self.images_loaded = False
        self.ocr_processing = False
        self.ocr_complete = False
        self.cooldown_complete = True
        
        print(f"  - images_loaded: {self.images_loaded}")
        print(f"  - ocr_processing: {self.ocr_processing}")
        print(f"  - ocr_complete: {self.ocr_complete}")
        print(f"  - cooldown_complete: {self.cooldown_complete}")
        print(f"  - showing_image_index: {self.showing_image_index} (type: {type(self.showing_image_index)})")
        print(f"  - current_index: {self.current_index} (type: {type(self.current_index)})")
        
        # Verify cleared - PERBAIKAN: gunakan widget.images
        print(f"\n[CLEAR] Verifying clear...")
        final_queue_size = len(self.widget.images) if self.widget else 0
        print(f"[CLEAR] Final queue size: {final_queue_size}")
        
        print(f"\n[OK] All data cleared successfully")
        print(f"[CLEAR] Ready for new operation")
        print("="*70)

    def on_mouse_click(self, event, x, y, flags, param):
        """Handle mouse click events - DENGAN NAVIGASI IMAGE LIST."""
        if event == cv2.EVENT_LBUTTONDOWN:
            half_width = self.window_width // 2

            # Left frame clicks
            if x < half_width:
                # Check image list click (untuk navigasi)
                if self.widget and self.widget.images and len(self.widget.images) > 0:
                    # Calculate list area
                    list_start_y = self.window_height // 4 + 50  # After buttons
                    item_height = 28
                    max_items = 6
                    
                    # Check if click is in list area
                    if y > list_start_y and y < list_start_y + (max_items * item_height) + 50:
                        # Calculate which item was clicked
                        item_index = (y - list_start_y - 8) // item_height
                        if 0 <= item_index < len(self.widget.images):
                            # Select this image - PERBAIKAN: ensure int
                            self.showing_image_index = int(item_index)
                            self.current_index = int(item_index)
                            
                            # Update preview
                            self.show_preview_image()
                            
                            print(f"[NAVIGATION] Showing image {item_index + 1}: {self.widget.images[item_index]['filename']}")
                
                # Button clicks
                for i, button in enumerate(self.buttons):
                    if button.is_clicked(x, y):
                        print(f"\n[CLICK] Button {i+1}: {button.text}")
                        if i == 0:
                            self.open_image()
                        elif i == 1:
                            self.detect_text()
                        elif i == 2:
                            self.export_result()
                        elif i == 3:
                            self.clear_all()
                        break

    def run(self):
        """Run aplikasi - DENGAN ERROR HANDLING LENGKAP."""
        print("\n" + "="*60)
        print("Aplikasi Python - Multiple Image OCR")
        print("="*60)
        print("\nLayout:")
        print("  - Frame Kiri: Controls + Queue Info + Results")
        print("  - Frame Kanan: Image Preview dengan Bounding Boxes")
        print("\nFeatures:")
        print("  - ✅ MULTIPLE image upload")
        print("  - ✅ Batch OCR processing")
        print("  - ✅ Queue status tracking")
        print("  - ✅ Export TXT + JSON")
        print("\nControls:")
        print("  - Click tombol untuk aksi")
        print("  - 'o' - Open images (multiple)")
        print("  - 'd' - Detect all")
        print("  - 'e' - Export results")
        print("  - 'c' - Clear all")
        print("  - 'q' / ESC - Quit")
        print("="*60 + "\n")

        # Create OpenCV window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.window_width, self.window_height)
        cv2.setMouseCallback(self.window_name, self.on_mouse_click)

        try:
            while True:
                try:
                    frame = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)

                    # Get preview frame - PERBAIKAN: gunakan showing_image_index
                    preview_frame = None
                    
                    # Set showing_image_index if not set - PERBAIKAN: check dengan int()
                    try:
                        showing_idx = int(self.showing_image_index) if self.showing_image_index is not None else -1
                    except (TypeError, ValueError, AttributeError) as e:
                        print(f"[DEBUG] showing_image_index error: {e}, value: {self.showing_image_index}")
                        showing_idx = -1
                    
                    if showing_idx < 0 and self.widget and self.widget.images and len(self.widget.images) > 0:
                        self.showing_image_index = 0  # Set to first image (int)
                        self.current_index = 0  # Set to first image (int)
                        showing_idx = 0
                    
                    # Get preview from current showing image
                    if showing_idx >= 0 and self.widget and showing_idx < len(self.widget.images):
                        img_data = self.widget.images[showing_idx]
                        display_frame = img_data.get('display_frame')
                        image = img_data.get('image')
                        
                        if display_frame is not None:
                            preview_frame = display_frame
                        elif image is not None:
                            preview_frame = image

                    self.draw(frame, preview_frame)
                    cv2.imshow(self.window_name, frame)
                    
                except Exception as frame_error:
                    print(f"\n[ERROR] Frame rendering error: {frame_error}")
                    print(f"[ERROR] Type: {type(frame_error).__name__}")
                    import traceback
                    traceback.print_exc()
                    # Continue running, skip this frame
                    continue

                key = cv2.waitKey(10) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('o'):
                    self.open_image()
                elif key == ord('d'):
                    self.detect_text()
                elif key == ord('e'):
                    self.export_result()
                elif key == ord('c'):
                    self.clear_all()
                elif key == 27:
                    break

        except Exception as e:
            print(f"\n{'='*60}")
            print(f"[FATAL ERROR] {e}")
            print(f"[ERROR TYPE] {type(e).__name__}")
            print(f"{'='*60}")
            import traceback
            traceback.print_exc()
        finally:
            self.widget.clear_all()
            self.tk_root.destroy()
            cv2.destroyAllWindows()
            print("\n[OK] Application closed")


def main():
    """Main function."""
    app = ResponsiveApp(window_width=1280, window_height=700)
    app.run()


if __name__ == "__main__":
    main()
