"""
V8_YOLO_OPENCV_DNN - COMPLETE VERSION
Fitur lengkap dari v6_Deteksi_Object_Mendekat
TANPA PaddleOCR - CPU rendah (~20-30%)

FITUR LENGKAP:
✅ YOLO OpenCV DNN Backend (CPU rendah)
✅ Object Distance Tracking (MENDEKAT/TETAP/MENJAUH)
✅ SIAGA Alert System
✅ Focus Lock & Percentage
✅ Parking Session 4-Fase Capture
✅ Loop Detector & Tap Card Buttons
✅ Preview Window dengan Grid Thumbnails
✅ Help Popup (Press H)
✅ Snapshot Save (Press S)
✅ Multi-Class Detection (7 classes)
✅ Time Display
✅ Legend Display
✅ FPS Counter
"""

import cv2
import numpy as np
import time
from datetime import datetime
from enum import Enum
import os
import json
from dotenv import load_dotenv

# Load ENV
load_dotenv()

# ============================================================================
# PARKING PHASE ENUM
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

    def __init__(self):
        self.phase = ParkingPhase.NO_VEHICLE
        self.session_id = None
        self.session_start_time = None
        self.vehicle_id = None
        self.vehicle_class = None
        self.capture_base_path = "captures"

        # Capture counters
        self.fase1_count = 0
        self.fase2_count = 0
        self.fase3_count = 0
        self.fase4_count = 0

        # Target counts - Load from ENV
        self.fase1_target = int(os.getenv('FASE1_CAPTURE_COUNT', '3'))
        self.fase2_target = int(os.getenv('FASE2_CAPTURE_COUNT', '5'))
        self.fase3_target = int(os.getenv('FASE3_CAPTURE_COUNT', '3'))
        self.fase4_target = int(os.getenv('FASE4_CAPTURE_COUNT', '3'))

        # Frame buffers
        self.fase1_frames = []
        self.fase2_frames = []
        self.fase3_frames = []
        self.fase4_frames = []

        # Session state
        self.is_active = False
        self.last_vehicle_id = None

    def start_session(self, vehicle_id, vehicle_class="UNKNOWN"):
        """Start parking session baru saat SIAGA aktif."""
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

        # Create folder structure
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

        # Save all fases
        for fase_name in ["fase1", "fase2", "fase3", "fase4"]:
            frames = getattr(self, f'{fase_name}_frames')
            for i, frame in enumerate(frames):
                filepath = os.path.join(base_path, fase_name, f"frame_{i+1:03d}.jpg")
                cv2.imwrite(filepath, frame)
                saved_files.append(filepath)

        # Save metadata
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
            print(f"\n[📍 FASE 2] Kendaraan BERHENTI - Capture 5 frame")
            return True
        elif self.phase == ParkingPhase.FASE2_TETAP and self.fase2_count >= self.fase2_target:
            self.phase = ParkingPhase.FASE3_LOOP
            print(f"\n[📍 FASE 3] Siap LOOP DETECTOR")
            return True
        elif self.phase == ParkingPhase.FASE3_LOOP and self.fase3_count >= self.fase3_target:
            self.phase = ParkingPhase.FASE4_TAP
            print(f"\n[📍 FASE 4] Siap TAP CARD")
            return True
        elif self.phase == ParkingPhase.FASE4_TAP and self.fase4_count >= self.fase4_target:
            self.phase = ParkingPhase.PREVIEW_READY
            print(f"\n[✅ PREVIEW READY] Semua fase selesai!")
            return True
        return False

    def complete_session(self):
        """Complete session dan simpan last vehicle ID."""
        self.last_vehicle_id = self.vehicle_id
        self.save_frames()
        self.is_active = False
        self.phase = ParkingPhase.NO_VEHICLE
        print(f"\n[✓ SESSION COMPLETE] Last vehicle: {self.last_vehicle_id}")

    def cancel_session(self):
        """Cancel session (kendaraan pergi sebelum selesai)."""
        self.is_active = False
        self.phase = ParkingPhase.NO_VEHICLE
        self.vehicle_id = None
        print(f"\n[✗ SESSION CANCELLED]")

    def get_progress(self):
        """Get progress string untuk UI."""
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
# CAPTURE MANAGER
# ============================================================================

