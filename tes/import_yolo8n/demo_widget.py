"""
Demo App - Cara menggunakan YOLO Widget

Ini contoh aplikasi yang menggunakan YOLO Widget.
Copy folder 'yolo_widget' ke project Anda, lalu import seperti ini:
"""

import cv2
import numpy as np
import sys
import os

# Import widget (setelah copy folder yolo_widget ke project Anda)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "yolo_widget"))
from yolo_widget import YOLOWidget, ParkingPhase


def main():
    """Demo aplikasi menggunakan YOLO Widget."""
    
    # 1. Buat widget instance
    widget = YOLOWidget(camera_id=0)
    
    # 2. Optional: Set custom config
    widget.set_target_classes([0])  # Hanya detect person
    widget.set_confidence_threshold(0.5)
    
    print("\n" + "="*60)
    print("YOLO Widget - Demo App")
    print("="*60)
    print("\nLayout:")
    print("  - Frame Kiri: Teks 'Selamat Datang' + 4 Tombol")
    print("  - Frame Kanan: YOLO Widget Output")
    print("\nControls:")
    print("  - 'q' / ESC: Quit")
    print("  - 'y': Toggle YOLO")
    print("  - 'r': Reset tracking")
    print("  - 'l': Loop Detector (FASE 3)")
    print("  - 't': Tap Card (FASE 4)")
    print("="*60 + "\n")
    
    # Create window
    window_name = "YOLO Widget Demo"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 700)
    
    try:
        while True:
            # 3. Get frame dari widget
            yolo_frame, state = widget.get_frame()
            
            if yolo_frame is not None:
                # 4. Handle parking session
                widget.handle_parking_session(yolo_frame, state)
                
                # 5. Draw UI pada frame YOLO
                widget.draw_ui(yolo_frame, state)
                
                # Resize YOLO frame untuk fit di layout
                yolo_resized = cv2.resize(yolo_frame, (640, 700))
            else:
                yolo_resized = np.zeros((700, 640, 3), dtype=np.uint8)
            
            # 6. Buat layout 2 frame
            full_frame = np.zeros((700, 1280, 3), dtype=np.uint8)
            
            # Frame kiri - Welcome + Buttons
            left_frame = full_frame[:, :640]
            left_frame[:] = 255  # White background
            
            # Draw teks
            cv2.putText(left_frame, "Selamat Datang", (170, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
            
            # Draw buttons
            button_colors = [(0, 120, 255), (0, 180, 0), (255, 100, 0), (200, 0, 200)]
            button_names = ["Tombol 1", "Tombol 2", "Tombol 3", "Tombol 4"]
            
            for i, (color, name) in enumerate(zip(button_colors, button_names)):
                x = 80 + i * 120
                y = 350
                cv2.rectangle(left_frame, (x, y), (x + 100, 400), color, -1)
                cv2.putText(left_frame, name, (x + 10, y + 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            full_frame[:, :640] = left_frame
            
            # Frame kanan - YOLO output
            full_frame[:, 640:] = yolo_resized
            
            # Divider
            cv2.line(full_frame, (640, 0), (640, 700), (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow(window_name, full_frame)
            
            # Handle keyboard
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('y'):
                widget.yolo_enabled = not widget.yolo_enabled
                print(f"[{'✅' if widget.yolo_enabled else '❌'}] YOLO {'enabled' if widget.yolo_enabled else 'disabled'}")
            elif key == ord('r'):
                widget.reset_tracking()
                print("[🔄] Tracking reset")
            elif key == ord('l'):
                widget.trigger_loop_detector()
                print("[🔵] Loop Detector triggered")
            elif key == ord('t'):
                widget.trigger_tap_card()
                print("[💳] Tap Card triggered")
    
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        widget.release()
        cv2.destroyAllWindows()
        print("\n[OK] Demo closed")


if __name__ == "__main__":
    main()
