"""
Minimal Test - Camera Only (No YOLO)
"""
import cv2

print("="*70)
print("MINIMAL TEST - Camera Only")
print("="*70)

# Open camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Cannot open camera!")
    exit(1)

print("✅ Camera opened successfully")
print(f"   Resolution: {int(cap.get(3))}x{int(cap.get(4))}")

# Create window
cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
print("✅ Window created")

print("\nPress 'q' to quit...")

# Main loop
while True:
    ret, frame = cap.read()
    
    if not ret:
        print("❌ Failed to grab frame")
        break
    
    # Show frame
    cv2.imshow('Test', frame)
    
    # Check key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("✅ Quit successfully")
        break

cap.release()
cv2.destroyAllWindows()
print("\n✅ Test COMPLETE")