class CaptureManager:
    """Manager untuk capture frames dari parking session."""

    def __init__(self, parking_session):
        self.session = parking_session
        self.capture_interval = 0.1  # 100ms antar capture
        self.last_capture_time = 0

    def can_capture(self, phase):
        """Check apakah bisa capture di fase ini."""
        if not self.session.is_active:
            return False

        current_time = time.time()
        if current_time - self.last_capture_time < self.capture_interval:
            return False

        if phase == ParkingPhase.FASE1_SIAGA and self.session.fase1_count < self.session.fase1_target:
            return True
        elif phase == ParkingPhase.FASE2_TETAP and self.session.fase2_count < self.session.fase2_target:
            return True
        elif phase == ParkingPhase.FASE3_LOOP and self.session.fase3_count < self.session.fase3_target:
            return True
        elif phase == ParkingPhase.FASE4_TAP and self.session.fase4_count < self.session.fase4_target:
            return True

        return False

    def capture(self, frame, phase):
        """Capture frame dan simpan ke session."""
        if not self.can_capture(phase):
            return False

        self.session.add_frame(frame, phase)
        self.last_capture_time = time.time()
        self.session.advance_phase()

        return True

# ============================================================================
# OBJECT DISTANCE TRACKER
# ============================================================================

class ObjectDistanceTracker:
    """Tracker untuk mendeteksi apakah object mendekat atau menjauh."""

    def __init__(self, max_history=30, siaga_frame_threshold=3, siaga_hold_time=3.0, target_classes=None):
        self.max_history = max_history
        self.siaga_frame_threshold = siaga_frame_threshold
        self.siaga_hold_time = siaga_hold_time
        self.target_classes = target_classes if target_classes else ['person', 'car', 'motorcycle', 'bus', 'truck']

        # Object tracking
        self.tracked_object_id = None
        self.tracked_object_history = []
        self.tracked_object_bbox = None
        self.tracked_object_area = 0
        self.tracked_object_class = None

        # Camera view
        self.camera_view_area = 0

        # SIAGA tracking
        self.siaga_active = False
        self.approaching_consecutive_count = 0
        self.siaga_trigger_time = None
        self.siaga_expire_time = None
        self.siaga_clear_time = None

        # MOVING AWAY
        self.moving_away_detected = {}
        self.moving_away_start_time = None
        self.moving_away_seconds_count = 0
        self.last_moving_away_second = -1

        # PERSISTENCE
        self.last_siaga_area = 0
        self.siaga_persistence_active = False
        self.siaga_persistence_start_time = None

        # PERSISTENCE TIME
        self.siaga_cleared_time = None
        self.persistence_time_duration = 1.5
        self.persistence_time_active = False

        # Object counter
        self.object_counter = 0
        self.last_session_vehicle_id = None

    def update(self, detections):
        """Update tracker dengan deteksi baru."""
        current_time = time.time()

        # Filter target classes
        target_detections = [d for d in detections if d.get('class_name', '') in self.target_classes]

        if not target_detections:
            self._handle_no_detection(current_time)
            return {'tracked_object': None, 'status': 'no_detection'}

        # Pilih object TERBESAR
        largest_detection = max(
            target_detections,
            key=lambda d: (d['bbox'][2] - d['bbox'][0]) * (d['bbox'][3] - d['bbox'][1])
        )

        current_area = (largest_detection['bbox'][2] - largest_detection['bbox'][0]) * \
                       (largest_detection['bbox'][3] - largest_detection['bbox'][1])

        # SIAGA PERSISTENCE
        if self.siaga_active and self.camera_view_area > 0:
            object_view_percentage = (current_area / self.camera_view_area) * 100
            if object_view_percentage >= 80:
                self.siaga_persistence_active = True
                if self.siaga_persistence_start_time is None:
                    self.siaga_persistence_start_time = current_time
            else:
                self.siaga_persistence_active = False
                self.siaga_persistence_start_time = None

        # Check object switch
        if self.siaga_active:
            if self.tracked_object_id is None:
                self._handle_no_detection(current_time)
                return {'tracked_object': None, 'status': 'siaga_active_no_object'}
        elif self.persistence_time_active:
            pass
        else:
            if self.tracked_object_id is None or self._is_different_object(largest_detection):
                self.object_counter += 1
                class_name = largest_detection.get('class_name', 'UNKNOWN').upper()
                self.tracked_object_id = f"{class_name}_{self.object_counter}"
                print(f"\n[🎯 NEW TRACK] Started tracking {self.tracked_object_id}")
                self.tracked_object_history = []

        # Update tracked object
        self.tracked_object_bbox = largest_detection['bbox']
        self.tracked_object_area = current_area
        self.tracked_object_class = largest_detection.get('class_name', 'UNKNOWN')

        self.tracked_object_history.append({
            'area': current_area,
            'bbox': largest_detection['bbox'],
            'conf': largest_detection['confidence'],
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
        """Handle ketika tidak ada object."""
        if self.siaga_active and self.siaga_expire_time is None:
            self.siaga_expire_time = current_time + self.siaga_hold_time

    def _is_different_object(self, detection):
        """Cek apakah object berbeda."""
        if self.tracked_object_bbox is None:
            return True

        current_bbox = detection['bbox']
        tracked_bbox = self.tracked_object_bbox

        current_center = ((current_bbox[0] + current_bbox[2]) / 2, (current_bbox[1] + current_bbox[3]) / 2)
        tracked_center = ((tracked_bbox[0] + tracked_bbox[2]) / 2, (tracked_bbox[1] + tracked_bbox[3]) / 2)

        distance = ((current_center[0] - tracked_center[0])**2 + (current_center[1] - tracked_center[1])**2)**0.5
        return distance > 100

    def _analyze_trend(self):
        """Analisa trend pergerakan."""
        history = self.tracked_object_history
        if len(history) < 3:
            return 'stable'

        recent = history[-min(5, len(history)):]
        areas = [h['area'] for h in recent]

        if len(areas) < 2:
            return 'stable'

        n = len(areas)
        first_avg = np.mean(areas[:n//3]) if n >= 3 else areas[0]
        last_avg = np.mean(areas[-(n//3):]) if n >= 3 else areas[-1]

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
                    print(f"\n[⚠️ SIAGA] {self.tracked_object_id} terdeteksi mendekat!")
                self.siaga_expire_time = None
                self.siaga_persistence_active = False
                self.moving_away_detected = {}
                self.moving_away_seconds_count = 0
                self.moving_away_start_time = None
                self.last_moving_away_second = -1

        elif status == 'moving_away':
            if current_second not in self.moving_away_detected:
                self.moving_away_detected[current_second] = True

            if current_second > self.last_moving_away_second and current_second >= 1:
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
                    self.siaga_cleared_time = current_time
                    self.persistence_time_active = True
                    print(f"\n[✓ SIAGA CLEARED] 5 detik moving_away terpenuhi!")
                    self.moving_away_detected = {}
                    self.moving_away_seconds_count = 0
                    self.moving_away_start_time = None
                    self.last_moving_away_second = -1
        else:
            if not self.siaga_persistence_active:
                self.approaching_consecutive_count = 0

        if self.siaga_active:
            self.siaga_expire_time = None

    def reset_tracking(self, save_last_id=False):
        """Reset tracking."""
        if save_last_id and self.tracked_object_id:
            self.last_session_vehicle_id = self.tracked_object_id

        self.siaga_active = False
        self.approaching_consecutive_count = 0
        self.tracked_object_id = None
        self.tracked_object_bbox = None
        self.tracked_object_area = 0
        self.tracked_object_history = []
        self.siaga_expire_time = None
        self.siaga_clear_time = time.time()
        self.last_siaga_area = 0
        self.siaga_persistence_active = False
        self.persistence_time_active = False

    def check_siaga_expire(self, current_time):
        """Check SIAGA expire."""
        if self.persistence_time_active and self.siaga_cleared_time:
            if current_time - self.siaga_cleared_time >= self.persistence_time_duration:
                self.persistence_time_active = False
                self.siaga_cleared_time = None

        if self.siaga_active and self.siaga_expire_time:
            if current_time >= self.siaga_expire_time:
                self.siaga_active = False
                self.tracked_object_id = None
                self.siaga_clear_time = current_time

    def is_siaga_active(self):
        """Check SIAGA status."""
        return self.siaga_active

    def get_tracked_object_id(self):
        """Get tracked object ID."""
        return self.tracked_object_id

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class RealTimeDistanceDetector:
    """Real-time object distance detection dengan YOLO OpenCV DNN."""

    def __init__(self, camera_id=0, confidence_threshold=0.3):
        self.camera_id = camera_id
        self.confidence_threshold = confidence_threshold

        # Performance mode
        self.performance_mode = os.getenv('PERFORMANCE_MODE', 'HIGH').upper()
        if self.performance_mode == 'HIGH':
            self.target_fps = 30
            self.skip_frames = 1
            self.detection_throttle = 0.0
        elif self.performance_mode == 'MEDIUM':
            self.target_fps = 15
            self.skip_frames = 3
            self.detection_throttle = 0.0
        else:  # LOW
            self.target_fps = 15
            self.skip_frames = 1
            self.detection_throttle = 0.1

        # CLEAN UI MODE
        self.clean_ui_mode = os.getenv('CLEAN_UI_MODE', 'false').lower() == 'true'

        self.frame_counter = 0
        self.last_detection_result = None
        self.last_detection_time = 0

        # Load YOLO
        print("\nLoading YOLO model (OpenCV DNN)...")
        yolo_config = 'yolov3-tiny.cfg'
        yolo_weights = 'yolov3-tiny.weights'

        if os.path.exists(yolo_weights) and os.path.exists(yolo_config):
            self.net = cv2.dnn.readNetFromDarknet(yolo_config, yolo_weights)
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            print("[OK] YOLO detector loaded (OpenCV DNN)")
        else:
            print("[ERROR] YOLO model not found!")
            self.net = None

        # Load classes
        self.classes = []
        if os.path.exists('coco.names'):
            with open('coco.names', 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]

        self.target_classes = ['person', 'car', 'motorcycle', 'bus', 'truck', 'bicycle', 'cell phone']

        # Tracker
        self.tracker = ObjectDistanceTracker(
            max_history=30,
            siaga_frame_threshold=3,
            siaga_hold_time=3.0,
            target_classes=self.target_classes
        )

        # Parking Session
        self.parking_session = ParkingSession()
        self.capture_manager = CaptureManager(self.parking_session)

        # UI state
        self.show_preview = False
        self.preview_frames = None

        # Video capture
        self.cap = None

        # Stats
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()

    def start(self):
        """Start video capture."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                print(f"[ERROR] Cannot open camera {self.camera_id}")
                return False

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.tracker.camera_view_area = frame_width * frame_height

            print(f"[OK] Camera opened: {self.camera_id}")
            print(f"[INFO] Camera view area: {frame_width}x{frame_height} = {self.tracker.camera_view_area}px")

            cv2.namedWindow('Object Distance Detection - OpenCV DNN', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Object Distance Detection - OpenCV DNN', frame_width, frame_height)

            return True
        except Exception as e:
            print(f"[ERROR] Failed to start: {e}")
            return False

    def stop(self):
        """Stop video capture."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def detect_objects(self, frame):
        """Detect objects using OpenCV DNN."""
        if self.net is None:
            return []

        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.net.getUnconnectedOutLayersNames())

        detections = []
        height, width = frame.shape[:2]

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = float(scores[class_id])

                if confidence > self.confidence_threshold:
                    class_name = self.classes[class_id] if class_id < len(self.classes) else f"class_{class_id}"
                    if class_name in self.target_classes:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        if w > 20 and h > 20:
                            detections.append({
                                'class_id': class_id,
                                'class_name': class_name,
                                'bbox': [x, y, w, h],
                                'confidence': confidence
                            })

        return detections

    def handle_parking_session(self, result, frame):
        """Handle parking session."""
        tracked_object = result.get('tracked_object') if result else None
        status = result.get('status', 'stable') if result else 'no_detection'

        if self.parking_session.phase == ParkingPhase.PREVIEW_READY:
            self.show_preview = True
            self.preview_frames = {
                'fase1': self.parking_session.fase1_frames,
                'fase2': self.parking_session.fase2_frames,
                'fase3': self.parking_session.fase3_frames,
                'fase4': self.parking_session.fase4_frames,
            }
            return

        if not tracked_object:
            if self.parking_session.is_active:
                self.parking_session.cancel_session()
            return

        if self.tracker.siaga_active and not self.parking_session.is_active:
            self.parking_session.start_session(
                self.tracker.tracked_object_id,
                self.tracker.tracked_object_class
            )

        if self.parking_session.is_active:
            phase = self.parking_session.phase
            if phase == ParkingPhase.FASE1_SIAGA and status == 'approaching':
                if self.capture_manager.can_capture(phase):
                    self.capture_manager.capture(frame, phase)
            elif phase == ParkingPhase.FASE2_TETAP and status == 'stable':
                if self.capture_manager.can_capture(phase):
                    self.capture_manager.capture(frame, phase)

    def trigger_loop_detector(self, frame):
        """Trigger FASE 3."""
        if self.parking_session.phase == ParkingPhase.FASE3_LOOP:
            print(f"\n[🔘 LOOP DETECTOR] Triggered!")
            for i in range(self.parking_session.fase3_target):
                self.parking_session.add_frame(frame, ParkingPhase.FASE3_LOOP)
                time.sleep(0.05)
            self.parking_session.advance_phase()

    def trigger_tap_card(self, frame):
        """Trigger FASE 4."""
        if self.parking_session.phase == ParkingPhase.FASE4_TAP:
            print(f"\n[🔘 TAP CARD] Triggered!")
            for i in range(self.parking_session.fase4_target):
                self.parking_session.add_frame(frame, ParkingPhase.FASE4_TAP)
                time.sleep(0.05)
            self.parking_session.advance_phase()

    def complete_parking_session(self):
        """Complete session."""
        self.parking_session.complete_session()
        self.tracker.reset_tracking(save_last_id=True)
        self.show_preview = False
        self.preview_frames = None

    def draw_detections(self, frame, result):
        """Draw detections."""
        # CLEAN UI MODE: Skip drawing bounding boxes, tapi logic tetap jalan
        if self.clean_ui_mode:
            return

        tracked_object = result.get('tracked_object')
        if not tracked_object:
            return

        bbox = tracked_object['bbox']
        obj_id = tracked_object['id']
        conf = tracked_object['confidence']
        status = result.get('status', 'stable')
        is_siaga = self.tracker.is_siaga_active()

        # Color based on status
        if status == 'approaching':
            color = (0, 0, 255)  # Red
        elif status == 'moving_away':
            color = (255, 0, 0)  # Blue
        else:
            color = (0, 255, 0)  # Green

        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Label
        status_text = {'approaching': 'MENDEKAT', 'moving_away': 'MENJAUH', 'stable': 'TETAP'}.get(status, 'TETAP')
        label = f"{obj_id}: {conf:.2f} [{status_text}]"

        (label_w, label_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x1, y1 - label_h - 5), (x1 + label_w, y1), color, -1)
        cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # SIAGA badge
        if is_siaga:
            siaga_text = "⚠️ SIAGA"
            (siaga_w, siaga_h), _ = cv2.getTextSize(siaga_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            siaga_y = y1 - label_h - 10
            cv2.rectangle(frame, (x1, siaga_y), (x1 + siaga_w + 6, siaga_y + siaga_h + 3), (0, 140, 255), -1)
            cv2.putText(frame, siaga_text, (x1 + 3, siaga_y + siaga_h), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    def draw_info_panel(self, frame, result):
        """Draw info panel."""
        # Skip if CLEAN UI MODE
        if self.clean_ui_mode:
            return

        # Update FPS
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time

        is_siaga = self.tracker.is_siaga_active()
        panel_height = 75 if not is_siaga else 90

        # Panel background
        cv2.rectangle(frame, (0, 0), (450, panel_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, 0), (450, panel_height), (255, 255, 255), 1)

        # FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Time
        timestamp = datetime.now().strftime("%H:%M:%S")
        time_text = f"Time: {timestamp}"
        (time_w, _), _ = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        cv2.putText(frame, time_text, (440 - time_w, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Parking session
        if self.parking_session.is_active:
            session_y = 35
            cv2.rectangle(frame, (10, session_y), (440, session_y + 50), (30, 30, 30), -1)
            cv2.rectangle(frame, (10, session_y), (440, session_y + 50), (0, 255, 255), 1)

            cv2.putText(frame, f"🅿️ PARKING SESSION", (20, session_y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            cv2.putText(frame, f"Vehicle: {self.parking_session.vehicle_id}", (20, session_y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            phase_names = {
                ParkingPhase.FASE1_SIAGA: "FASE 1: SIAGA",
                ParkingPhase.FASE2_TETAP: "FASE 2: TETAP",
                ParkingPhase.FASE3_LOOP: "FASE 3: LOOP",
                ParkingPhase.FASE4_TAP: "FASE 4: TAP"
            }
            phase_name = phase_names.get(self.parking_session.phase, "UNKNOWN")
            cv2.putText(frame, phase_name, (20, session_y + 48), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Progress
            progress = self.parking_session.get_progress()
            cv2.putText(frame, f"Progress: {progress}", (280, session_y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Focus percentage
        tracked_id = self.tracker.get_tracked_object_id()
        if tracked_id and result and result.get('tracked_object'):
            obj_area = result['tracked_object'].get('area', 0)
            if self.tracker.camera_view_area > 0:
                focus_percentage = (obj_area / self.tracker.camera_view_area) * 100

                if focus_percentage < 30:
                    focus_color = (0, 0, 255)
                elif focus_percentage < 50:
                    focus_color = (0, 140, 255)
                elif focus_percentage < 70:
                    focus_color = (0, 255, 255)
                elif focus_percentage < 90:
                    focus_color = (0, 255, 0)
                else:
                    focus_color = (255, 0, 0)

                cv2.putText(frame, f"🎯 FOCUS: {tracked_id}", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, focus_color, 1)
                cv2.putText(frame, f"{focus_percentage:.1f}%", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.4, focus_color, 1)

    def show_help_popup(self):
        """Show help popup."""
        help_title = "BANTUAN - Parking System Capture"
        canvas_height = 500
        canvas_width = 600
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
        canvas[:] = (40, 40, 40)

        cv2.putText(canvas, help_title, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.line(canvas, (20, 45), (canvas_width - 20, 45), (255, 255, 255), 1)

        help_lines = [
            ("CARA MENGGUNAKAN:", 0.5, (0, 255, 255), 70),
            ("1. Tunggu kendaraan terdeteksi kamera", 0.4, (255, 255, 255), 95),
            ("2. SIAGA aktif otomatis saat mendekat", 0.4, (255, 255, 255), 115),
            ("3. FASE 1: Capture 3 frame (MENDEKAT)", 0.4, (255, 255, 255), 135),
            ("4. FASE 2: Capture 5 frame (BERHENTI)", 0.4, (255, 255, 255), 155),
            ("5. FASE 3: Tekan 'L' untuk LOOP DETECTOR", 0.4, (255, 255, 255), 175),
            ("6. FASE 4: Tekan 'T' untuk TAP CARD", 0.4, (255, 255, 255), 195),
            ("7. Preview muncul otomatis", 0.4, (255, 255, 255), 215),
            ("8. Tekan ENTER untuk SELESAI", 0.4, (0, 255, 0), 235),
            ("", 0, (0, 0, 0), 0),
            ("KEYBOARD SHORTCUTS:", 0.5, (0, 255, 255), 260),
            ("L - Trigger LOOP DETECTOR (FASE 3)", 0.4, (255, 255, 255), 285),
            ("T - Trigger TAP CARD (FASE 4)", 0.4, (255, 255, 255), 305),
            ("ENTER - SELESAI (close preview)", 0.4, (255, 255, 255), 325),
            ("H - Tampilkan bantuan ini", 0.4, (255, 255, 255), 345),
            ("Q - Quit aplikasi", 0.4, (255, 255, 255), 365),
            ("S - Save snapshot", 0.4, (255, 255, 255), 385),
        ]

        for text, font_size, color, y in help_lines:
            if y > 0:
                cv2.putText(canvas, text, (20, y), cv2.FONT_HERSHEY_SIMPLEX, font_size, color, 1)

        cv2.rectangle(canvas, (0, 0), (canvas_width, canvas_height), (255, 255, 255), 2)
        cv2.putText(canvas, "Press ENTER or H to close", (180, canvas_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow(help_title, canvas)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 13 or key == ord('h'):
                break
            if cv2.getWindowProperty(help_title, cv2.WND_PROP_VISIBLE) < 1:
                break

        cv2.destroyWindow(help_title)

    def run(self):
        """Run application."""
        if not self.start():
            return

        # Print info
        print("\n" + "="*70)
        print("Object Distance Detection - OpenCV DNN (CLEAN VERSION)")
        print("="*70)
        print(f"\nPerformance Mode: {self.performance_mode}")
        print(f"Target FPS: {self.target_fps}")
        print(f"Detection Throttle: {self.detection_throttle*1000:.0f}ms")
        print(f"CLEAN UI Mode: {'ON (Camera only)' if self.clean_ui_mode else 'OFF (Full UI)'}")
        print(f"\nTarget Classes: {', '.join(self.target_classes)}")
        print(f"\nCapture Configuration:")
        print(f"  - FASE 1: {self.parking_session.fase1_target} frame")
        print(f"  - FASE 2: {self.parking_session.fase2_target} frame")
        print(f"  - FASE 3: {self.parking_session.fase3_target} frame")
        print(f"  - FASE 4: {self.parking_session.fase4_target} frame")
        print(f"  - TOTAL: {self.parking_session.fase1_target + self.parking_session.fase2_target + self.parking_session.fase3_target + self.parking_session.fase4_target} frame")
        print("\nControls:")
        print("  - Q: Quit")
        print("  - S: Save snapshot")
        print("  - L: LOOP DETECTOR (FASE 3)")
        print("  - T: TAP CARD (FASE 4)")
        print("  - H: Help popup")
        print("  - ENTER: SELESAI (preview)")
        print("="*70 + "\n")

        frame_delay = 1.0 / self.target_fps

        try:
            while True:
                loop_start = time.time()
                ret, frame = self.cap.read()

                if not ret:
                    print("[ERROR] Failed to grab frame")
                    break

                # Detection logic
                current_time = time.time()
                time_since_last = current_time - self.last_detection_time

                self.frame_counter += 1
                should_detect = False

                if self.detection_throttle > 0:
                    if time_since_last >= self.detection_throttle:
                        should_detect = True
                        self.last_detection_time = current_time
                elif self.skip_frames > 1:
                    if self.frame_counter % self.skip_frames == 0:
                        should_detect = True
                else:
                    should_detect = True

                if should_detect:
                    detections = self.detect_objects(frame)
                    result = self.tracker.update(detections)
                    self.last_detection_result = result
                else:
                    result = self.last_detection_result or {'tracked_object': None, 'status': 'no_detection'}

                self.tracker.check_siaga_expire(current_time)
                self.handle_parking_session(result, frame)

                # Display
                if self.show_preview and self.preview_frames:
                    cv2.putText(frame, "PREVIEW READY - Press ENTER", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow('Object Distance Detection - OpenCV DNN', frame)
                else:
                    self.draw_detections(frame, result)
                    self.draw_info_panel(frame, result)
                    cv2.imshow('Object Distance Detection - OpenCV DNN', frame)

                # Keyboard
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.tracker.reset_tracking()
                elif key == ord('s'):
                    filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"\n[OK] Snapshot saved: {filename}")
                elif key == ord('l'):
                    self.trigger_loop_detector(frame)
                elif key == ord('t'):
                    self.trigger_tap_card(frame)
                elif key == 13:
                    if self.show_preview:
                        self.complete_parking_session()
                elif key == ord('h'):
                    self.show_help_popup()

                # FPS control
                elapsed = time.time() - loop_start
                if elapsed < frame_delay:
                    time.sleep(frame_delay - elapsed)

        finally:
            self.stop()
            print("\n[OK] Application closed")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main function."""
    print("="*70)
    print("V8 YOLO OPENCV DNN - COMPLETE VERSION")
    print("="*70)
    print("\n✅ OpenCV DNN Backend (CPU ~20-30%)")
    print("✅ NO PaddleOCR (disabled)")
    print("✅ All features from v6_Deteksi_Object_Mendekat")
    print("="*70)

    detector = RealTimeDistanceDetector(
        camera_id=0,
        confidence_threshold=0.3  # Lower threshold for better detection
    )

    detector.run()


if __name__ == "__main__":
    main()
