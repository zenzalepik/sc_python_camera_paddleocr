"""
Test script untuk Object Distance Detection
Tanpa GUI, hanya test logic tracking
"""

import cv2
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import time


def test_yolo_detection():
    """Test YOLO detection pada image statis."""
    print("="*70)
    print("Testing YOLO Detection")
    print("="*70)
    
    # Load model
    print("\nLoading YOLOv8n model...")
    model = YOLO('yolov8n.pt')
    print("[OK] Model loaded\n")
    
    # Test dengan webcam frame
    print("Capturing test frame from camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR] Cannot open camera")
        return
    
    # Grab beberapa frame untuk warmup
    for i in range(10):
        ret, frame = cap.read()
    
    if not ret:
        print("[ERROR] Cannot capture frame")
        cap.release()
        return
    
    print(f"[OK] Frame captured: {frame.shape[1]}x{frame.shape[0]}")
    
    # Run inference
    print("\nRunning inference...")
    start = time.time()
    results = model(frame, verbose=False, conf=0.5)
    elapsed = time.time() - start
    
    print(f"Inference time: {elapsed:.3f}s")
    print(f"FPS: {1/elapsed:.1f}")
    
    # Parse results
    det_count = 0
    if results[0].boxes is not None:
        for i in range(len(results[0].boxes)):
            box = results[0].boxes[i]
            class_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = model.names[class_id]
            
            print(f"\n  Detected: {class_name}")
            print(f"    Confidence: {conf:.2f}")
            print(f"    Class ID: {class_id}")
            
            det_count += 1
    
    if det_count == 0:
        print("\n  No objects detected")
    
    cap.release()
    
    print(f"\n[OK] Test complete - {det_count} object(s) detected")
    print("="*70)


def test_distance_logic():
    """Test logic distance estimation dengan data simulasi."""
    print("\n" + "="*70)
    print("Testing Distance Estimation Logic")
    print("="*70)
    
    # Simulasi data area dari object yang mendekat
    print("\nTest 1: Object MENDEKAT (area bertambah)")
    approaching_areas = [1000, 1100, 1200, 1350, 1500, 1700, 1900, 2100]
    
    first_half = np.mean(approaching_areas[:len(approaching_areas)//2])
    second_half = np.mean(approaching_areas[len(approaching_areas)//2:])
    change = ((second_half - first_half) / first_half) * 100
    
    print(f"  Areas: {approaching_areas}")
    print(f"  First half avg: {first_half:.1f}")
    print(f"  Second half avg: {second_half:.1f}")
    print(f"  Change: {change:.1f}%")
    print(f"  Status: {'MENDEKAT ✓' if change > 10 else 'SALAH'}")
    
    # Simulasi data area dari object yang menjauh
    print("\nTest 2: Object MENJAUH (area berkurang)")
    moving_away_areas = [2000, 1800, 1600, 1400, 1200, 1000, 800, 600]
    
    first_half = np.mean(moving_away_areas[:len(moving_away_areas)//2])
    second_half = np.mean(moving_away_areas[len(moving_away_areas)//2:])
    change = ((second_half - first_half) / first_half) * 100
    
    print(f"  Areas: {moving_away_areas}")
    print(f"  First half avg: {first_half:.1f}")
    print(f"  Second half avg: {second_half:.1f}")
    print(f"  Change: {change:.1f}%")
    print(f"  Status: {'MENJAUH ✓' if change < -10 else 'SALAH'}")
    
    # Simulasi data area dari object yang tetap
    print("\nTest 3: Object TETAP (area stabil)")
    stable_areas = [1000, 1050, 980, 1020, 990, 1010, 1005, 995]
    
    first_half = np.mean(stable_areas[:len(stable_areas)//2])
    second_half = np.mean(stable_areas[len(stable_areas)//2:])
    change = ((second_half - first_half) / first_half) * 100
    
    print(f"  Areas: {stable_areas}")
    print(f"  First half avg: {first_half:.1f}")
    print(f"  Second half avg: {second_half:.1f}")
    print(f"  Change: {change:.1f}%")
    print(f"  Status: {'TETAP ✓' if abs(change) <= 10 else 'SALAH'}")
    
    print("\n[OK] Logic test complete")
    print("="*70)


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("Object Distance Detection - Test Suite")
    print("="*70)
    
    # Test 1: YOLO detection
    test_yolo_detection()
    
    # Test 2: Distance logic
    test_distance_logic()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
    print("\nNext step: Run 'python main.py' for real-time testing")
    print("="*70)


if __name__ == "__main__":
    main()
