"""
Real-time Object Distance Detection with YOLO - Single Object Tracking
Deteksi object mendekat/menjauh dari kamera secara real-time

LOGIKA BARU:
- Fokus track 1 object terbesar (paling dekat)
- Beri ID unik (PERSON_1, PERSON_2, dst)
- SIAGA harus hilang dulu sebelum track object baru
- Tampilkan ID di label
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime


class ObjectDistanceTracker:
    """Tracker untuk mendeteksi apakah object mendekat atau menjauh.
    
    LOGIKA BARU:
    - Hanya track 1 object terbesar (paling dekat)
    - Beri ID unik yang konsisten
    - SIAGA harus hilang dulu sebelum track object baru
    """

    def __init__(self, max_history=30, siaga_frame_threshold=3, siaga_hold_time=3.0):
        self.max_history = max_history
        self.siaga_frame_threshold = siaga_frame_threshold
        self.siaga_hold_time = siaga_hold_time
        
        # Object tracking dengan ID unik
        self.tracked_object_id = None
        self.tracked_object_history = []
        self.tracked_object_bbox = None
        self.tracked_object_area = 0  # Area object yang di-track
        
        # Camera view info untuk focus percentage
        self.camera_view_area = 0  # Total area camera view
        
        # SIAGA tracking
        self.siaga_active = False
        self.approaching_consecutive_count = 0
        self.siaga_trigger_time = None
        self.siaga_expire_time = None
        self.siaga_clear_time = None
        
        # SIAGA PERSISTENCE - untuk handle object sangat dekat
        self.last_siaga_area = 0  # Area terakhir saat SIAGA aktif
        self.siaga_persistence_active = False  # Mode persistence
        self.siaga_persistence_start_time = None  # Waktu mulai persistence
        self.siaga_persistence_delay = 0.02  # 20ms delay sebelum clear SIAGA
        
        # Object counter untuk ID
        self.object_counter = 0
        
    def update(self, detections):
        """Update tracker dengan deteksi baru."""
        current_time = time.time()
        
        # Filter hanya person (class_id = 0)
        person_detections = [d for d in detections if d['class_id'] == 0]
        
        # Jika tidak ada person, handle SIAGA timer
        if not person_detections:
            self._handle_no_detection(current_time)
            return {'tracked_object': None, 'status': 'no_detection'}
        
        # Pilih object TERBESAR (area terbesar = paling dekat)
        largest_detection = max(
            person_detections,
            key=lambda d: (d['bbox'][2] - d['bbox'][0]) * (d['bbox'][3] - d['bbox'][1])
        )
        
        current_area = (largest_detection['bbox'][2] - largest_detection['bbox'][0]) * \
                       (largest_detection['bbox'][3] - largest_detection['bbox'][1])

        # SIAGA PERSISTENCE LOGIC (BARU):
        # Jika SIAGA aktif dan object ≥80% camera view,
        # anggap object terlalu DEKAT (melebihi layar), JANGAN clear SIAGA!
        if self.siaga_active and self.camera_view_area > 0:
            # Hitung persentase object terhadap camera view
            object_view_percentage = (current_area / self.camera_view_area) * 100
            
            # Jika object ≥80% camera view → PERSISTENCE MODE!
            if object_view_percentage >= 80:
                self.siaga_persistence_active = True
                if self.siaga_persistence_start_time is None:
                    self.siaga_persistence_start_time = current_time
                    print(f"\n[🔒 PERSISTENCE] Object {object_view_percentage:.1f}% camera view - SIAGA dipertahankan!")
            else:
                # Object <80% → reset persistence timer
                self.siaga_persistence_active = False
                self.siaga_persistence_start_time = None
        
        # Cek apakah kita boleh ganti object
        if self.siaga_active:
            # SIAGA masih aktif, HARUS track object yang sama
            if self.tracked_object_id is None:
                # Object hilang tapi SIAGA masih aktif (masih dalam hold time)
                self._handle_no_detection(current_time)
                return {'tracked_object': None, 'status': 'siaga_active_no_object'}
        else:
            # SIAGA cleared, boleh pilih object baru
            if self.tracked_object_id is None or self._is_different_object(largest_detection):
                if self.tracked_object_id is None:
                    self.object_counter += 1
                    self.tracked_object_id = f"PERSON_{self.object_counter}"
                    print(f"\n[🎯 NEW TRACK] Started tracking {self.tracked_object_id}")
                else:
                    self.object_counter += 1
                    self.tracked_object_id = f"PERSON_{self.object_counter}"
                    print(f"\n[🎯 NEW TRACK] Switched to {self.tracked_object_id}")
                
                self.tracked_object_history = []
        
        # Update tracked object info
        self.tracked_object_bbox = largest_detection['bbox']
        self.tracked_object_area = current_area  # Simpan area untuk persistence check
        
        # Simpan ke history
        self.tracked_object_history.append({
            'area': current_area,
            'bbox': largest_detection['bbox'],
            'conf': largest_detection['confidence'],
            'time': current_time
        })
        
        # Batasi history
        if len(self.tracked_object_history) > self.max_history:
            self.tracked_object_history = self.tracked_object_history[-self.max_history:]
        
        # Analisa trend
        status = self._analyze_trend()
        
        # Update SIAGA logic
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
                print(f"\n[⏱️ SIAGA TIMER] Object hilang - expire dalam {self.siaga_hold_time}s")
    
    def _is_different_object(self, detection):
        """Cek apakah detection ini object yang berbeda."""
        if self.tracked_object_bbox is None:
            return True
        
        current_bbox = detection['bbox']
        tracked_bbox = self.tracked_object_bbox
        
        # Hitung center distance
        current_center = ((current_bbox[0] + current_bbox[2]) / 2, 
                         (current_bbox[1] + current_bbox[3]) / 2)
        tracked_center = ((tracked_bbox[0] + tracked_bbox[2]) / 2, 
                         (tracked_bbox[1] + tracked_bbox[3]) / 2)
        
        distance = ((current_center[0] - tracked_center[0])**2 + 
                   (current_center[1] - tracked_center[1])**2)**0.5
        
        # Jika distance > 100 pixel, anggap object berbeda
        return distance > 100

    def _analyze_trend(self):
        """Analisa trend pergerakan object yang di-track."""
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
        """Update SIAGA status untuk object yang di-track.
        
        LOGIKA BARU:
        - SIAGA aktif setelah 3 frame MENDEKAT
        - SIAGA HILANG jika object MENJAUH
        - SIAGA hold 3 detik jika object hilang
        - SIAGA PERSISTENCE: Jika object ≥80% camera view, tunggu 20ms sebelum clear
        """
        # Update last_siaga_area jika SIAGA aktif
        if self.siaga_active and self.tracked_object_area > 0:
            self.last_siaga_area = self.tracked_object_area
        
        if status == 'approaching':
            self.approaching_consecutive_count += 1

            if self.approaching_consecutive_count >= self.siaga_frame_threshold:
                if not self.siaga_active:
                    self.siaga_active = True
                    self.siaga_trigger_time = current_time
                    print(f"\n[⚠️ SIAGA] {self.tracked_object_id} terdeteksi mendekat!")
                self.siaga_expire_time = None
                self.siaga_persistence_active = False
                self.siaga_persistence_start_time = None
        elif status == 'moving_away':
            # Object MENJAUH → Cek persistence dulu
            if self.siaga_persistence_active:
                # Cek apakah sudah 20ms
                persistence_duration = current_time - self.siaga_persistence_start_time
                if persistence_duration < self.siaga_persistence_delay:
                    # Belum 20ms → PERTAHANKAN SIAGA!
                    print(f"\n[⏱️ PERSISTENCE] {persistence_duration*1000:.1f}ms/20ms - SIAGA masih dipertahankan!")
                    self.siaga_expire_time = None
                else:
                    # Sudah 20ms → Clear SIAGA
                    self.siaga_active = False
                    self.approaching_consecutive_count = 0
                    self.siaga_expire_time = None
                    self.last_siaga_area = 0
                    self.siaga_persistence_active = False
                    self.siaga_persistence_start_time = None
                    print(f"\n[✓ SIAGA CLEARED] {self.tracked_object_id} - 20ms persistence complete!")
            else:
                # Object MENJAUH (tidak dalam persistence) → RESET SIAGA langsung!
                if self.siaga_active:
                    self.siaga_active = False
                    self.approaching_consecutive_count = 0
                    self.siaga_expire_time = None
                    self.last_siaga_area = 0
                    self.siaga_persistence_active = False
                    self.siaga_persistence_start_time = None
                    print(f"\n[✓ SIAGA CLEARED] {self.tracked_object_id} MENJAUH - SIAGA direset!")
                self.approaching_consecutive_count = 0
        else:
            # STABLE - cek persistence
            if self.siaga_persistence_active:
                # Mode persistence aktif, JANGAN clear SIAGA!
                pass
            else:
                # Reset counter tapi jangan clear SIAGA
                self.approaching_consecutive_count = 0

        if self.siaga_active:
            self.siaga_expire_time = None
    
    def reset_tracking(self):
        """Reset semua tracking dan SIAGA (untuk tombol reset)."""
        was_siaga = self.siaga_active
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
        
        if was_siaga:
            print(f"\n[🔄 RESET] Tracking dan SIAGA direset manual!")
        else:
            print(f"\n[🔄 RESET] Tracking direset!")
    
    def check_siaga_expire(self, current_time):
        """Check apakah SIAGA sudah expire."""
        if self.siaga_active and self.siaga_expire_time is not None:
            if current_time >= self.siaga_expire_time:
                self.siaga_active = False
                self.approaching_consecutive_count = 0
                self.tracked_object_id = None
                self.tracked_object_bbox = None
                self.tracked_object_history = []
                self.siaga_clear_time = current_time
                self.siaga_expire_time = None
                
                print(f"\n[✓ SIAGA CLEARED] Siap track object baru")
    
    def is_siaga_active(self):
        """Check apakah SIAGA aktif."""
        return self.siaga_active
    
    def get_tracked_object_id(self):
        """Get ID object yang di-track."""
        return self.tracked_object_id


class RealTimeDistanceDetector:
    """Real-time object distance detection dengan YOLO."""

    def __init__(self, camera_id=0, confidence_threshold=0.5):
        self.camera_id = camera_id
        self.confidence_threshold = confidence_threshold
        
        # Load YOLO model
        print("Loading YOLO model...")
        self.model = YOLO('yolov8n.pt')
        print("[OK] YOLO model loaded!")
        
        # Initialize tracker
        self.tracker = ObjectDistanceTracker(
            max_history=30,
            siaga_frame_threshold=3,
            siaga_hold_time=3.0
        )
        
        # Class names dari YOLO
        self.class_names = self.model.names
        
        # Target classes untuk tracking (0 = person)
        self.target_classes = [0]
        
        # Video capture
        self.cap = None
        
        # Stats
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
        
    def start(self):
        """Start video capture."""
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            print(f"[ERROR] Cannot open camera {self.camera_id}")
            return False
        
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Set camera view area untuk focus percentage calculation
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.tracker.camera_view_area = frame_width * frame_height
        
        print(f"[OK] Camera opened: {self.camera_id}")
        print(f"[INFO] Camera view area: {frame_width}x{frame_height} = {self.tracker.camera_view_area}px")
        return True
    
    def stop(self):
        """Stop video capture."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def detect_objects(self, frame):
        """Detect objects in frame."""
        results = self.model(frame, verbose=False, conf=self.confidence_threshold)[0]
        
        detections = []
        
        if results.boxes is not None:
            for i in range(len(results.boxes)):
                box = results.boxes[i]
                class_id = int(box.cls[0])
                conf = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy()
                
                if class_id in self.target_classes:
                    detections.append({
                        'class_id': class_id,
                        'bbox': bbox,
                        'confidence': conf,
                        'class_name': self.class_names[class_id]
                    })
        
        return detections
    
    def draw_detections(self, frame, result):
        """Draw detection pada frame dengan ID dan status."""
        tracked_object = result.get('tracked_object')
        status = result.get('status', 'stable')

        if tracked_object is None:
            return

        bbox = tracked_object['bbox']
        obj_id = tracked_object['id']
        conf = tracked_object['confidence']

        # Check SIAGA status untuk badge (tapi TIDAK untuk warna box)
        is_siaga = self.tracker.is_siaga_active()

        # LOGIKA BARU: Warna bounding box SELALU sesuai status, terlepas dari SIAGA
        # SIAGA hanya tampilkan badge, tidak ubah warna bounding box
        if status == 'approaching':
            color = (0, 0, 255)  # Merah - Mendekat
        elif status == 'moving_away':
            color = (255, 0, 0)  # Biru - Menjauh
        else:
            color = (0, 255, 0)  # Hijau - Tetap

        # Draw bounding box
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

        # Status text
        if status == 'approaching':
            status_text = "MENDEKAT"
        elif status == 'moving_away':
            status_text = "MENJAUH"
        else:
            status_text = "TETAP"

        # Label dengan ID, confidence, dan status
        label = f"{obj_id}: {conf:.2f} [{status_text}]"

        # Background untuk label
        (label_w, label_h), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
        )
        cv2.rectangle(
            frame,
            (x1, y1 - label_h - baseline - 5),
            (x1 + label_w, y1),
            color,
            -1
        )
        
        # Text label
        cv2.putText(
            frame,
            label,
            (x1, y1 - baseline),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        # SIAGA indicator (jika aktif)
        if is_siaga:
            siaga_text = "⚠️ SIAGA"
            (siaga_w, siaga_h), siaga_baseline = cv2.getTextSize(
                siaga_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 3
            )
            
            siaga_y = y1 - label_h - baseline - 10 - siaga_h - 5
            cv2.rectangle(
                frame,
                (x1, siaga_y),
                (x1 + siaga_w + 10, siaga_y + siaga_h + 5),
                (0, 140, 255),
                -1
            )
            
            # Blinking border
            if int(time.time() * 3) % 2 == 0:
                cv2.rectangle(
                    frame,
                    (x1, siaga_y),
                    (x1 + siaga_w + 10, siaga_y + siaga_h + 5),
                    (0, 0, 255),
                    2
                )
            
            cv2.putText(
                frame,
                siaga_text,
                (x1 + 5, siaga_y + siaga_h),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                3
            )

    def draw_info_panel(self, frame, result):
        """Draw info panel dengan FPS dan SIAGA status."""
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
        
        # Check SIAGA status
        is_siaga = self.tracker.is_siaga_active()
        siaga_cleared = self.tracker.siaga_clear_time is not None
        
        # Panel height
        panel_height = 120 if (is_siaga or siaga_cleared) else 100
        cv2.rectangle(frame, (0, 0), (450, panel_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, 0), (450, panel_height), (255, 255, 255), 2)
        
        # FPS
        cv2.putText(
            frame,
            f"FPS: {self.fps:.1f}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(
            frame,
            f"Time: {timestamp}",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )
        
        # SIAGA ALERT
        if is_siaga:
            blink_color = (0, 0, 255) if int(time.time() * 4) % 2 == 0 else (0, 140, 255)
            
            cv2.rectangle(
                frame,
                (10, 65),
                (440, 95),
                blink_color,
                -1
            )
            
            cv2.putText(
                frame,
                f"⚠️ SIAGA: Object MENDEKAT!",
                (20, 87),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            print(f"\r[⚠️ SIAGA ACTIVE] Object approaching - {timestamp}", end='')
        
        # SIAGA CLEARED feedback
        elif siaga_cleared:
            if current_time - self.tracker.siaga_clear_time <= 2.0:
                cv2.rectangle(
                    frame,
                    (10, 65),
                    (440, 95),
                    (0, 255, 0),
                    -1
                )
                
                cv2.putText(
                    frame,
                    f"✓ SIAGA CLEARED - Siap track object baru",
                    (20, 87),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
                
                print(f"\r[✓ SIAGA CLEARED] Siap track object baru - {timestamp}", end='')
            else:
                self.tracker.siaga_clear_time = None
        
        # Legend
        legend_y = 105 if not (is_siaga or siaga_cleared) else 105
        cv2.putText(
            frame,
            "Legend:",
            (10, legend_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )
        
        # FOCUS PERCENTAGE DISPLAY (NEW!)
        tracked_id = self.tracker.get_tracked_object_id()
        if tracked_id and result and result.get('tracked_object'):
            obj_area = result['tracked_object'].get('area', 0)
            if self.tracker.camera_view_area > 0:
                focus_percentage = (obj_area / self.tracker.camera_view_area) * 100
                
                # Focus bar color based on percentage
                if focus_percentage < 30:
                    focus_color = (0, 0, 255)  # Merah - Sangat jauh
                elif focus_percentage < 50:
                    focus_color = (0, 140, 255)  # Orange - Jauh
                elif focus_percentage < 70:
                    focus_color = (0, 255, 255)  # Kuning - Sedang
                elif focus_percentage < 90:
                    focus_color = (0, 255, 0)  # Hijau - Dekat (optimal)
                else:
                    focus_color = (255, 0, 0)  # Biru - Sangat dekat
                
                # Draw focus bar text
                cv2.putText(
                    frame,
                    f"🎯 FOCUS: {focus_percentage:.1f}%",
                    (10, legend_y + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    focus_color,
                    2
                )
                
                # Draw focus bar (10 segments)
                bar_x = 160
                bar_y = legend_y + 33
                segment_width = 25
                total_segments = 10
                filled_segments = int(focus_percentage / 10)
                
                for i in range(total_segments):
                    if i < filled_segments:
                        cv2.rectangle(
                            frame,
                            (bar_x + i * segment_width, bar_y),
                            (bar_x + (i + 1) * segment_width - 2, bar_y + 12),
                            focus_color,
                            -1
                        )
                    else:
                        cv2.rectangle(
                            frame,
                            (bar_x + i * segment_width, bar_y),
                            (bar_x + (i + 1) * segment_width - 2, bar_y + 12),
                            (100, 100, 100),
                            -1
                        )
        
        # Tambahkan debug info - status saat ini
        tracked_id = self.tracker.get_tracked_object_id()
        if tracked_id:
            status = result.get('status', 'N/A') if result else 'N/A'
            persistence_status = " [PERSISTENCE]" if self.tracker.siaga_persistence_active else ""
            debug_status = f"Tracking: {tracked_id} | Status: {status}{persistence_status}"
            cv2.putText(
                frame,
                debug_status,
                (10, legend_y + 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1
            )
        
        # Merah - Mendekat
        cv2.circle(frame, (100, legend_y + 15), 8, (0, 0, 255), -1)
        cv2.putText(
            frame,
            "Mendekat",
            (115, legend_y + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
        
        # Hijau - Tetap
        cv2.circle(frame, (220, legend_y + 15), 8, (0, 255, 0), -1)
        cv2.putText(
            frame,
            "Tetap",
            (235, legend_y + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
        
        # Biru - Menjauh
        cv2.circle(frame, (100, legend_y + 35), 8, (255, 0, 0), -1)
        cv2.putText(
            frame,
            "Menjauh",
            (115, legend_y + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
    
    def run(self):
        """Run real-time detection."""
        if not self.start():
            return
        
        print("\n" + "="*70)
        print("Real-time Object Distance Detection - Single Object Tracking")
        print("="*70)
        print("\nControls:")
        print("  - Press 'q' to quit")
        print("  - Press 's' to save snapshot")
        print("  - Press '+' to increase confidence threshold")
        print("  - Press '-' to decrease confidence threshold")
        print("\nLogic:")
        print("  1. Track 1 object TERBESAR (paling dekat)")
        print("  2. Beri ID unik (PERSON_1, PERSON_2, dst)")
        print("  3. SIAGA aktif setelah 3 frame MENDEKAT")
        print("  4. SIAGA hold 3 detik setelah object hilang")
        print("  5. SIAGA CLEARED → Boleh track object baru")
        print("  6. SIAGA hilang otomatis jika object MENJAUH")
        print("\nControls:")
        print("  - Press 'q' to quit")
        print("  - Press 'r' to RESET tracking dan SIAGA")
        print("  - Press 's' to save snapshot")
        print("  - Press '+' to increase confidence threshold")
        print("  - Press '-' to decrease confidence threshold")
        print("="*70 + "\n")

        try:
            while True:
                ret, frame = self.cap.read()

                if not ret:
                    print("[ERROR] Failed to grab frame")
                    break

                # Detect objects
                detections = self.detect_objects(frame)

                # Update tracker (pilih 1 object terbesar)
                result = self.tracker.update(detections)

                # Check SIAGA expire
                self.tracker.check_siaga_expire(time.time())

                # Draw detections
                self.draw_detections(frame, result)

                # Draw info panel (pass result sebagai parameter)
                self.draw_info_panel(frame, result)

                # Show frame
                cv2.imshow('Object Distance Detection - Single Object Tracking', frame)

                # Handle keyboard
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # RESET tracking dan SIAGA
                    self.tracker.reset_tracking()
                elif key == ord('s'):
                    filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"\n[OK] Snapshot saved: {filename}")
                elif key == ord('+') or key == ord('='):
                    self.confidence_threshold = min(0.9, self.confidence_threshold + 0.05)
                    print(f"\nConfidence threshold: {self.confidence_threshold:.2f}")
                elif key == ord('-'):
                    self.confidence_threshold = max(0.1, self.confidence_threshold - 0.05)
                    print(f"\nConfidence threshold: {self.confidence_threshold:.2f}")
        
        finally:
            self.stop()
            print("\n[OK] Application closed")


def main():
    """Main function."""
    print("="*70)
    print("Object Distance Detection with YOLO - Single Object Tracking")
    print("="*70)
    
    detector = RealTimeDistanceDetector(
        camera_id=0,
        confidence_threshold=0.5
    )
    
    detector.run()


if __name__ == "__main__":
    main()
