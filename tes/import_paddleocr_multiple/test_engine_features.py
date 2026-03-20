"""
Test script untuk verify semua fitur engine sudah ter-copy
"""

import sys
import os

# Import multiple engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "paddleocr_multiple_engine"))
from paddleocr_multiple_engine import PaddleOCRMultipleEngine

import tkinter as tk

print("\n" + "="*70)
print("TEST: Verify All Engine Features Copied")
print("="*70 + "\n")

# Create Tkinter root
root = tk.Tk()
root.withdraw()

# Create engine
print("[TEST] Creating PaddleOCRMultipleEngine...")
engine = PaddleOCRMultipleEngine()  # Tidak perlu root!

# Verify features
print("\n[VERIFY] Checking features...")
print(f"  - Engine type: {type(engine).__name__}")
print(f"  - Widget type: {type(engine.widget).__name__}")
print(f"  - License plate detection: {engine.widget.detect_license_plate}")
print(f"  - Delete space: {engine.widget.delete_space}")
print(f"  - Group by line: {engine.widget.group_by_line}")
print(f"  - Line tolerance: {engine.widget.line_tolerance}")
print(f"  - Conf threshold: {engine.widget.conf_threshold}")

# Check if plat_processor available
print("\n[VERIFY] Checking plate processor...")
try:
    from paddleocr_engine.indonesia import plat_processor
    print(f"  ✓ Plate processor imported successfully")
    print(f"  ✓ Module: {plat_processor.__file__}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test add image
print("\n[TEST] Adding test image...")
test_image = r"D:\Github\sc_python_camera_paddleocr\tes\import_paddleocr_multiple\Screenshot_2026-03-07_142543.png"

if os.path.exists(test_image):
    result = engine.add_image(test_image)
    print(f"  {'✓' if result else '✗'} Add image: {'Success' if result else 'Failed'}")
    
    if result:
        # Test process
        print("\n[TEST] Processing image...")
        try:
            process_result = engine.process_image(0)
            if process_result:
                print(f"  ✓ Processing successful")
                print(f"  - Texts detected: {process_result.get('total_texts', 0)}")
                print(f"  - Plate detected: {process_result.get('plate', 'N/A')}")
                
                # Verify plate detection
                plate = process_result.get('plate')
                if plate:
                    print(f"\n✓✓✓ PLATE DETECTION WORKING! ✓✓✓")
                    print(f"    Detected plate: {plate}")
                else:
                    print(f"\n  Note: No plate detected in this image")
            else:
                print(f"  ✗ Processing failed")
        except Exception as e:
            print(f"  ✗ Error during processing: {e}")
            import traceback
            traceback.print_exc()
else:
    print(f"  ✗ Test image not found: {test_image}")

# Test export
print("\n[TEST] Testing export...")
try:
    txt_path, json_path = engine.export_batch()
    print(f"  ✓ Export successful")
    print(f"  - TXT: {txt_path}")
    print(f"  - JSON: {json_path}")
    
    # Check if files exist
    if os.path.exists(txt_path):
        print(f"  ✓ TXT file created ({os.path.getsize(txt_path)} bytes)")
    if os.path.exists(json_path):
        print(f"  ✓ JSON file created ({os.path.getsize(json_path)} bytes)")
except Exception as e:
    print(f"  ✗ Export failed: {e}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70 + "\n")

root.destroy()
