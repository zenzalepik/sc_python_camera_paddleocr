"""
Test YOLO Detection dengan OpenCV DNN
"""
import cv2
import numpy as np
import time

print("="*70)
print("YOLO DETECTION TEST")
print("="*70)

# Load model
print("\nLoading model...")
net = cv2.dnn.readNetFromDarknet('yolov3-tiny.cfg', 'yolov3-tiny.weights')
print(f"Model loaded: {net is not None}")
print(f"Layers: {len(net.getLayerNames())}")

# Set CPU
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
print("Using CPU backend")

# Get output layers
layer_names = net.getLayerNames()
try:
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
except:
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
print(f"Output layers: {len(output_layers)}")

# COCO classes
classes = []
with open('coco.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]
print(f"Classes loaded: {len(classes)}")

# Target classes
target_classes = ['person', 'car', 'motorcycle', 'bus', 'truck', 'bicycle']
print(f"Target classes: {target_classes}")

# Open camera
print("\nOpening camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Cannot open camera!")
    exit(1)

print("Camera opened")
print(f"Resolution: {int(cap.get(3))}x{int(cap.get(4))}")
print("\nPress 'q' to quit...")
print()

# Create window
cv2.namedWindow('YOLO Test', cv2.WINDOW_NORMAL)

frame_count = 0
last_detect_time = 0
last_detections = []

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("ERROR: Failed to grab frame")
        break
    
    frame_count += 1
    height, width = frame.shape[:2]
    
    # Detection setiap 0.5 detik (untuk test)
    current_time = time.time()
    if current_time - last_detect_time >= 0.5:
        last_detect_time = current_time
        
        # Pre-process
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        
        # Forward pass
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
                
                # Filter threshold dan target classes
                if confidence > 0.5:
                    class_name = classes[class_id] if class_id < len(classes) else f"class_{class_id}"
                    
                    if class_name in target_classes:
                        # Get box
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        
                        # Validate
                        if w > 10 and h > 10:
                            boxes.append([x, y, w, h])
                            confidences.append(confidence)
                            class_ids.append(class_id)
        
        # NMS
        if len(boxes) > 0:
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            
            last_detections = []
            if len(indices) > 0:
                for i in indices.flatten():
                    last_detections.append({
                        'class': classes[class_ids[i]],
                        'conf': confidences[i],
                        'box': boxes[i]
                    })
        
        print(f"Frame {frame_count}: Detected {len(last_detections)} object(s)")
        for det in last_detections:
            print(f"  - {det['class']}: {det['conf']:.2f} @ {det['box']}")
    
    # Draw detections
    for det in last_detections:
        x, y, w, h = det['box']
        class_name = det['class']
        conf = det['conf']
        
        # Draw box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Draw label
        label = f"{class_name}: {conf:.2f}"
        cv2.putText(frame, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Draw FPS
    cv2.putText(frame, f"Detections: {len(last_detections)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Show
    cv2.imshow('YOLO Test', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\nTest COMPLETE")
