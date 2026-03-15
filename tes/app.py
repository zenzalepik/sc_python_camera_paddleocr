"""
Aplikasi Python dengan Layout Responsive - 2 Frame Kiri-Kanan
- Frame kiri: Teks "Selamat Datang"
- Frame kanan: Kotak abu-abu
- UI elements scale otomatis saat window resize
"""

import cv2
import numpy as np


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
        self.window_name = "Aplikasi Python - Responsive Layout"

        # Initialize buttons
        self.buttons = [
            Button("Tombol 1", color=(0, 120, 255)),
            Button("Tombol 2", color=(0, 180, 0)),
            Button("Tombol 3", color=(255, 100, 0)),
            Button("Tombol 4", color=(200, 0, 200)),
        ]

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

    def draw_right_frame(self, frame, start_x, width, height):
        """Draw frame kanan dengan kotak abu-abu dan kotak biru 90% di tengah."""
        # Background abu-abu
        cv2.rectangle(frame, (start_x, 0), (start_x + width, height), (128, 128, 128), -1)

        # Border putih untuk frame kanan
        cv2.rectangle(frame, (start_x, 0), (start_x + width, height), (255, 255, 255), 2)

        # Kotak biru di tengah (90% dari frame kanan)
        box_width = int(width * 0.9)
        box_height = int(height * 0.9)
        box_x = start_x + (width - box_width) // 2
        box_y = (height - box_height) // 2
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), (255, 0, 0), -1)
        cv2.rectangle(frame, (box_x, box_y), (box_x + box_width, box_y + box_height), (255, 255, 255), 2)

    def draw(self, frame):
        """Draw semua UI elements."""
        height, width = frame.shape[:2]

        # Split 50/50 - kiri dan kanan
        half_width = width // 2

        # Draw frame kiri (white background dengan teks)
        self.draw_left_frame(frame[:, :half_width], half_width, height)

        # Draw frame kanan (gray box)
        self.draw_right_frame(frame, half_width, half_width, height)

        # Draw divider line di tengah
        cv2.line(frame, (half_width, 0), (half_width, height), (255, 255, 255), 2)

    def run(self):
        """Run aplikasi."""
        print("\n" + "="*60)
        print("Aplikasi Python - Responsive Layout")
        print("="*60)
        print("\nLayout:")
        print("  - Frame Kiri: Teks 'Selamat Datang'")
        print("  - Frame Kanan: Kotak Abu-abu")
        print("\nFeatures:")
        print("  - UI scale otomatis saat window resize")
        print("  - Tidak ada overlap elemen UI")
        print("  - Reusable Button component")
        print("\nControls:")
        print("  - Resize window untuk lihat efek responsive")
        print("  - Press 'q' atau ESC to quit")
        print("="*60 + "\n")

        # Create named window dengan WINDOW_NORMAL agar bisa resize
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        # Set initial window size
        cv2.resizeWindow(self.window_name, self.window_width, self.window_height)

        try:
            while True:
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
                self.draw(frame)

                # Show frame
                cv2.imshow(self.window_name, frame)

                # Handle keyboard
                key = cv2.waitKey(10) & 0xFF
                if key == ord('q') or key == 27:  # 'q' atau ESC
                    break

        except Exception as e:
            print(f"\n[ERROR] {e}")
        finally:
            cv2.destroyAllWindows()
            print("\n[OK] Application closed")


def main():
    """Main function."""
    app = ResponsiveApp(window_width=1280, window_height=700)
    app.run()


if __name__ == "__main__":
    main()
