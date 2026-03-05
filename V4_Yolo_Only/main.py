"""
YOLOv8 Live Streaming Camera
Real-time object detection dengan YOLOv8

Model: YOLOv8-Nano (tercepat untuk real-time)
- 3.2M parameters
- ~12MB model size
- Real-time inference (30+ FPS pada GPU, 15+ FPS pada CPU)

Fitur:
- Live camera streaming
- Real-time object detection (80 COCO classes)
- FPS counter
- Confidence threshold adjustment
- Class filter
- Snapshot capture
- Recording support
"""

import os
import cv2
import time
from datetime import datetime
from dotenv import load_dotenv

try:
    from ultralytics import YOLO
except ImportError:
    print("❌ ultralytics tidak terinstall!")
    print("💡 Install dengan: pip install ultralytics")
    exit(1)

# Load konfigurasi
load_dotenv()


class YOLOLiveStream:
    """YOLOv8 Live Streaming Camera."""

    # COCO dataset classes (80 objek)
    COCO_CLASSES = [
        'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
        'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
        'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
        'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
        'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
        'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
        'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
        'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator',
        'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
    ]

    # Warna untuk setiap kelas (BGR format untuk OpenCV)
    COLORS = [
        (0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255),
        (0, 255, 255), (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0),
        (128, 0, 128), (0, 128, 128), (255, 128, 0), (255, 0, 128), (128, 255, 0),
        (0, 255, 128), (128, 0, 255), (0, 128, 255), (255, 255, 128), (255, 128, 255)
    ]

    def __init__(self):
        """Initialize YOLO Live Stream."""
        # Camera settings
        self.camera_id = int(os.getenv('CAMERA_ID', '0'))
        self.camera_width = int(os.getenv('CAMERA_WIDTH', '640'))
        self.camera_height = int(os.getenv('CAMERA_HEIGHT', '480'))
        self.camera_fps = int(os.getenv('CAMERA_FPS', '30'))

        # YOLO model settings
        self.yolo_model = os.getenv('YOLO_MODEL', 'yolov8n.pt')  # nano = fastest
        self.conf_threshold = float(os.getenv('CONF_THRESHOLD', '0.4'))
        self.iou_threshold = float(os.getenv('IOU_THRESHOLD', '0.45'))

        # Class filter (optional - detect specific classes only)
        classes_filter = os.getenv('CLASSES_FILTER', '')
        if classes_filter.strip():
            # Convert class names to IDs
            self.classes_filter = []
            for cls_name in classes_filter.split(','):
                cls_name = cls_name.strip().lower()
                if cls_name in [c.lower() for c in self.COCO_CLASSES]:
                    cls_id = [i for i, c in enumerate(self.COCO_CLASSES) if c.lower() == cls_name][0]
                    self.classes_filter.append(cls_id)
            print(f"📋 Filtering classes: {[self.COCO_CLASSES[i] for i in self.classes_filter]}")
        else:
            self.classes_filter = None  # Detect all classes

        # Display settings
        self.show_fps = os.getenv('SHOW_FPS', 'True') == 'True'
        self.show_confidence = os.getenv('SHOW_CONFIDENCE', 'True') == 'True'
        self.show_class_id = os.getenv('SHOW_CLASS_ID', 'False') == 'True'
        self.show_labels = os.getenv('SHOW_LABELS', 'True') == 'True'
        self.box_thickness = int(os.getenv('BOX_THICKNESS', '2'))
        self.text_size = float(os.getenv('TEXT_SIZE', '0.5'))
        self.text_thickness = int(os.getenv('TEXT_THICKNESS', '1'))

        # Performance settings
        self.use_gpu = os.getenv('USE_GPU', 'True') == 'True'
        self.half_precision = os.getenv('HALF_PRECISION', 'True') == 'True'

        # Save settings
        self.save_snapshots = os.getenv('SAVE_SNAPSHOTS', 'True') == 'True'
        self.snapshot_dir = os.getenv('SNAPSHOT_DIR', 'snapshots')
        self.save_recording = os.getenv('SAVE_RECORDING', 'False') == 'True'
        self.recording_dir = os.getenv('RECORDING_DIR', 'recordings')

        # Create directories
        if self.save_snapshots:
            os.makedirs(self.snapshot_dir, exist_ok=True)
        if self.save_recording:
            os.makedirs(self.recording_dir, exist_ok=True)

        # Load YOLO model
        print(f"\n🔍 Loading YOLO model: {self.yolo_model}...")
        try:
            self.model = YOLO(self.yolo_model)
            
            # Set device
            if self.use_gpu:
                try:
                    import torch
                    if torch.cuda.is_available():
                        self.device = 'cuda'
                        print(f"✅ Using GPU: {torch.cuda.get_device_name(0)}")
                    else:
                        self.device = 'cpu'
                        print("⚠️ CUDA not available, using CPU")
                except ImportError:
                    self.device = 'cpu'
                    print("⚠️ PyTorch not installed, using CPU")
            else:
                self.device = 'cpu'
                print("ℹ️ Using CPU (GPU disabled by config)")

            # Enable half precision if supported
            if self.half_precision and self.device == 'cuda':
                self.model.fuse()
                print("✅ Half precision enabled")

            print(f"✅ Model loaded successfully!")
            print(f"   • Device: {self.device}")
            print(f"   • Model: {self.yolo_model}")
            print(f"   • Classes: {len(self.COCO_CLASSES)} COCO classes")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("💡 Make sure you have internet connection for first-time download")
            exit(1)

        # Initialize camera
        print(f"\n📷 Initializing camera (ID: {self.camera_id})...")
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            print(f"❌ Error: Cannot open camera {self.camera_id}")
            print("💡 Check camera connection and camera ID")
            exit(1)

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.camera_fps)

        # Get actual camera properties
        self.actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        print(f"✅ Camera initialized!")
        print(f"   • Resolution: {self.actual_width}x{self.actual_height}")
        print(f"   • FPS: {self.actual_fps}")

        # Video writer for recording
        self.writer = None
        self.is_recording = False
        self.recording_start_time = None

        # State variables
        self.last_detections = []
        self.frame_count = 0
        self.start_time = time.time()
        self.current_fps = 0.0
        self.detection_count = 0

        # Print configuration
        self.print_config()

    def print_config(self):
        """Print configuration."""
        print("\n" + "="*60)
        print("🎯 YOLOv8 Live Stream - Configuration")
        print("="*60)
        print(f"📷 Camera: {self.actual_width}x{self.actual_height}@{self.actual_fps}fps")
        print(f"🤖 Model: {self.yolo_model}")
        print(f"   • Confidence Threshold: {self.conf_threshold}")
        print(f"   • IoU Threshold: {self.iou_threshold}")
        if self.classes_filter:
            print(f"   • Classes Filter: {[self.COCO_CLASSES[i] for i in self.classes_filter]}")
        else:
            print(f"   • Classes: ALL (80 COCO classes)")
        print(f"💻 Device: {self.device}")
        print(f"⚡ Performance:")
        print(f"   • Half Precision: {'ON' if self.half_precision else 'OFF'}")
        print(f"   • Show FPS: {'ON' if self.show_fps else 'OFF'}")
        print(f"💾 Storage:")
        print(f"   • Snapshots: {'ON' if self.save_snapshots else 'OFF'}")
        print(f"   • Recording: {'ON' if self.save_recording else 'OFF'}")
        print("="*60)
        print("\n🎮 Controls:")
        print("   • q - Quit")
        print("   • s - Save snapshot")
        print("   • r - Start/stop recording")
        print("   • c - Change confidence threshold")
        print("   • f - Toggle class filter (person only / all)")
        print("   • + - Increase confidence")
        print("   • - - Decrease confidence")
        print("="*60 + "\n")

    def get_color(self, class_id):
        """Get color for class ID."""
        return self.COLORS[class_id % len(self.COLORS)]

    def run_detection(self, frame):
        """
        Run YOLO detection on frame.
        Returns: list of detections
        """
        # Run inference
        results = self.model(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            classes=self.classes_filter,
            verbose=False,
            device=self.device
        )

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                cls_id = int(box.cls[0].cpu().numpy())
                confidence = float(box.conf[0].cpu().numpy())

                cls_name = self.COCO_CLASSES[cls_id] if cls_id < len(self.COCO_CLASSES) else f'class_{cls_id}'

                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'class_id': cls_id,
                    'class_name': cls_name,
                    'confidence': confidence
                })

        return detections

    def draw_detections(self, frame, detections):
        """Draw detections on frame."""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            cls_id = det['class_id']
            cls_name = det['class_name']
            confidence = det['confidence']

            color = self.get_color(cls_id)
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.box_thickness)

            # Draw label
            if self.show_labels:
                label_parts = [cls_name]
                if self.show_confidence:
                    label_parts.append(f"{confidence:.2f}")
                if self.show_class_id:
                    label_parts.append(f"#{cls_id}")
                
                label = " | ".join(label_parts)

                # Calculate label size
                (label_w, label_h), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, self.text_size, self.text_thickness
                )

                # Draw label background
                cv2.rectangle(frame, (x1, y1 - label_h - baseline - 5), 
                             (x1 + label_w, y1), color, -1)
                
                # Draw label text
                cv2.putText(
                    frame, label, (x1, y1 - baseline),
                    cv2.FONT_HERSHEY_SIMPLEX, self.text_size, (255, 255, 255),
                    self.text_thickness, cv2.LINE_AA
                )

    def draw_ui(self, frame):
        """Draw UI elements."""
        frame_height, frame_width = frame.shape[:2]
        y_offset = 25

        # FPS counter
        if self.show_fps:
            fps_color = (0, 255, 0) if self.current_fps >= 25 else (0, 255, 255)
            if self.current_fps < 15:
                fps_color = (0, 0, 255)
            
            cv2.putText(
                frame, f"FPS: {self.current_fps:.1f}",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, fps_color, 2, cv2.LINE_AA
            )
            y_offset += 30

        # Detection count
        det_count = len(self.last_detections)
        cv2.putText(
            frame, f"Objects: {det_count}", (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2, cv2.LINE_AA
        )
        y_offset += 30

        # Confidence threshold
        cv2.putText(
            frame, f"Conf: {self.conf_threshold:.2f}", (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2, cv2.LINE_AA
        )
        y_offset += 30

        # Recording indicator
        if self.is_recording:
            elapsed = time.time() - self.recording_start_time
            cv2.putText(
                frame, f"● REC {elapsed:.1f}s", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA
            )

        # Device info
        cv2.putText(
            frame, f"Device: {self.device.upper()}", (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1, cv2.LINE_AA
        )

    def save_snapshot(self, frame):
        """Save snapshot."""
        if not self.save_snapshots:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.snapshot_dir, f"snapshot_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        print(f"📸 Snapshot saved: {filename}")

    def toggle_recording(self, frame):
        """Toggle video recording."""
        if not self.save_recording:
            print("⚠️ Recording is disabled in config")
            return

        if not self.is_recording:
            # Start recording
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.recording_dir, f"recording_{timestamp}.avi")
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.writer = cv2.VideoWriter(
                filename, fourcc, 
                self.actual_fps, 
                (self.actual_width, self.actual_height)
            )
            
            self.is_recording = True
            self.recording_start_time = time.time()
            print(f"🔴 Recording started: {filename}")
        else:
            # Stop recording
            if self.writer:
                self.writer.release()
                self.writer = None
            
            elapsed = time.time() - self.recording_start_time
            print(f"⬛ Recording stopped ({elapsed:.1f}s)")
            self.is_recording = False
            self.recording_start_time = None

    def adjust_confidence(self, delta):
        """Adjust confidence threshold."""
        self.conf_threshold = max(0.1, min(0.9, self.conf_threshold + delta))
        print(f"📊 Confidence threshold: {self.conf_threshold:.2f}")

    def toggle_class_filter(self):
        """Toggle class filter (person only / all classes)."""
        if self.classes_filter is None:
            # Filter to person only (class 0)
            self.classes_filter = [0]
            print("📋 Filter: PERSON only")
        else:
            # Remove filter
            self.classes_filter = None
            print("📋 Filter: ALL classes")

    def cleanup(self):
        """Cleanup resources."""
        print("\n🧹 Cleaning up...")
        
        if self.cap:
            self.cap.release()
        
        if self.writer:
            self.writer.release()
        
        cv2.destroyAllWindows()
        
        print(f"📊 Total frames processed: {self.frame_count}")
        print(f"⏱️  Total time: {time.time() - self.start_time:.1f}s")
        print(f"📈 Average FPS: {self.frame_count / (time.time() - self.start_time):.1f}")
        print("✅ Done!")

    def run(self):
        """Main loop."""
        print("\n🚀 Starting YOLOv8 Live Stream...")
        print("Press 'q' to quit\n")

        try:
            while True:
                frame_start = time.time()

                # Read frame from camera
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break

                self.frame_count += 1

                # Run detection
                self.last_detections = self.run_detection(frame)
                self.detection_count += len(self.last_detections)

                # Draw detections
                self.draw_detections(frame, self.last_detections)

                # Draw UI
                self.draw_ui(frame)

                # Record if enabled
                if self.is_recording and self.writer:
                    self.writer.write(frame)

                # Calculate FPS
                frame_time = time.time() - frame_start
                self.current_fps = 1.0 / frame_time if frame_time > 0 else 0

                # Update FPS counter every second
                if time.time() - self.start_time >= 1.0:
                    elapsed = time.time() - self.start_time
                    self.current_fps = self.frame_count / elapsed
                    self.start_time = time.time()

                # Display
                cv2.imshow('YOLOv8 Live Stream', frame)

                # Keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 Quitting...")
                    break
                elif key == ord('s'):
                    self.save_snapshot(frame)
                elif key == ord('r'):
                    self.toggle_recording(frame)
                elif key == ord('c'):
                    self.adjust_confidence(0.1)
                elif key == ord('f'):
                    self.toggle_class_filter()
                elif key == ord('+') or key == ord('='):
                    self.adjust_confidence(0.05)
                elif key == ord('-') or key == ord('_'):
                    self.adjust_confidence(-0.05)

        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    detector = YOLOLiveStream()
    detector.run()


if __name__ == "__main__":
    main()
