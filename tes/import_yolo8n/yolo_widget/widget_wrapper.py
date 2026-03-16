"""
YOLO Widget Wrapper
Wrapper untuk menggunakan RealTimeDistanceDetector dari main.py sebagai widget reusable.
"""

# Import semua dari main.py
from .main import (
    RealTimeDistanceDetector,
    ParkingPhase,
    ParkingSession,
    CaptureManager,
    ObjectDistanceTracker,
)

# Import config dari variables.py
from .variables import (
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
)

# Build DEFAULT_CONFIG from variables
DEFAULT_CONFIG = {
    'CLEAN_UI': CLEAN_UI,
    'CAMERA_WIDTH': CAMERA_WIDTH,
    'CAMERA_HEIGHT': CAMERA_HEIGHT,
    'YOLO_SKIP_FRAMES': YOLO_SKIP_FRAMES,
    'YOLO_ENABLED_DEFAULT': YOLO_ENABLED_DEFAULT,
    'YOLO_CONFIDENCE_THRESHOLD': YOLO_CONFIDENCE_THRESHOLD,
    'TARGET_CLASSES': TARGET_CLASSES,
    'MAX_HISTORY': MAX_HISTORY,
    'SIAGA_FRAME_THRESHOLD': SIAGA_FRAME_THRESHOLD,
    'SIAGA_HOLD_TIME': SIAGA_HOLD_TIME,
    'FASE1_TARGET': FASE1_TARGET,
    'FASE2_TARGET': FASE2_TARGET,
    'FASE3_TARGET': FASE3_TARGET,
    'FASE4_TARGET': FASE4_TARGET,
    'WINDOW_SCALE': WINDOW_SCALE,
    'SHOW_FPS': SHOW_FPS,
}

import cv2
import time


