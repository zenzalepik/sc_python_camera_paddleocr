"""
Parking LPR System - License Plate Recognition
Sistem deteksi plat nomor untuk parkir dengan ROI + Motion Trigger
"""

import os
import cv2
import warnings
import time
import threading
import gc
import re
import sqlite3
from datetime import datetime
from queue import Queue
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings('ignore')
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'


def calculate_blur_score(frame):
    """Menghitung blur score menggunakan Laplacian variance."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def calculate_brightness(frame):
    """Menghitung brightness (kecerahan) frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.mean(gray)[0]


def detect_motion(frame1, frame2, threshold=25):
    """Deteksi motion antara 2 frame."""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    frame_diff = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
    motion_area = cv2.countNonZero(thresh)
    total_pixels = frame1.shape[0] * frame1.shape[1]
    motion_percentage = (motion_area / total_pixels) * 100
    return motion_percentage > threshold


def detect_plate_contours(frame, min_area=500, max_area=50000):
    """Deteksi kandidat plat nomor menggunakan contour detection."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(edges, kernel, iterations=2)
    eroded = cv2.erode(dilated, kernel, iterations=1)
    contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    plates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if min_area <= area <= max_area:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / float(h)
            if 1.5 <= aspect_ratio <= 6.0:
                plates.append((x, y, w, h, cnt))
    return plates


def validate_plate_format(text):
    """Validasi format plat nomor Indonesia."""
    text = text.upper().strip()
    text = re.sub(r'[^\w\s]', '', text)
    pattern = r'^[A-Z]{1,2}\s?\d{3,4}\s?[A-Z]{0,3}$'
    return bool(re.match(pattern, text))


def init_database(db_path):
    """Inisialisasi database SQLite."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT NOT NULL,
            confidence REAL,
            entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            exit_time TIMESTAMP,
            image_path TEXT,
            status TEXT DEFAULT 'inside',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_plate ON parking_logs(plate_number)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_entry_time ON parking_logs(entry_time)')
    conn.commit()
    return conn


