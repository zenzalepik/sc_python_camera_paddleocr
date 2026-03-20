"""
Debug script untuk mencari sumber error numpy array comparison
"""

import sys
import os

# Import widget
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "paddleocr_multiple_widget"))
from paddleocr_multiple_widget import PaddleOCRMultipleWidget

import tkinter as tk
import numpy as np

print("\n" + "="*70)
print("DEBUG: Testing numpy array comparison")
print("="*70 + "\n")

# Test 1: Check showing_image_index initialization
print("[TEST 1] showing_image_index initialization")
showing_image_index = -1
print(f"  showing_image_index = {showing_image_index}")
print(f"  type: {type(showing_image_index)}")

try:
    if showing_image_index < 0:
        print("  ✓ showing_image_index < 0 works")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 2: Check with numpy array
print("\n[TEST 2] Numpy array comparison (should fail)")
showing_image_index = np.array([-1])
print(f"  showing_image_index = {showing_image_index}")
print(f"  type: {type(showing_image_index)}")

try:
    if showing_image_index < 0:
        print("  ✓ showing_image_index < 0 works")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 3: Check widget initialization
print("\n[TEST 3] Widget initialization")
root = tk.Tk()
root.withdraw()

widget = PaddleOCRMultipleWidget(root=root)

print(f"  widget.images = {widget.images}")
print(f"  type: {type(widget.images)}")
print(f"  len: {len(widget.images)}")

# Test 4: Check image data
print("\n[TEST 4] Adding test image")
test_image = r"D:\Github\sc_python_camera_paddleocr\tes\import_paddleocr_multiple\Screenshot_2026-03-07_142543.png"

if os.path.exists(test_image):
    result = widget.add_image(test_image)
    print(f"  Added: {result}")
    print(f"  widget.images[0] keys: {widget.images[0].keys() if widget.images else 'N/A'}")
    
    if widget.images:
        img_data = widget.images[0]
        print(f"  image type: {type(img_data.get('image'))}")
        print(f"  image shape: {img_data.get('image').shape if img_data.get('image') is not None else 'N/A'}")
else:
    print(f"  Test image not found: {test_image}")

print("\n" + "="*70)
print("DEBUG COMPLETE")
print("="*70 + "\n")
