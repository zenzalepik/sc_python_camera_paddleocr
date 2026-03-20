"""
Aplikasi Python - Multiple Image OCR dengan Grid View Layout
- Layout optimized untuk batch processing banyak gambar
- Grid thumbnail display untuk overview semua gambar
- Detail panel untuk gambar yang dipilih
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

# Import PaddleOCR Multiple Engine (MENGGUNAKAN ENGINE YANG SAMA!)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "paddleocr_multiple_engine"))
from paddleocr_multiple_engine import PaddleOCRMultipleEngine


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

        cv2.rectangle(frame, (x, y), (x + width, y + height), self.color, -1)
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 255), 2)

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
    """Aplikasi dengan Grid View Layout untuk Multiple Image Processing."""

    def __init__(self, window_width=1400, window_height=800):
        self.window_width = window_width
        self.window_height = window_height
        self.window_name = "Multiple Image OCR - Grid View"

        # Initialize buttons
        self.buttons = [
            Button("Open", color=(0, 120, 255)),
            Button("Detect All", color=(0, 180, 0)),
            Button("Export", color=(255, 100, 0)),
            Button("Clear", color=(200, 0, 200)),
        ]

        # Initialize Tkinter root
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()

        # Initialize PaddleOCR Multiple Engine (MENGGUNAKAN ENGINE YANG SAMA!)
        self.engine = PaddleOCRMultipleEngine()  # Tidak perlu root

        # State variables
        self.current_image = None
        self.current_image_path = None
        self.selected_index = -1  # Selected image in grid
        self.grid_scroll_offset = 0  # Grid scroll position

        # Mouse callback
        self.mouse_callback = None

        # Loading state
        self.is_loading = False
        self.loading_start_time = 0
        self.ocr_error = None
        self.ocr_thread = None

        # Export message
        self.show_export_message = False
        self.export_message_time = 0

    def draw_top_bar(self, frame, width, height):
        """Draw top bar dengan buttons dan queue info."""
        bar_height = 80
        
        # Background
        cv2.rectangle(frame, (0, 0), (width, bar_height), (30, 30, 30), -1)
        
        # Draw buttons
        button_width = 140
        button_height = 50
        button_spacing = 20
        start_x = 20
        start_y = 15
        
        for i, button in enumerate(self.buttons):
            btn_x = start_x + i * (button_width + button_spacing)
            btn_y = start_y
            button.draw(frame, btn_x, btn_y, button_width, button_height, 0.7)
        
        # Draw queue info
        if self.engine and self.engine.images:
            total = len(self.engine.images)
            completed = sum(1 for img in self.engine.images if img.get('status') == 'completed')
            processing = sum(1 for img in self.engine.images if img.get('status') == 'processing')
            failed = sum(1 for img in self.engine.images if img.get('status') == 'failed')
            
            info_text = f"Queue: {total} | ✓:{completed} ⏳:{processing} ✗:{failed}"
            cv2.putText(frame, info_text, (width - 350, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Progress bar
            progress_width = 300
            progress_height = 20
            progress_x = width - 350
            progress_y = 50
            
            cv2.rectangle(frame, (progress_x, progress_y),
                         (progress_x + progress_width, progress_y + progress_height), 
                         (100, 100, 100), -1)
            
            if total > 0:
                fill_width = int(progress_width * completed / total)
                cv2.rectangle(frame, (progress_x, progress_y),
                             (progress_x + fill_width, progress_y + progress_height), 
                             (0, 255, 0), -1)
                
                percent = int(completed / total * 100)
                cv2.putText(frame, f"{percent}%", (progress_x + progress_width + 10, progress_y + 18),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Export success message
        if self.show_export_message:
            if time.time() - self.export_message_time > 2:
                self.show_export_message = False
            else:
                msg = "✓ Export Berhasil!"
                cv2.putText(frame, msg, (width // 2 - 100, bar_height - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def draw_grid(self, frame, width, height):
        """Draw grid thumbnail untuk semua gambar."""
        grid_start_y = 80
        grid_height = height * 0.45  # 45% dari height untuk grid
        margin = 10
        
        if not self.engine or not self.engine.images:
            # No images message
            msg = "No images loaded. Click 'Open' to add images."
            cv2.putText(frame, msg, (width // 2 - 250, grid_start_y + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (128, 128, 128), 2)
            return
        
        # Calculate grid layout
        total_images = len(self.engine.images)
        cols = 5
        rows = (total_images + cols - 1) // cols
        
        thumb_width = (width - margin * (cols + 1)) // cols
        thumb_height = int((grid_height - margin * (rows + 1)) // rows)
        
        # Draw thumbnails
        for i, img_data in enumerate(self.engine.images):
            col = i % cols
            row = i // cols
            
            x = margin + col * (thumb_width + margin)
            y = grid_start_y + margin + row * (thumb_height + margin)
            
            # Draw thumbnail background
            cv2.rectangle(frame, (x, y), (x + thumb_width, y + thumb_height), 
                         (40, 40, 40), -1)
            cv2.rectangle(frame, (x, y), (x + thumb_width, y + thumb_height), 
                         (100, 100, 100), 1)
            
            # Highlight selected
            if i == self.selected_index:
                cv2.rectangle(frame, (x, y), (x + thumb_width, y + thumb_height), 
                             (0, 255, 255), 3)
            
            # Draw image or placeholder
            image = img_data.get('image')
            if image is not None:
                # Resize image to fit thumbnail
                try:
                    thumb_img = cv2.resize(image, (thumb_width - 10, thumb_height - 40))
                    frame[y+5:y+thumb_height-35, x+5:x+thumb_width-5] = thumb_img
                except:
                    pass
            
            # Draw status overlay
            status = img_data.get('status', 'pending')
            status_icon = "○"
            status_color = (128, 128, 128)
            
            if status == 'completed':
                status_icon = "✓"
                status_color = (0, 255, 0)
            elif status == 'processing':
                status_icon = "⏳"
                status_color = (0, 165, 255)
            elif status == 'failed':
                status_icon = "✗"
                status_color = (0, 0, 255)
            
            # Status badge
            cv2.circle(frame, (x + thumb_width - 20, y + 20), 12, status_color, -1)
            cv2.putText(frame, status_icon, (x + thumb_width - 25, y + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw filename (truncated)
            filename = img_data.get('filename', 'Unknown')
            if len(filename) > 20:
                filename = filename[:17] + "..."
            cv2.putText(frame, filename, (x + 5, y + thumb_height - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            
            # Draw text count if completed
            if status == 'completed' and img_data.get('result'):
                texts_count = img_data['result'].get('total_texts', 0)
                cv2.putText(frame, f"{texts_count}t", (x + 5, y + thumb_height - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
            # Draw index
            cv2.putText(frame, f"#{i+1}", (x + 5, y + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def draw_detail_panel(self, frame, width, height):
        """Draw detail panel untuk gambar yang dipilih."""
        panel_start_y = int(height * 0.55)
        panel_height = height - panel_start_y - 30
        margin = 10
        
        # Background
        cv2.rectangle(frame, (margin, panel_start_y),
                     (width - margin, height - 20), (35, 35, 35), -1)
        cv2.rectangle(frame, (margin, panel_start_y),
                     (width - margin, height - 20), (80, 80, 80), 2)
        
        # Check if image selected
        if self.selected_index < 0 or not self.engine or self.selected_index >= len(self.engine.images):
            msg = "Select an image from the grid to view details"
            cv2.putText(frame, msg, (width // 2 - 250, panel_start_y + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
            return
        
        img_data = self.engine.images[self.selected_index]
        result = img_data.get('result')
        
        # Draw header
        filename = img_data.get('filename', 'Unknown')
        header_text = f"Image #{self.selected_index + 1}: {filename}"
        cv2.putText(frame, header_text, (margin + 15, panel_start_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw status
        status = img_data.get('status', 'pending')
        status_text = f"Status: {status.upper()}"
        cv2.putText(frame, status_text, (width - 200, panel_start_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Check if has result
        if not result:
            if status == 'pending':
                msg = "Image not processed yet. Click 'Detect All'."
            elif status == 'processing':
                msg = "Processing..."
            elif status == 'failed':
                msg = f"Failed: {img_data.get('error', 'Unknown error')}"
            else:
                msg = "No result available"
            
            cv2.putText(frame, msg, (margin + 15, panel_start_y + 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 1)
            return
        
        # Draw results
        texts = result.get('texts', [])
        plate = result.get('plate', None)
        
        info_y = panel_start_y + 70
        
        # Text count
        cv2.putText(frame, f"Total Texts: {len(texts)}", (margin + 15, info_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Plate info
        if plate:
            cv2.putText(frame, f"Plate: {plate}", (margin + 200, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Draw text list
        list_y = info_y + 40
        line_height = 25
        max_display = min(len(texts), 15)
        
        for i in range(max_display):
            text_item = texts[i]
            text = text_item.get('text', '')
            conf = text_item.get('confidence', 0)
            
            # Truncate long text
            if len(text) > 80:
                text = text[:77] + "..."
            
            y_pos = list_y + i * line_height
            
            # Background
            cv2.rectangle(frame, (margin + 10, y_pos - 18),
                         (width - margin - 10, y_pos + 5), (50, 50, 50), -1)
            
            # Text
            label = f"{i+1}. {text}"
            cv2.putText(frame, label, (margin + 15, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Confidence
            conf_label = f"({conf:.2f})"
            cv2.putText(frame, conf_label, (width - 100, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        if len(texts) > max_display:
            more_text = f"... and {len(texts) - max_display} more texts"
            cv2.putText(frame, more_text, (margin + 15, list_y + max_display * line_height + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)

    def draw(self, frame):
        """Draw semua UI elements."""
        self.draw_top_bar(frame, self.window_width, 80)
        self.draw_grid(frame, self.window_width, self.window_height)
        self.draw_detail_panel(frame, self.window_width, self.window_height)

    def open_image(self):
        """Open file dialog untuk pilih MULTIPLE images."""
        print("\n" + "="*70)
        print("  [OPEN] OPEN BUTTON CLICKED")
        print("="*70)
        
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("All files", "*.*")
        ]

        filepaths = filedialog.askopenfilenames(
            title="Select Multiple Images",
            filetypes=filetypes,
            parent=self.tk_root
        )

        if filepaths:
            print(f"\n[OPEN] Files selected: {len(filepaths)}")
            for i, path in enumerate(filepaths, 1):
                filename = os.path.basename(path)
                size = os.path.getsize(path) / 1024
                print(f"  [{i}] {filename} ({size:.1f} KB)")
            
            count = self.engine.add_images(list(filepaths))
            
            # Auto-select first image
            if count > 0 and self.selected_index < 0:
                self.selected_index = 0
            
            print(f"\n[OK] Added {count} images to queue")
            print(f"[OK] Queue size: {len(self.engine.images)}")
            print("="*70)
            return True
        
        print("[OPEN] No files selected")
        print("="*70)
        return False

    def detect_text(self):
        """Detect text dari SEMUA images dalam queue."""
        print("\n" + "="*70)
        print("  [DETECT] DETECT ALL BUTTON CLICKED")
        print("="*70)
        
        if not self.engine or not self.engine.images:
            print("[WARNING] No images in queue!")
            print("="*70)
            return
        
        total = len(self.engine.images)
        print(f"[DETECT] Queue: {total} images")
        print(f"[DETECT] Starting batch processing...")
        
        self.ocr_thread = threading.Thread(target=self._ocr_worker)
        self.ocr_thread.daemon = True
        self.ocr_thread.start()
        
        print(f"[OK] OCR thread started")
        print("="*70)

    def _ocr_worker(self):
        """OCR worker thread untuk batch processing."""
        self.is_loading = True
        self.loading_start_time = time.time()
        
        try:
            results = self.engine.process_all()
            
            print(f"\n[SUCCESS] Batch processing complete!")
            print(f"  - Processed: {len(results)}")
            
            # Auto-select first completed image
            for i, img_data in enumerate(self.engine.images):
                if img_data['status'] == 'completed':
                    self.selected_index = i
                    break
            
        except Exception as e:
            print(f"\n[ERROR] OCR failed: {e}")
        finally:
            self.is_loading = False

    def export_result(self):
        """Export hasil OCR dari semua images."""
        print("\n" + "="*70)
        print("  [EXPORT] EXPORT BUTTON CLICKED")
        print("="*70)
        
        if not self.engine.images or not any(img.get('result') for img in self.engine.images):
            print("[WARNING] No results to export!")
            print("="*70)
            return
        
        try:
            txt_path, json_path = self.engine.export_batch()
            print(f"\n[OK] Export successful!")
            print(f"  TXT: {txt_path}")
            print(f"  JSON: {json_path}")
            
            self.show_export_message = True
            self.export_message_time = time.time()
            
        except Exception as e:
            print(f"\n[ERROR] Export failed: {e}")
        
        print("="*70)

    def clear_all(self):
        """Clear semua data."""
        print("\n" + "="*70)
        print("  [CLEAR] CLEAR BUTTON CLICKED")
        print("="*70)
        
        self.engine.clear_all()
        self.selected_index = -1
        self.current_image = None
        
        print("[OK] All data cleared")
        print("="*70)

    def on_mouse_click(self, event, x, y, flags, param):
        """Handle mouse click events."""
        if event == cv2.EVENT_LBUTTONDOWN:
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
                    return
            
            # Grid thumbnail clicks
            if y > 80:  # Below top bar
                cols = 5
                margin = 10
                grid_height = self.window_height * 0.45
                
                if self.engine and self.engine.images:
                    total = len(self.engine.images)
                    rows = (total + cols - 1) // cols
                    thumb_width = (self.window_width - margin * (cols + 1)) // cols
                    thumb_height = int((grid_height - margin * (rows + 1)) // rows)
                    
                    for i, img_data in enumerate(self.engine.images):
                        col = i % cols
                        row = i // cols
                        
                        tx = margin + col * (thumb_width + margin)
                        ty = 80 + margin + row * (thumb_height + margin)
                        
                        if (tx <= x <= tx + thumb_width and 
                            ty <= y <= ty + thumb_height):
                            self.selected_index = i
                            print(f"[NAVIGATION] Selected image #{i+1}: {img_data['filename']}")
                            return

    def run(self):
        """Run aplikasi."""
        print("\n" + "="*60)
        print("Multiple Image OCR - Grid View")
        print("="*60)
        print("\nLayout:")
        print("  - Top Bar: Controls + Queue Info + Progress")
        print("  - Grid View: All images as thumbnails")
        print("  - Detail Panel: Selected image results")
        print("\nControls:")
        print("  - Click buttons untuk aksi")
        print("  - Click thumbnail untuk select image")
        print("  - 'o' - Open images")
        print("  - 'd' - Detect all")
        print("  - 'e' - Export")
        print("  - 'c' - Clear")
        print("  - 'q' / ESC - Quit")
        print("="*60 + "\n")

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.window_width, self.window_height)
        cv2.setMouseCallback(self.window_name, self.on_mouse_click)

        try:
            while True:
                frame = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)
                self.draw(frame)
                cv2.imshow(self.window_name, frame)

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
            print(f"\n[ERROR] {e}")
        finally:
            self.engine.clear_all()
            self.tk_root.destroy()
            cv2.destroyAllWindows()
            print("\n[OK] Application closed")


def main():
    """Main function."""
    app = ResponsiveApp(window_width=1400, window_height=800)
    app.run()


if __name__ == "__main__":
    main()
