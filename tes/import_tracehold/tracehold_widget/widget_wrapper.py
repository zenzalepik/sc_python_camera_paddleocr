"""
TraceHold Widget Wrapper
Wrapper untuk menggunakan TraceHold detector sebagai widget reusable.

Semua sistem, fitur, dan UI dari main.py tetap sama, hanya di-refactor jadi class.
"""

import cv2
import numpy as np
import time

# Import helper function dari main.py
from .main import is_intersecting

# Import config dari variables.py
from .variables import (
    AUTO_RESET_ENABLED as INITIAL_AUTO_RESET_MODE,
    NO_MOTION_THRESHOLD,
    OBJECT_CONFIRM_THRESHOLD,
    OBJECT_LOST_THRESHOLD,
    ROI_WIDTH_FRACTION,
    ROI_HEIGHT_FRACTION,
    BLINK_INTERVAL,
    CAMERA_INDEX,
    BLUR_KERNEL_SIZE,
    BG_DIFF_THRESHOLD,
    FRAME_DIFF_THRESHOLD,
    INIT_CAPTURE_COUNT,
    MIN_CONTOUR_AREA,
    BG_SUBTRACTOR_HISTORY,
    BG_SUBTRACTOR_VAR_THRESHOLD,
)


# Constants (sama seperti di main.py non_widget line 178-179)
MIN_BOX_WIDTH = 120
MIN_BOX_HEIGHT = 120


