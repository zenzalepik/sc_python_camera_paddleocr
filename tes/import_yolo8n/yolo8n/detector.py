"""
YOLOv8n Full Detector - Reusable Component
Deteksi object real-time dengan semua fitur dari main.py:
- Object detection & tracking
- Distance tracking (mendekat/menjauh)
- SIAGA system
- Parking session (4 fase)
- UI overlays lengkap

Usage:
    from detector import YOLOFullDetector
    
    detector = YOLOFullDetector(camera_id=0)
    frame, state = detector.get_frame()  # Get frame dengan semua state
    # atau
    detector.run()  # Run standalone
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime
from enum import Enum
import os
import json


# ============================================================================
# CONFIGURATION - Default values (bisa di-override via constructor)
# ============================================================================
DEFAULT_CONFIG = {
    'CLEAN_UI': False,
    'CAMERA_WIDTH': 640,
    'CAMERA_HEIGHT': 480,
    'YOLO_SKIP_FRAMES': 2,
    'YOLO_ENABLED_DEFAULT': True,
    'YOLO_CONFIDENCE_THRESHOLD': 0.5,
    'TARGET_CLASSES': [0],  # person
    'MAX_HISTORY': 30,
    'SIAGA_FRAME_THRESHOLD': 3,
    'SIAGA_HOLD_TIME': 3.0,
    'FASE1_TARGET': 3,
    'FASE2_TARGET': 5,
    'FASE3_TARGET': 3,
    'FASE4_TARGET': 3,
    'WINDOW_SCALE': 1.0,
    'SHOW_FPS': True,
}


# ============================================================================
# ENUMS
# ============================================================================
class ParkingPhase(Enum):
    """Enum untuk fase-fase dalam parking session."""
    NO_VEHICLE = 0
    FASE1_SIAGA = 1
    FASE2_TETAP = 2
    FASE3_LOOP = 3
    FASE4_TAP = 4
    PREVIEW_READY = 5


# ============================================================================
# PARKING SESSION MANAGER
# ============================================================================
class ParkingSession:
    """Manager untuk parking session dengan 4 fase capture."""

    def __init__(self, config=None):
        self.config = config or DEFAULT_CONFIG
        self.phase = ParkingPhase.NO_VEHICLE
        self.session_id = None
        self.session_start_time = None
        self.vehicle_id = None
        self.vehicle_class = None
        self.capture_base_path = "captures"

        self.fase1_count = 0
        self.fase2_count = 0
        self.fase3_count = 0
        self.fase4_count = 0

        self.fase1_target = self.config['FASE1_TARGET']
        self.fase2_target = self.config['FASE2_TARGET']
        self.fase3_target = self.config['FASE3_TARGET']
        self.fase4_target = self.config['FASE4_TARGET']

        self.fase1_frames = []
        self.fase2_frames = []
        self.fase3_frames = []
        self.fase4_frames = []

        self.is_active = False
        self.last_vehicle_id = None

    def start_session(self, vehicle_id, vehicle_class="UNKNOWN"):
        """Start parking session baru."""
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start_time = datetime.now()
        self.vehicle_id = vehicle_id
        self.vehicle_class = vehicle_class
        self.phase = ParkingPhase.FASE1_SIAGA
        self.is_active = True
        self.fase1_count = 0
        self.fase2_count = 0
        self.fase3_count = 0
        self.fase4_count = 0
        self.fase1_frames = []
        self.fase2_frames = []
        self.fase3_frames = []
        self.fase4_frames = []

        base_path = os.path.join(self.capture_base_path, self.session_id)
        for fase in ["fase1", "fase2", "fase3", "fase4"]:
            os.makedirs(os.path.join(base_path, fase), exist_ok=True)

        print(f"\n[🅿️ PARKING SESSION] Started - {self.session_id}")
        print(f"   Vehicle: {vehicle_id} ({vehicle_class})")

    def add_frame(self, frame, phase):
        """Simpan frame ke fase yang sesuai."""
        if phase == ParkingPhase.FASE1_SIAGA and self.fase1_count < self.fase1_target:
            self.fase1_frames.append(frame.copy())
            self.fase1_count += 1
            return True
        elif phase == ParkingPhase.FASE2_TETAP and self.fase2_count < self.fase2_target:
            self.fase2_frames.append(frame.copy())
            self.fase2_count += 1
            return True
        elif phase == ParkingPhase.FASE3_LOOP and self.fase3_count < self.fase3_target:
            self.fase3_frames.append(frame.copy())
            self.fase3_count += 1
            return True
        elif phase == ParkingPhase.FASE4_TAP and self.fase4_count < self.fase4_target:
            self.fase4_frames.append(frame.copy())
            self.fase4_count += 1
            return True
        return False

    def save_frames(self):
        """Simpan semua frame ke disk."""
        if not self.session_id:
            return []

        base_path = os.path.join(self.capture_base_path, self.session_id)
        saved_files = []

        for i, frame in enumerate(self.fase1_frames):
            filepath = os.path.join(base_path, "fase1", f"frame_{i+1:03d}.jpg")
            cv2.imwrite(filepath, frame)
            saved_files.append(filepath)

        for i, frame in enumerate(self.fase2_frames):
            filepath = os.path.join(base_path, "fase2", f"frame_{i+1:03d}.jpg")
            cv2.imwrite(filepath, frame)
            saved_files.append(filepath)

        for i, frame in enumerate(self.fase3_frames):
            filepath = os.path.join(base_path, "fase3", f"frame_{i+1:03d}.jpg")
            cv2.imwrite(filepath, frame)
            saved_files.append(filepath)

        for i, frame in enumerate(self.fase4_frames):
            filepath = os.path.join(base_path, "fase4", f"frame_{i+1:03d}.jpg")
            cv2.imwrite(filepath, frame)
            saved_files.append(filepath)

        metadata = {
            "session_id": self.session_id,
            "vehicle_id": self.vehicle_id,
            "vehicle_class": self.vehicle_class,
            "start_time": self.session_start_time.isoformat() if self.session_start_time else None,
            "fase1_count": self.fase1_count,
            "fase2_count": self.fase2_count,
            "fase3_count": self.fase3_count,
            "fase4_count": self.fase4_count
        }

        metadata_path = os.path.join(base_path, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        saved_files.append(metadata_path)

        print(f"\n[💾 CAPTURE SAVED] {len(saved_files)} files saved to {base_path}")
        return saved_files

    def advance_phase(self):
        """Advance ke fase berikutnya."""
        if self.phase == ParkingPhase.FASE1_SIAGA and self.fase1_count >= self.fase1_target:
            self.phase = ParkingPhase.FASE2_TETAP
            return True
        elif self.phase == ParkingPhase.FASE2_TETAP and self.fase2_count >= self.fase2_target:
            self.phase = ParkingPhase.FASE3_LOOP
            return True
        elif self.phase == ParkingPhase.FASE3_LOOP and self.fase3_count >= self.fase3_target:
            self.phase = ParkingPhase.FASE4_TAP
            return True
        elif self.phase == ParkingPhase.FASE4_TAP and self.fase4_count >= self.fase4_target:
            self.phase = ParkingPhase.PREVIEW_READY
            return True
        return False

    def complete_session(self):
        """Complete session."""
        self.last_vehicle_id = self.vehicle_id
        self.save_frames()
        self.is_active = False
        self.phase = ParkingPhase.NO_VEHICLE

    def cancel_session(self):
        """Cancel session."""
        self.is_active = False
        self.phase = ParkingPhase.NO_VEHICLE
        self.vehicle_id = None
        self.fase1_frames = []
        self.fase2_frames = []
        self.fase3_frames = []
        self.fase4_frames = []

    def get_progress(self):
        """Get progress string."""
        total = self.fase1_target + self.fase2_target + self.fase3_target + self.fase4_target
        current = self.fase1_count + self.fase2_count + self.fase3_count + self.fase4_count
        return f"{current}/{total}"

    def is_button_active(self, button):
        """Check apakah tombol aktif."""
        if button == "loop_detector":
            return self.phase == ParkingPhase.FASE3_LOOP
        elif button == "tap_card":
            return self.phase == ParkingPhase.FASE4_TAP
        return False


# ============================================================================
# OBJECT DISTANCE TRACKER
# ============================================================================
class ObjectDistanceTracker:
    """Tracker untuk mendeteksi apakah object mendekat atau menjauh."""

    def __init__(self, config=None):
        self.config = config or DEFAULT_CONFIG
        
        self.max_history = self.config['MAX_HISTORY']
        self.siaga_frame_threshold = self.config['SIAGA_FRAME_THRESHOLD']
        self.siaga_hold_time = self.config['SIAGA_HOLD_TIME']
        self.target_classes = self.config['TARGET_CLASSES']

        self.tracked_object_id = None
        self.tracked_object_history = []
        self.tracked_object_bbox = None
        self.tracked_object_area = 0
        self.tracked_object_class = None

        self.camera_view_area = 0

        self.siaga_active = False
        self.approaching_consecutive_count = 0
        self.siaga_trigger_time = None
        self.siaga_expire_time = None
        self.siaga_clear_time = None

        self.moving_away_detected = {}
        self.moving_away_start_time = None
        self.moving_away_seconds_count = 0
        self.last_moving_away_second = -1

        self.siaga_persistence_active = False
        self.siaga_persistence_start_time = None
        self.siaga_persistence_delay = 0.02

        self.siaga_cleared_time = None
        self.persistence_time_duration = 1.5
        self.persistence_time_active = False
        self.persistence_time_object_bbox = None

        self.object_counter = 0
        self.last_session_vehicle_id = None

    def update(self, detections, frame_shape=None):
        """Update tracker dengan deteksi baru."""
        current_time = time.time()

        if frame_shape:
            self.camera_view_area = frame_shape[0] * frame_shape[1]

        target_detections = [d for d in detections if d['class_id'] in self.target_classes]

        if not target_detections:
            self._handle_no_detection(current_time)
            return {'tracked_object': None, 'status': 'no_detection'}

        largest_detection = max(
            target_detections,
            key=lambda d: (d['bbox'][2] - d['bbox'][0]) * (d['bbox'][3] - d['bbox'][1])
        )

        current_area = (largest_detection['bbox'][2] - largest_detection['bbox'][0]) * \
                       (largest_detection['bbox'][3] - largest_detection['bbox'][1])

        # SIAGA PERSISTENCE LOGIC
        if self.siaga_active and self.camera_view_area > 0:
            object_view_percentage = (current_area / self.camera_view_area) * 100
            if object_view_percentage >= 80:
                self.siaga_persistence_active = True
                if self.siaga_persistence_start_time is None:
                    self.siaga_persistence_start_time = current_time
            else:
                self.siaga_persistence_active = False
                self.siaga_persistence_start_time = None

        if self.siaga_active:
            if self.tracked_object_id is None:
                self._handle_no_detection(current_time)
                return {'tracked_object': None, 'status': 'siaga_active_no_object'}
        elif self.persistence_time_active:
            pass
        else:
            if self.tracked_object_id is None or self._is_different_object(largest_detection):
                if self.tracked_object_id is None:
                    self.object_counter += 1
                    class_name = largest_detection.get('class_name', 'UNKNOWN').upper()
                    self.tracked_object_id = f"{class_name}_{self.object_counter}"
                    print(f"\n[🎯 NEW TRACK] Started tracking {self.tracked_object_id}")
                else:
                    self.object_counter += 1
                    class_name = largest_detection.get('class_name', 'UNKNOWN').upper()
                    self.tracked_object_id = f"{class_name}_{self.object_counter}"
                    print(f"\n[🎯 NEW TRACK] Switched to {self.tracked_object_id}")

                self.tracked_object_history = []

        self.tracked_object_bbox = largest_detection['bbox']
        self.tracked_object_area = current_area
        self.tracked_object_class = largest_detection.get('class_name', 'UNKNOWN')

        self.tracked_object_history.append({
            'area': current_area,
            'bbox': largest_detection['bbox'],
            'confidence': largest_detection['confidence'],
            'time': current_time
        })

        if len(self.tracked_object_history) > self.max_history:
            self.tracked_object_history = self.tracked_object_history[-self.max_history:]

        status = self._analyze_trend()
        self._update_siaga(status, current_time)

        return {
            'tracked_object': {
                'id': self.tracked_object_id,
                'bbox': largest_detection['bbox'],
                'confidence': largest_detection['confidence'],
                'area': current_area
            },
            'status': status
        }

    def _handle_no_detection(self, current_time):
        """Handle ketika tidak ada object terdeteksi."""
        if self.siaga_active:
            if self.siaga_expire_time is None:
                self.siaga_expire_time = current_time + self.siaga_hold_time

    def _is_different_object(self, detection):
        """Cek apakah detection ini object yang berbeda."""
        if self.tracked_object_bbox is None:
            return True

        current_bbox = detection['bbox']
        tracked_bbox = self.tracked_object_bbox

        current_center = ((current_bbox[0] + current_bbox[2]) / 2,
                         (current_bbox[1] + current_bbox[3]) / 2)
        tracked_center = ((tracked_bbox[0] + tracked_bbox[2]) / 2,
                         (tracked_bbox[1] + tracked_bbox[3]) / 2)

        distance = ((current_center[0] - tracked_center[0])**2 +
                   (current_center[1] - tracked_center[1])**2)**0.5

        return distance > 100

    def _analyze_trend(self):
        """Analisa trend pergerakan object."""
        history = self.tracked_object_history

        if len(history) < 3:
            return 'stable'

        recent_count = min(5, len(history))
        recent = history[-recent_count:]
        areas = [h['area'] for h in recent]

        if len(areas) < 2:
            return 'stable'

        n = len(areas)
        first_third = areas[:n//3] if n >= 3 else [areas[0]]
        last_third = areas[-(n//3):] if n >= 3 else [areas[-1]]

        first_avg = np.mean(first_third)
        last_avg = np.mean(last_third)

        change_percent = ((last_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0

        if change_percent > 5:
            return 'approaching'
        elif change_percent < -5:
            return 'moving_away'
        else:
            return 'stable'

    def _update_siaga(self, status, current_time):
        """Update SIAGA status."""
        if self.siaga_active and self.tracked_object_area > 0:
            self.last_siaga_area = self.tracked_object_area

        if self.moving_away_start_time is None:
            self.moving_away_start_time = current_time

        elapsed_time = current_time - self.moving_away_start_time
        current_second = int(elapsed_time)

        if status == 'approaching':
            self.approaching_consecutive_count += 1

            if self.approaching_consecutive_count >= self.siaga_frame_threshold:
                if not self.siaga_active:
                    self.siaga_active = True
                    self.siaga_trigger_time = current_time
                self.siaga_expire_time = None
                self.siaga_persistence_active = False
                self.siaga_persistence_start_time = None

                self.moving_away_detected = {}
                self.moving_away_seconds_count = 0
                self.moving_away_start_time = None
                self.last_moving_away_second = -1

        elif status == 'moving_away':
            if self.moving_away_start_time is None:
                self.moving_away_start_time = current_time
                current_second = 0

            if current_second not in self.moving_away_detected:
                self.moving_away_detected[current_second] = True

            if current_second > self.last_moving_away_second:
                self.last_moving_away_second = current_second

                if current_second >= 1:
                    prev_second = current_second - 1
                    if prev_second in self.moving_away_detected:
                        self.moving_away_seconds_count = current_second
                    else:
                        self.moving_away_detected = {current_second: True}
                        self.moving_away_seconds_count = 0
                        self.moving_away_start_time = current_time

            if self.moving_away_seconds_count >= 5:
                if self.siaga_active:
                    self.siaga_active = False
                    self.approaching_consecutive_count = 0
                    self.siaga_expire_time = None
                    self.last_siaga_area = 0
                    self.siaga_persistence_active = False
                    self.siaga_persistence_start_time = None

                    self.siaga_cleared_time = current_time
                    self.persistence_time_active = True
                    self.persistence_time_object_bbox = self.tracked_object_bbox

                    self.moving_away_detected = {}
                    self.moving_away_seconds_count = 0
                    self.moving_away_start_time = None
                    self.last_moving_away_second = -1
        else:
            if self.siaga_persistence_active:
                pass
            else:
                self.approaching_consecutive_count = 0

        if self.siaga_active:
            self.siaga_expire_time = None

    def check_siaga_expire(self, current_time):
        """Check SIAGA expire time."""
        if self.siaga_active and self.siaga_expire_time:
            if current_time >= self.siaga_expire_time:
                self.siaga_active = False
                self.approaching_consecutive_count = 0
                self.siaga_expire_time = None
                print(f"\n[⏱️ SIAGA TIMEOUT] Object hilang > {self.siaga_hold_time}s")

    def reset_tracking(self, save_last_id=False):
        """Reset semua tracking."""
        if save_last_id and self.tracked_object_id:
            self.last_session_vehicle_id = self.tracked_object_id

        self.siaga_active = False
        self.approaching_consecutive_count = 0
        self.tracked_object_id = None
        self.tracked_object_history = []
        self.tracked_object_bbox = None
        self.tracked_object_area = 0
        self.tracked_object_class = None
        self.siaga_expire_time = None
        self.siaga_trigger_time = None
        self.siaga_clear_time = None
        self.siaga_persistence_active = False
        self.siaga_persistence_start_time = None
        self.persistence_time_active = False
        self.persistence_time_object_bbox = None
        self.moving_away_detected = {}
        self.moving_away_seconds_count = 0
        self.moving_away_start_time = None
        self.last_moving_away_second = -1

    def get_tracked_object_id(self):
        """Get ID object yang di-track."""
        return self.tracked_object_id

    def is_siaga_active(self):
        """Check apakah SIAGA aktif."""
        return self.siaga_active

    def is_persistence_time_active(self):
        """Check apakah persistence time aktif."""
        if self.persistence_time_active and self.siaga_cleared_time:
            if time.time() - self.siaga_cleared_time > self.persistence_time_duration:
                self.persistence_time_active = False
        return self.persistence_time_active


# ============================================================================
# MAIN DETECTOR CLASS
# ============================================================================
class YOLOFullDetector:
    """
    YOLO Full Detector dengan semua fitur:
    - Object detection
    - Distance tracking (mendekat/menjauh)
    - SIAGA system
    - Parking session (4 fase)
    - UI overlays
    """

    def __init__(self, camera_id=0, config=None, model_path=None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.camera_id = camera_id
        
        # Model path
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "yolov8n.pt")
        self.model_path = model_path
        
        # Load model
        self.model = None
        self._load_model()
        
        # Camera
        self.cap = None
        self._init_camera()
        
        # Components
        self.tracker = ObjectDistanceTracker(self.config)
        self.parking_session = ParkingSession(self.config)
        
        # State
        self.yolo_enabled = self.config['YOLO_ENABLED_DEFAULT']
        self.confidence_threshold = self.config['YOLO_CONFIDENCE_THRESHOLD']
        self.yolo_skip_frames = self.config['YOLO_SKIP_FRAMES']
        self.current_frame_count = 0
        self.last_detections = []
        
        # UI state
        self.clean_ui = self.config['CLEAN_UI']
        self.show_fps = self.config['SHOW_FPS']
        self.fps_counter = 0
        self.fps_last_time = time.time()
        self.fps = 0

    def _load_model(self):
        """Load YOLO model."""
        if os.path.exists(self.model_path):
            self.model = YOLO(self.model_path)
            print(f"[✅ YOLO] Model loaded: {self.model_path}")
        else:
            print(f"[⚠️ WARNING] Model not found: {self.model_path}")
            self.model = None

    def _init_camera(self):
        """Initialize camera."""
        self.cap = cv2.VideoCapture(self.camera_id)
        if self.cap.isOpened():
            print(f"[✅ CAMERA] Opened camera {self.camera_id}")
        else:
            print(f"[❌ ERROR] Failed to open camera {self.camera_id}")

    def set_target_classes(self, classes):
        """Set target classes."""
        self.tracker.target_classes = classes
        self.config['TARGET_CLASSES'] = classes

    def set_confidence_threshold(self, threshold):
        """Set confidence threshold."""
        self.confidence_threshold = max(0.1, min(0.9, threshold))

    def detect_objects(self, frame):
        """Detect objects in frame."""
        if self.model is None:
            return []

        results = self.model(frame, verbose=False, conf=self.confidence_threshold)
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
                
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                
                detections.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': conf,
                    'class_id': class_id,
                    'class_name': class_name
                })
        
        return detections

    def get_frame(self):
        """
        Get frame dengan semua processing.
        
        Returns:
            tuple: (frame, state_dict)
                state_dict berisi:
                - detections: list of detections
                - tracked_object: tracked object info
                - status: approaching/moving_away/stable
                - siaga_active: bool
                - parking_phase: ParkingPhase enum
                - fps: current FPS
        """
        if self.cap is None or not self.cap.isOpened():
            return None, {}

        ret, frame = self.cap.read()
        if not ret:
            return None, {}

        self.current_frame_count += 1

        # FPS counter
        self.fps_counter += 1
        if time.time() - self.fps_last_time >= 1.0:
            self.fps = self.fps_counter
            self.fps_counter = 0
            self.fps_last_time = time.time()

        # YOLO detection
        if self.yolo_enabled:
            if self.yolo_skip_frames > 0 and self.current_frame_count % (self.yolo_skip_frames + 1) != 0:
                detections = self.last_detections
            else:
                detections = self.detect_objects(frame)
                self.last_detections = detections

            # Update tracker
            tracker_result = self.tracker.update(detections, frame.shape)
            self.tracker.check_siaga_expire(time.time())
        else:
            detections = []
            tracker_result = {'tracked_object': None, 'status': 'yolo_off'}

        state = {
            'detections': detections,
            'tracked_object': tracker_result.get('tracked_object'),
            'status': tracker_result.get('status'),
            'siaga_active': self.tracker.is_siaga_active(),
            'parking_phase': self.parking_session.phase,
            'parking_session_active': self.parking_session.is_active,
            'fps': self.fps,
            'yolo_enabled': self.yolo_enabled,
        }

        return frame, state

    def draw_detections(self, frame, state):
        """Draw semua UI elements pada frame."""
        detections = state.get('detections', [])
        tracked_object = state.get('tracked_object')
        status = state.get('status', '')
        siaga_active = state.get('siaga_active', False)
        fps = state.get('fps', 0)

        # Draw detections
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            color = (0, 255, 0)  # Green default
            
            # Highlight tracked object
            if tracked_object and det == tracked_object:
                if status == 'approaching':
                    color = (0, 0, 255)  # Red - mendekat
                elif status == 'moving_away':
                    color = (255, 0, 0)  # Blue - menjauh
                else:
                    color = (0, 255, 0)  # Green - tetap

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = f"{det['class_name']} {det['confidence']:.2f}"
            if tracked_object and det.get('id') == tracked_object.get('id'):
                label += f" [{tracked_object.get('id', '')}]"
            
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # SIAGA indicator
        if siaga_active:
            h, w = frame.shape[:2]
            text = "⚠️ SIAGA - Object Mendekat"
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            x = (w - text_w) // 2
            cv2.rectangle(frame, (x - 10, 10), (x + text_w + 10, 45), (0, 0, 255), -1)
            cv2.putText(frame, text, (x, 33),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # FPS
        if self.show_fps:
            cv2.putText(frame, f"FPS: {fps}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        return frame

    def trigger_loop_detector(self):
        """Trigger loop detector button (FASE 3)."""
        if self.parking_session.is_button_active("loop_detector"):
            print("\n[🔵 LOOP DETECTOR] Triggered!")

    def trigger_tap_card(self):
        """Trigger tap card button (FASE 4)."""
        if self.parking_session.is_button_active("tap_card"):
            print("\n[💳 TAP CARD] Triggered!")

    def reset_tracking(self):
        """Reset tracking."""
        self.tracker.reset_tracking()
        self.parking_session.cancel_session()

    def release(self):
        """Release resources."""
        if self.cap is not None:
            self.cap.release()
        print("[OK] YOLOFullDetector released")

    def run(self):
        """Run standalone."""
        if not self.cap or not self.cap.isOpened():
            return

        print("\n" + "="*60)
        print("YOLOv8n Full Detector - All Features")
        print("="*60)
        print("\nControls:")
        print("  - 'q': Quit")
        print("  - 'y': Toggle YOLO")
        print("  - 'r': Reset tracking")
        print("  - 'l': Loop Detector (FASE 3)")
        print("  - 't': Tap Card (FASE 4)")
        print("="*60 + "\n")

        try:
            while True:
                frame, state = self.get_frame()
                if frame is None:
                    break

                self.draw_detections(frame, state)

                cv2.imshow('YOLO Full Detector', frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('y'):
                    self.yolo_enabled = not self.yolo_enabled
                elif key == ord('r'):
                    self.reset_tracking()
                elif key == ord('l'):
                    self.trigger_loop_detector()
                elif key == ord('t'):
                    self.trigger_tap_card()

        finally:
            self.release()
            cv2.destroyAllWindows()


# Convenience function
def create_detector(camera_id=0, config=None):
    """Create YOLOFullDetector instance."""
    return YOLOFullDetector(camera_id=camera_id, config=config)
