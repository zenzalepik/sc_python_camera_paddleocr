"""
V8_YOLO_OPENCV_DNN - SIMPLE VERSION
Versi sederhana untuk testing detection
Tanpa OCR, tanpa fitur berat
"""

import cv2
import numpy as np
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load ENV
load_dotenv()

print("="*70)
print("V8 YOLO OPENCV DNN - SIMPLE VERSION")
print("="*70)

# Load YOLO
print("\nLoading YOLO model...")
yolo_config = 'yolov3-tiny.cfg'
yolo_weights = 'yolov3-tiny.weights'

if not os.path.exists(yolo_weights):
    print(f"[ERROR] Weights not found: {yolo_weights}")
    exit(1)

net = cv2.dnn.readNetFromDarknet(yolo_config, yolo_weights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
print("[OK] Model loaded")

# Get output layers
layer_names = net.getLayerNames()
try:
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
except:
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
print(f"[OK] Output layers: {len(output_layers)}")

# Load classes
with open('coco.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]
print(f"[OK] Classes: {len(classes)}")

# Target classes
target_classes = ['person', 'car', 'motorcycle', 'bus', 'truck', 'bicycle', 'cell phone']
print(f"Target: {target_classes}")

# Open camera
print("\nOpening camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[ERROR] Cannot open camera!")
    exit(1)

# Set resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
print(f"[OK] Camera opened: 640x480")

# Create window
cv2.namedWindow('YOLO Detection', cv2.WINDOW_NORMAL)
print("[OK] Window created")

print("\n" + "="*70)
print("DETECTION STARTED")
print("Move around in front of camera!")
print("Press 'q' to quit")
print("="*70 + "\n")

# Main loop
frame_count = 0
last_detect_time = 0
last_detections = []

# Stats
fps = 0
last_fps_time = time.time()

while True:
    start_time = time.time()
    
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
                
                # Threshold 0.25 (rendah untuk test)
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
        last_detections = []
        if len(boxes) > 0:
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.4)
            if len(indices) > 0:
                for i in indices:
                    idx = i[0] if isinstance(i, (list, np.ndarray)) else i
                    last_detections.append({
                        'class': classes[class_ids[idx]],
                        'conf': confidences[idx],
                        'box': boxes[idx]
                    })
                
                print(f"[DETECT] {len(last_detections)} object(s):")
                for det in last_detections:
                    print(f"  - {det['class']}: {det['conf']:.2f}")
    
    # Draw detections
    for det in last_detections:
        x, y, w, h = det['box']
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        label = f"{det['class']}: {det['conf']:.2f}"
        cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Draw info
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Detections: {len(last_detections)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Show
    cv2.imshow('YOLO Detection', frame)
    
    # Calculate FPS
    elapsed = time.time() - start_time
    if elapsed > 0:
        fps = 1.0 / elapsed
    
    # Check key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n[OK] Test COMPLETE")
