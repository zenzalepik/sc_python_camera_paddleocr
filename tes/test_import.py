"""
Test Import Widget
Script sederhana untuk test import widget
"""

import sys
import os

# Add widget path
widget_path = os.path.join(os.path.dirname(__file__), '..', 'v6_Deteksi_Object_Mendekat', 'export_to_widget')
sys.path.insert(0, widget_path)

print("="*60)
print("Test Import Object Distance Widget")
print("="*60)
print()

try:
    print("[1/3] Importing widget package...")
    from object_distance_widget import ObjectDistanceWidget
    print("      ✅ Success importing ObjectDistanceWidget")
    
    print("[2/3] Checking widget attributes...")
    print(f"      ✅ ObjectDistanceWidget class exists")
    print(f"      ✅ Has 'start' method: {hasattr(ObjectDistanceWidget, 'start')}")
    print(f"      ✅ Has 'stop' method: {hasattr(ObjectDistanceWidget, 'stop')}")
    print(f"      ✅ Has 'toggle_yolo' method: {hasattr(ObjectDistanceWidget, 'toggle_yolo')}")
    
    print("[3/3] Importing configuration...")
    from object_distance_widget import (
        CLEAN_UI,
        CAMERA_WIDTH,
        CAMERA_HEIGHT,
        YOLO_SKIP_FRAMES,
        YOLO_ENABLED_DEFAULT,
        YOLO_CONFIDENCE_THRESHOLD,
        TARGET_CLASSES,
    )
    print(f"      ✅ CLEAN_UI: {CLEAN_UI}")
    print(f"      ✅ CAMERA_WIDTH: {CAMERA_WIDTH}")
    print(f"      ✅ CAMERA_HEIGHT: {CAMERA_HEIGHT}")
    print(f"      ✅ TARGET_CLASSES: {TARGET_CLASSES}")
    
    print()
    print("="*60)
    print("✅ SEMUA TEST BERHASIL!")
    print("="*60)
    print()
    print("Widget siap digunakan!")
    print()
    print("Usage:")
    print("  import tkinter as tk")
    print("  from object_distance_widget import ObjectDistanceWidget")
    print()
    print("  root = tk.Tk()")
    print("  widget = ObjectDistanceWidget(root, camera_id=0)")
    print("  widget.pack(fill=tk.BOTH, expand=True)")
    print("  widget.start()")
    print("  root.mainloop()")
    print()
    
except ImportError as e:
    print()
    print("="*60)
    print("❌ IMPORT ERROR!")
    print("="*60)
    print()
    print(f"Error: {e}")
    print()
    print("Solusi:")
    print("  1. Pastikan dependencies terinstall:")
    print("     pip install ultralytics opencv-python Pillow numpy")
    print()
    print("  2. Pastikan widget path benar:")
    print(f"     {widget_path}")
    print()
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print()
    print("="*60)
    print("❌ ERROR!")
    print("="*60)
    print()
    print(f"Error: {e}")
    print()
    import traceback
    traceback.print_exc()

print()
input("Press Enter to exit...")
