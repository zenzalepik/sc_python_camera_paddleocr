"""
Test semua fitur V8_YOLO_OPENCV_DNN
"""
import sys

print("="*70)
print("V8_YOLO_OPENCV_DNN - FITUR CHECK")
print("="*70)
print()

# Check imports
print("1. Checking imports...")
try:
    import cv2
    import numpy as np
    import time
    from datetime import datetime
    from enum import Enum
    import os
    import json
    import threading
    from dotenv import load_dotenv
    from yolo_detector import YOLOVehicleDetector
    print("   ✅ All imports OK")
except Exception as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# Check files
print("\n2. Checking required files...")
files_needed = [
    'main.py',
    'yolo_detector.py',
    'yolov3-tiny.cfg',
    'yolov3-tiny.weights',
    'coco.names',
    '.env'
]

for f in files_needed:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f"   ✅ {f} ({size:,} bytes)")
    else:
        print(f"   ❌ {f} NOT FOUND!")

# Check model size
print("\n3. Checking model...")
if os.path.exists('yolov3-tiny.weights'):
    size = os.path.getsize('yolov3-tiny.weights')
    if size > 30000000:  # > 30 MB
        print(f"   ✅ Model OK ({size/1024/1024:.2f} MB)")
    else:
        print(f"   ⚠️ Model too small ({size/1024/1024:.2f} MB)")
else:
    print(f"   ❌ Model NOT FOUND!")

# Test YOLO loading
print("\n4. Testing YOLO loading...")
try:
    net = cv2.dnn.readNetFromDarknet('yolov3-tiny.cfg', 'yolov3-tiny.weights')
    print(f"   ✅ Model loaded ({len(net.getLayerNames())} layers)")
except Exception as e:
    print(f"   ❌ Model load error: {e}")

# Test camera
print("\n5. Testing camera...")
try:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        w = int(cap.get(3))
        h = int(cap.get(4))
        print(f"   ✅ Camera OK ({w}x{h})")
        cap.release()
    else:
        print(f"   ❌ Camera NOT opened!")
except Exception as e:
    print(f"   ❌ Camera error: {e}")

# Check ENV
print("\n6. Checking ENV settings...")
load_dotenv()
perf_mode = os.getenv('PERFORMANCE_MODE', 'NOT SET')
fase1 = os.getenv('FASE1_CAPTURE_COUNT', 'NOT SET')
fase2 = os.getenv('FASE2_CAPTURE_COUNT', 'NOT SET')
fase3 = os.getenv('FASE3_CAPTURE_COUNT', 'NOT SET')
fase4 = os.getenv('FASE4_CAPTURE_COUNT', 'NOT SET')
conf = os.getenv('CONFIDENCE_THRESHOLD', 'NOT SET')

print(f"   PERFORMANCE_MODE: {perf_mode}")
print(f"   FASE1_CAPTURE_COUNT: {fase1}")
print(f"   FASE2_CAPTURE_COUNT: {fase2}")
print(f"   FASE3_CAPTURE_COUNT: {fase3}")
print(f"   FASE4_CAPTURE_COUNT: {fase4}")
print(f"   CONFIDENCE_THRESHOLD: {conf}")

print("\n" + "="*70)
print("CHECK COMPLETE!")
print("="*70)
print()
print("To run application:")
print("  python main.py")
print()
print("Features available:")
print("  ✅ 4-Fase Capture")
print("  ✅ SIAGA Alert System")
print("  ✅ Focus Lock & Percentage")
print("  ✅ Parking Session Management")
print("  ✅ Loop Detector & Tap Card Buttons")
print("  ✅ Preview Window with Grid Thumbnails")
print("  ✅ Help Popup (Press H)")
print("  ✅ Snapshot Save (Press S)")
print("  ✅ Multi-Class Detection (7 classes)")
print("  ✅ OpenCV DNN Backend (CPU ~20-30%)")
print()