def save_parking_record(conn, plate_number, confidence, image_path=None):
    """Simpan record parkir ke database."""
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM parking_logs WHERE plate_number = ? AND status = \'inside\' ORDER BY entry_time DESC LIMIT 1', (plate_number,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute('UPDATE parking_logs SET status = \'out\', exit_time = CURRENT_TIMESTAMP WHERE id = ?', (existing[0],))
        action = 'EXIT'
    else:
        cursor.execute('INSERT INTO parking_logs (plate_number, confidence, image_path, status) VALUES (?, ?, ?, \'inside\')', (plate_number, confidence, image_path))
        action = 'ENTRY'
    conn.commit()
    return action


class ParkingLPR:
    """Main class untuk Parking LPR System."""

    def __init__(self):
        # Load konfigurasi
        self.camera_width = int(os.getenv('CAMERA_WIDTH', '640'))
        self.camera_height = int(os.getenv('CAMERA_HEIGHT', '480'))
        self.camera_fps = int(os.getenv('CAMERA_FPS', '30'))

        # Parking mode
        self.parking_mode = os.getenv('PARKING_MODE', 'True') == 'True'
        self.lpr_mode = os.getenv('LPR_MODE', 'True') == 'True'
        self.motion_trigger = os.getenv('MOTION_TRIGGER', 'True') == 'True'
        self.motion_threshold = int(os.getenv('MOTION_THRESHOLD', '25'))

        # ROI
        self.roi_enabled = os.getenv('ROI_ENABLED', 'True') == 'True'
        self.roi_x = int(os.getenv('ROI_X', '150'))
        self.roi_y = int(os.getenv('ROI_Y', '180'))
        self.roi_width = int(os.getenv('ROI_WIDTH', '340'))
        self.roi_height = int(os.getenv('ROI_HEIGHT', '200'))

        # Auto-adjust based on mode
        if not self.lpr_mode:
            self.roi_enabled = False
            self.enable_validation = False
            print(f"\n📝 MODE: GENERAL OCR (detect all text)")
        else:
            print(f"\n🅿️ MODE: LPR (license plate only)")

        # Plate detection
        self.plate_detection_mode = os.getenv('PLATE_DETECTION_MODE', 'contour')
        self.min_plate_area = int(os.getenv('MIN_PLATE_AREA', '500'))
        self.max_plate_area = int(os.getenv('MAX_PLATE_AREA', '50000'))

        # Multi-frame selection
        self.multi_frame_selection = os.getenv('MULTI_FRAME_SELECTION', 'True') == 'True'
        self.best_frame_count = int(os.getenv('BEST_FRAME_COUNT', '8'))
        self.focus_weight = float(os.getenv('FOCUS_WEIGHT', '0.5'))
        self.brightness_weight = float(os.getenv('BRIGHTNESS_WEIGHT', '0.3'))
        self.angle_weight = float(os.getenv('ANGLE_WEIGHT', '0.2'))

        # OCR - PaddleOCR dengan ONNX support
        self.ocr_scale = float(os.getenv('OCR_SCALE', '1.0'))
        paddle_lang = os.getenv('PADDLE_LANG', 'en')
        paddle_use_angle_cls = os.getenv('PADDLE_USE_ANGLE_CLS', 'True') == 'True'
        self.paddle_use_onnx = os.getenv('PADDLE_OCR_ONNX', 'False') == 'True'

        # Validation
        self.enable_validation = os.getenv('ENABLE_PLATE_VALIDATION', 'True') == 'True'
        self.plate_regex = os.getenv('PLATE_FORMAT_REGEX', '^[A-Z]{1,2}\\s?\\d{3,4}\\s?[A-Z]{0,3}$')

        # Display
        self.show_fps = os.getenv('SHOW_FPS', 'True') == 'True'
        self.show_roi_box = os.getenv('SHOW_ROI_BOX', 'True') == 'True'
        self.show_plate_box = os.getenv('SHOW_PLATE_BOX', 'True') == 'True'
        self.show_debug_info = os.getenv('SHOW_DEBUG_INFO', 'True') == 'True'
        self.result_display_duration = int(os.getenv('RESULT_DISPLAY_DURATION', '10'))

        # Database
        self.enable_database = os.getenv('ENABLE_DATABASE', 'True') == 'True'
        self.db_path = os.getenv('DATABASE_PATH', 'parking.db')
        self.auto_save = os.getenv('AUTO_SAVE', 'True') == 'True'

        # Memory
        self.debug_mode = os.getenv('DEBUG_MODE', 'False') == 'False'
        self.enable_memory_cleanup = os.getenv('ENABLE_MEMORY_CLEANUP', 'True') == 'True'
        self.memory_cleanup_interval = int(os.getenv('MEMORY_CLEANUP_INTERVAL', '60'))

        # Inisialisasi PaddleOCR dengan ONNX support
        print("Initializing PaddleOCR...")
        if self.paddle_use_onnx:
            print("  🚀 Using ONNX optimized model (faster)")
            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(
                    use_angle_cls=paddle_use_angle_cls,
                    lang=paddle_lang,
                    use_onnx=True
                )
            except Exception as e:
                print(f"  ⚠️ ONNX not available, fallback to mobile model: {e}")
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(use_angle_cls=paddle_use_angle_cls, lang=paddle_lang)
        else:
            print("  📱 Using mobile model (default)")
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=paddle_use_angle_cls, lang=paddle_lang)

        # Inisialisasi kamera
        print("Initializing camera...")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.camera_fps)

        if not self.cap.isOpened():
            print("Error: Cannot open camera")
            return

        # Inisialisasi database
        if self.enable_database:
            print(f"Initializing database: {self.db_path}")
            self.conn = init_database(self.db_path)
        else:
            self.conn = None

        # State variables
        self.last_frame = None
        self.motion_detected = False
        self.collecting_frames = False
        self.frame_buffer = []
        self.last_plate_result = None
        self.last_plate_time = None
        self.cooldown_time = 0
        self.cooldown_duration = 3

        # FPS counter
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0

        # Memory cleanup
        self.last_cleanup_time = time.time()
        self.cleanup_count = 0

        self.print_config()

    def print_config(self):
        """Print konfigurasi."""
        print("\n" + "="*50)
        print("PARKING LPR SYSTEM - Configuration")
        print("="*50)
        print(f"Camera: {self.camera_width}x{self.camera_height}@{self.camera_fps}fps")
        print(f"Mode: {'LPR' if self.lpr_mode else 'GENERAL OCR'}")
        print(f"OCR Model: {'ONNX (fast)' if self.paddle_use_onnx else 'Mobile (default)'}")
        print(f"Parking Mode: {'ON' if self.parking_mode else 'OFF'}")
        print(f"Motion Trigger: {'ON' if self.motion_trigger else 'OFF'}")

        if self.lpr_mode:
            print(f"ROI: ({self.roi_x}, {self.roi_y}) {self.roi_width}x{self.roi_height}")
            print(f"Plate Detection: {self.plate_detection_mode}")
            print(f"Plate Validation: {'ON' if self.enable_validation else 'OFF'}")
        else:
            print(f"Scan: FULL FRAME (all text)")
            print(f"Validation: OFF")

        print(f"Multi-frame: {'ON' if self.multi_frame_selection else 'OFF'} ({self.best_frame_count} frames)")
        print(f"Database: {'ON' if self.enable_database else 'OFF'}")
        print("="*50 + "\n")

    def extract_roi(self, frame):
        """Extract ROI dari frame."""
        if not self.roi_enabled:
            return frame
        x, y, w, h = self.roi_x, self.roi_y, self.roi_width, self.roi_height
        x = max(0, min(x, frame.shape[1] - 1))
        y = max(0, min(y, frame.shape[0] - 1))
        w = min(w, frame.shape[1] - x)
        h = min(h, frame.shape[0] - y)
        return frame[y:y+h, x:x+w]

    def score_frame(self, frame):
        """Score frame untuk best frame selection."""
        focus_score = calculate_blur_score(frame)
        focus_norm = min(100, focus_score / 5)
        brightness = calculate_brightness(frame)
        brightness_score = 100 - abs(150 - brightness) * 0.67
        brightness_norm = max(0, min(100, brightness_score))
        h, w = frame.shape[:2]
        angle_score = 100 - (abs(w/2 - w/2) + abs(h/2 - h/2)) / 5
        angle_norm = max(0, min(100, angle_score))
        total_score = (focus_norm * self.focus_weight + brightness_norm * self.brightness_weight + angle_norm * self.angle_weight)
        return total_score

    def perform_ocr(self, plate_crop):
        """Perform OCR pada plat nomor."""
        if plate_crop is None or plate_crop.size == 0:
            return None, 0.0
        if self.ocr_scale != 1.0:
            h, w = plate_crop.shape[:2]
            plate_crop = cv2.resize(plate_crop, (int(w * self.ocr_scale), int(h * self.ocr_scale)))
        result = self.ocr.ocr(plate_crop)
        if not result:
            return None, 0.0
        best_text = None
        best_confidence = 0.0
        for res in result:
            if isinstance(res, dict):
                rec_texts = res.get('rec_texts', [])
                rec_scores = res.get('rec_scores', [])
                for text, score in zip(rec_texts, rec_scores):
                    if score > best_confidence:
                        best_text = text.strip()
                        best_confidence = score
            elif isinstance(res, (list, tuple)) and len(res) >= 2:
                rec_result = res[1]
                if isinstance(rec_result, (list, tuple)) and len(rec_result) >= 2:
                    text = rec_result[0].strip()
                    score = rec_result[1]
                    if score > best_confidence:
                        best_text = text
                        best_confidence = score
        return best_text, best_confidence

    def run(self):
        """Main loop."""
        print("🚀 Starting Parking LPR System...")
        print("Press 'q' to exit\n")

        while True:
            loop_start = time.time()
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to read frame")
                break

            self.fps_counter += 1
            if time.time() - self.fps_start_time >= 1.0:
                self.current_fps = self.fps_counter / (time.time() - self.fps_start_time)
                self.fps_counter = 0
                self.fps_start_time = time.time()

            motion_detected = False
            if self.motion_trigger and self.last_frame is not None:
                motion_detected = detect_motion(self.last_frame, frame, self.motion_threshold)

            self.last_frame = frame.copy()
            in_cooldown = time.time() - self.cooldown_time < self.cooldown_duration

            plate_crop = None
            plate_location = None
            detected_plate_text = None
            detected_confidence = 0.0

            if not in_cooldown:
                if self.multi_frame_selection and motion_detected and not self.collecting_frames:
                    self.collecting_frames = True
                    self.frame_buffer = []
                    print("\n📸 Motion detected! Collecting frames...")

                if self.collecting_frames:
                    roi_frame = self.extract_roi(frame)
                    score = self.score_frame(roi_frame)
                    self.frame_buffer.append({'frame': roi_frame.copy(), 'score': score, 'time': time.time()})

                    if len(self.frame_buffer) >= self.best_frame_count:
                        self.frame_buffer.sort(key=lambda x: x['score'], reverse=True)
                        best = self.frame_buffer[0]
                        print(f"  Best frame score: {best['score']:.1f}")

                        plates = detect_plate_contours(best['frame'], self.min_plate_area, self.max_plate_area)

                        if plates:
                            plates.sort(key=lambda x: x[2] * x[3], reverse=True)
                            x, y, w, h, cnt = plates[0]
                            padding = 5
                            x1 = max(0, x - padding)
                            y1 = max(0, y - padding)
                            x2 = min(best['frame'].shape[1], x + w + padding)
                            y2 = min(best['frame'].shape[0], y + h + padding)
                            plate_crop = best['frame'][y1:y2, x1:x2]
                            plate_location = (x, y, w, h)

                            print("  Performing OCR...")
                            detected_plate_text, detected_confidence = self.perform_ocr(plate_crop)

                            if detected_plate_text:
                                print(f"  OCR Result: {detected_plate_text} ({detected_confidence:.2f})")

                                if self.enable_validation:
                                    if validate_plate_format(detected_plate_text):
                                        print(f"  ✅ Plate format VALID")
                                    else:
                                        print(f"  ❌ Plate format INVALID - rejecting")
                                        detected_plate_text = None

                                if detected_plate_text and self.auto_save and self.conn:
                                    action = save_parking_record(self.conn, detected_plate_text, detected_confidence)
                                    print(f"  💾 Saved to database: {action}")

                                self.last_plate_result = detected_plate_text
                                self.last_plate_time = time.time()
                                self.cooldown_time = time.time()

                        self.collecting_frames = False
                        self.frame_buffer = []

            self.draw_ui(frame, plate_location, detected_plate_text, detected_confidence, motion_detected, in_cooldown)

            cv2.imshow('Parking LPR System', frame)

            if self.enable_memory_cleanup:
                if time.time() - self.last_cleanup_time >= self.memory_cleanup_interval:
                    self.frame_buffer.clear()
                    gc.collect()
                    self.cleanup_count += 1
                    self.last_cleanup_time = time.time()
                    if self.debug_mode:
                        print(f"[CLEANUP #{self.cleanup_count}] Memory cleaned")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def draw_ui(self, frame, plate_location, plate_text, confidence, motion_detected, in_cooldown):
        """Draw UI elements on frame."""
        frame_height, frame_width = frame.shape[:2]

        if self.show_roi_box and self.roi_enabled:
            cv2.rectangle(frame, (self.roi_x, self.roi_y), (self.roi_x + self.roi_width, self.roi_y + self.roi_height), (255, 255, 0), 2)
            cv2.putText(frame, "ROI Zone", (self.roi_x, self.roi_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        if self.show_plate_box and plate_location and self.roi_enabled:
            x, y, w, h = plate_location
            global_x = x + self.roi_x
            global_y = y + self.roi_y
            cv2.rectangle(frame, (global_x, global_y), (global_x + w, global_y + h), (0, 255, 0), 2)

        status_color = (0, 255, 0) if in_cooldown else (0, 255, 255)
        status_text = "READY" if not in_cooldown else f"COOLDOWN ({self.cooldown_duration - (time.time() - self.cooldown_time):.1f}s)"
        cv2.putText(frame, f"Status: {status_text}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)

        motion_color = (0, 0, 255) if motion_detected else (100, 100, 100)
        cv2.circle(frame, (frame_width - 20, 20), 8, motion_color, -1)

        if self.last_plate_result:
            time_ago = time.time() - self.last_plate_time if self.last_plate_time else 0
            if time_ago <= self.result_display_duration:
                bg_color = (0, 100, 0) if time_ago < 5 else (50, 50, 50)
                overlay = frame.copy()
                cv2.rectangle(overlay, (frame_width - 220, 10), (frame_width - 10, 85), bg_color, -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                cv2.putText(frame, f"Last: {self.last_plate_result}", (frame_width - 210, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(frame, f"{time_ago:.0f}s ago", (frame_width - 210, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                remaining = self.result_display_duration - time_ago
                progress_width = int((remaining / self.result_display_duration) * 200)
                progress_color = (0, 255, 0) if remaining > 5 else (0, 0, 255)
                cv2.rectangle(frame, (frame_width - 215, 65), (frame_width - 215 + progress_width, 75), progress_color, -1)

        if plate_text:
            cv2.putText(frame, f"Detected: {plate_text} ({confidence:.2f})", (10, frame_height - 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if self.show_fps:
            fps_color = (0, 255, 0) if self.current_fps >= self.camera_fps * 0.9 else (0, 255, 255)
            cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, fps_color, 1)

        if self.show_debug_info:
            info_y = 75
            cv2.putText(frame, f"Motion: {'YES' if motion_detected else 'NO'}", (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            cv2.putText(frame, f"Collecting: {len(self.frame_buffer)}/{self.best_frame_count}", (10, info_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    def cleanup(self):
        """Cleanup resources."""
        print("\nCleaning up...")
        if self.cap:
            self.cap.release()
        if self.conn:
            self.conn.close()
        cv2.destroyAllWindows()
        if self.enable_memory_cleanup:
            gc.collect()
            print(f"Total memory cleanups: {self.cleanup_count}")
        print("Done!")


def main():
    """Main entry point."""
    lpr = ParkingLPR()
    lpr.run()


if __name__ == "__main__":
    main()
