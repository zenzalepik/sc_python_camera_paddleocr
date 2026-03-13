"""
Object Distance Detection Widget - Core Module
Reusable widget untuk deteksi object mendekat/menjauh dengan YOLO
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime
from enum import Enum
import os
import tkinter as tk
from PIL import Image, ImageTk
import threading

# Import configuration from widget_variables
from .widget_variables import (
    CLEAN_UI,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    YOLO_SKIP_FRAMES,
    YOLO_ENABLED_DEFAULT,
    YOLO_CONFIDENCE_THRESHOLD,
    TARGET_CLASSES,
    MAX_HISTORY,
    SIAGA_FRAME_THRESHOLD,
    SIAGA_HOLD_TIME,
    FASE1_TARGET,
    FASE2_TARGET,
    FASE3_TARGET,
    FASE4_TARGET,
    WINDOW_SCALE,
    SHOW_FPS,
    STATIONARY_TIMEOUT,
    MOVEMENT_THRESHOLD,
)


class ParkingPhase(Enum):
    """Enum untuk fase-fase dalam parking session."""
    NO_VEHICLE = 0
    FASE1_SIAGA = 1
    FASE2_TETAP = 2
    FASE3_LOOP = 3
    FASE4_TAP = 4
    PREVIEW_READY = 5


class ParkingSession:
    """Manager untuk parking session dengan 4 fase capture."""

    def __init__(self):
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
        self.fase1_target = FASE1_TARGET
        self.fase2_target = FASE2_TARGET
        self.fase3_target = FASE3_TARGET
        self.fase4_target = FASE4_TARGET
        self.fase1_frames = []
        self.fase2_frames = []
        self.fase3_frames = []
        self.fase4_frames = []
        self.is_active = False
        self.last_vehicle_id = None

    def start_session(self, vehicle_id, vehicle_class="UNKNOWN"):
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

    def add_frame(self, frame, phase):
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
        import json
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
        return saved_files

    def advance_phase(self):
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
        self.last_vehicle_id = self.vehicle_id
        self.save_frames()
        self.is_active = False
        self.phase = ParkingPhase.NO_VEHICLE

    def cancel_session(self):
        self.is_active = False
        self.phase = ParkingPhase.NO_VEHICLE
        self.vehicle_id = None
        self.fase1_frames = []
        self.fase2_frames = []
        self.fase3_frames = []
        self.fase4_frames = []

    def get_progress(self):
        total = self.fase1_target + self.fase2_target + self.fase3_target + self.fase4_target
        current = self.fase1_count + self.fase2_count + self.fase3_count + self.fase4_count
        return f"{current}/{total}"

    def is_button_active(self, button):
        if button == "loop_detector":
            return self.phase == ParkingPhase.FASE3_LOOP
        elif button == "tap_card":
            return self.phase == ParkingPhase.FASE4_TAP
        return False


class CaptureManager:
    """Manager untuk capture frames dari parking session."""

    def __init__(self, parking_session):
        self.session = parking_session
        self.capture_interval = 0.1
        self.last_capture_time = 0

    def can_capture(self, phase):
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
        if not self.can_capture(phase):
            return False
        self.session.add_frame(frame, phase)
        self.last_capture_time = time.time()
        self.session.advance_phase()
        return True


class ObjectDistanceTracker:
    """Tracker untuk mendeteksi apakah object mendekat atau menjauh."""

    def __init__(self, max_history=30, siaga_frame_threshold=3, siaga_hold_time=3.0, target_classes=None):
        self.max_history = max_history
        self.siaga_frame_threshold = siaga_frame_threshold
        self.siaga_hold_time = siaga_hold_time
        self.target_classes = target_classes if target_classes else [0]
        self.tracked_object_id = None
        self.tracked_object_history = []
        self.tracked_object_bbox = None
        self.tracked_object_area = 0
        self.tracked_object_class = None
        self.camera_view_area = 0
        self.siaga_active = False
        self.approaching_consecutive_count = 0
        self.siaga_expire_time = None
        self.siaga_clear_time = None
        self.moving_away_detected = {}
        self.moving_away_start_time = None
        self.moving_away_seconds_count = 0
        self.last_moving_away_second = -1
        self.last_siaga_area = 0
        self.siaga_persistence_active = False
        self.siaga_persistence_start_time = None
        self.siaga_cleared_time = None
        self.persistence_time_duration = 1.5
        self.persistence_time_active = False
        self.persistence_time_object_bbox = None
        self.object_counter = 0
        self.last_session_vehicle_id = None
        
        # Stationary detection settings
        self.stationary_timeout = 30.0  # 30 detik object diam maka bounding box hilang
        self.movement_threshold = 10.0  # 10px gerakan minimal (kanan/kiri/atas/bawah)
        self.last_center_position = None  # (x, y) center position terakhir
        self.stationary_start_time = None  # Waktu mulai diam
        self.is_stationary = False  # Status apakah object sedang diam

    def update(self, detections):
        current_time = time.time()
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
                self.object_counter += 1
                class_name = largest_detection.get('class_name', 'UNKNOWN').upper()
                self.tracked_object_id = f"{class_name}_{self.object_counter}"
                self.tracked_object_history = []
        self.tracked_object_bbox = largest_detection['bbox']
        self.tracked_object_area = current_area
        self.tracked_object_class = largest_detection.get('class_name', 'UNKNOWN')
        
        # Hitung center position saat ini
        current_center = (
            (largest_detection['bbox'][0] + largest_detection['bbox'][2]) / 2,
            (largest_detection['bbox'][1] + largest_detection['bbox'][3]) / 2
        )
        
        # Cek apakah object bergerak atau diam
        self._check_stationary(current_center, current_time)
        
        self.tracked_object_history.append({
            'area': current_area,
            'bbox': largest_detection['bbox'],
            'conf': largest_detection['confidence'],
            'time': current_time,
            'center': current_center
        })
        if len(self.tracked_object_history) > self.max_history:
            self.tracked_object_history = self.tracked_object_history[-self.max_history:]
        
        status = self._analyze_trend()
        self._update_siaga(status, current_time)
        
        # Jika object diam (stationary), kembalikan status None agar bounding box tidak tampil
        if self.is_stationary:
            return {
                'tracked_object': None,
                'status': 'stationary'
            }
        
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
        if self.siaga_active:
            if self.siaga_expire_time is None:
                self.siaga_expire_time = current_time + self.siaga_hold_time

    def _check_stationary(self, current_center, current_time):
        """
        Cek apakah object diam (stationary).
        Object dianggap diam jika:
        - Gerakan tidak melebihi movement_threshold (10px) ke kanan/kiri/atas/bawah
        - Sudah diam selama stationary_timeout (30 detik)
        
        Jika object diam, bounding box akan dihilangkan.
        """
        if self.last_center_position is None:
            # First detection, set initial position
            self.last_center_position = current_center
            self.stationary_start_time = current_time
            self.is_stationary = False
            return
        
        last_x, last_y = self.last_center_position
        curr_x, curr_y = current_center
        
        # Hitung pergerakan (abs distance) pada sumbu X dan Y
        delta_x = abs(curr_x - last_x)
        delta_y = abs(curr_y - last_y)
        
        # Cek apakah ada gerakan signifikan (> 10px pada salah satu sumbu)
        has_significant_movement = delta_x > self.movement_threshold or delta_y > self.movement_threshold
        
        if has_significant_movement:
            # Object bergerak - reset timer stationary
            self.is_stationary = False
            self.stationary_start_time = current_time
        else:
            # Object tidak bergerak signifikan - cek sudah berapa lama
            if self.stationary_start_time is None:
                self.stationary_start_time = current_time
            else:
                elapsed_time = current_time - self.stationary_start_time
                if elapsed_time >= self.stationary_timeout:
                    # Object sudah diam selama 30 detik - hilangkan bounding box
                    self.is_stationary = True
        
        # Update posisi terakhir
        self.last_center_position = current_center

    def _is_different_object(self, detection):
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

    def reset_tracking(self, save_last_id=False):
        was_siaga = self.siaga_active
        if save_last_id and self.tracked_object_id:
            self.last_session_vehicle_id = self.tracked_object_id
        self.siaga_active = False
        self.approaching_consecutive_count = 0
        self.tracked_object_id = None
        self.tracked_object_area = 0
        self.tracked_object_history = []
        self.tracked_object_class = None
        self.siaga_expire_time = None
        self.siaga_clear_time = time.time()
        self.last_siaga_area = 0
        self.siaga_persistence_active = False
        self.persistence_time_active = False
        
        # Reset stationary detection state
        self.last_center_position = None
        self.stationary_start_time = None
        self.is_stationary = False

    def check_siaga_expire(self, current_time):
        if self.persistence_time_active and self.siaga_cleared_time is not None:
            persistence_elapsed = current_time - self.siaga_cleared_time
            if persistence_elapsed >= self.persistence_time_duration:
                self.persistence_time_active = False
                self.siaga_cleared_time = None
                self.persistence_time_object_bbox = None
        if self.siaga_active and self.siaga_expire_time is not None:
            if current_time >= self.siaga_expire_time:
                self.siaga_active = False
                self.approaching_consecutive_count = 0
                self.tracked_object_id = None
                self.tracked_object_bbox = None
                self.tracked_object_history = []
                self.siaga_clear_time = current_time
                self.siaga_expire_time = None

    def is_siaga_active(self):
        return self.siaga_active

    def get_tracked_object_id(self):
        return self.tracked_object_id


class ObjectDistanceWidget(tk.Frame):
    """
    Reusable Widget untuk Object Distance Detection.
    
    Widget ini dapat dipasang di frame apapun dan bersifat flexible.
    Fitur:
    - Real-time object detection dengan YOLO
    - Deteksi object mendekat/menjauh
    - SIAGA alert system
    - Parking system dengan 4 fase capture
    
    Usage:
        widget = ObjectDistanceWidget(parent_frame, camera_id=0)
        widget.pack(fill=tk.BOTH, expand=True)
        widget.start()  # Start detection
        widget.stop()   # Stop detection
    """

    def __init__(self, parent, camera_id=0, confidence_threshold=None, on_session_complete=None, **kwargs):
        """
        Initialize ObjectDistanceWidget.
        
        Args:
            parent: Parent frame/container
            camera_id: Camera device ID (default: 0)
            confidence_threshold: YOLO confidence threshold (default: from config)
            on_session_complete: Callback function when parking session completes
            **kwargs: Additional tkinter.Frame options
        """
        super().__init__(parent, **kwargs)
        
        self.camera_id = camera_id
        self.confidence_threshold = confidence_threshold if confidence_threshold is not None else YOLO_CONFIDENCE_THRESHOLD
        self.on_session_complete = on_session_complete
        
        # Widget configuration
        self.config(bg='#2b2b2b')
        
        # Create UI elements
        self._create_widgets()
        
        # Initialize detection components
        self.model = None
        self.tracker = None
        self.parking_session = None
        self.capture_manager = None
        self.cap = None
        
        # State variables
        self.yolo_enabled = YOLO_ENABLED_DEFAULT
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.yolo_skip_frames = YOLO_SKIP_FRAMES
        self.current_frame_count = 0
        self.last_detections = None
        
        # Threading
        self.running = False
        self.update_thread = None
        
    def _create_widgets(self):
        """Create widget UI components."""
        # Main container untuk video (stretch sempurna)
        self.video_container = tk.Frame(self, bg='#000000')
        self.video_container.pack(fill=tk.BOTH, expand=True)
        
        # Video label (untuk menampilkan frame camera)
        self.video_label = tk.Label(self.video_container, bg='#000000')
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Download overlay label (untuk menampilkan progress download YOLO)
        self.download_overlay = tk.Frame(self.video_container, bg='#000000')
        
        # Container untuk konten overlay (agar centered)
        overlay_content = tk.Frame(self.download_overlay, bg='#000000')
        overlay_content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Icon download (besar)
        download_icon = tk.Label(
            overlay_content,
            text="📥",
            font=("Segoe UI Emoji", 48),
            bg='#000000',
            fg='#00ff00'
        )
        download_icon.pack(pady=(0, 20))
        
        # Main download text
        self.download_label = tk.Label(
            overlay_content,
            text="⏳ Sedang mendownload YOLO...",
            font=("Arial", 18, "bold"),
            bg='#000000',
            fg='#00ff00',
            justify=tk.CENTER
        )
        self.download_label.pack(pady=(0, 10))
        
        # Subtitle
        download_subtitle = tk.Label(
            overlay_content,
            text="Please wait while the model is being downloaded",
            font=("Arial", 11),
            bg='#000000',
            fg='#aaaaaa',
            justify=tk.CENTER
        )
        download_subtitle.pack(pady=(0, 20))

        # Progress text untuk download
        self.download_progress = tk.Label(
            overlay_content,
            text="🔄 Initializing model...",
            font=("Arial", 12),
            bg='#000000',
            fg='#00ffff'
        )
        self.download_progress.pack()

        # Status frame (opsional, bisa di-hide dengan CLEAN_UI)
        if not CLEAN_UI:
            self.status_frame = tk.Frame(self, bg='#1a1a1a', height=30)
            self.status_frame.pack(fill=tk.X, padx=5, pady=2)

            self.status_label = tk.Label(
                self.status_frame,
                text="Ready",
                font=("Arial", 9),
                bg='#1a1a1a',
                fg='#00ff00'
            )
            self.status_label.pack(side=tk.LEFT, padx=10)

            self.fps_label = tk.Label(
                self.status_frame,
                text="FPS: 0.0",
                font=("Arial", 9),
                bg='#1a1a1a',
                fg='#00ff00'
            )
            self.fps_label.pack(side=tk.RIGHT, padx=10)
    
    def _initialize_detector(self):
        """Initialize YOLO model and tracker."""
        # Tampilkan download overlay
        self._show_download_overlay(True)
        self._update_download_status("📥 Loading YOLO model...")
        self.update()  # Force UI update

        # Load YOLO model (ini akan mendownload jika belum ada)
        print("[INFO] Loading YOLO model (this may take a while if downloading)...")
        
        try:
            # Coba load model dengan timeout handling
            import time
            start_time = time.time()
            
            self.model = YOLO('yolov8n.pt')
            
            elapsed = time.time() - start_time
            print(f"[OK] Model loaded in {elapsed:.2f}s")
            
        except Exception as e:
            print(f"[ERROR] Failed to load YOLO model: {e}")
            self._update_download_status(f"❌ Error: {str(e)}")
            self.update()
            time.sleep(2)
            raise

        # Sembunyikan download overlay setelah model berhasil dimuat
        self._show_download_overlay(False)
        self._update_status("Model loaded", '#00ff00')

        # Initialize tracker
        self.tracker = ObjectDistanceTracker(
            max_history=MAX_HISTORY,
            siaga_frame_threshold=SIAGA_FRAME_THRESHOLD,
            siaga_hold_time=SIAGA_HOLD_TIME,
            target_classes=TARGET_CLASSES
        )

        # Parking session
        self.parking_session = ParkingSession()
        self.capture_manager = CaptureManager(self.parking_session)

        print("[OK] Detector initialized")
    
    def _show_download_overlay(self, show):
        """Show or hide download overlay."""
        if show:
            # Overlay memenuhi seluruh video container
            self.download_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.download_overlay.lift()  # Bring to front
        else:
            self.download_overlay.place_forget()

    def _update_download_status(self, text):
        """Update download status text."""
        self.download_progress.config(text=text)
        self.download_overlay.update()
    
    def _update_status(self, text, color='#00ff00'):
        """Update status label text."""
        if not CLEAN_UI and hasattr(self, 'status_label'):
            self.status_label.config(text=text, fg=color)
    
    def _open_camera(self):
        """Open camera capture."""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {self.camera_id}")
        
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Set camera view area
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if self.tracker:
            self.tracker.camera_view_area = frame_width * frame_height
    
    def _close_camera(self):
        """Close camera capture."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def _detect_objects(self, frame):
        """Detect objects in frame."""
        results = self.model(frame, verbose=False, conf=self.confidence_threshold)[0]
        detections = []
        if results.boxes is not None:
            for i in range(len(results.boxes)):
                box = results.boxes[i]
                class_id = int(box.cls[0])
                conf = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy()
                if class_id in TARGET_CLASSES:
                    detections.append({
                        'class_id': class_id,
                        'bbox': bbox,
                        'confidence': conf,
                        'class_name': self.model.names[class_id]
                    })
        return detections
    
    def _process_frame(self, frame):
        """Process frame with detection and tracking."""
        current_time = time.time()
        
        # Check if YOLO disabled
        if not self.yolo_enabled:
            detections = []
            result = {'tracked_object': None, 'status': 'yolo_off'}
        else:
            # Frame skipping optimization
            self.current_frame_count += 1
            if self.yolo_skip_frames > 0 and self.current_frame_count % (self.yolo_skip_frames + 1) != 0:
                detections = self.last_detections if self.last_detections else []
            else:
                detections = self._detect_objects(frame)
                self.last_detections = detections
            
            # Update tracker
            result = self.tracker.update(detections)
        
        # Check SIAGA expire
        if self.yolo_enabled:
            self.tracker.check_siaga_expire(current_time)
        
        # Handle parking session
        if self.yolo_enabled:
            self._handle_parking_session(result, frame)
        
        # Draw detections
        if not CLEAN_UI:
            self._draw_detections(frame, result)
        
        # Update FPS
        self._update_fps(current_time)
        
        return frame
    
    def _handle_parking_session(self, result, frame):
        """Handle parking session state machine."""
        tracked_object = result.get('tracked_object') if result else None
        status = result.get('status', 'stable') if result else 'no_detection'

        if self.parking_session.phase == ParkingPhase.PREVIEW_READY:
            if self.on_session_complete:
                self.on_session_complete(self.parking_session)
            self.parking_session = ParkingSession()
            self.tracker.reset_tracking()
            return

        # Jika object stationary tapi parking session sedang aktif, lanjutkan session
        if status == 'stationary' and self.parking_session.is_active:
            # Object diam, tapi session masih jalan - abaikan stationary untuk session
            # Tetap capture frames jika diperlukan
            phase = self.parking_session.phase
            if phase == ParkingPhase.FASE2_TETAP and self.capture_manager.can_capture(phase):
                self.capture_manager.capture(frame, phase)
            self.parking_session.advance_phase()
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
            if phase == ParkingPhase.FASE1_SIAGA:
                if status == 'approaching' and self.capture_manager.can_capture(phase):
                    self.capture_manager.capture(frame, phase)
            elif phase == ParkingPhase.FASE2_TETAP:
                if status == 'stable' and self.capture_manager.can_capture(phase):
                    self.capture_manager.capture(frame, phase)

        self.parking_session.advance_phase()
    
    def _draw_detections(self, frame, result):
        """Draw detection on frame."""
        tracked_object = result.get('tracked_object')
        status = result.get('status', 'stable')
        
        if tracked_object is None:
            return
        
        bbox = tracked_object['bbox']
        obj_id = tracked_object['id']
        conf = tracked_object['confidence']
        is_siaga = self.tracker.is_siaga_active()
        
        # Color based on status
        if status == 'approaching':
            color = (0, 0, 255)  # Red
        elif status == 'moving_away':
            color = (255, 0, 0)  # Blue
        else:
            color = (0, 255, 0)  # Green
        
        # Draw bounding box
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Status text
        if status == 'approaching':
            status_text = "MENDEKAT"
        elif status == 'moving_away':
            status_text = "MENJAUH"
        else:
            status_text = "TETAP"
        
        # Label
        label = f"{obj_id}: {conf:.2f} [{status_text}]"
        (label_w, label_h), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1
        )
        cv2.rectangle(
            frame,
            (x1, y1 - label_h - baseline - 3),
            (x1 + label_w, y1),
            color,
            -1
        )
        cv2.putText(
            frame,
            label,
            (x1, y1 - baseline),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (255, 255, 255),
            1
        )
        
        # SIAGA indicator
        if is_siaga:
            siaga_text = "⚠️ SIAGA"
            (siaga_w, siaga_h), siaga_baseline = cv2.getTextSize(
                siaga_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1
            )
            siaga_y = y1 - label_h - baseline - 5 - siaga_h - 3
            cv2.rectangle(
                frame,
                (x1, siaga_y),
                (x1 + siaga_w + 6, siaga_y + siaga_h + 3),
                (0, 140, 255),
                -1
            )
            cv2.putText(
                frame,
                siaga_text,
                (x1 + 3, siaga_y + siaga_h),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                1
            )
    
    def _update_fps(self, current_time):
        """Update FPS counter."""
        self.frame_count += 1
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
            if not CLEAN_UI and hasattr(self, 'fps_label'):
                self.fps_label.config(text=f"FPS: {self.fps:.1f}")
    
    def _update_video(self):
        """Update video display."""
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # Process frame
        processed_frame = self._process_frame(frame)

        # Convert to RGB for tkinter
        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)

        # Resize to fit widget - gunakan video_container untuk ukuran yang akurat
        try:
            widget_width = self.video_container.winfo_width()
            widget_height = self.video_container.winfo_height()
            
            # Pastikan ukuran valid
            if widget_width > 1 and widget_height > 1:
                rgb_frame = cv2.resize(rgb_frame, (widget_width, widget_height))
        except:
            # Fallback ke ukuran default jika winfo belum tersedia
            pass

        # Convert to PhotoImage
        img = Image.fromarray(rgb_frame)
        photo = ImageTk.PhotoImage(image=img)

        # Update label
        self.video_label.config(image=photo)
        self.video_label.image = photo  # Keep reference

        # Schedule next update
        if self.running:
            self.after(1, self._update_video)
    
    def _run_detector(self):
        """Run detector in separate thread."""
        try:
            self._initialize_detector()
            self._open_camera()
            
            self.running = True
            self._update_video()
            
        except Exception as e:
            print(f"[ERROR] Detector error: {e}")
            self.running = False
    
    def start(self):
        """Start the widget detection."""
        if self.update_thread and self.update_thread.is_alive():
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._run_detector, daemon=True)
        self.update_thread.start()
        
        if not CLEAN_UI and hasattr(self, 'status_label'):
            self.status_label.config(text="Running")
    
    def stop(self):
        """Stop the widget detection."""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
        self._close_camera()
        
        if not CLEAN_UI and hasattr(self, 'status_label'):
            self.status_label.config(text="Stopped")
    
    def toggle_yolo(self):
        """Toggle YOLO detection on/off."""
        self.yolo_enabled = not self.yolo_enabled
        if self.yolo_enabled:
            print("[✅ YOLO ON] Detection enabled")
        else:
            print("[❌ YOLO OFF] Detection disabled")
        self.tracker.reset_tracking()
    
    def reset_tracking(self):
        """Reset tracking."""
        if self.tracker:
            self.tracker.reset_tracking()
    
    def trigger_loop_detector(self):
        """Trigger loop detector capture."""
        if self.parking_session and self.parking_session.phase == ParkingPhase.FASE3_LOOP:
            for i in range(self.parking_session.fase3_target):
                ret, frame = self.cap.read()
                if ret:
                    self.parking_session.add_frame(frame, ParkingPhase.FASE3_LOOP)
                    time.sleep(0.05)
            self.parking_session.advance_phase()
    
    def trigger_tap_card(self):
        """Trigger tap card capture."""
        if self.parking_session and self.parking_session.phase == ParkingPhase.FASE4_TAP:
            for i in range(self.parking_session.fase4_target):
                ret, frame = self.cap.read()
                if ret:
                    self.parking_session.add_frame(frame, ParkingPhase.FASE4_TAP)
                    time.sleep(0.05)
            self.parking_session.advance_phase()
    
    def get_parking_session(self):
        """Get current parking session."""
        return self.parking_session
    
    def is_yolo_enabled(self):
        """Check if YOLO is enabled."""
        return self.yolo_enabled