class TraceHoldWidget:
    """
    TraceHold Widget - Reusable component untuk ROI Object Detection.
    
    Fitur (SAMA PERSIS dengan main.py):
    - Object Detection (OpenCV-based, tanpa YOLO)
    - Dual Mode: MOG2 Adaptive vs Static Background
    - ROI (Region of Interest) tracking
    - Auto Reset setelah ROI kosong
    - Canny Edge backup detection
    - Persistent tracking
    - MOG2 learning phase
    
    Usage:
        widget = TraceHoldWidget(camera_id=0)
        frame, state = widget.get_frame()
    """

    def __init__(self, camera_id=0, config=None):
        """
        Initialize TraceHold Widget.
        
        Args:
            camera_id: Camera device ID (default: 0)
            config: Configuration dict (optional)
        """
        self.camera_id = camera_id
        self.config = config or {}
        
        # Load config dari variables.py atau override
        self._load_config()
        
        # Initialize camera
        self.cap = None
        self._init_camera()
        
        # Initialize all state variables (sama seperti main.py)
        self._init_state()
        
        # Initialize background (MOG2 atau Static)
        self._init_background()

    def _load_config(self):
        """Load configuration."""
        self.auto_reset_enabled = self.config.get('AUTO_RESET_ENABLED', INITIAL_AUTO_RESET_MODE)
        self.no_motion_threshold = self.config.get('NO_MOTION_THRESHOLD', NO_MOTION_THRESHOLD)
        self.object_confirm_threshold = self.config.get('OBJECT_CONFIRM_THRESHOLD', OBJECT_CONFIRM_THRESHOLD)
        self.object_lost_threshold = self.config.get('OBJECT_LOST_THRESHOLD', OBJECT_LOST_THRESHOLD)
        self.roi_width_fraction = self.config.get('ROI_WIDTH_FRACTION', ROI_WIDTH_FRACTION)
        self.roi_height_fraction = self.config.get('ROI_HEIGHT_FRACTION', ROI_HEIGHT_FRACTION)
        self.blink_interval = self.config.get('BLINK_INTERVAL', BLINK_INTERVAL)
        self.blur_kernel_size = self.config.get('BLUR_KERNEL_SIZE', BLUR_KERNEL_SIZE)
        self.bg_diff_threshold = self.config.get('BG_DIFF_THRESHOLD', BG_DIFF_THRESHOLD)
        self.frame_diff_threshold = self.config.get('FRAME_DIFF_THRESHOLD', FRAME_DIFF_THRESHOLD)
        self.init_capture_count = self.config.get('INIT_CAPTURE_COUNT', INIT_CAPTURE_COUNT)
        self.min_contour_area = self.config.get('MIN_CONTOUR_AREA', MIN_CONTOUR_AREA)
        self.min_box_width = self.config.get('MIN_BOX_WIDTH', MIN_BOX_WIDTH)
        self.min_box_height = self.config.get('MIN_BOX_HEIGHT', MIN_BOX_HEIGHT)
        self.bg_subtractor_history = self.config.get('BG_SUBTRACTOR_HISTORY', BG_SUBTRACTOR_HISTORY)
        self.bg_subtractor_var_threshold = self.config.get('BG_SUBTRACTOR_VAR_THRESHOLD', BG_SUBTRACTOR_VAR_THRESHOLD)

    def _init_camera(self):
        """Initialize camera."""
        self.cap = cv2.VideoCapture(self.camera_id)
        if self.cap.isOpened():
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Calculate ROI (sama seperti main.py)
            self.roi_width = int(self.frame_width * self.roi_width_fraction)
            self.roi_height = int(self.frame_height * self.roi_height_fraction)
            self.roi_x = (self.frame_width - self.roi_width) // 2
            self.roi_y = (self.frame_height - self.roi_height) // 2
        else:
            self.frame_width = 640
            self.frame_height = 480
            self.roi_x = self.roi_y = self.roi_width = self.roi_height = 0

    def _init_state(self):
        """Initialize all state variables (sama seperti main.py)."""
        # Detection state
        self.object_detected_frames = 0
        self.object_lost_frames = 0
        self.object_present = False
        self.has_detected_object = False
        self.has_green_box = False
        self.object_in_roi = False
        
        # ROI tracking
        self.roi_occupied = False
        self.persistent_object_in_roi = False
        self.roi_empty_frames = 0
        self.object_in_roi_frames = 0
        self.last_object_bbox_in_roi = None
        self.current_object_bbox_in_roi = None
        self.object_stationary_counter = 0
        
        # Indicator state
        self.indicator_on = False
        self.blink_state = False
        self.roi_box_blink = False
        self.label_object_in_roi = False
        
        # Auto reset
        self.auto_reset_state = self.auto_reset_enabled
        self.last_log_second = 0
        
        # Canny edge tracking
        self.canny_roi_edge_counter = 0
        self.canny_min_edge_threshold = 50
        self.canny_detecting = False
        self.ignore_canny_after_reset = False
        
        # MOG2 learning phase
        self.mog2_reset_counter = 0
        self.mog2_learning_phase = False
        
        # Movement tracking
        self.object_moving = False
        self.last_movement_time = time.time()
        self.movement_log_counter = 0
        
        # Frame counter
        self.frame_count = 0
        
        # Buffers
        self.prev_frame = None
        self.fg_mask = None
        self.fg_mask_bg = None
        self.fg_mask_diff = None
        
        # Preview window state
        self.show_preview = False
        self.preview_mog2 = None
        self.prev_frame_preview = None

    def _init_background(self):
        """Initialize background (MOG2 atau Static)."""
        if self.auto_reset_state:
            # MOG2 mode
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=self.bg_subtractor_history,
                varThreshold=self.bg_subtractor_var_threshold,
                detectShadows=False
            )
            # Preview MOG2 (terpisah dari main, untuk preview window)
            self.preview_mog2 = cv2.createBackgroundSubtractorMOG2(
                history=self.bg_subtractor_history,
                varThreshold=self.bg_subtractor_var_threshold,
                detectShadows=False
            )
            self.background_reference = None
        else:
            # Static mode - capture background
            self.bg_subtractor = None
            self.preview_mog2 = None
            self.background_reference = self._capture_background()

    def _capture_background(self):
        """Capture background reference untuk static mode."""
        if self.cap is None or not self.cap.isOpened():
            return None
        
        init_frames = []
        for i in range(self.init_capture_count):
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_blurred = cv2.GaussianBlur(gray, self.blur_kernel_size, 0)
            init_frames.append(gray_blurred)
        
        if init_frames:
            return init_frames[-1].copy()
        return None

    def get_frame(self):
        """
        Get frame dengan semua processing (SAMA PERSIS logic dengan main.py).
        
        Returns:
            tuple: (frame, state_dict)
                frame: Camera frame dengan ROI dan detection overlays
                state_dict: Dictionary dengan semua state info
        """
        if self.cap is None or not self.cap.isOpened():
            return None, {}
        
        # Get frame
        ret, frame = self.cap.read()
        if not ret:
            return None, {}
        
        self.frame_count += 1
        
        # Preprocessing (sama seperti main.py)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, self.blur_kernel_size, 0)
        
        # Canny edge detection untuk backup
        edges = cv2.Canny(blurred, 50, 150)
        edges_dilated = cv2.dilate(edges, None, iterations=2)
        
        # ROI edge check
        roi_edges = edges_dilated[self.roi_y:self.roi_y+self.roi_height, 
                                   self.roi_x:self.roi_x+self.roi_width]
        roi_edge_pixels = cv2.countNonZero(roi_edges)
        
        # Simpan roi_edge_pixels untuk preview
        self.roi_edge_pixels = roi_edge_pixels
        
        # Detection based on mode (SAMA PERSIS dengan main.py)
        if self.auto_reset_state:
            # MOG2 mode
            self.fg_mask = self.bg_subtractor.apply(blurred, learningRate=0.005)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            self.fg_mask = cv2.morphologyEx(self.fg_mask, cv2.MORPH_OPEN, kernel)
            self.fg_mask = cv2.dilate(self.fg_mask, kernel, iterations=2)
        else:
            # Static mode
            bg_diff = cv2.absdiff(self.background_reference, blurred)
            _, self.fg_mask_bg = cv2.threshold(bg_diff, self.bg_diff_threshold, 255, cv2.THRESH_BINARY)
            
            if self.prev_frame is not None:
                frame_diff = cv2.absdiff(self.prev_frame, blurred)
                _, self.fg_mask_diff = cv2.threshold(frame_diff, self.frame_diff_threshold, 255, cv2.THRESH_BINARY)
            else:
                self.fg_mask_diff = np.zeros_like(self.fg_mask_bg)
            
            self.prev_frame = blurred.copy()
            self.fg_mask = cv2.bitwise_or(self.fg_mask_bg, self.fg_mask_diff)
            
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            self.fg_mask = cv2.morphologyEx(self.fg_mask, cv2.MORPH_OPEN, kernel)
            self.fg_mask = cv2.dilate(self.fg_mask, kernel, iterations=3)
            self.fg_mask = cv2.erode(self.fg_mask, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(self.fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Simpan contours untuk debug display
        self.contours = contours
        
        # Reset detection flags
        self.object_in_roi = False
        self.has_detected_object = False
        self.has_green_box = False
        self.current_object_bbox_in_roi = None
        
        # Process contours (SAMA PERSIS dengan main.py)
        for contour in contours:
            if cv2.contourArea(contour) < self.min_contour_area:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            self.has_detected_object = True
            
            # Check ROI intersection
            if is_intersecting(x, y, w, h, self.roi_x, self.roi_y, self.roi_width, self.roi_height):
                self.object_in_roi = True
                self.current_object_bbox_in_roi = (x, y, w, h)
            
            # Draw green box jika large enough
            if w >= self.min_box_width and h >= self.min_box_height:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self.has_green_box = True
        
        # Canny edge check
        has_canny_edge_in_roi = roi_edge_pixels >= self.canny_min_edge_threshold
        
        # Persistent ROI tracking (SAMA PERSIS dengan main.py)
        self._update_roi_tracking(has_canny_edge_in_roi)
        
        # Set persistent_object_in_roi = roi_occupied (SAMA PERSIS dengan main.py line 421)
        self.persistent_object_in_roi = self.roi_occupied
        
        # Auto reset logic (SAMA PERSIS dengan main.py)
        self._update_auto_reset()
        
        # State management (SAMA PERSIS dengan main.py)
        self._update_state()
        
        # Draw ROI and overlays (SAMA PERSIS dengan main.py)
        self._draw_overlays(frame)
        
        # Build state dict
        state = self._build_state()
        
        return frame, state

    def _update_roi_tracking(self, has_canny_edge):
        """Update ROI persistent tracking (SAMA PERSIS dengan main.py)."""
        prev_object_moving = self.object_moving
        
        # MOG2 learning phase
        if self.mog2_learning_phase:
            self.mog2_reset_counter += 1
            if self.mog2_reset_counter >= 100:
                self.mog2_learning_phase = False
                self.roi_occupied = False
                self.persistent_object_in_roi = False
                self.indicator_on = False
                self.blink_state = False
                print(f"\n  ✅ [MOG2] Natural learning phase complete - MOG2 ready!")
                print(f"  ✅ [MOG2] Full reset complete - waiting for NEW motion")
            elif self.mog2_reset_counter % 20 == 0:
                print(f"  🔄 [MOG2] Learning... {self.mog2_reset_counter}/100 frames ({self.mog2_reset_counter/30:.1f}s)")
            return
        
        if self.current_object_bbox_in_roi is not None:
            # Object moving in ROI
            self.roi_occupied = True
            self.last_object_bbox_in_roi = self.current_object_bbox_in_roi
            self.canny_roi_edge_counter = 0
            self.canny_detecting = False
            self.object_moving = True
            self.ignore_canny_after_reset = False
            
            # Log movement changes
            if self.object_moving and not prev_object_moving:
                print(f"\n  🚀 [ROI] Object started MOVING")
                self.last_movement_time = time.time()
            elif not self.object_moving and prev_object_moving:
                print(f"\n  ⏸️ [ROI] Object stopped - now STATIONARY")
                self.last_movement_time = time.time()
                
            # Log periodic status
            if self.object_moving and self.movement_log_counter % 100 == 0 and self.movement_log_counter > 0:
                print(f"  🟢 [ROI] Object MOVING - {self.movement_log_counter/30:.1f}s")
            elif not self.object_moving and self.canny_detecting and self.movement_log_counter % 100 == 0 and self.movement_log_counter > 0:
                print(f"  🟡 [ROI] Object STATIONARY (Canny) - {self.movement_log_counter/30:.1f}s")
            
            self.movement_log_counter += 1
            
        elif has_canny_edge and self.roi_occupied and not self.ignore_canny_after_reset:
            # Object stationary (Canny backup)
            self.canny_roi_edge_counter += 1
            self.canny_detecting = True
            self.object_moving = False
            self.movement_log_counter += 1
            
            # Auto reset if stationary too long
            if self.canny_roi_edge_counter >= self.no_motion_threshold:
                self._reset_background()
        elif self.roi_occupied:
            # Object left
            self.canny_roi_edge_counter = 0
            self.canny_detecting = False
            
            if self.object_moving:
                self.object_moving = False
            
            # Grace period
            self.object_stationary_counter += 1
            if self.object_stationary_counter > 60:
                self.roi_occupied = False
                self.last_object_bbox_in_roi = None
                self.ignore_canny_after_reset = False

    def _update_auto_reset(self):
        """Update auto reset logic (SAMA PERSIS dengan main.py)."""
        if self.auto_reset_state:
            if self.persistent_object_in_roi:
                # Ada object di ROI → Reset counter, JANGAN auto reset
                self.roi_empty_frames = 0
                self.object_in_roi_frames += 1
                
                # Debug: object masih di ROI
                if self.object_in_roi_frames % 100 == 0:
                    print(f"  🟢 [{self.object_in_roi_frames/30:.1f}s] Object still in ROI - no auto reset")
            else:
                # Tidak ada object di ROI → Increment counter untuk auto reset
                self.roi_empty_frames += 1
                self.object_in_roi_frames = 0
                
                # Hitung berapa detik ROI kosong
                roi_empty_seconds = int(self.roi_empty_frames / 30)
                
                # Log setiap 1 detik (30 frames)
                if roi_empty_seconds > self.last_log_second and roi_empty_seconds % 1 == 0:
                    remaining = NO_MOTION_THRESHOLD - self.roi_empty_frames
                    remaining_seconds = int(remaining / 30)
                    print(f"  ⏳ [{roi_empty_seconds}s] ROI empty: {self.roi_empty_frames}/{NO_MOTION_THRESHOLD} frames (remaining: ~{remaining_seconds}s)")
                    self.last_log_second = roi_empty_seconds
                
                # Cek apakah sudah mencapai threshold
                if self.roi_empty_frames >= self.no_motion_threshold:
                    self._reset_background()
        else:
            self.roi_empty_frames = 0
            self.last_log_second = 0

    def _reset_background(self):
        """Reset background (SAMA PERSIS dengan main.py)."""
        total_wait_seconds = self.roi_empty_frames / 30
        
        if self.auto_reset_state:
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=self.bg_subtractor_history,
                varThreshold=self.bg_subtractor_var_threshold,
                detectShadows=False
            )
        else:
            self.background_reference = self._capture_background()
            self.prev_frame = None  # Reset prev_frame untuk static mode
        
        # Reset counters
        self.roi_empty_frames = 0
        self.indicator_on = False
        self.blink_state = False
        self.object_present = False
        self.mog2_learning_phase = True
        self.mog2_reset_counter = 0
        self.last_log_second = 0
        
        # Print auto reset log
        print(f"\n{'='*60}")
        print(f"  🔄 [AUTO RESET] Background reset - frame {self.frame_count}")
        print(f"  ⏱️  [AUTO RESET] ROI empty time: {total_wait_seconds:.1f} detik ({int(total_wait_seconds * 30)} frames)")
        print(f"  📊 [AUTO RESET] Threshold: {NO_MOTION_THRESHOLD} frames")
        print(f"{'='*60}\n")
        
        print(f"  ✅ [RESET] ROI status cleared - waiting for new motion detection")
        print(f"  🔄 [MOG2] Starting natural learning phase (3-5 detik)...")

    def _update_state(self):
        """Update indicator state (SAMA PERSIS dengan main.py)."""
        if self.persistent_object_in_roi and self.roi_occupied:
            self.object_detected_frames += 1
            self.object_lost_frames = 0
            
            if self.object_detected_frames >= self.object_confirm_threshold:
                self.object_present = True
                self.roi_box_blink = True
                
                if self.frame_count % self.blink_interval == 0:
                    self.blink_state = not self.blink_state
        else:
            self.object_detected_frames = 0
            self.object_lost_frames = 0
            self.object_present = False
            self.roi_box_blink = False
            self.blink_state = False
        
        self.label_object_in_roi = self.roi_box_blink and self.object_present

    def _draw_overlays(self, frame):
        """Draw ROI and status overlays (SAMA PERSIS dengan main.py)."""
        height, width = frame.shape[:2]
        
        # Draw ROI box
        if self.roi_box_blink and self.blink_state:
            # Kotak biru berkedip (object di ROI)
            roi_color = (255, 0, 0)  # Blue (BGR)
            roi_thickness = 3
        else:
            # Kotak normal (abu-abu tipis)
            roi_color = (128, 128, 128)  # Gray
            roi_thickness = 2

        cv2.rectangle(frame, (self.roi_x, self.roi_y), 
                     (self.roi_x + self.roi_width, self.roi_y + self.roi_height),
                     roi_color, roi_thickness)
        
        # Status label
        if self.label_object_in_roi:
            # Label "OBJECT IN ROI" (hanya saat MOG2 detect)
            status_text = "OBJECT IN ROI"
            status_color = (0, 255, 0)  # Green
        else:
            # Label "NO OBJECT" (MOG2 tidak detect)
            status_text = "NO OBJECT"
            status_color = (0, 0, 255)  # Red
        
        cv2.putText(frame, status_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        
        # Tampilkan status auto reset
        reset_status = f"AUTO RESET: {'ON' if self.auto_reset_state else 'OFF'}"
        reset_color = (0, 255, 255) if self.auto_reset_state else (0, 128, 255)  # Yellow / Orange
        cv2.putText(frame, reset_status, (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, reset_color, 2)
        
        # Tampilkan mode deteksi
        mode_text = "MODE: MOG2 (Adaptive)" if self.auto_reset_state else "MODE: Static BG"
        mode_color = (255, 255, 0) if self.auto_reset_state else (255, 128, 0)  # Cyan / Orange
        cv2.putText(frame, mode_text, (10, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, mode_color, 2)
        
        # Tampilkan counter debug
        debug_text = f"Detected: {self.object_detected_frames} | Lost: {self.object_lost_frames}"
        cv2.putText(frame, debug_text, (10, height - 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        debug_text2 = f"ROI Empty: {self.roi_empty_frames}/{NO_MOTION_THRESHOLD}"
        cv2.putText(frame, debug_text2, (10, height - 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Debug: object detection status
        debug_text4 = f"Obj: {'YES' if self.has_detected_object else 'NO'} | ROI: {'YES' if self.persistent_object_in_roi else 'NO'}"
        cv2.putText(frame, debug_text4, (10, height - 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 255, 150), 1)
        
        # Debug: Movement status
        movement_status = "MOVING" if self.object_moving else "STATIONARY"
        movement_color = (0, 255, 255) if self.object_moving else (0, 128, 255)  # Cyan / Orange
        debug_text5 = f"Status: {movement_status} | Canny: {self.canny_roi_edge_counter}/{NO_MOTION_THRESHOLD}"
        cv2.putText(frame, debug_text5, (10, height - 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, movement_color, 2)
        
        # Debug: contour count dan total area
        debug_text3 = f"Contours: {len(self.contours) if hasattr(self, 'contours') else 0} | Mask: {cv2.countNonZero(self.fg_mask) if self.fg_mask is not None else 0}px"
        cv2.putText(frame, debug_text3, (10, height - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    def _build_state(self):
        """Build state dictionary."""
        return {
            'object_in_roi': self.object_in_roi,
            'object_present': self.object_present,
            'persistent_object_in_roi': self.persistent_object_in_roi,
            'roi_occupied': self.roi_occupied,
            'auto_reset_state': self.auto_reset_state,
            'roi_empty_frames': self.roi_empty_frames,
            'has_detected_object': self.has_detected_object,
            'has_green_box': self.has_green_box,
            'mode': 'MOG2' if self.auto_reset_state else 'Static',
            'indicator_on': self.indicator_on,
            'blink_state': self.blink_state,
            'frame_count': self.frame_count,
        }

    def toggle_auto_reset(self):
        """Toggle auto reset mode (SAMA PERSIS dengan main.py tombol 'o')."""
        self.auto_reset_state = not self.auto_reset_state
        
        if not self.auto_reset_state:
            # Switch to static mode
            self.background_reference = self._capture_background()
        else:
            # Switch to MOG2 mode
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=self.bg_subtractor_history,
                varThreshold=self.bg_subtractor_var_threshold,
                detectShadows=False
            )
        
        return self.auto_reset_state

    def reset_background(self):
        """Manual background reset (SAMA PERSIS dengan main.py tombol 'r')."""
        self._reset_background()

    def toggle_preview(self):
        """Toggle preview window (SAMA PERSIS dengan main.py tombol 'u')."""
        self.show_preview = not self.show_preview
        return self.show_preview

    def draw_preview(self, frame):
        """Draw preview window (SAMA PERSIS dengan main.py)."""
        if not self.show_preview:
            return
        
        # Preprocessing untuk preview
        preview_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        preview_blurred = cv2.GaussianBlur(preview_gray, self.blur_kernel_size, 0)
        
        # Convert ke BGR untuk display
        current_bgr = cv2.cvtColor(preview_blurred, cv2.COLOR_GRAY2BGR)
        
        # Edge detection untuk preview
        preview_edges = cv2.Canny(preview_blurred, 50, 150)
        edges_bgr = cv2.cvtColor(preview_edges, cv2.COLOR_GRAY2BGR)
        
        # Highlight ROI di edge image
        edges_roi_color = edges_bgr.copy()
        cv2.rectangle(edges_roi_color, (self.roi_x, self.roi_y), 
                     (self.roi_x + self.roi_width, self.roi_y + self.roi_height), (0, 255, 0), 2)
        
        if self.auto_reset_state:
            # MOG2 Mode
            fg_mask_preview = self.preview_mog2.apply(preview_blurred, learningRate=0.005)
            _, fg_mask_preview = cv2.threshold(fg_mask_preview, 50, 255, cv2.THRESH_BINARY)
            
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            fg_mask_preview = cv2.morphologyEx(fg_mask_preview, cv2.MORPH_OPEN, kernel)
            fg_mask_preview = cv2.dilate(fg_mask_preview, kernel, iterations=2)
            
            mask_bgr = cv2.cvtColor(fg_mask_preview, cv2.COLOR_GRAY2BGR)
            
            # Resize
            target_height = 200
            h, w = preview_blurred.shape
            scale = target_height / h
            new_size = (int(w * scale), int(h * scale))
            
            current_resized = cv2.resize(current_bgr, new_size)
            edges_resized = cv2.resize(edges_roi_color, new_size)
            mask_resized = cv2.resize(mask_bgr, new_size)
            
            # Add labels
            cv2.putText(current_resized, "GRAYSCALE", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(edges_resized, f"CANNY EDGE (ROI: {self.roi_edge_pixels if hasattr(self, 'roi_edge_pixels') else 0}px)", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(mask_resized, "MOG2 FOREGROUND", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Stack
            combined = np.hstack([current_resized, edges_resized, mask_resized])
            
            # Info
            info_text = [
                f"Mode: MOG2 (Adaptive) - REALTIME",
                f"Resolution: {w}x{h}",
                f"Foreground pixels: {cv2.countNonZero(fg_mask_preview)}",
                "",
                "Press 'u' to close preview"
            ]
        else:
            # Static BG Mode
            bg_diff = cv2.absdiff(self.background_reference, preview_blurred)
            _, mask_bg = cv2.threshold(bg_diff, self.bg_diff_threshold, 255, cv2.THRESH_BINARY)
            
            if self.prev_frame_preview is not None:
                frame_diff = cv2.absdiff(self.prev_frame_preview, preview_blurred)
                _, mask_diff = cv2.threshold(frame_diff, self.frame_diff_threshold, 255, cv2.THRESH_BINARY)
            else:
                mask_diff = np.zeros_like(mask_bg)
            
            self.prev_frame_preview = preview_blurred.copy()
            
            fg_mask_preview = cv2.bitwise_or(mask_bg, mask_diff)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fg_mask_preview = cv2.morphologyEx(fg_mask_preview, cv2.MORPH_OPEN, kernel)
            fg_mask_preview = cv2.dilate(fg_mask_preview, kernel, iterations=3)
            
            # Convert masks to BGR
            bg_bgr = cv2.cvtColor(self.background_reference, cv2.COLOR_GRAY2BGR)
            mask_bg_bgr = cv2.cvtColor(mask_bg, cv2.COLOR_GRAY2BGR)
            mask_diff_bgr = cv2.cvtColor(mask_diff, cv2.COLOR_GRAY2BGR)
            mask_combined_bgr = cv2.cvtColor(fg_mask_preview, cv2.COLOR_GRAY2BGR)
            
            # Resize
            target_height = 150
            h, w = preview_blurred.shape
            scale = target_height / h
            new_size = (int(w * scale), int(h * scale))
            
            current_resized = cv2.resize(current_bgr, new_size)
            bg_resized = cv2.resize(bg_bgr, new_size)
            mask_bg_resized = cv2.resize(mask_bg_bgr, new_size)
            mask_diff_resized = cv2.resize(mask_diff_bgr, new_size)
            mask_combined_resized = cv2.resize(mask_combined_bgr, new_size)
            
            # Add labels
            cv2.putText(current_resized, "CURRENT", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(bg_resized, "BG REFERENCE", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(mask_bg_resized, f"BG DIFF (>{self.bg_diff_threshold})", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(mask_diff_resized, f"FRAME DIFF (>{self.frame_diff_threshold})", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(mask_combined_resized, "COMBINED", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Stack
            combined = np.hstack([
                current_resized,
                bg_resized,
                mask_bg_resized,
                mask_diff_resized,
                mask_combined_resized
            ])
            
            # Info
            info_text = [
                f"Mode: Static Background - REALTIME",
                f"Resolution: {w}x{h}",
                f"BG Threshold: {self.bg_diff_threshold} | Frame Threshold: {self.frame_diff_threshold}",
                f"Combined mask pixels: {cv2.countNonZero(fg_mask_preview)}",
                "",
                "Press 'u' to close preview"
            ]
        
        # Buat panel info
        info_height = 140
        info_panel = np.zeros((info_height, combined.shape[1], 3), dtype=np.uint8)
        for i, text in enumerate(info_text):
            color = (200, 200, 200) if text else (100, 100, 100)
            cv2.putText(info_panel, text, (10, 30 + i * 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1)
        
        # Gabungkan
        full_preview = np.vstack([combined, info_panel])
        
        # Tampilkan preview window
        cv2.imshow('Threshold & Grayscale Preview', full_preview)

    def release(self):
        """Release resources."""
        if self.cap is not None:
            self.cap.release()

    def run_standalone(self):
        """Run sebagai standalone app (testing)."""
        print("TraceHold Widget - Standalone Mode")
        print("Press 'q' to quit, 'r' to reset, 'o' to toggle auto reset")
        
        try:
            while True:
                frame, state = self.get_frame()
                
                if frame is None:
                    break
                
                cv2.imshow('TraceHold Widget', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.reset_background()
                elif key == ord('o'):
                    self.toggle_auto_reset()
        
        finally:
            self.release()
            cv2.destroyAllWindows()


__all__ = ['TraceHoldWidget']
