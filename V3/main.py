"""
YOLOv8-Nano + HyperLPR - License Plate Recognition
Real-time object detection dengan YOLOv8-nano + HyperLPR untuk plat nomor

Fitur:
- YOLOv8-nano: 3.2M parameters, ~12MB, real-time inference
- HyperLPR3: Dedicated license plate recognition (100% offline)
- Vehicle detection mode: ON/OFF via ENV
- Multi-object tracking
- Memory management otomatis
"""

import os
import cv2
import warnings
import time
import gc
import re
from dotenv import load_dotenv

try:
    from ultralytics import YOLO
except ImportError:
    print("❌ ultralytics tidak terinstall. Jalankan: pip install ultralytics")
    exit(1)

# PaddleOCR will be imported lazily (fallback only)
PaddleOCR = None

# Load konfigurasi
load_dotenv()

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
os.environ['SUPPRESS_DEPRECATION_WARNINGS'] = '1'


class LPREngine:
    """
    License Plate Recognition Engine
    Primary: HyperLPR (optimized for license plates)
    Fallback: PaddleOCR (general OCR)
    Fully offline after first model download.
    """
    
    def __init__(self, engine='hyperlpr', country='id'):
        self.engine = engine
        self.country = country
        self.model = None
        self._initialized = False
        
        # Indonesia plate pattern
        self.plate_pattern = re.compile(r'^[A-Z]{1,2}\s?\d{3,4}\s?[A-Z]{0,3}$')
        
    def initialize(self):
        """Initialize LPR engine (lazy load)"""
        if self._initialized:
            return True
        
        # Try primary engine first
        if self.engine == 'hyperlpr':
            if self._init_hyperlpr():
                return True
        
        # Fallback to PaddleOCR
        print(f"[LPR] Falling back to PaddleOCR...")
        return self._init_paddleocr()
    
    def _init_hyperlpr(self):
        """Initialize HyperLPR backend (primary choice)"""
        try:
            import hyperlpr3 as hpr
            self.model = hpr
            self._initialized = True
            print("[LPR] ✅ HyperLPR engine initialized (OPTIMAL)")
            return True
        except ImportError:
            print("[LPR] ⚠️ HyperLPR not installed (pip install hyperlpr3)")
            return False
        except Exception as e:
            print(f"[LPR] ⚠️ HyperLPR init error: {e}")
            return False
    
    def _init_paddleocr(self):
        """Initialize PaddleOCR backend (fallback)"""
        try:
            if PaddleOCR is None:
                from paddleocr import PaddleOCR as OCRClass
                globals()['PaddleOCR'] = OCRClass

            # PaddleOCR newer versions don't support 'log' parameter
            self.model = PaddleOCR(lang='en')
            self._initialized = True
            print("[LPR] PaddleOCR engine initialized (FALLBACK)")
            return True
        except Exception as e:
            print(f"[LPR] PaddleOCR init error: {e}")
            return False
    
    def recognize(self, plate_image):
        """
        Recognize license plate from image.
        Returns: (plate_number, confidence)
        """
        if not self._initialized:
            if not self.initialize():
                return None, 0.0
        
        # Use HyperLPR if available
        if self.engine == 'hyperlpr' and hasattr(self.model, 'LicensePlateCatcher'):
            return self._recognize_hyperlpr(plate_image)
        else:
            return self._recognize_paddleocr(plate_image)
    
    def _recognize_hyperlpr(self, plate_image):
        """Recognize plate using HyperLPR"""
        try:
            from hyperlpr3 import LicensePlateCatcher
            catcher = LicensePlateCatcher()
            # HyperLPR3 uses __call__ method, not recognize()
            results = catcher(plate_image)

            if results and len(results) > 0:
                # Get best result
                best = results[0]
                # HyperLPR3 returns tuple: (plate_text, confidence)
                if isinstance(best, (list, tuple)) and len(best) >= 2:
                    plate_text = str(best[0]).upper()
                    confidence = float(best[1])
                else:
                    plate_text = str(best).upper()
                    confidence = 0.5
                return plate_text, confidence
        except Exception as e:
            print(f"[LPR] HyperLPR recognition error: {e}")

        return None, 0.0
    
    def _recognize_paddleocr(self, plate_image):
        """Recognize plate using PaddleOCR"""
        try:
            # PaddleOCR newer versions return dict with 'rec_texts', 'rec_scores', etc.
            result = self.model.predict(plate_image)
            
            if result and len(result) > 0:
                first_result = result[0]
                
                # Check if it's a dict (newer API)
                if isinstance(first_result, dict):
                    rec_texts = first_result.get('rec_texts', [])
                    rec_scores = first_result.get('rec_scores', [])
                    
                    if rec_texts and rec_scores:
                        # Get best result
                        best_idx = 0
                        best_score = max(rec_scores)
                        best_text = rec_texts[best_idx].strip().upper()
                        
                        # Validate plate format
                        if self.plate_pattern.match(best_text):
                            return best_text, best_score
                        else:
                            return best_text, best_score
            
            return None, 0.0

        except Exception as e:
            print(f"[LPR] PaddleOCR recognition error: {e}")

        return None, 0.0
    
    def validate_plate(self, plate_text):
        """Validate plate format (Indonesia)"""
        if not plate_text:
            return False
        return bool(self.plate_pattern.match(plate_text.upper()))


