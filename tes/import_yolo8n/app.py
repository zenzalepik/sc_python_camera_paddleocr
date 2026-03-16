"""
Aplikasi Python dengan Layout Responsive - 2 Frame Kiri-Kanan
- Frame kiri: Teks "Selamat Datang" + 4 tombol
- Frame kanan: YOLO Widget output (dengan semua fitur lengkap)
- UI elements scale otomatis saat window resize
"""

import cv2
import numpy as np
import sys
import os

# Import widget
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "yolo_widget"))
from yolo_widget import YOLOWidget


class Button:
    """Reusable Button component."""

    def __init__(self, text, color=(0, 120, 255), text_color=(255, 255, 255)):
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, frame, x, y, width, height, font_scale=None):
        """Draw button on frame."""
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


class ResponsiveApp:
    """Aplikasi dengan UI responsive yang scale otomatis."""

    def __init__(self, window_width=1280, window_height=700):
        self.window_width = window_width
        self.window_height = window_height
        self.window_name = "Aplikasi Python - YOLO Widget"

        # Initialize buttons
        self.buttons = [
            Button("Tombol 1", color=(0, 120, 255)),
            Button("Tombol 2", color=(0, 180, 0)),
            Button("Tombol 3", color=(255, 100, 0)),
            Button("Tombol 4", color=(200, 0, 200)),
        ]

        # Initialize YOLO widget dengan camera index yang bisa dicoba
        # Coba camera_id=0 (default), jika error coba 1, 2, dst
        self.widget = YOLOWidget(camera_id=0)

    def draw_left_frame(self, frame, width, height):
        """Draw frame kiri dengan teks 'Selamat Datang' dan 4 tombol horizontal."""
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
        text_y = height // 6

        cv2.putText(frame, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)

        # Draw buttons horizontal
        button_width = width // 6
        button_height = height // 10
        button_spacing = width // 40
        total_buttons_width = len(self.buttons) * button_width + (len(self.buttons) - 1) * button_spacing
        start_x = (width - total_buttons_width) // 2
        start_y = height // 2

        font_scale_btn = min(width, height) / 1500

        for i, button in enumerate(self.buttons):
            btn_x = start_x + i * (button_width + button_spacing)
            btn_y = start_y
            button.draw(frame, btn_x, btn_y, button_width, button_height, font_scale_btn)

    def draw_right_frame(self, frame, start_x, width, height, yolo_frame=None):
        """Draw frame kanan dengan YOLO widget."""
        if yolo_frame is not None:
            # Resize YOLO frame to fit right frame
            yolo_resized = cv2.resize(yolo_frame, (width, height))
            
            # Copy to main frame
            frame[:height, start_x:start_x + width] = yolo_resized
        else:
            # Fallback
            cv2.rectangle(frame, (start_x, 0), (start_x + width, height), (128, 128, 128), -1)
            text = "YOLO Disabled"
            cv2.putText(frame, text, (start_x + 10, height // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    def draw(self, frame, yolo_frame=None):
        """Draw semua UI elements."""
        height, width = frame.shape[:2]
        half_width = width // 2

        self.draw_left_frame(frame[:, :half_width], half_width, height)
        self.draw_right_frame(frame, half_width, half_width, height, yolo_frame)

        # Divider line
        cv2.line(frame, (half_width, 0), (half_width, height), (255, 255, 255), 2)

    def run(self):
        """Run aplikasi."""
        print("\n" + "="*60)
        print("Aplikasi Python - YOLO Widget")
        print("="*60)
        print("\nLayout:")
        print("  - Frame Kiri: Teks 'Selamat Datang' + 4 Tombol")
        print("  - Frame Kanan: YOLO Widget (dengan semua fitur lengkap)")
        print("    - Object Detection")
        print("    - Distance Tracking (mendekat/menjauh)")
        print("    - SIAGA System")
        print("    - Parking Session (4 Fase)")
        print("    - UI Overlays lengkap")
        print("\nControls:")
        print("  - Resize window untuk lihat efek responsive")
        print("  - 'q' / ESC: Quit")
        print("  - 'y': Toggle YOLO")
        print("  - 'r': Reset tracking")
        print("  - 'l': Loop Detector (FASE 3)")
        print("  - 't': Tap Card (FASE 4)")
        print("="*60 + "\n")

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.window_width, self.window_height)

        try:
            while True:
                # Get frame dari widget
                yolo_frame = None
                
                if self.widget.detector.yolo_enabled:
                    yolo_frame, _ = self.widget.get_frame()

                # Get window size
                window_size = cv2.getWindowImageRect(self.window_name)
                current_width = window_size[2]
                current_height = window_size[3]

                if current_width <= 0 or current_height <= 0:
                    continue

                # Create frame
                frame = np.zeros((current_height, current_width, 3), dtype=np.uint8)

                # Draw UI
                self.draw(frame, yolo_frame)

                # Show
                cv2.imshow(self.window_name, frame)

                # Handle keyboard
                key = cv2.waitKey(10) & 0xFF
                if key == ord('q') or key == 27:
                    break
                elif key == ord('y'):
                    self.widget.toggle_yolo()
                    print(f"[{'✅' if self.widget.detector.yolo_enabled else '❌'}] YOLO {'enabled' if self.widget.detector.yolo_enabled else 'disabled'}")
                elif key == ord('r'):
                    self.widget.reset_tracking()
                    print("[🔄] Tracking reset")
                elif key == ord('l'):
                    self.widget.trigger_loop_detector(yolo_frame)
                    print("[🔵] Loop Detector triggered")
                elif key == ord('t'):
                    self.widget.trigger_tap_card(yolo_frame)
                    print("[💳] Tap Card triggered")

        except Exception as e:
            print(f"\n[ERROR] {e}")
        finally:
            self.widget.release()
            cv2.destroyAllWindows()
            print("\n[OK] Application closed")


def main():
    """Main function."""
    app = ResponsiveApp(window_width=1280, window_height=700)
    app.run()


if __name__ == "__main__":
    main()
