"""
Quick test untuk YOLOv8 model
"""
import cv2
import numpy as np
from ultralytics import YOLO

print("="*60)
print("YOLOv8 Quick Test")
print("="*60)

# Load model
print("\nLoading model: yolov8n.pt...")
model = YOLO("yolov8n.pt")
print("✅ Model loaded!")

# Create test image
print("\nCreating test image with objects...")
img = np.ones((480, 640, 3), dtype=np.uint8) * 255

# Draw some shapes to simulate objects
cv2.rectangle(img, (100, 100), (200, 200), (0, 255, 0), -1)  # Green box
cv2.circle(img, (400, 150), 50, (255, 0, 0), -1)  # Red circle
cv2.putText(img, "TEST", (250, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

# Save test image
cv2.imwrite("test_image.jpg", img)
print("✅ Test image saved as test_image.jpg")

# Run detection
print("\nRunning detection...")
results = model(img, verbose=False)

# Show results
print("\nDetection results:")
for result in results:
    boxes = result.boxes
    if boxes is not None:
        print(f"   Objects detected: {len(boxes)}")
        for box in boxes:
            cls_id = int(box.cls[0].cpu().numpy())
            conf = float(box.conf[0].cpu().numpy())
            print(f"      - Class: {model.names[cls_id]}, Confidence: {conf:.2f}")
    else:
        print("   No objects detected (expected for synthetic image)")

print("\n" + "="*60)
print("Test completed!")
print("="*60)
print("\nNext: Run 'python main.py' for live camera streaming")
