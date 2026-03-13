# Test Import Library - Object Distance Detection
import sys
import os

# Path ke export_to_library
EXPORT_PATH = r'd:\Github\sc_python_camera_paddleocr\v6_Deteksi_Object_Mendekat\export_to_library'
sys.path.insert(0, EXPORT_PATH)

print("=" * 70)
print("TEST IMPORT LIBRARY")
print("=" * 70)

# TEST 1: Check files
print("\nTEST 1: Check Files")
print("-" * 70)
files = ['main.py', 'variables.py', 'yolov8n.pt']
for f in files:
    path = os.path.join(EXPORT_PATH, f)
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  [OK] {f} ({size:,} bytes)")
    else:
        print(f"  [ERROR] {f} NOT FOUND!")

# TEST 2: Import dependencies
print("\nTEST 2: Import Dependencies")
print("-" * 70)
try:
    import cv2
    print(f"  [OK] cv2 - {cv2.__version__}")
except Exception as e:
    print(f"  [ERROR] cv2 - {e}")

try:
    import numpy as np
    print(f"  [OK] numpy - {np.__version__}")
except Exception as e:
    print(f"  [ERROR] numpy - {e}")

try:
    from ultralytics import YOLO
    print(f"  [OK] ultralytics (YOLO)")
except Exception as e:
    print(f"  [ERROR] ultralytics - {e}")

# TEST 3: Import configuration
print("\nTEST 3: Import Configuration")
print("-" * 70)
try:
    from variables import CAMERA_WIDTH, CAMERA_HEIGHT
    print(f"  [OK] Configuration loaded")
    print(f"       Camera: {CAMERA_WIDTH}x{CAMERA_HEIGHT}")
except Exception as e:
    print(f"  [ERROR] Configuration - {e}")

# TEST 4: Import main module
print("\nTEST 4: Import Main Module")
print("-" * 70)
try:
    from main import RealTimeDistanceDetector
    print(f"  [OK] RealTimeDistanceDetector imported")
except Exception as e:
    print(f"  [ERROR] Main module - {e}")
    import traceback
    traceback.print_exc()

# TEST 5: Run application
print("\nTEST 5: Run Application")
print("-" * 70)
print("Starting application...")
print("Press 'Q' to quit\n")

try:
    detector = RealTimeDistanceDetector(camera_id=0)
    detector.run()
    print("\n[OK] Application completed successfully!")
except Exception as e:
    print(f"\n[ERROR] Application failed: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
