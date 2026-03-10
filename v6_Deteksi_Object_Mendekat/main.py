"""
Real-time Object Distance Detection with YOLO - Parking System 4-Phase Capture
Deteksi object mendekat/menjauh dari kamera secara real-time dengan sistem parkir

LOGIKA BARU:
- Fokus track 1 object terbesar (paling dekat)
- Beri ID unik (PERSON_1, PERSON_2, dst)
- SIAGA harus hilang dulu sebelum track object baru
- Tampilkan ID di label
- 4 FASE CAPTURE: SIAGA → TETAP → LOOP DETECTOR → TAP CARD
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime
from enum import Enum
import os


class ParkingPhase(Enum):
    """Enum untuk fase-fase dalam parking session."""
    NO_VEHICLE = 0       # Tidak ada kendaraan
    FASE1_SIAGA = 1      # SIAGA aktif, capture 3 frame
    FASE2_TETAP = 2      # Kendaraan berhenti, capture 5 frame
    FASE3_LOOP = 3       # Menunggu tombol loop detector
    FASE4_TAP = 4        # Menunggu tombol tap card
    PREVIEW_READY = 5    # Semua fase selesai, tampilkan preview


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

        # Target counts
        self.fase1_target = 3
        self.fase2_target = 5
        self.fase3_target = 3
        self.fase4_target = 3

        # Frame buffers
        self.fase1_frames = []
        self.fase2_frames = []
        self.fase3_frames = []
        self.fase4_frames = []

        # Session state
        self.is_active = False
        self.last_vehicle_id = None  # ID kendaraan terakhir (disimpan setelah selesai)

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

        # Save fase 1
        for i, frame in enumerate(self.fase1_frames):
            filepath = os.path.join(base_path, "fase1", f"frame_{i+1:03d}.jpg")
            cv2.imwrite(filepath, frame)
            saved_files.append(filepath)

        # Save fase 2
        for i, frame in enumerate(self.fase2_frames):
            filepath = os.path.join(base_path, "fase2", f"frame_{i+1:03d}.jpg")
            cv2.imwrite(filepath, frame)
            saved_files.append(filepath)

        # Save fase 3
        for i, frame in enumerate(self.fase3_frames):
            filepath = os.path.join(base_path, "fase3", f"frame_{i+1:03d}.jpg")
            cv2.imwrite(filepath, frame)
            saved_files.append(filepath)

        # Save fase 4
        for i, frame in enumerate(self.fase4_frames):
            filepath = os.path.join(base_path, "fase4", f"frame_{i+1:03d}.jpg")
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

        import json
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
        self.fase1_frames = []
        self.fase2_frames = []
        self.fase3_frames = []
        self.fase4_frames = []
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

        # Check apakah perlu advance phase
        self.session.advance_phase()

        return True


class ObjectDistanceTracker:
    """Tracker untuk mendeteksi apakah object mendekat atau menjauh.
    
    LOGIKA BARU:
    - Hanya track 1 object terbesar (paling dekat)
    - Beri ID unik yang konsisten
    - SIAGA harus hilang dulu sebelum track object baru
    - Support parking session dengan 4 fase capture
    """

    def __init__(self, max_history=30, siaga_frame_threshold=3, siaga_hold_time=3.0, target_classes=None):
        self.max_history = max_history
        self.siaga_frame_threshold = siaga_frame_threshold
        self.siaga_hold_time = siaga_hold_time
        self.target_classes = target_classes if target_classes else [0]  # Default person only

        # Object tracking dengan ID unik
        self.tracked_object_id = None
        self.tracked_object_history = []
        self.tracked_object_bbox = None
        self.tracked_object_area = 0  # Area object yang di-track
        self.tracked_object_class = None  # Class name object yang di-track

        # Camera view info untuk focus percentage
        self.camera_view_area = 0  # Total area camera view

        # SIAGA tracking
        self.siaga_active = False
        self.approaching_consecutive_count = 0
        self.siaga_trigger_time = None
        self.siaga_expire_time = None
        self.siaga_clear_time = None

        # MOVING AWAY DETECTION - untuk handle SIAGA hilang karena menjauh
        self.moving_away_detected = {}  # Track moving_away per detik: {second_count: has_detection}
        self.moving_away_start_time = None  # Waktu mulai hitung 5 detik
        self.moving_away_seconds_count = 0  # Jumlah detik yang valid (max 5)
        self.last_moving_away_second = -1  # Detik terakhir terdeteksi moving_away

        # SIAGA PERSISTENCE - untuk handle object sangat dekat
        self.last_siaga_area = 0  # Area terakhir saat SIAGA aktif
        self.siaga_persistence_active = False  # Mode persistence
        self.siaga_persistence_start_time = None  # Waktu mulai persistence
        self.siaga_persistence_delay = 0.02  # 20ms delay sebelum clear SIAGA

        # PERSISTENCE TIME - untuk handle object masih terdeteksi setelah SIAGA hilang
        self.siaga_cleared_time = None  # Waktu SIAGA cleared
        self.persistence_time_duration = 1.5  # 1.5 detik persistence time
        self.persistence_time_active = False  # Mode persistence time
        self.persistence_time_object_bbox = None  # Last bbox object saat persistence time

        # Object counter untuk ID
        self.object_counter = 0

        # PARKING SESSION - untuk tracking session terakhir
        self.last_session_vehicle_id = None  # ID kendaraan dari session terakhir
        
    def update(self, detections):
        """Update tracker dengan deteksi baru."""
        current_time = time.time()

        # Filter hanya target classes yang dipilih
        target_detections = [d for d in detections if d['class_id'] in self.target_classes]

        # Jika tidak ada object target, handle SIAGA timer
        if not target_detections:
            self._handle_no_detection(current_time)
            return {'tracked_object': None, 'status': 'no_detection'}

        # Pilih object TERBESAR (area terbesar = paling dekat)
        largest_detection = max(
            target_detections,
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
        elif self.persistence_time_active:
            # PERSISTENCE TIME (1.5 detik): Object masih terdeteksi, PERTAHANKAN ID!
            # Jangan ganti object walaupun SIAGA sudah cleared
            # Ini handle kasus object diam → bergerak
            pass  # Tetap track object yang sama
        else:
            # SIAGA cleared dan persistence time habis, boleh pilih object baru
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
        
        # Update tracked object info
        self.tracked_object_bbox = largest_detection['bbox']
        self.tracked_object_area = current_area  # Simpan area untuk persistence check
        self.tracked_object_class = largest_detection.get('class_name', 'UNKNOWN')  # Simpan class name
        
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
        - SIAGA HILANG jika object MENJAUH selama 5 detik berturut-turut
          (setiap detik HARUS ada minimal 1 frame MENJAUH)
        - SIAGA hold 3 detik jika object hilang
        - SIAGA PERSISTENCE: Jika object ≥80% camera view, tunggu 20ms sebelum clear
        """
        # Update last_siaga_area jika SIAGA aktif
        if self.siaga_active and self.tracked_object_area > 0:
            self.last_siaga_area = self.tracked_object_area
        
        # Hitung detik saat ini untuk moving_away tracking
        if self.moving_away_start_time is None:
            self.moving_away_start_time = current_time
        
        elapsed_time = current_time - self.moving_away_start_time
        current_second = int(elapsed_time)  # Detik ke-0, 1, 2, 3, 4, 5
        
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
                
                # Reset moving_away counter
                self.moving_away_detected = {}
                self.moving_away_seconds_count = 0
                self.moving_away_start_time = None
                self.last_moving_away_second = -1
                
        elif status == 'moving_away':
            # Object MENJAUH → Track per detik untuk 5 detik requirement
            if self.moving_away_start_time is None:
                self.moving_away_start_time = current_time
                current_second = 0
            
            # Mark detik ini sebagai terdeteksi moving_away
            if current_second not in self.moving_away_detected:
                self.moving_away_detected[current_second] = True
                print(f"\n[📉 MOVING AWAY] Detik ke-{current_second}/5 - terdeteksi!")
            
            # Check apakah detik ini berbeda dari last second (artinya masuk detik baru)
            if current_second > self.last_moving_away_second:
                self.last_moving_away_second = current_second
                
                # Check apakah detik sebelumnya sudah terpenuhi
                if current_second >= 1:
                    prev_second = current_second - 1
                    if prev_second in self.moving_away_detected:
                        # Detik sebelumnya valid!
                        self.moving_away_seconds_count = current_second
                        print(f"\n[⏱️ MOVING AWAY] {self.moving_away_seconds_count}/5 detik valid")
                    else:
                        # Detik sebelumnya TIDAK valid → RESET!
                        print(f"\n[⚠️ MOVING AWAY] Detik ke-{prev_second} tidak valid - RESET!")
                        self.moving_away_detected = {current_second: True}
                        self.moving_away_seconds_count = 0
                        self.moving_away_start_time = current_time
            
            # Check apakah sudah 5 detik valid
            if self.moving_away_seconds_count >= 5:
                # 5 detik terpenuhi! Clear SIAGA
                if self.siaga_active:
                    self.siaga_active = False
                    self.approaching_consecutive_count = 0
                    self.siaga_expire_time = None
                    self.last_siaga_area = 0
                    self.siaga_persistence_active = False
                    self.siaga_persistence_start_time = None
                    
                    # START PERSISTENCE TIME!
                    self.siaga_cleared_time = current_time
                    self.persistence_time_active = True
                    self.persistence_time_object_bbox = self.tracked_object_bbox
                    
                    print(f"\n[✓ SIAGA CLEARED] 5 detik moving_away terpenuhi!")
                    
                    # Reset moving_away counter
                    self.moving_away_detected = {}
                    self.moving_away_seconds_count = 0
                    self.moving_away_start_time = None
                    self.last_moving_away_second = -1
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
    
    def reset_tracking(self, save_last_id=False):
        """Reset semua tracking dan SIAGA (untuk tombol reset).
        
        Args:
            save_last_id: Jika True, simpan tracked_object_id sebagai last_session_vehicle_id
        """
        was_siaga = self.siaga_active
        
        # Simpan last vehicle ID jika diminta
        if save_last_id and self.tracked_object_id:
            self.last_session_vehicle_id = self.tracked_object_id
            print(f"\n[💾 SAVED] Last vehicle ID: {self.last_session_vehicle_id}")
        
        self.siaga_active = False
        self.approaching_consecutive_count = 0
        self.tracked_object_id = None
        self.tracked_object_bbox = None
        self.tracked_object_area = 0
        self.tracked_object_history = []
        self.tracked_object_class = None
        self.siaga_expire_time = None
        self.siaga_clear_time = time.time()
        self.last_siaga_area = 0
        self.siaga_persistence_active = False
        self.persistence_time_active = False

        if was_siaga:
            print(f"\n[🔄 RESET] Tracking dan SIAGA direset manual!")
        else:
            print(f"\n[🔄 RESET] Tracking direset!")
    
    def check_siaga_expire(self, current_time):
        """Check apakah SIAGA sudah expire dan handle persistence time."""
        # Check persistence time (1.5 detik)
        if self.persistence_time_active and self.siaga_cleared_time is not None:
            persistence_elapsed = current_time - self.siaga_cleared_time
            
            if persistence_elapsed >= self.persistence_time_duration:
                # Persistence time 1.5 detik HABIS!
                self.persistence_time_active = False
                self.siaga_cleared_time = None
                self.persistence_time_object_bbox = None
                print(f"\n[✓ PERSISTENCE TIME DONE] 1.5s elapsed - ID lock released!")
            # else: Masih dalam persistence time, ID masih dipertahankan
        
        # Check SIAGA expire (object hilang)
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

        # Target classes untuk tracking:
        # 0=person, 67=cell phone, 1=bicycle, 2=car, 3=motorcycle, 5=bus, 7=truck
        self.target_classes = [0, 67, 1, 2, 3, 5, 7]
        # self.target_classes = [67]

        # Initialize tracker dengan target classes
        self.tracker = ObjectDistanceTracker(
            max_history=30,
            siaga_frame_threshold=3,
            siaga_hold_time=3.0,
            target_classes=self.target_classes
        )

        # Class names dari YOLO
        self.class_names = self.model.names

        # Parking Session & Capture Manager
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
        self.cap = cv2.VideoCapture(self.camera_id)

        if not self.cap.isOpened():
            print(f"[ERROR] Cannot open camera {self.camera_id}")
            return False

        # Set camera resolution (tetap 640x480)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Set camera view area untuk focus percentage calculation
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.tracker.camera_view_area = frame_width * frame_height

        print(f"[OK] Camera opened: {self.camera_id}")
        print(f"[INFO] Camera view area: {frame_width}x{frame_height} = {self.tracker.camera_view_area}px")
        
        # Create window dengan ukuran sama dengan frame camera (640x480)
        cv2.namedWindow('Object Distance Detection - Parking System', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Object Distance Detection - Parking System', frame_width, frame_height)
        
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

    def handle_parking_session(self, result, frame):
        """Handle parking session state machine."""
        tracked_object = result.get('tracked_object') if result else None
        status = result.get('status', 'stable') if result else 'no_detection'
        current_time = time.time()

        # Check jika preview sudah ready
        if self.parking_session.phase == ParkingPhase.PREVIEW_READY:
            self.show_preview = True
            self.preview_frames = {
                'fase1': self.parking_session.fase1_frames,
                'fase2': self.parking_session.fase2_frames,
                'fase3': self.parking_session.fase3_frames,
                'fase4': self.parking_session.fase4_frames,
            }
            return

        # Check jika tidak ada tracked object
        if not tracked_object:
            if self.parking_session.is_active:
                # Kendaraan pergi sebelum sesi selesai → CANCEL
                self.parking_session.cancel_session()
            return

        # Check SIAGA aktif → Start FASE1
        if self.tracker.siaga_active and not self.parking_session.is_active:
            self.parking_session.start_session(
                self.tracker.tracked_object_id,
                self.tracker.tracked_object_class
            )

        # Jika session aktif, handle capture
        if self.parking_session.is_active:
            phase = self.parking_session.phase

            # FASE1: SIAGA aktif (approaching)
            if phase == ParkingPhase.FASE1_SIAGA:
                if status == 'approaching' and self.capture_manager.can_capture(phase):
                    self.capture_manager.capture(frame, phase)
                    print(f"\n[📸 FASE 1] Capture {self.parking_session.fase1_count}/{self.parking_session.fase1_target}")

            # FASE2: Status TETAP (stable)
            elif phase == ParkingPhase.FASE2_TETAP:
                if status == 'stable' and self.capture_manager.can_capture(phase):
                    self.capture_manager.capture(frame, phase)
                    print(f"\n[📸 FASE 2] Capture {self.parking_session.fase2_count}/{self.parking_session.fase2_target}")

            # FASE3 & FASE4: Menunggu tombol manual
            elif phase == ParkingPhase.FASE3_LOOP or phase == ParkingPhase.FASE4_TAP:
                pass  # Menunggu tombol ditekan
        
        # Auto-advance phase jika capture sudah selesai
        if self.parking_session.is_active:
            self.parking_session.advance_phase()

    def trigger_loop_detector(self, current_frame):
        """Trigger capture untuk FASE3 (Loop Detector)."""
        if self.parking_session.phase == ParkingPhase.FASE3_LOOP:
            print(f"\n[🔘 LOOP DETECTOR] Triggered!")
            # Capture 3 frame dari current frame (dengan sedikit variasi)
            for i in range(self.parking_session.fase3_target):
                self.parking_session.add_frame(current_frame, ParkingPhase.FASE3_LOOP)
                time.sleep(0.05)  # Small delay untuk variasi
            self.parking_session.advance_phase()

    def trigger_tap_card(self, current_frame):
        """Trigger capture untuk FASE4 (Tap Card)."""
        if self.parking_session.phase == ParkingPhase.FASE4_TAP:
            print(f"\n[🔘 TAP CARD] Triggered!")
            # Capture 3 frame dari current frame
            for i in range(self.parking_session.fase4_target):
                self.parking_session.add_frame(current_frame, ParkingPhase.FASE4_TAP)
                time.sleep(0.05)  # Small delay untuk variasi
            self.parking_session.advance_phase()

    def complete_parking_session(self):
        """Complete parking session dan reset."""
        self.parking_session.complete_session()
        
        # Reset tracking dengan save last vehicle ID
        self.tracker.reset_tracking(save_last_id=True)
        
        # Reset UI
        self.show_preview = False
        self.preview_frames = None

    def show_help_popup(self):
        """Tampilkan popup bantuan."""
        help_title = "BANTUAN - Parking System Capture"
        
        # Create canvas untuk help popup
        canvas_height = 500
        canvas_width = 600
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
        canvas[:] = (40, 40, 40)  # Dark gray background
        
        # Help content (line by line)
        help_lines = [
            ("CARA MENGGUNAKAN:", 0.5, (0, 255, 255), 25),
            ("", 0, (0, 0, 0), 0),
            ("1. Tunggu kendaraan terdeteksi kamera", 0.4, (255, 255, 255), 50),
            ("2. SIAGA aktif otomatis saat kendaraan mendekat", 0.4, (255, 255, 255), 70),
            ("3. FASE 1: Capture 3 frame otomatis (MENDEKAT)", 0.4, (255, 255, 255), 90),
            ("4. FASE 2: Capture 5 frame otomatis (BERHENTI)", 0.4, (255, 255, 255), 110),
            ("5. FASE 3: Tekan 'L' untuk LOOP DETECTOR (3 frame)", 0.4, (255, 255, 255), 130),
            ("6. FASE 4: Tekan 'T' untuk TAP CARD (3 frame)", 0.4, (255, 255, 255), 150),
            ("7. Preview muncul otomatis setelah FASE 4", 0.4, (255, 255, 255), 170),
            ("8. Tekan ENTER untuk SELESAI", 0.4, (0, 255, 0), 190),
            ("", 0, (0, 0, 0), 0),
            ("KEYBOARD SHORTCUTS:", 0.5, (0, 255, 255), 220),
            ("", 0, (0, 0, 0), 0),
            ("L - Trigger LOOP DETECTOR (FASE 3 - 3 frame)", 0.4, (255, 255, 255), 250),
            ("T - Trigger TAP CARD (FASE 4 - 3 frame)", 0.4, (255, 255, 255), 270),
            ("ENTER - SELESAI (saat preview)", 0.4, (255, 255, 255), 290),
            ("H - Tampilkan bantuan ini", 0.4, (255, 255, 255), 310),
            ("Q - Quit aplikasi", 0.4, (255, 255, 255), 330),
            ("S - Save snapshot", 0.4, (255, 255, 255), 350),
            ("+/- - Adjust confidence threshold", 0.4, (255, 255, 255), 370),
        ]
        
        y_offset = 0
        for text, font_size, color, y in help_lines:
            if y > 0:
                cv2.putText(canvas, text, (20, y),
                           cv2.FONT_HERSHEY_SIMPLEX, font_size, color, 1)
        
        # Draw border
        cv2.rectangle(canvas, (0, 0), (canvas_width, canvas_height), (255, 255, 255), 2)
        
        # Title (small, inside border)
        cv2.putText(canvas, help_title, (20, canvas_height - 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Show help window
        cv2.imshow(help_title, canvas)
        
        # Wait for user to close
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 13 or key == ord('h'):  # Enter or H
                break
            
            # Check mouse click or window closed
            if cv2.getWindowProperty(help_title, cv2.WND_PROP_VISIBLE) < 1:
                break
        
        # Close window (ignore error if already closed)
        try:
            cv2.destroyWindow(help_title)
        except:
            pass
        
        return True

    def show_capture_preview(self):
        """Tampilkan window preview untuk semua capture."""
        if not self.preview_frames:
            return

        # Create preview window
        preview_title = f"📸 Capture Preview - {self.parking_session.session_id}"
        
        # Calculate grid layout
        fase_names = ["FASE 1: SIAGA", "FASE 2: TETAP", "FASE 3: LOOP", "FASE 4: TAP"]
        fase_data = [
            self.preview_frames['fase1'],
            self.preview_frames['fase2'],
            self.preview_frames['fase3'],
            self.preview_frames['fase4'],
        ]
        fase_counts = [3, 5, 3, 3]

        # Create a large canvas for preview
        canvas_height = 800
        canvas_width = 1200
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
        canvas[:] = (40, 40, 40)  # Dark gray background

        # Title
        cv2.putText(canvas, preview_title, (20, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        y_offset = 60
        thumb_width = 100
        thumb_height = 75
        spacing = 15

        for fase_idx, (fase_name, frames, target_count) in enumerate(zip(fase_names, fase_data, fase_counts)):
            # Fase title
            cv2.putText(canvas, fase_name, (20, y_offset + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

            # Draw thumbnails
            x_offset = 20
            y_offset += 30

            for i in range(target_count):
                if i < len(frames):
                    # Resize frame to thumbnail
                    thumb = cv2.resize(frames[i], (thumb_width, thumb_height))
                    
                    # Draw thumbnail border
                    border_color = (0, 255, 0) if i < len(frames) else (100, 100, 100)
                    cv2.rectangle(canvas, 
                                 (x_offset, y_offset), 
                                 (x_offset + thumb_width, y_offset + thumb_height),
                                 border_color, 2)
                    
                    # Place thumbnail
                    canvas[y_offset:y_offset + thumb_height, 
                           x_offset:x_offset + thumb_width] = thumb
                else:
                    # Empty placeholder
                    cv2.rectangle(canvas,
                                 (x_offset, y_offset),
                                 (x_offset + thumb_width, y_offset + thumb_height),
                                 (80, 80, 80), -1)
                    cv2.rectangle(canvas,
                                 (x_offset, y_offset),
                                 (x_offset + thumb_width, y_offset + thumb_height),
                                 (100, 100, 100), 1)

                x_offset += thumb_width + spacing

            y_offset += thumb_height + 30

        # Draw SELESAI button
        button_w, button_h = 200, 50
        button_x = (canvas_width - button_w) // 2
        button_y = canvas_height - button_h - 30
        
        cv2.rectangle(canvas, (button_x, button_y), 
                     (button_x + button_w, button_y + button_h),
                     (0, 255, 0), -1)
        cv2.rectangle(canvas, (button_x, button_y),
                     (button_x + button_w, button_y + button_h),
                     (255, 255, 255), 2)
        cv2.putText(canvas, "SELESAI", (button_x + 45, button_y + 32),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        # Show canvas
        cv2.imshow(preview_title, canvas)

        # Handle button click (simple: check if user presses Enter or clicks)
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter key
            self.complete_parking_session()
            return True

        return False
    
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
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

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
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1
        )
        cv2.rectangle(
            frame,
            (x1, y1 - label_h - baseline - 3),
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
            0.35,
            (255, 255, 255),
            1
        )

        # SIAGA indicator (jika aktif)
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

            # Blinking border
            if int(time.time() * 3) % 2 == 0:
                cv2.rectangle(
                    frame,
                    (x1, siaga_y),
                    (x1 + siaga_w + 6, siaga_y + siaga_h + 3),
                    (0, 0, 255),
                    1
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

        # Panel height (tanpa SIAGA di dalam box)
        panel_height = 65
        panel_width = 220  # Same as focus box width
        cv2.rectangle(frame, (0, 0), (panel_width, panel_height), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, 0), (panel_width, panel_height), (255, 255, 255), 1)

        # FPS
        cv2.putText(
            frame,
            f"FPS: {self.fps:.1f}",
            (10, 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 255, 0),
            1
        )

        # Status - di bawah FPS (di dalam box hitam)
        tracked_id = self.tracker.get_tracked_object_id()
        if tracked_id:
            status = result.get('status', 'N/A') if result else 'N/A'
            persistence_status = " [PERSISTENCE]" if self.tracker.siaga_persistence_active else ""

            # Tambahkan persistence time status
            persistence_time_status = ""
            if self.tracker.persistence_time_active:
                persistence_elapsed = time.time() - (self.tracker.siaga_cleared_time or time.time())
                persistence_remaining = self.tracker.persistence_time_duration - persistence_elapsed
                if persistence_remaining > 0:
                    persistence_time_status = f" [PERSISTENCE: {persistence_remaining:.1f}s]"

            debug_status = f"Status: {status}{persistence_status}{persistence_time_status}"
            cv2.putText(
                frame,
                debug_status,
                (10, 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.3,
                (200, 200, 200),
                1
            )

        # SIAGA ALERT - Di atas tengah (di luar box hitam)
        if is_siaga:
            blink_color = (0, 0, 255) if int(time.time() * 4) % 2 == 0 else (0, 140, 255)
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Get frame width for centering
            frame_height, frame_width = frame.shape[:2]
            siaga_text = "SIAGA: Object MENDEKAT!"
            (siaga_w, siaga_h), _ = cv2.getTextSize(siaga_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            siaga_x = (frame_width - siaga_w) // 2

            # Background box (blinking)
            cv2.rectangle(frame, (siaga_x - 10, 10), (siaga_x + siaga_w + 10, 45), blink_color, -1)
            cv2.rectangle(frame, (siaga_x - 10, 10), (siaga_x + siaga_w + 10, 45), (255, 255, 255), 2)

            cv2.putText(
                frame,
                siaga_text,
                (siaga_x, 33),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

            print(f"\r[⚠️ SIAGA ACTIVE] Object approaching - {timestamp}", end='')

        # SIAGA CLEARED feedback - Di atas tengah (di luar box hitam)
        elif siaga_cleared:
            if current_time - self.tracker.siaga_clear_time <= 2.0:
                timestamp = datetime.now().strftime("%H:%M:%S")

                # Get frame width for centering
                frame_height, frame_width = frame.shape[:2]
                siaga_text = "✓ SIAGA CLEARED - Siap track object baru"
                (siaga_w, siaga_h), _ = cv2.getTextSize(siaga_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                siaga_x = (frame_width - siaga_w) // 2

                # Background box (green)
                cv2.rectangle(frame, (siaga_x - 10, 10), (siaga_x + siaga_w + 10, 45), (0, 255, 0), -1)
                cv2.rectangle(frame, (siaga_x - 10, 10), (siaga_x + siaga_w + 10, 45), (255, 255, 255), 2)

                cv2.putText(
                    frame,
                    siaga_text,
                    (siaga_x, 33),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2
                )

                print(f"\r[✓ SIAGA CLEARED] Siap track object baru - {timestamp}", end='')
            else:
                self.tracker.siaga_clear_time = None

        # Define legend_y for positioning (removed Legend text)
        legend_y = 75 if not (is_siaga or siaga_cleared) else 75

        # FASE & PROGRESS BAR - Di atas Legend (Pojok Kiri Bawah, Horizontal)
        # Define variables first for focus box positioning
        fase_margin = 10
        fase_box_width = 220
        fase_box_height = 35
        legend_box_height = 32
        
        if self.parking_session.is_active:
            frame_height, frame_width = frame.shape[:2]
            fase_y_bottom = frame_height - fase_margin - legend_box_height - 5 - fase_box_height

            # Background box untuk fase
            cv2.rectangle(frame, (fase_margin, fase_y_bottom),
                         (fase_margin + fase_box_width, fase_y_bottom + fase_box_height),
                         (30, 30, 30), -1)
            cv2.rectangle(frame, (fase_margin, fase_y_bottom),
                         (fase_margin + fase_box_width, fase_y_bottom + fase_box_height),
                         (0, 255, 255), 1)

            # Phase name (kiri)
            phase_names = {
                ParkingPhase.FASE1_SIAGA: "FASE 1",
                ParkingPhase.FASE2_TETAP: "FASE 2",
                ParkingPhase.FASE3_LOOP: "FASE 3",
                ParkingPhase.FASE4_TAP: "FASE 4",
            }
            phase_name = phase_names.get(self.parking_session.phase, "FASE ?")
            cv2.putText(frame, phase_name, (fase_margin + 8, fase_y_bottom + 22),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

            # Progress bar (kanan - horizontal)
            progress = self.parking_session.get_progress()
            total_frames = 14  # 3+5+3+3
            progress_width = 100
            progress_x = fase_margin + 75
            progress_y = fase_y_bottom + 18

            # Progress background
            cv2.rectangle(frame, (progress_x, progress_y - 5),
                         (progress_x + progress_width, progress_y + 5),
                         (60, 60, 60), -1)

            # Progress filled
            filled_width = int(progress_width * (int(progress.split('/')[0]) / total_frames))
            cv2.rectangle(frame, (progress_x, progress_y - 5),
                         (progress_x + filled_width, progress_y + 5),
                         (0, 255, 0), -1)

            # Progress text (di sebelah kanan progress bar)
            cv2.putText(frame, progress, (progress_x + progress_width + 5, progress_y + 4),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

        # FOCUS PERCENTAGE DISPLAY - Di atas kotak Fase (Pojok Kiri Bawah)
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

                # Position: di atas fase box
                focus_margin = 10
                focus_box_height = 35
                frame_height, frame_width = frame.shape[:2]
                legend_box_height = 32
                fase_box_height = 35
                focus_y_bottom = frame_height - focus_margin - legend_box_height - 5 - fase_box_height - 5 - focus_box_height

                # Background box untuk focus
                cv2.rectangle(frame, (focus_margin, focus_y_bottom),
                             (focus_margin + fase_box_width, focus_y_bottom + focus_box_height),
                             (30, 30, 30), -1)
                cv2.rectangle(frame, (focus_margin, focus_y_bottom),
                             (focus_margin + fase_box_width, focus_y_bottom + focus_box_height),
                             focus_color, 1)

                # Focus lock text (kiri)
                cv2.putText(frame, f"Focus: {tracked_id}", (focus_margin + 8, focus_y_bottom + 22),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, focus_color, 1)

                # Focus percentage (kanan)
                focus_text = f"{focus_percentage:.1f}%"
                (focus_w, focus_h), _ = cv2.getTextSize(focus_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                cv2.putText(frame, focus_text, (focus_margin + fase_box_width - focus_w - 8, focus_y_bottom + 22),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, focus_color, 1)

        # LEGEND - Pojok Kiri Bawah (1 baris)
        legend_margin = 10
        legend_box_width = 220
        legend_box_height = 32
        frame_height, frame_width = frame.shape[:2]
        legend_y_bottom = frame_height - legend_margin - legend_box_height

        # Background box untuk legend
        cv2.rectangle(frame, (legend_margin, legend_y_bottom),
                     (legend_margin + legend_box_width, legend_y_bottom + legend_box_height),
                     (0, 0, 0), -1)
        cv2.rectangle(frame, (legend_margin, legend_y_bottom),
                     (legend_margin + legend_box_width, legend_y_bottom + legend_box_height),
                     (255, 255, 255), 1)

        # Merah - Mendekat
        cv2.circle(frame, (legend_margin + 12, legend_y_bottom + 16), 5, (0, 0, 255), -1)
        cv2.putText(frame, "Mendekat", (legend_margin + 22, legend_y_bottom + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 255, 255), 1)

        # Hijau - Tetap
        cv2.circle(frame, (legend_margin + 80, legend_y_bottom + 16), 5, (0, 255, 0), -1)
        cv2.putText(frame, "Tetap", (legend_margin + 90, legend_y_bottom + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 255, 255), 1)

        # Biru - Menjauh
        cv2.circle(frame, (legend_margin + 135, legend_y_bottom + 16), 5, (255, 0, 0), -1)
        cv2.putText(frame, "Menjauh", (legend_margin + 145, legend_y_bottom + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 255, 255), 1)

        # Time - Tengah Bawah (di atas legend)
        timestamp = datetime.now().strftime("%H:%M:%S")
        time_text = f"{timestamp}"
        (time_w, time_h), _ = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        time_x = (frame_width - time_w) // 2  # Center horizontal
        time_y = legend_y_bottom - 10  # Just above legend box
        cv2.putText(
            frame,
            time_text,
            (time_x, time_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # BUTTONS - Pojok Kanan Bawah (Loop Detector & Tap Card)
        # Ukuran kecil
        button_margin = 8
        button_w, button_h = 90, 22
        button_spacing = 4

        # Get frame size
        frame_height, frame_width = frame.shape[:2]

        # Position: pojok kanan bawah
        button_y = frame_height - button_margin - button_h
        button1_x = frame_width - button_w - button_margin - button_w - button_spacing  # Loop Detector
        button2_x = frame_width - button_w - button_margin  # Tap Card

        # Loop Detector Button
        loop_active = self.parking_session.is_button_active("loop_detector")
        loop_color = (0, 255, 0) if loop_active else (50, 50, 50)
        loop_text_color = (255, 255, 255) if loop_active else (120, 120, 120)

        cv2.rectangle(frame, (button1_x, button_y),
                     (button1_x + button_w, button_y + button_h),
                     loop_color, -1)
        cv2.rectangle(frame, (button1_x, button_y),
                     (button1_x + button_w, button_y + button_h),
                     (255, 255, 255), 1 if loop_active else 0)
        cv2.putText(frame, "L - LOOP",
                   (button1_x + 6, button_y + 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, loop_text_color, 1)

        # Tap Card Button
        tap_active = self.parking_session.is_button_active("tap_card")
        tap_color = (0, 255, 0) if tap_active else (50, 50, 50)
        tap_text_color = (255, 255, 255) if tap_active else (120, 120, 120)

        cv2.rectangle(frame, (button2_x, button_y),
                     (button2_x + button_w, button_y + button_h),
                     tap_color, -1)
        cv2.rectangle(frame, (button2_x, button_y),
                     (button2_x + button_w, button_y + button_h),
                     (255, 255, 255), 1 if tap_active else 0)
        cv2.putText(frame, "T - TAP",
                   (button2_x + 8, button_y + 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, tap_text_color, 1)
    
    def run(self):
        """Run real-time detection."""
        if not self.start():
            return

        print("\n" + "="*70)
        print("Real-time Object Distance Detection - Multi-Class Tracking")
        print("="*70)
        print("\nTarget Classes:")
        print("  - 0: person (orang)")
        print("  - 1: bicycle (sepeda)")
        print("  - 2: car (mobil)")
        print("  - 3: motorcycle (motor)")
        print("  - 5: bus (bus)")
        print("  - 7: truck (truk)")
        print("  - 67: cell phone (ponsel)")
        print("\nLogic:")
        print("  1. Track 1 object TERBESAR (paling dekat) dari semua classes")
        print("  2. Beri ID unik (PERSON_1, CAR_2, MOTORCYCLE_3, dst)")
        print("  3. SIAGA aktif setelah 3 frame MENDEKAT")
        print("  4. SIAGA hold 3 detik setelah object hilang")
        print("  5. SIAGA CLEARED → Boleh track object baru")
        print("  6. SIAGA hilang otomatis jika object MENJAUH")
        print("\nParking System:")
        print("  - FASE 1: Capture 3 frame saat SIAGA aktif (MENDEKAT)")
        print("  - FASE 2: Capture 5 frame saat kendaraan BERHENTI (TETAP)")
        print("  - FASE 3: Capture 3 frame saat tombol LOOP DETECTOR ditekan")
        print("  - FASE 4: Capture 3 frame saat tombol TAP CARD ditekan")
        print("\nControls:")
        print("  - Press 'q' to quit")
        print("  - Press 'r' to RESET tracking dan SIAGA")
        print("  - Press 's' to save snapshot")
        print("  - Press 'l' to trigger LOOP DETECTOR (FASE 3)")
        print("  - Press 't' to trigger TAP CARD (FASE 4)")
        print("  - Press ENTER to SELESAI (saat preview)")
        print("  - Press 'h' to show HELP/BANTUAN")
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

                # Handle parking session
                self.handle_parking_session(result, frame)

                # Check if preview should be shown
                if self.show_preview and self.preview_frames:
                    if self.show_capture_preview():
                        continue  # Preview sudah ditutup
                else:
                    # Draw detections (hanya jika tidak show preview)
                    self.draw_detections(frame, result)

                    # Draw info panel (pass result sebagai parameter)
                    self.draw_info_panel(frame, result)

                    # Show frame (tanpa resize - tetap 640x480)
                    cv2.imshow('Object Distance Detection - Parking System', frame)

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
                elif key == ord('l'):
                    # Trigger LOOP DETECTOR
                    self.trigger_loop_detector(frame)
                elif key == ord('t'):
                    # Trigger TAP CARD
                    self.trigger_tap_card(frame)
                elif key == 13:  # Enter key
                    # SELESAI (hanya jika preview aktif)
                    if self.show_preview:
                        self.complete_parking_session()
                elif key == ord('h'):
                    # Show help popup
                    self.show_help_popup()
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
    print("Object Distance Detection with YOLO - Multi-Class Tracking")
    print("="*70)
    print("\nTarget Classes: person, cell phone, bicycle, car, motorcycle, bus, truck")
    print("="*70)

    detector = RealTimeDistanceDetector(
        camera_id=0,
        confidence_threshold=0.5
    )

    detector.run()


if __name__ == "__main__":
    main()
