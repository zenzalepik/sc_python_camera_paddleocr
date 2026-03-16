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

        # Draw hasil deteksi panel di bawah tombol
        self.draw_result_panel(frame, width, height, start_y + button_height)

    def draw_result_panel(self, frame, width, height, y_start):
        """Draw panel hasil deteksi di bawah tombol."""
        # Panel area
        panel_y = y_start + 20
        panel_height = height - panel_y - 20
        margin = 10
        
        # Draw panel background
        cv2.rectangle(frame, (margin, panel_y), 
                     (width - margin, height - 20), (240, 240, 240), -1)
        cv2.rectangle(frame, (margin, panel_y), 
                     (width - margin, height - 20), (128, 128, 128), 1)
        
        # Title
        title = "Hasil Deteksi:"
        cv2.putText(frame, title, (margin + 10, panel_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Check ada result
        if self.widget.current_result is None:
            info = "Belum ada hasil deteksi"
            cv2.putText(frame, info, (margin + 10, panel_y + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
            return
        
        # Get texts
        texts = self.widget.get_texts()
        total = len(texts)
        
        # Show count
        count_info = f"Total: {total} teks"
        cv2.putText(frame, count_info, (width - margin - 100, panel_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 128, 0), 1)
        
        # Draw texts (max 10 yang ditampilkan)
        max_display = 10
        start_idx = 0
        line_height = 25
        max_lines = (panel_height - 60) // line_height
        
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
            max_chars = (width - 40) // 10
            if len(text) > max_chars:
                text = text[:max_chars-3] + "..."
            
            # Draw text line
            y_pos = panel_y + 50 + (i - start_idx) * line_height
            
            # Background selang-seling
            color = (255, 255, 255) if i % 2 == 0 else (240, 240, 240)
            cv2.rectangle(frame, (margin + 5, y_pos - 18),
                         (width - margin - 5, y_pos + 5), color, -1)
            
            # Text
            label = f"{i+1}. {text}"
            cv2.putText(frame, label, (margin + 10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
            
            # Confidence (kanan)
            conf_label = f"({conf:.2f})"
            (conf_w, conf_h), _ = cv2.getTextSize(conf_label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.putText(frame, conf_label, (width - margin - conf_w - 10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 128, 0), 1)
        
        # Info jika ada lebih banyak teks
        if total > max_display:
            info = f"... dan {total - max_display} teks lainnya"
            cv2.putText(frame, info, (margin + 10, height - 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (128, 128, 128), 1)

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
            print(f"[OK] Loaded: {filepath}")
            return True
        
        return False

    def detect_text(self):
        """Detect text dalam gambar."""
        if self.current_image is None:
            print("[WARNING] No image loaded. Open image first.")
            return
        
        print("\n" + "="*60)
        print("Running OCR...")
        print("="*60)
        
        try:
            # Process dengan widget
            frame_with_boxes, result = self.widget.process_frame(self.current_image)
            
            # Update current image dengan bounding boxes
            self.current_image = frame_with_boxes
            
            # Print results
            texts = self.widget.get_texts()
            print(f"\n[SUCCESS] Detected {len(texts)} text(s):")
            for i, text in enumerate(texts, 1):
                print(f"  [{i}] {text}")
            
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"\n[ERROR] OCR failed: {e}")

    def export_result(self):
        """Export hasil OCR."""
        if self.widget.current_result is None:
            print("[WARNING] No result to export. Detect text first.")
            return
        
        # Export ke TXT
        txt_path = self.widget.export_to_txt()
        print(f"[OK] Exported to {txt_path}")
        
        # Export ke JSON
        json_path = self.widget.export_to_json()
        print(f"[OK] Exported to {json_path}")
        
        # Copy to clipboard
        try:
            self.widget.copy_to_clipboard()
        except Exception as e:
            print(f"[WARNING] Copy to clipboard failed: {e}")

    def clear_all(self):
        """Clear semua."""
        self.current_image = None
        self.current_image_path = None
        self.widget.clear_result()
        print("[OK] Cleared")

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

        # Create OpenCV window dengan mouse callback
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.window_width, self.window_height)
        cv2.setMouseCallback(self.window_name, self.on_mouse_click)

        # Button click state
        button_clicked = [False] * len(self.buttons)

        try:
            while True:
                # Create frame
                frame = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)

                # Draw UI
                if self.current_image is not None:
                    # Show image dengan/without bounding boxes
                    ocr_frame = self.current_image
                else:
                    ocr_frame = None

                self.draw(frame, ocr_frame)

                # Show
                cv2.imshow(self.window_name, frame)

                # Handle keyboard
                key = cv2.waitKey(10) & 0xFF
                if key == ord('q') or key == 27:
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