class YOLOv8ObjectDetector:
    """Main class untuk YOLOv8 Object Detection + LPR."""

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

    # Warna untuk setiap kelas (RGB)
    COLORS = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255),
        (0, 255, 255), (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0),
        (128, 0, 128), (0, 128, 128), (255, 128, 0), (255, 0, 128), (128, 255, 0),
        (0, 255, 128), (128, 0, 255), (0, 128, 255), (255, 255, 128), (255, 128, 255)
    ]

    def __init__(self):
        # Load konfigurasi dari environment
        self.camera_width = int(os.getenv('CAMERA_WIDTH', '640'))
        self.camera_height = int(os.getenv('CAMERA_HEIGHT', '480'))
        self.camera_fps = int(os.getenv('CAMERA_FPS', '30'))

        # YOLO Model
        self.yolo_model = os.getenv('YOLO_MODEL', 'yolov8n.pt')
        self.yolo_conf_threshold = float(os.getenv('YOLO_CONF_THRESHOLD', '0.4'))
        self.yolo_iou_threshold = float(os.getenv('YOLO_IOU_THRESHOLD', '0.45'))

        # Vehicle Detection Mode
        self.vehicle_detection_active = os.getenv('VEHICLE_DETECTION_ACTIVE', 'False') == 'True'
        
        # Object Classes Filter
        classes_filter = os.getenv('YOLO_CLASSES_FILTER', '')
        if self.vehicle_detection_active:
            # Filter untuk kendaraan saja
            self.classes_filter = [int(x.strip()) for x in classes_filter.split(',') if x.strip()]
        else:
            # Semua kelas (untuk testing plat langsung)
            self.classes_filter = None

        # LPR Settings
        self.lpr_active = os.getenv('LPR_ACTIVE', 'True') == 'True'
        self.lpr_engine_name = os.getenv('LPR_ENGINE', 'hyperlpr')
        self.lpr_detection_mode = os.getenv('LPR_DETECTION_MODE', 'FULL_FRAME')  # FULL_FRAME or DETECTION_BASED
        self.lpr_min_plate_area = int(os.getenv('LPR_MIN_PLATE_AREA', '500'))
        self.lpr_max_plate_aspect = float(os.getenv('LPR_MAX_PLATE_ASPECT', '5.0'))
        self.lpr_min_plate_aspect = float(os.getenv('LPR_MIN_PLATE_ASPECT', '1.5'))
        self.lpr_validate_plate = os.getenv('LPR_VALIDATE_PLATE', 'True') == 'True'
        self.lpr_country = os.getenv('LPR_PLATE_COUNTRY', 'id')
        
        # Full frame LPR interval (process every N frames)
        self.lpr_interval = 2  # Process full frame every 2 frames (more frequent for testing)

        # Cell Phone OCR Settings
        self.phone_ocr_active = os.getenv('PHONE_OCR_ACTIVE', 'True') == 'True'
        self.phone_ocr_interval = int(os.getenv('PHONE_OCR_INTERVAL', '3'))
        self.ocr_enabled = os.getenv('OCR_ENABLED', 'True') == 'True'
        self.ocr_on_classes = os.getenv('OCR_ON_CLASSES', 'cell phone,book,laptop').split(',')
        self.ocr_scale = float(os.getenv('OCR_SCALE', '1.0'))
        
        # Auto Capture Settings
        self.stop_camera_when_detect = os.getenv('STOP_CAMERA_WHEN_DETECT', 'False') == 'True'
        self.auto_capture_ocr = os.getenv('AUTO_CAPTURE_OCR', 'True') == 'True'
        
        # Capture & OCR Settings
        self.capture_and_ocr = False  # Trigger for capture+OCR mode
        self.captured_image = None
        self.capture_ocr_result = None
        self.camera_stopped = False  # Camera freeze state

        # Display
        self.show_fps = os.getenv('SHOW_FPS', 'True') == 'True'
        self.show_confidence = os.getenv('SHOW_CONFIDENCE', 'True') == 'True'
        self.show_class_id = os.getenv('SHOW_CLASS_ID', 'False') == 'True'
        self.show_ocr_result = os.getenv('SHOW_OCR_RESULT', 'True') == 'True'
        self.text_size = float(os.getenv('TEXT_SIZE', '0.5'))
        self.text_thickness = int(os.getenv('TEXT_THICKNESS', '1'))
        self.box_thickness = int(os.getenv('BOX_THICKNESS', '2'))

        # Performance
        self.frame_skip = int(os.getenv('FRAME_SKIP', '1'))
        self.debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        self.enable_memory_cleanup = os.getenv('ENABLE_MEMORY_CLEANUP', 'True') == 'True'
        self.memory_cleanup_interval = int(os.getenv('MEMORY_CLEANUP_INTERVAL', '30'))

        # Tracking
        self.enable_tracking = os.getenv('ENABLE_TRACKING', 'True') == 'True'
        self.tracker_type = os.getenv('TRACKER_TYPE', 'bytetrack.yaml')

        # Inisialisasi YOLO model
        print(f"🔍 Loading YOLOv8 model: {self.yolo_model}...")
        try:
            self.model = YOLO(self.yolo_model)
            print(f"✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("💡 Pastikan internet aktif untuk download model pertama kali")
            exit(1)

        # Inisialisasi LPR Engine
        self.lpr = None
        if self.lpr_active:
            print("🚗 Initializing LPR Engine...")
            print(f"   • Engine: {self.lpr_engine_name}")
            print(f"   • Detection Mode: {self.lpr_detection_mode}")
            print(f"   • Validate Plate: {'ON' if self.lpr_validate_plate else 'OFF'}")
            try:
                self.lpr = LPREngine(engine=self.lpr_engine_name, country=self.lpr_country)
                if self.lpr.initialize():
                    print("✅ LPR Engine ready!")
                else:
                    print("⚠️ LPR Engine failed to initialize")
                    self.lpr = None
            except Exception as e:
                print(f"⚠️ LPR Engine init error: {e}")
                self.lpr = None

        # Inisialisasi PaddleOCR untuk General OCR (cell phone, book, dll)
        self.ocr = None
        if self.ocr_enabled and self.phone_ocr_active:
            print("Initializing PaddleOCR for general OCR...")
            try:
                if PaddleOCR is None:
                    from paddleocr import PaddleOCR as OCRClass
                    globals()['PaddleOCR'] = OCRClass
                # PaddleOCR newer versions don't support 'log' parameter
                self.ocr = PaddleOCR(lang='en')
                print("[OK] PaddleOCR ready!")
            except Exception as e:
                print(f"[WARN] PaddleOCR init error: {e}")
                print("   [INFO] PaddleOCR will not be available for general OCR")
                self.ocr = None

        # Inisialisasi kamera
        print("📷 Initializing camera...")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.camera_fps)

        if not self.cap.isOpened():
            print("❌ Error: Cannot open camera")
            exit(1)

        # State variables
        self.last_detections = []
        self.lpr_results = {}
        self.frame_count = 0

        # FPS counter
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0

        # Memory cleanup
        self.last_cleanup_time = time.time()
        self.cleanup_count = 0

        # Print konfigurasi
        self.print_config()

    def print_config(self):
        """Print konfigurasi."""
        print("\n" + "="*60)
        print("🎯 YOLOv8-Nano + HyperLPR - Configuration")
        print("="*60)
        print(f"📷 Camera: {self.camera_width}x{self.camera_height}@{self.camera_fps}fps")
        print(f"🤖 YOLO Model: {self.yolo_model}")
        print(f"   • Confidence Threshold: {self.yolo_conf_threshold}")
        print(f"   • IoU Threshold: {self.yolo_iou_threshold}")
        
        # Vehicle Detection Mode
        print(f"🚗 Vehicle Detection: {'ACTIVE' if self.vehicle_detection_active else 'INACTIVE'}")
        if self.vehicle_detection_active:
            print(f"   • Classes: car, motorcycle, bus, truck")
        else:
            print(f"   • Mode: ALL OBJECTS (80 COCO classes)")
        
        # LPR Mode
        print(f"📝 LPR Mode: {'ACTIVE' if self.lpr_active else 'INACTIVE'}")
        if self.lpr_active:
            print(f"   • Detection Mode: {self.lpr_detection_mode}")
            print(f"   • Engine: {self.lpr_engine_name}")
            print(f"   • Validate Plate: {'ON' if self.lpr_validate_plate else 'OFF'}")
        
        # Phone OCR
        print(f"📱 Phone OCR: {'ACTIVE' if self.phone_ocr_active else 'INACTIVE'}")
        if self.phone_ocr_active:
            print(f"   • Classes: {', '.join(self.ocr_on_classes)}")
        
        # Auto Capture
        print(f"📸 Auto Capture: {'ACTIVE' if self.auto_capture_ocr else 'INACTIVE'}")
        if self.auto_capture_ocr:
            print(f"   • Stop Camera on Detect: {'ON' if self.stop_camera_when_detect else 'OFF'}")
        
        # Capture & OCR
        print(f"📸 Manual Capture: ENABLED (press 'c')")
        
        print(f"⚡ Performance:")
        print(f"   • Frame Skip: {self.frame_skip}")
        print(f"   • Tracking: {'ENABLED' if self.enable_tracking else 'DISABLED'}")
        print("="*60 + "\n")

    def get_color(self, class_id):
        """Dapatkan warna untuk class ID."""
        return self.COLORS[class_id % len(self.COLORS)]

    def extract_plate_region(self, frame, bbox):
        """
        Extract region plat nomor dari bounding box kendaraan.
        Fokus pada bagian bawah kendaraan (area plat nomor).
        """
        x1, y1, x2, y2 = bbox
        
        # Ambil bagian bawah bounding box (area plat nomor)
        h = y2 - y1
        plate_y1 = y1 + int(h * 0.5)  # Mulai dari 50% bawah
        plate_y2 = y2
        
        plate_roi = frame[plate_y1:plate_y2, x1:x2]
        
        if plate_roi.size == 0:
            return None
        
        return plate_roi

    def run_lpr_full_frame(self, frame):
        """
        Scan seluruh frame untuk deteksi teks/plat nomor.
        Returns: list of (text, confidence, bbox)
        """
        if not self.lpr or not self.lpr_active:
            if self.debug_mode:
                print("[LPR-FULL] LPR not active or not initialized")
            return []

        results = []

        # Run LPR on full frame
        try:
            if self.lpr_engine_name == 'hyperlpr' and hasattr(self.lpr.model, 'LicensePlateCatcher'):
                from hyperlpr3 import LicensePlateCatcher
                catcher = LicensePlateCatcher()
                # HyperLPR3 uses __call__ method, not recognize()
                lpr_results = catcher(frame)

                if lpr_results:
                    for result in lpr_results:
                        # HyperLPR3 returns tuple: (plate_text, confidence, bbox)
                        if isinstance(result, (list, tuple)) and len(result) >= 2:
                            plate_text = str(result[0]).upper()
                            confidence = float(result[1])
                            bbox = result[2] if len(result) > 2 else None
                        else:
                            plate_text = str(result).upper()
                            confidence = 0.5
                            bbox = None

                        # Validate if enabled
                        if self.lpr_validate_plate:
                            if self.lpr.validate_plate(plate_text):
                                results.append((f"{plate_text} ({confidence:.2f})", confidence, bbox))
                                print(f"[LPR-FULL] Plate: {plate_text} (conf: {confidence:.2f})")
                            else:
                                results.append((f"{plate_text}? ({confidence:.2f})", confidence, bbox))
                                print(f"[LPR-FULL] Plate (invalid): {plate_text}? (conf: {confidence:.2f})")
                        else:
                            results.append((f"{plate_text} ({confidence:.2f})", confidence, bbox))
                            print(f"[LPR-FULL] Plate: {plate_text} (conf: {confidence:.2f})")
                else:
                    # No plates detected - log for debugging
                    if self.debug_mode:
                        print("[LPR-FULL] No plates detected in frame")
            else:
                # Fallback to PaddleOCR (newer API returns dict with 'rec_texts', 'rec_scores', 'rec_polys')
                lpr_results = self.lpr.model.predict(frame)
                if lpr_results and len(lpr_results) > 0:
                    first_result = lpr_results[0]
                    if isinstance(first_result, dict):
                        rec_texts = first_result.get('rec_texts', [])
                        rec_scores = first_result.get('rec_scores', [])
                        rec_polys = first_result.get('rec_polys', [])
                        
                        for i, (text, score) in enumerate(zip(rec_texts, rec_scores)):
                            text = text.strip().upper()
                            bbox = rec_polys[i] if i < len(rec_polys) else None
                            
                            if text:
                                if self.lpr_validate_plate and self.lpr.validate_plate(text):
                                    results.append((f"{text} ({score:.2f})", score, bbox))
                                    print(f"[LPR-FULL] Plate: {text} (conf: {score:.2f})")
                                elif not self.lpr_validate_plate:
                                    results.append((f"{text} ({score:.2f})", score, bbox))
                                    print(f"[LPR-FULL] Text: {text} (conf: {score:.2f})")
                else:
                    # No text detected - log for debugging
                    if self.debug_mode:
                        print("[LPR-FULL] No text detected in frame (PaddleOCR)")
        except Exception as e:
            print(f"[LPR] Full frame error: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()

        return results

    def run_ocr_on_object(self, frame, detection):
        """
        Run OCR on detected object (cell phone, book, laptop, etc.)
        Returns: OCR text result
        """
        if not self.ocr:
            return None
        
        x1, y1, x2, y2 = detection['bbox']
        class_name = detection['class_name']
        
        # Cek apakah kelas ini perlu di-OCR
        if class_name.lower() not in [c.lower().strip() for c in self.ocr_on_classes]:
            return None
        
        # Crop object
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return None
        
        # Resize jika perlu
        if self.ocr_scale != 1.0:
            h, w = roi.shape[:2]
            roi = cv2.resize(roi, (int(w * self.ocr_scale), int(h * self.ocr_scale)))
        
        # Run OCR
        try:
            # PaddleOCR newer versions use predict() instead of ocr()
            result = self.ocr.predict(roi)

            if not result or len(result) == 0:
                return None

            first_result = result[0]
            if isinstance(first_result, dict):
                rec_texts = first_result.get('rec_texts', [])
                rec_scores = first_result.get('rec_scores', [])
                
                if rec_texts and rec_scores:
                    # Join all detected texts
                    all_text = " | ".join([t.strip() for t in rec_texts[:3]])  # Max 3 texts
                    avg_score = sum(rec_scores) / len(rec_scores)

                    # Log to console
                    track_id = detection.get('track_id', 'N/A')
                    print(f"[OCR] Text detected on {class_name} [ID:{track_id}]: {all_text} (conf: {avg_score:.2f})")

                    return f"{all_text} ({avg_score:.2f})"
                
        except Exception as e:
            if self.debug_mode:
                print(f"[OCR] Error: {e}")
        
        return None

    def capture_and_ocr_image(self, frame):
        """
        Capture image from camera, run OCR on full image, display result.
        Returns: (captured_image, ocr_results)
        """
        print("\n" + "="*60)
        print("📸 CAPTURE & OCR - Processing...")
        print("="*60)
        
        # Save captured image
        self.captured_image = frame.copy()
        
        results = []
        
        # Run LPR on full image
        if self.lpr and self.lpr_active:
            print("[CAPTURE] Running LPR on captured image...")
            lpr_results = self.run_lpr_full_frame(frame)
            if lpr_results:
                results.extend(lpr_results)
                print(f"[CAPTURE] ✅ Found {len(lpr_results)} plate(s)/text(s)")
        
        # Run OCR on detected objects
        if self.ocr and self.phone_ocr_active:
            print("[CAPTURE] Running OCR on detected objects...")
            detections = self.run_yolo_detection(frame)
            for det in detections:
                ocr_text = self.run_ocr_on_object(frame, det)
                if ocr_text:
                    results.append((ocr_text, 0.0, det['bbox']))
                    print(f"[CAPTURE] ✅ Found text on {det['class_name']}: {ocr_text}")
        
        self.capture_ocr_result = results
        
        print("="*60)
        print(f"[CAPTURE] Total results: {len(results)}")
        print("="*60 + "\n")
        
        return self.captured_image, results

    def run_yolo_detection(self, frame):
        """
        Jalankan YOLOv8 detection pada frame.
        Returns: list of detections
        """
        # Run inference
        if self.enable_tracking and self.vehicle_detection_active:
            results = self.model.track(
                frame,
                conf=self.yolo_conf_threshold,
                iou=self.yolo_iou_threshold,
                classes=self.classes_filter,
                tracker=self.tracker_type,
                verbose=False
            )
        else:
            results = self.model(
                frame,
                conf=self.yolo_conf_threshold,
                iou=self.yolo_iou_threshold,
                classes=self.classes_filter,
                verbose=False
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

                track_id = None
                if hasattr(box, 'id') and box.id is not None:
                    track_id = int(box.id[0].cpu().numpy())

                cls_name = self.COCO_CLASSES[cls_id] if cls_id < len(self.COCO_CLASSES) else f'class_{cls_id}'
                
                # Log vehicle detection
                if cls_name in ['car', 'motorcycle', 'bus', 'truck']:
                    print(f"[YOLO] 🚗 Vehicle detected: {cls_name} (conf: {confidence:.2f}) [ID:{track_id}]")
                
                # Log cell phone detection
                if cls_name == 'cell phone':
                    print(f"[YOLO] 📱 Cell phone detected (conf: {confidence:.2f}) [ID:{track_id}]")

                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'class_id': cls_id,
                    'class_name': cls_name,
                    'confidence': confidence,
                    'track_id': track_id
                })

        return detections

    def run_lpr_on_detection(self, frame, detection):
        """
        Jalankan LPR pada ROI dari detection.
        Returns: OCR text result
        """
        x1, y1, x2, y2 = detection['bbox']
        class_name = detection['class_name']

        # Vehicle Detection Mode: Extract plate from vehicle
        if self.vehicle_detection_active:
            vehicle_classes = ['car', 'motorcycle', 'bus', 'truck']
            if class_name.lower() not in vehicle_classes:
                return None
            
            roi = self.extract_plate_region(frame, detection['bbox'])
            if roi is None:
                return None
        else:
            # Direct Mode: Run LPR on any detected object
            roi = frame[y1:y2, x1:x2]
            if roi.size == 0:
                return None

        # Run LPR
        if self.lpr and self.lpr_active:
            plate_text, confidence = self.lpr.recognize(roi)
            
            if plate_text:
                # Log to console
                track_id = detection.get('track_id', 'N/A')
                print(f"[LPR] 🚗 Plate detected on {class_name} [ID:{track_id}]: {plate_text} (conf: {confidence:.2f})")
                
                if self.lpr_validate_plate:
                    if self.lpr.validate_plate(plate_text):
                        return f"{plate_text} ({confidence:.2f})"
                    else:
                        return f"{plate_text}? ({confidence:.2f})"
                else:
                    return f"{plate_text} ({confidence:.2f})"
        
        return None

    def draw_detections(self, frame, detections):
        """Gambar detections pada frame."""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            cls_id = det['class_id']
            cls_name = det['class_name']
            confidence = det['confidence']
            track_id = det['track_id']

            color = self.get_color(cls_id)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.box_thickness)

            # Label
            label_parts = [cls_name]
            if self.show_confidence:
                label_parts.append(f"{confidence:.2f}")
            label = " | ".join(label_parts)

            if track_id is not None and self.enable_tracking:
                label += f" [ID:{track_id}]"

            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, self.text_size, self.text_thickness
            )
            cv2.rectangle(frame, (x1, y1 - label_h - baseline - 5), (x1 + label_w, y1), color, -1)
            cv2.putText(
                frame, label, (x1, y1 - baseline),
                cv2.FONT_HERSHEY_SIMPLEX, self.text_size, (255, 255, 255),
                self.text_thickness, cv2.LINE_AA
            )

            # LPR Result
            if self.show_ocr_result and track_id is not None and track_id in self.lpr_results:
                lpr_text = self.lpr_results[track_id]
                if lpr_text:
                    cv2.putText(
                        frame, f"Plate: {lpr_text}", (x1, y2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA
                    )
            
            # Cell Phone / General OCR Result
            if self.show_ocr_result and track_id is not None and track_id in self.phone_ocr_results:
                ocr_text = self.phone_ocr_results[track_id]
                if ocr_text:
                    cv2.putText(
                        frame, f"Text: {ocr_text}", (x1, y2 + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv2.LINE_AA
                    )

    def draw_ui(self, frame):
        """Gambar UI elements."""
        frame_height, frame_width = frame.shape[:2]

        if self.show_fps:
            fps_color = (0, 255, 0) if self.current_fps >= self.camera_fps * 0.9 else (0, 255, 255)
            cv2.putText(
                frame, f"FPS: {self.current_fps:.1f}",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, fps_color, 1, cv2.LINE_AA
            )

        det_count = len(self.last_detections)
        mode_text = "VEHICLE MODE" if self.vehicle_detection_active else "FREE MODE"
        lpr_mode = "FULL-FRAME" if self.lpr_detection_mode == 'FULL_FRAME' else "DETECT-BASED"
        cv2.putText(
            frame, f"Objects: {det_count} | {mode_text} | LPR: {lpr_mode}",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA
        )

    def draw_full_frame_lpr(self, frame, results):
        """
        Draw full-frame LPR results on frame.
        results: list of (text, confidence, bbox)
        """
        if not results:
            return
        
        frame_height, frame_width = frame.shape[:2]
        
        # Draw each detected plate/text
        for i, (text, confidence, bbox) in enumerate(results):
            # Draw on bottom of frame
            y_offset = frame_height - 30 - (i * 25)
            
            # Background
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, y_offset - 20), (frame_width, y_offset + 5), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # Text
            cv2.putText(
                frame, f"Plate: {text}", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA
            )
            
            # Draw bounding box if available
            if bbox is not None:
                try:
                    x1, y1, x2, y2 = map(int, bbox)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                except:
                    pass

    def draw_capture_results(self, frame, results):
        """
        Draw capture & OCR results on captured image.
        results: list of (text, confidence, bbox)
        """
        if not results:
            # Show "no results" message
            frame_height, frame_width = frame.shape[:2]
            cv2.putText(
                frame, "No text/plate detected - Press 'x' to return", (10, frame_height - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA
            )
            return
        
        frame_height, frame_width = frame.shape[:2]
        
        # Draw title
        cv2.putText(
            frame, "=== CAPTURE & OCR RESULT ===", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA
        )
        
        # Draw each detected plate/text
        for i, (text, confidence, bbox) in enumerate(results):
            y_offset = 60 + (i * 35)
            
            # Background bar
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, y_offset - 25), (frame_width, y_offset + 10), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            # Text
            cv2.putText(
                frame, f"[{i+1}] {text}", (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA
            )
            
            # Draw bounding box if available
            if bbox is not None:
                try:
                    x1, y1, x2, y2 = map(int, bbox)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                except:
                    pass
        
        # Instructions
        instr_y = frame_height - 30
        cv2.putText(
            frame, "Press 'x' to return to live view", (10, instr_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA
        )

    def memory_cleanup(self):
        """Lakukan memory cleanup."""
        if self.enable_memory_cleanup:
            current_time = time.time()
            if current_time - self.last_cleanup_time >= self.memory_cleanup_interval:
                if len(self.lpr_results) > 50:
                    keys = list(self.lpr_results.keys())
                    for key in keys[:len(keys)//2]:
                        del self.lpr_results[key]
                gc.collect()
                self.cleanup_count += 1
                self.last_cleanup_time = current_time

    def run(self):
        """Main loop."""
        print("\n🚀 Starting YOLOv8-Nano + HyperLPR...")
        print("Press 'q' to exit, 'c' to capture+OCR, 's' to save snapshot, 'v' to toggle vehicle mode, 'f' to toggle full-frame LPR\n")

        # Full-frame LPR results
        self.full_frame_lpr_results = []
        
        # Cell phone OCR results
        self.phone_ocr_results = {}
        
        # Capture mode
        self.capture_and_ocr = False
        self.captured_image = None
        self.capture_ocr_result = None
        self.show_capture_result = False
        self.camera_stopped = False

        while True:
            loop_start = time.time()

            # Read frame from camera (unless camera is stopped)
            if not self.camera_stopped:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break
            else:
                # Use captured image if camera stopped
                if self.captured_image is not None:
                    frame = self.captured_image.copy()
                else:
                    ret, frame = self.cap.read()
                    if not ret:
                        print("❌ Failed to read frame")
                        break

            self.frame_count += 1

            # FPS counter
            self.fps_counter += 1
            if time.time() - self.fps_start_time >= 1.0:
                self.current_fps = self.fps_counter / (time.time() - self.fps_start_time)
                self.fps_counter = 0
                self.fps_start_time = time.time()

            # Handle capture mode (manual trigger with 'c')
            if self.capture_and_ocr:
                self.captured_image, self.capture_ocr_result = self.capture_and_ocr_image(frame)
                self.show_capture_result = True
                self.capture_and_ocr = False
            
            # Show capture result mode
            if self.show_capture_result and self.captured_image is not None:
                display_frame = self.captured_image.copy()
                self.draw_capture_results(display_frame, self.capture_ocr_result)
            else:
                # Normal mode - YOLO Detection
                if self.frame_count % (self.frame_skip + 1) == 0:
                    self.last_detections = self.run_yolo_detection(frame)

                    # Run LPR on detections
                    for det in self.last_detections:
                        track_id = det['track_id']
                        if track_id is not None and track_id not in self.lpr_results:
                            lpr_text = self.run_lpr_on_detection(frame, det)
                            if lpr_text:
                                self.lpr_results[track_id] = lpr_text
                    
                    # Run OCR on cell phone / other objects
                    if self.ocr_enabled and self.phone_ocr_active:
                        if self.frame_count % self.phone_ocr_interval == 0:
                            for det in self.last_detections:
                                track_id = det['track_id']
                                class_name = det['class_name'].lower()
                                
                                # Check if this object should be OCR'd
                                if class_name in [c.lower().strip() for c in self.ocr_on_classes]:
                                    # Auto capture if enabled and camera not stopped
                                    if self.auto_capture_ocr and not self.camera_stopped and self.stop_camera_when_detect:
                                        # Trigger auto capture
                                        print(f"\n[AUTO CAPTURE] 📱 {class_name} detected! Capturing for OCR...")
                                        self.captured_image = frame.copy()
                                        self.camera_stopped = True
                                        self.capture_ocr_result = []
                                        
                                        # Run OCR immediately
                                        ocr_text = self.run_ocr_on_object(frame, det)
                                        if ocr_text:
                                            self.capture_ocr_result.append((ocr_text, 0.0, det['bbox']))
                                            print(f"[AUTO CAPTURE] ✅ Text found: {ocr_text}")
                                        
                                        self.show_capture_result = True
                                        print("[AUTO CAPTURE] Camera stopped. Press 'x' to resume.\n")
                                    
                                    # Normal OCR processing
                                    elif track_id is not None and track_id not in self.phone_ocr_results:
                                        ocr_text = self.run_ocr_on_object(frame, det)
                                        if ocr_text:
                                            self.phone_ocr_results[track_id] = ocr_text
                                    elif track_id is None:
                                        # No tracking - run OCR anyway for every detection
                                        ocr_text = self.run_ocr_on_object(frame, det)
                                        if ocr_text:
                                            # Use bbox as key instead of track_id
                                            bbox_key = str(det['bbox'])
                                            self.phone_ocr_results[bbox_key] = ocr_text
                                            # Print OCR result to console
                                            print(f"[OCR] 📱 Text detected on {class_name}: {ocr_text}")

                # Full-Frame LPR (scan entire frame for plates/text)
                if self.lpr_detection_mode == 'FULL_FRAME' and self.frame_count % self.lpr_interval == 0:
                    if self.debug_mode:
                        print(f"\n[LPR-FULL] 🔍 Running full-frame LPR (frame {self.frame_count})...")
                    self.full_frame_lpr_results = self.run_lpr_full_frame(frame)
                    if self.full_frame_lpr_results:
                        print(f"[LPR-FULL] ✅ Found {len(self.full_frame_lpr_results)} plate(s)/text(s)")
                    elif self.debug_mode:
                        print(f"[LPR-FULL] ❌ No plates/text found in frame {self.frame_count}")

                # Draw detections
                self.draw_detections(frame, self.last_detections)

                # Draw full-frame LPR results
                self.draw_full_frame_lpr(frame, self.full_frame_lpr_results)

                # Draw UI
                self.draw_ui(frame)

                display_frame = frame

            # Display
            cv2.imshow('YOLOv8-Nano + HyperLPR', display_frame)

            # Memory cleanup
            self.memory_cleanup()

            # Keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                # Trigger capture + OCR
                self.capture_and_ocr = True
                print("\n[INPUT] 📸 Capture triggered!")
            elif key == ord('s'):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"snapshot_{timestamp}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"📸 Snapshot saved: {filename}")
            elif key == ord('v'):
                self.vehicle_detection_active = not self.vehicle_detection_active
                mode = "VEHICLE" if self.vehicle_detection_active else "FREE"
                print(f"🚗 Vehicle Detection: {mode} MODE")
            elif key == ord('f'):
                if self.lpr_detection_mode == 'FULL_FRAME':
                    self.lpr_detection_mode = 'DETECTION_BASED'
                    print("📝 LPR Mode: DETECTION_BASED (only on detected objects)")
                else:
                    self.lpr_detection_mode = 'FULL_FRAME'
                    print("📝 LPR Mode: FULL_FRAME (scan entire frame)")
            elif key == ord('x'):
                # Resume camera / Close capture result
                if self.camera_stopped:
                    self.camera_stopped = False
                    self.show_capture_result = False
                    print("[INPUT] 📷 Camera resumed - Live view")
                else:
                    self.show_capture_result = False
                    self.captured_image = None
                    self.capture_ocr_result = None
                    print("[INPUT] Back to live view")

        self.cleanup()

    def cleanup(self):
        """Cleanup resources."""
        print("\n🧹 Cleaning up...")
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        gc.collect()
        print(f"Total memory cleanups: {self.cleanup_count}")
        print("✅ Done!")


def main():
    """Main entry point."""
    detector = YOLOv8ObjectDetector()
    detector.run()


if __name__ == "__main__":
    main()
