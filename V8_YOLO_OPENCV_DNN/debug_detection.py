"""
Debug script untuk test detection
"""
import cv2
import numpy as np
import time

print("="*70)
print("YOLO DETECTION DEBUG TEST")
print("="*70)

# Load model
print("\nLoading YOLO model...")
net = cv2.dnn.readNetFromDarknet('yolov3-tiny.cfg', 'yolov3-tiny.weights')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
print("Model loaded OK")

# Get output layers
layer_names = net.getLayerNames()
try:
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
except:
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
print(f"Output layers: {len(output_layers)}")

# Load classes
classes = []
with open('coco.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]
print(f"Classes loaded: {len(classes)}")

# Target classes
target_classes = ['person', 'car', 'motorcycle', 'bus', 'truck', 'bicycle', 'cell phone']
print(f"Target classes: {target_classes}")

# Open camera
print("\nOpening camera...")
cap = cv2.VideoCapture(0)
print(f"Camera opened: {cap.isOpened()}")

# Create window
cv2.namedWindow('DEBUG - YOLO Detection', cv2.WINDOW_NORMAL)

print("\n" + "="*70)
print("TESTING DETECTION...")
print("Move around in front of the camera!")
print("Press 'q' to quit")
print("="*70 + "\n")

frame_count = 0
detect_count = 0

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("ERROR: Failed to grab frame")
        break
    
    frame_count += 1
    height, width = frame.shape[:2]
    
    # Detection setiap 5 frame (untuk performance)
    if frame_count % 5 == 0:
        # Pre-process
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        
        # Forward pass
        print(f"Frame {frame_count}: Running detection...")
        outputs = net.forward(output_layers)
        
        # Process outputs
        boxes = []
        confidences = []
        class_ids = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = float(scores[class_id])
                
                # Filter dengan threshold RENDAH (0.2) untuk test
                if confidence > 0.2:
                    class_name = classes[class_id] if class_id < len(classes) else f"class_{class_id}"
                    
                    if class_name in target_classes:
                        # Get box
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        
                        # Validate box size
                        if w > 20 and h > 20:
                            boxes.append([x, y, w, h])
                            confidences.append(confidence)
                            class_ids.append(class_id)
        
        # NMS
        detect_count = 0
        if len(boxes) > 0:
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)
            
            if len(indices) > 0:
                detect_count = len(indices)
                print(f"  >>> Detected {detect_count} object(s)!")
                for i in indices.flatten():
                    print(f"      - {classes[class_ids[i]]}: {confidences[i]:.2f} @ {boxes[i]}")
    
    # Draw ALL boxes (bahkan yang lama)
    for i in range(len(boxes)):
        x, y, w, h = boxes[i]
        class_name = classes[class_ids[i]]
        conf = confidences[i]
        
        # Draw box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Draw label
        label = f"{class_name}: {conf:.2f}"
        cv2.putText(frame, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Draw info
    cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Detections: {detect_count}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Threshold: 0.2", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Show
    cv2.imshow('DEBUG - YOLO Detection', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\nTest COMPLETE")
