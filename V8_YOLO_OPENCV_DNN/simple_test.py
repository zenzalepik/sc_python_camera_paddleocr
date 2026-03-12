"""
Simple test untuk cek apakah YOLO detection jalan
"""
import cv2
import numpy as np
import time
import os

print("="*70)
print("SIMPLE YOLO TEST")
print("="*70)

# Check files
print("\n1. Checking files...")
files = ['yolov3-tiny.cfg', 'yolov3-tiny.weights', 'coco.names']
for f in files:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f"   [OK] {f} ({size:,} bytes)")
    else:
        print(f"   [MISSING] {f}")

# Load model
print("\n2. Loading YOLO model...")
try:
    net = cv2.dnn.readNetFromDarknet('yolov3-tiny.cfg', 'yolov3-tiny.weights')
    print(f"   [OK] Model loaded")
    
    # Set CPU
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    print(f"   [OK] Using CPU")
    
    # Get layers
    layer_names = net.getLayerNames()
    try:
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except:
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    print(f"   [OK] Output layers: {len(output_layers)}")
    
except Exception as e:
    print(f"   [ERROR] Model load failed: {e}")
    exit(1)

# Load classes
print("\n3. Loading classes...")
with open('coco.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]
print(f"   [OK] Loaded {len(classes)} classes")

# Target classes
target_classes = ['person', 'car', 'motorcycle', 'bus', 'truck', 'bicycle', 'cell phone']
print(f"   Target: {target_classes}")

# Open camera
print("\n4. Opening camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("   [ERROR] Cannot open camera!")
    exit(1)

print(f"   [OK] Camera opened")
print(f"   Resolution: {int(cap.get(3))}x{int(cap.get(4))}")

# Create window
print("\n5. Creating window...")
cv2.namedWindow('YOLO Simple Test', cv2.WINDOW_NORMAL)
print("   [OK] Window created")

print("\n" + "="*70)
print("TESTING DETECTION...")
print("Move around in front of camera!")
print("Press 'q' to quit")
print("="*70 + "\n")

# Test loop
frame_count = 0
detect_count = 0
last_detect_time = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("[ERROR] Failed to grab frame")
        break
    
    frame_count += 1
    height, width = frame.shape[:2]
    
    # Detection setiap 0.2 detik
    current_time = time.time()
    if current_time - last_detect_time >= 0.2:
        last_detect_time = current_time
        
        # Pre-process
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        
        # Forward
        outputs = net.forward(output_layers)
        
        # Process
        boxes = []
        confidences = []
        class_ids = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = float(scores[class_id])
                
                # Threshold RENDAH (0.25) untuk test
                if confidence > 0.25:
                    class_name = classes[class_id] if class_id < len(classes) else f"class_{class_id}"
                    
                    if class_name in target_classes:
                        # Get box
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        
                        if w > 20 and h > 20:
                            boxes.append([x, y, w, h])
                            confidences.append(confidence)
                            class_ids.append(class_id)
        
        # NMS
        detect_count = 0
        if len(boxes) > 0:
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.4)
            if len(indices) > 0:
                detect_count = len(indices)
                print(f"Frame {frame_count}: Detected {detect_count} object(s)")
                for i in indices:
                    idx = i[0] if isinstance(i, (list, np.ndarray)) else i
                    print(f"  - {classes[class_ids[idx]]}: {confidences[idx]:.2f}")
        
        # Draw boxes
        for i in range(len(boxes)):
            x, y, w, h = boxes[i]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"{classes[class_ids[i]]}: {confidences[i]:.2f}"
            cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Draw info
    cv2.putText(frame, f"Frame: {frame_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Detections: {detect_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Show
    cv2.imshow('YOLO Simple Test', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n[OK] Test COMPLETE")