class YOLOWidget:
    """
    YOLO Widget - Wrapper untuk RealTimeDistanceDetector.
    
    Widget ini memiliki semua fitur dari non_widget/main.py:
    - Object Detection (YOLOv8n)
    - Distance Tracking (mendekat/menjauh)
    - SIAGA System
    - Parking Session (4 Fase)
    - UI Overlays lengkap
    
    Usage:
        widget = YOLOWidget(camera_id=0)
        frame, state = widget.get_frame()
        # Frame sudah ada UI lengkap, siap ditampilkan!
    """

    def __init__(self, camera_id=0, config=None):
        """
        Initialize YOLO Widget.
        
        Args:
            camera_id: Camera device ID (default: 0)
            config: Configuration dict (optional)
        """
        self.camera_id = camera_id
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        
        # Create detector instance (tanpa start camera)
        self.detector = self._create_detector()
        
        # Override config if provided
        if config:
            if 'TARGET_CLASSES' in config:
                self.detector.tracker.target_classes = config['TARGET_CLASSES']
            if 'YOLO_SKIP_FRAMES' in config:
                self.detector.yolo_skip_frames = config['YOLO_SKIP_FRAMES']
            if 'CLEAN_UI' in config:
                self.detector.clean_ui = config['CLEAN_UI']
        
        # Start camera
        self._start_camera()

    def _create_detector(self):
        """Create detector instance tanpa start camera."""
        detector = RealTimeDistanceDetector(
            camera_id=self.camera_id,
            confidence_threshold=self.config.get('YOLO_CONFIDENCE_THRESHOLD', YOLO_CONFIDENCE_THRESHOLD)
        )
        # Stop camera yang di-start di __init__ detector
        if detector.cap is not None:
            detector.cap.release()
            detector.cap = None
        # Set clean_ui attribute (untuk compatibility)
        detector.clean_ui = self.config.get('CLEAN_UI', False)
        return detector

    def _start_camera(self):
        """Start camera."""
        self.detector.cap = cv2.VideoCapture(self.camera_id)
        if not self.detector.cap.isOpened():
            print(f"[ERROR] Cannot open camera {self.camera_id}")

    def start(self):
        """Start camera dan initialize."""
        if not self.detector.cap.isOpened():
            self.detector.cap.open(self.camera_id)
        
        if not self.detector.start():
            return False
        
        return True

    def get_frame(self):
        """
        Get frame dengan semua processing.
        
        Returns:
            tuple: (frame, state_dict)
                frame: Camera frame dengan UI overlays
                state_dict: Dictionary dengan semua state info
        """
        # Ensure camera started
        if self.detector.cap is None or not self.detector.cap.isOpened():
            self._start_camera()
        
        if self.detector.cap is None or not self.detector.cap.isOpened():
            return None, {}
        
        # Get frame from camera
        ret, frame = self.detector.cap.read()
        if not ret:
            return None, {}

        # Increment frame count
        self.detector.current_frame_count += 1

        # Check jika YOLO disabled
        if not self.detector.yolo_enabled:
            detections = []
            result = {'tracked_object': None, 'status': 'yolo_off'}
        else:
            # YOLO ON - run detection dengan frame skipping
            if self.detector.yolo_skip_frames > 0 and self.detector.current_frame_count % (self.detector.yolo_skip_frames + 1) != 0:
                detections = self.detector.last_detections if self.detector.last_detections else []
            else:
                detections = self.detector.detect_objects(frame)
                self.detector.last_detections = detections

            # Update tracker
            result = self.detector.tracker.update(detections)

        # Check SIAGA expire
        if self.detector.yolo_enabled:
            self.detector.tracker.check_siaga_expire(time.time())

        # Handle parking session
        if self.detector.yolo_enabled:
            self.detector.handle_parking_session(result, frame)

        # Draw UI (kecuali preview mode)
        if not (self.detector.show_preview and self.detector.preview_frames):
            if not self.detector.yolo_enabled:
                self.detector.draw_yolo_off_indicator(frame)
            
            self.detector.draw_detections(frame, result)
            self.detector.draw_info_panel(frame, result)

        # Build state dict
        state = {
            'detections': detections,
            'tracked_object': result.get('tracked_object'),
            'tracked_object_id': self.detector.tracker.get_tracked_object_id(),
            'status': result.get('status', 'no_detection'),
            'siaga_active': self.detector.tracker.siaga_active,
            'siaga_cleared': self.detector.tracker.persistence_time_active,
            'parking_phase': self.detector.parking_session.phase,
            'parking_session_active': self.detector.parking_session.is_active,
            'fps': self.detector.fps,
            'yolo_enabled': self.detector.yolo_enabled,
            'clean_ui': self.detector.clean_ui,
        }
        
        return frame, state

    def draw_ui(self, frame, state):
        """
        Draw UI overlays pada frame.
        Note: UI sudah di-draw oleh get_frame(), method ini untuk compatibility.
        """
        # UI sudah di-draw di get_frame()
        return frame

    def handle_parking_session(self, frame, state):
        """Handle parking session logic."""
        # Sudah di-handle di get_frame()
        pass

    def set_target_classes(self, classes):
        """Set target classes."""
        self.detector.tracker.target_classes = list(classes)

    def set_confidence_threshold(self, threshold):
        """Set confidence threshold."""
        self.detector.confidence_threshold = max(0.1, min(0.9, threshold))

    def toggle_yolo(self):
        """Toggle YOLO on/off."""
        self.detector.yolo_enabled = not self.detector.yolo_enabled
        if self.detector.yolo_enabled:
            self.detector.tracker.reset_tracking()
        return self.detector.yolo_enabled

    def trigger_loop_detector(self, frame=None):
        """Trigger loop detector (FASE 3)."""
        if frame is not None:
            self.detector.trigger_loop_detector(frame)
        elif self.detector.parking_session.phase == ParkingPhase.FASE3_LOOP:
            # Jika tidak ada frame, gunakan last frame dari detector atau skip
            print(f"\n[🔘 LOOP DETECTOR] Triggered! (no frame)")
            # Advance phase tanpa capture
            self.detector.parking_session.advance_phase()

    def trigger_tap_card(self, frame=None):
        """Trigger tap card (FASE 4)."""
        if frame is not None:
            self.detector.trigger_tap_card(frame)
        elif self.detector.parking_session.phase == ParkingPhase.FASE4_TAP:
            # Jika tidak ada frame, gunakan last frame dari detector atau skip
            print(f"\n[🔘 TAP CARD] Triggered! (no frame)")
            # Advance phase tanpa capture
            self.detector.parking_session.advance_phase()

    def reset_tracking(self):
        """Reset semua tracking."""
        self.detector.tracker.reset_tracking()
        self.detector.parking_session.cancel_session()

    def release(self):
        """Release resources."""
        self.detector.stop()

    def run_standalone(self):
        """Run widget sebagai standalone app (testing)."""
        self.detector.run()


__all__ = [
    'YOLOWidget',
    'ParkingPhase',
    'ParkingSession',
    'ObjectDistanceTracker',
    'CaptureManager',
    'DEFAULT_CONFIG',
]
