"""
Aplikasi Python dengan Layout Responsive - 2 Frame Kiri-Kanan
- Frame kiri: Teks "Selamat Datang" + 4 tombol
- Frame kanan: YOLO Full Detector (import dari yolo8n module)
  Dengan semua fitur: detection, distance tracking, SIAGA, parking session
- UI elements scale otomatis saat window resize
"""

import cv2
import numpy as np
import sys
import os

# Add yolo8n to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "yolo8n"))
from yolo8n import YOLOFullDetector, ParkingPhase


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
        return self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height


class ResponsiveApp:
    """Aplikasi dengan UI responsive yang scale otomatis."""

    def __init__(self, window_width=1280, window_height=700):
        self.window_width = window_width
        self.window_height = window_height
        self.window_name = "Aplikasi Python - YOLO Full Detector"

        # Initialize buttons
        self.buttons = [
            Button("Tombol 1", color=(0, 120, 255)),
            Button("Tombol 2", color=(0, 180, 0)),
            Button("Tombol 3", color=(255, 100, 0)),
            Button("Tombol 4", color=(200, 0, 200)),
        ]

        # Initialize YOLO full detector
        self.yolo_detector = None
        self.yolo_enabled = True
        self._init_yolo()

    def _init_yolo(self):
        """Initialize YOLO full detector."""
        model_path = os.path.join(os.path.dirname(__file__), "yolo8n", "yolov8n.pt")
        self.yolo_detector = YOLOFullDetector(camera_id=0, model_path=model_path)
        self.yolo_enabled = self.yolo_detector.model is not None

    def draw_left_frame(self, frame, width, height):
        """Draw frame kiri dengan teks 'Selamat Datang' dan 4 tombol horizontal."""
        # Background putih
        cv2.rectangle(frame, (0, 0), (width, height), (255, 255, 255), -1)

        # Teks "Selamat Datang" - di bagian atas
        text = "Selamat Datang"
        font_scale = min(width, height) / 500
        thickness = max(1, int(font_scale * 2))

        (text_w, text_h), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )

        text_x = (width - text_w) // 2
        text_y = height // 6

        cv2.putText(frame, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)

        # Draw buttons horizontal di tengah
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

    def draw_right_frame(self, frame, start_x, width, height, yolo_frame=None, state=None):
        """
        Draw frame kanan dengan YOLO full detector.
        
        Args:
            frame: Main frame to draw on
            start_x: X start position
            width: Width of right frame
            height: Height of right frame
            yolo_frame: Frame from YOLO camera (optional)
            state: State dict from YOLO detector (optional)
        """
        if yolo_frame is not None:
            # Resize YOLO frame to fit right frame
            yolo_resized = cv2.resize(yolo_frame, (width, height))
            
            # Draw detections dengan state lengkap
            if state and self.yolo_enabled:
                self._draw_full_detections(yolo_resized, state, width, height)
            
            # Copy to main frame (correct slicing: frame[y, x])
            frame[:height, start_x:start_x + width] = yolo_resized
        else:
            # Fallback: gray background with text
            cv2.rectangle(frame, (start_x, 0), (start_x + width, height), (128, 128, 128), -1)
            text = "YOLO Disabled"
            cv2.putText(frame, text, (start_x + 10, height // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    def _draw_full_detections(self, frame, state, width, height):
        """Draw full detections dengan semua info."""
        detections = state.get('detections', [])
        tracked_object = state.get('tracked_object')
        status = state.get('status', '')
        siaga_active = state.get('siaga_active', False)
        fps = state.get('fps', 0)
        yolo_enabled = state.get('yolo_enabled', True)

        # Scale factor untuk koordinat
        frame_h, frame_w = frame.shape[:2]

        # Draw detections
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            
            # Scale coordinates
            x1_scaled = int(x1 * frame_w / state.get('original_width', frame_w))
            y1_scaled = int(y1 * frame_h / state.get('original_height', frame_h))
            x2_scaled = int(x2 * frame_w / state.get('original_width', frame_w))
            y2_scaled = int(y2 * frame_h / state.get('original_height', frame_h))

            color = (0, 255, 0)  # Green default
            
            # Highlight tracked object dengan warna status
            if tracked_object:
                if status == 'approaching':
                    color = (0, 0, 255)  # Red - mendekat
                elif status == 'moving_away':
                    color = (255, 0, 0)  # Blue - menjauh
                else:
                    color = (0, 255, 0)  # Green - tetap

            cv2.rectangle(frame, (x1_scaled, y1_scaled), (x2_scaled, y2_scaled), color, 2)
            
            label = f"{det['class_name']} {det['confidence']:.2f}"
            if tracked_object and det.get('class_id') == tracked_object.get('id'):
                label += f" [{tracked_object.get('id', '')}]"
            
            cv2.putText(frame, label, (x1_scaled, y1_scaled - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # SIAGA indicator - di atas tengah
        if siaga_active:
            text = "⚠️ SIAGA - Object Mendekat"
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            x = (frame_w - text_w) // 2
            cv2.rectangle(frame, (x - 10, 10), (x + text_w + 10, 40), (0, 0, 255), -1)
            cv2.putText(frame, text, (x, 32),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # FPS counter
        cv2.putText(frame, f"FPS: {fps}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # YOLO status
        if not yolo_enabled:
            cv2.putText(frame, "YOLO OFF", (frame_w - 100, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    def draw(self, frame, yolo_frame=None, state=None):
        """Draw semua UI elements."""
        height, width = frame.shape[:2]

        # Split 50/50 - kiri dan kanan
        half_width = width // 2

        # Draw frame kiri (white background dengan teks)
        self.draw_left_frame(frame[:, :half_width], half_width, height)

        # Draw frame kanan (YOLO full detector)
        self.draw_right_frame(frame, half_width, half_width, height, yolo_frame, state)

        # Draw divider line di tengah
        cv2.line(frame, (half_width, 0), (half_width, height), (255, 255, 255), 2)

    def run(self):
        """Run aplikasi."""
        print("\n" + "="*60)
        print("Aplikasi Python - YOLO Full Detector")
        print("="*60)
        print("\nLayout:")
        print("  - Frame Kiri: Teks 'Selamat Datang' + 4 Tombol")
        print("  - Frame Kanan: YOLO Full Detector")
        print("    - Object Detection")
        print("    - Distance Tracking (mendekat/menjauh)")
        print("    - SIAGA System")
        print("    - Parking Session (4 Fase)")
        print("\nFeatures:")
        print("  - UI scale otomatis saat window resize")
        print("  - Reusable Button component")
        print("  - Reusable YOLOFullDetector component")
        print("\nControls:")
        print("  - Resize window untuk lihat efek responsive")
        print("  - 'q' / ESC: Quit")
        print("  - 'y': Toggle YOLO")
        print("  - 'r': Reset tracking")
        print("  - 'l': Loop Detector (FASE 3)")
        print("  - 't': Tap Card (FASE 4)")
        print("="*60 + "\n")

        # Create named window dengan WINDOW_NORMAL agar bisa resize
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        # Set initial window size
        cv2.resizeWindow(self.window_name, self.window_width, self.window_height)

        try:
            while True:
                # Get YOLO frame and state
                yolo_frame = None
                state = {}
                
                if self.yolo_enabled and self.yolo_detector:
                    yolo_frame, state = self.yolo_detector.get_frame()
                    
                    # Store original dimensions for scaling
                    if yolo_frame is not None:
                        state['original_width'] = yolo_frame.shape[1]
                        state['original_height'] = yolo_frame.shape[0]

                # Get current window size (untuk handle resize)
                window_size = cv2.getWindowImageRect(self.window_name)
                current_width = window_size[2]
                current_height = window_size[3]

                # Skip jika window terlalu kecil
                if current_width <= 0 or current_height <= 0:
                    continue

                # Create blank frame dengan ukuran window saat ini
                frame = np.zeros((current_height, current_width, 3), dtype=np.uint8)

                # Draw UI elements (scale otomatis)
                self.draw(frame, yolo_frame, state)

                # Show frame
                cv2.imshow(self.window_name, frame)

                # Handle keyboard
                key = cv2.waitKey(10) & 0xFF
                if key == ord('q') or key == 27:  # 'q' atau ESC
                    break
                elif key == ord('y'):  # Toggle YOLO
                    if self.yolo_detector:
                        self.yolo_detector.yolo_enabled = not self.yolo_detector.yolo_enabled
                        self.yolo_enabled = self.yolo_detector.yolo_enabled
                        print(f"[{'✅' if self.yolo_enabled else '❌'}] YOLO {'enabled' if self.yolo_enabled else 'disabled'}")
                elif key == ord('r'):  # Reset tracking
                    if self.yolo_detector:
                        self.yolo_detector.reset_tracking()
                        print("[🔄] Tracking reset")
                elif key == ord('l'):  # Loop Detector
                    if self.yolo_detector:
                        self.yolo_detector.trigger_loop_detector()
                elif key == ord('t'):  # Tap Card
                    if self.yolo_detector:
                        self.yolo_detector.trigger_tap_card()

        except Exception as e:
            print(f"\n[ERROR] {e}")
        finally:
            if self.yolo_detector:
                self.yolo_detector.release()
            cv2.destroyAllWindows()
            print("\n[OK] Application closed")


def main():
    """Main function."""
    app = ResponsiveApp(window_width=1280, window_height=700)
    app.run()


if __name__ == "__main__":
    main()
