"""
Test camera saja (tanpa YOLO)
"""
import cv2
import time

print("="*70)
print("CAMERA TEST")
print("="*70)

# Open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ ERROR: Cannot open camera!")
    print("   Check if camera is connected")
    print("   Try different camera ID (0, 1, 2)")
    exit(1)

print("✅ Camera opened successfully")
print(f"   Resolution: {int(cap.get(3))}x{int(cap.get(4))}")
print(f"   FPS: {cap.get(cv2.CAP_PROP_FPS)}")
print()
print("Press 'q' to quit...")
print()

# Create window
cv2.namedWindow('Camera Test', cv2.WINDOW_NORMAL)

frame_count = 0
last_fps_time = time.time()
fps = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("❌ ERROR: Failed to grab frame")
        break
    
    frame_count += 1
    
    # Calculate FPS
    current_time = time.time()
    if current_time - last_fps_time >= 1.0:
        fps = frame_count / (current_time - last_fps_time)
        frame_count = 0
        last_fps_time = current_time
    
    # Draw FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Show frame
    cv2.imshow('Camera Test', frame)
    
    # Check key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n✅ Quit successfully")
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Test COMPLETE")
