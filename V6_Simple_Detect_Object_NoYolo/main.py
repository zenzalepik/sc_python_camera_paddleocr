"""
Simple Object Detection with ROI (Region of Interest)
Flow: OpenCV-based motion/contour detection without YOLO

Detection Mode:
- AUTO_RESET_ENABLED = True  → MOG2 Background Subtractor (adaptive, auto reset)
- AUTO_RESET_ENABLED = False → Background Reference (static, object diam tetap terdeteksi)
"""

import cv2
import numpy as np
import time
from variables import (
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
)


def main():
    # 1. INIT
    # Buka kamera
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    # Tentukan ukuran frame
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Definisikan ROI (Region of Interest)
    roi_width = int(width * ROI_WIDTH_FRACTION)
    roi_height = int(height * ROI_HEIGHT_FRACTION)
    roi_x = (width - roi_width) // 2
    roi_y = (height - roi_height) // 2

    # =========================================
    # INISIALISASI BACKGROUND REFERENCE
    # (Hanya jika INITIAL_AUTO_RESET_MODE = False)
    # =========================================
    background_reference = None
    prev_frame = None
    
    if not INITIAL_AUTO_RESET_MODE:
        # Mode static background reference - capture background awal
        print(f"\n=== CAPTURING BACKGROUND REFERENCE ===")
        print(f"Capturing {INIT_CAPTURE_COUNT} frames...")
        print(f"Please ensure NO objects in the scene!\n")
        
        init_frames = []
        for i in range(INIT_CAPTURE_COUNT):
            ret, frame = cap.read()
            if not ret:
                print("Error: Cannot read frame during initialization")
                return
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_blurred = cv2.GaussianBlur(gray, BLUR_KERNEL_SIZE, 0)
            init_frames.append(gray_blurred)
            
            cv2.putText(frame, f"Capturing frame {i+1}/{INIT_CAPTURE_COUNT}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow('ROI Object Detection', frame)
            cv2.waitKey(300)
        
        # Gunakan frame terakhir sebagai background reference
        background_reference = init_frames[-1].copy()
        print(f"Background reference captured!\n")
        print("=== MODE: STATIC BACKGROUND (Object diam tetap terdeteksi) ===\n")
    else:
        print("=== MODE: AUTO RESET (MOG2 Adaptive Background) ===\n")

    # =========================================
    # VARIABEL UNTUK MAIN LOOP
    # =========================================

    # Status indikator
    indicator_on = False

    # Untuk efek berkedip
    blink_state = False
    frame_count = 0
    
    # Variabel terpisah untuk kotak dan label
    roi_box_blink = False  # Kontrol kotak ROI berkedip
    label_object_in_roi = False  # Kontrol label "OBJECT IN ROI"

    # Background subtractor (hanya untuk mode AUTO_RESET = True)
    # learningRate=0.01 = MOG2 belajar lebih lambat (object diam tidak cepat hilang)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=50,
        detectShadows=False
    ) if INITIAL_AUTO_RESET_MODE else None
    
    # Preview MOG2 (terpisah dari main, untuk preview window)
    preview_mog2 = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=50,
        detectShadows=False
    ) if INITIAL_AUTO_RESET_MODE else None
    
    # Previous frame untuk preview (Static BG mode)
    prev_frame_preview = None
    
    # ROI-based tracking untuk auto reset
    # Object di ROI tidak akan di-reset meskipun MOG2 sudah "belajar"
    object_in_roi_frames = 0  # Counter berapa lama object ada di ROI
    roi_empty_frames = 0  # Counter berapa lama ROI kosong (untuk auto reset)
    last_roi_object_time = time.time()  # Waktu terakhir object terdeteksi di ROI
    last_log_second = 0  # Counter untuk log per detik
    
    # Persistent tracking untuk object di ROI
    # Track posisi object terakhir di ROI agar tidak hilang saat MOG2 "belajar"
    last_object_bbox_in_roi = None  # Bounding box terakhir object di ROI
    object_stationary_counter = 0  # Counter berapa lama object diam di ROI
    roi_occupied = False  # Status apakah ROI sedang ditempati object
    
    # Canny edge tracking untuk backup detection
    canny_roi_edge_counter = 0  # Counter berapa lama ada edge di ROI
    canny_min_edge_threshold = 50  # Minimum edge pixels untuk dianggap ada object
    canny_detecting = False  # Status apakah Canny sedang detect object
    
    # Object movement tracking
    object_moving = False  # Status apakah object sedang bergerak
    last_movement_time = time.time()  # Waktu terakhir object terdeteksi bergerak
    movement_log_counter = 0  # Counter untuk log movement

    # Preprocessing kernel untuk blur
    blur_kernel = (5, 5)

    # Tracking object presence
    object_detected_frames = 0
    object_lost_frames = 0
    object_present = False

    # Mask buffers (untuk preview)
    fg_mask_bg = None
    fg_mask_diff = None
    fg_mask = None

    # Preview window state
    show_preview = False

    # Auto reset state - ini yang di-toggle dengan tombol 'o'
    auto_reset_state = INITIAL_AUTO_RESET_MODE

    print("Press 'q' to quit")
    print("Press 'r' to manually reset background")
    print("Press 'o' to toggle auto reset (ON/OFF)")
    print("Press 'u' to toggle threshold & grayscale preview")
    print(f"Initial auto reset state: {'ON' if auto_reset_state else 'OFF'}")
    print(f"NO_MOTION_THRESHOLD: {NO_MOTION_THRESHOLD} frames (≈{NO_MOTION_THRESHOLD/30:.1f} detik @30FPS)")
    if not INITIAL_AUTO_RESET_MODE:
        print(f"Thresholds - BG: {BG_DIFF_THRESHOLD}, Frame: {FRAME_DIFF_THRESHOLD}")
    print(f"\n[INFO] Auto reset: ROI empty for {NO_MOTION_THRESHOLD} frames")
    print(f"[INFO] Object in ROI will NOT trigger auto reset\n")

    # Minimum dimensions for bounding box display
    MIN_BOX_WIDTH = 120
    MIN_BOX_HEIGHT = 120
    
    # Minimum contour area
    MIN_CONTOUR_AREA = 500

    # Debug: print threshold value
    print(f"\n[CONFIG] NO_MOTION_THRESHOLD = {NO_MOTION_THRESHOLD} frames")
    print(f"[CONFIG] MIN_CONTOUR_AREA = {MIN_CONTOUR_AREA} pixels\n")

    # 2. LOOP
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame")
            break

        frame_count += 1

        # Preprocessing: grayscale dan blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, blur_kernel, 0)
        
        # Canny edge detection untuk backup detection
        edges = cv2.Canny(blurred, 50, 150)
        edges_dilated = cv2.dilate(edges, None, iterations=2)
        
        # Cek edge di ROI area untuk backup detection
        roi_edges = edges_dilated[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
        roi_edge_pixels = cv2.countNonZero(roi_edges)

        # =========================================
        # DETEKSI OBJEK - Mode tergantung auto_reset_state
        # =========================================
        if auto_reset_state:
            # Mode MOG2 Background Subtractor (adaptive)
            # learningRate=0.005 = belajar lebih lambat (object diam tidak cepat dianggap background)
            fg_mask = bg_subtractor.apply(blurred, learningRate=0.005)
            # Morphological operations untuk membersihkan noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)
        else:
            # Mode Static Background Reference (object diam tetap terdeteksi)
            # 1. Background Reference Differencing (untuk object diam)
            bg_diff = cv2.absdiff(background_reference, blurred)
            _, fg_mask_bg = cv2.threshold(bg_diff, BG_DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)

            # 2. Frame Differencing (untuk object bergerak)
            if prev_frame is not None:
                frame_diff = cv2.absdiff(prev_frame, blurred)
                _, fg_mask_diff = cv2.threshold(frame_diff, FRAME_DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
            else:
                fg_mask_diff = np.zeros_like(fg_mask_bg)

            # Update previous frame
            prev_frame = blurred.copy()

            # 3. Combine masks (OR operation)
            fg_mask = cv2.bitwise_or(fg_mask_bg, fg_mask_diff)

            # 4. Morphological operations untuk membersihkan noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            fg_mask = cv2.dilate(fg_mask, kernel, iterations=3)
            fg_mask = cv2.erode(fg_mask, kernel, iterations=1)

        # Cari contour untuk mendapatkan bounding box objek
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # === DETEKSI OBJECT ===
        object_in_roi = False

        # Track object untuk auto reset
        has_detected_object = False  # Ada object terdeteksi (untuk auto reset)
        has_green_box = False  # Ada bounding box hijau yang ditampilkan (untuk visual)
        
        # Persistent tracking - track bbox terakhir di ROI
        current_object_bbox_in_roi = None

        for contour in contours:
            # Filter contour kecil
            if cv2.contourArea(contour) < MIN_CONTOUR_AREA:
                continue

            # Ambil bounding box
            x, y, w, h = cv2.boundingRect(contour)

            # Object terdeteksi (untuk auto reset logic)
            has_detected_object = True

            # Cek apakah bounding box bersinggungan dengan ROI
            if is_intersecting(x, y, w, h, roi_x, roi_y, roi_width, roi_height):
                object_in_roi = True
                current_object_bbox_in_roi = (x, y, w, h)

            # Filter visual: hanya tampilkan bounding box jika lebar DAN tinggi >= 120
            if w < MIN_BOX_WIDTH or h < MIN_BOX_HEIGHT:
                continue

            # Gambar bounding box objek (hijau) - hanya yang besar enough
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            has_green_box = True
        
        # === PERSISTENT ROI TRACKING dengan CANNY EDGE BACKUP ===
        # Logic sederhana:
        # 1. Jika MOG2 detect → object ada
        # 2. Jika MOG2 tidak detect tapi Canny detect edge → object masih ada (diam)
        # 3. Jalankan counter ke NO_MOTION_THRESHOLD
        # 4. Jika counter habis → reset
        
        has_canny_edge_in_roi = roi_edge_pixels >= canny_min_edge_threshold
        
        # Track movement status
        prev_object_moving = object_moving
        
        if current_object_bbox_in_roi is not None:
            # MOG2 detect object di ROI → object BERGERAK
            roi_occupied = True
            last_object_bbox_in_roi = current_object_bbox_in_roi
            canny_roi_edge_counter = 0
            canny_detecting = False
            object_moving = True
            movement_log_counter = 0
        elif has_canny_edge_in_roi and roi_occupied:
            # MOG2 tidak detect, tapi Canny detect edge → object DIAM
            canny_roi_edge_counter += 1
            canny_detecting = True
            object_moving = False
            movement_log_counter += 1
            
            # Jika Canny detect sampai NO_MOTION_THRESHOLD → jalankan AUTO RESET
            if canny_roi_edge_counter >= NO_MOTION_THRESHOLD:
                # Object diam terlalu lama → jalankan reset!
                print(f"\n{'='*60}")
                print(f"  🔄 [AUTO RESET] Object STATIONARY too long - frame {frame_count}")
                print(f"  ⏱️  [AUTO RESET] Stationary time: {NO_MOTION_THRESHOLD/30:.1f} detik")
                print(f"  📊 [AUTO RESET] Threshold: {NO_MOTION_THRESHOLD} frames")
                print(f"{'='*60}\n")
                
                # Reset MOG2 background subtractor
                if auto_reset_state:
                    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                        history=500,
                        varThreshold=50,
                        detectShadows=False
                    )
                    preview_mog2 = cv2.createBackgroundSubtractorMOG2(
                        history=500,
                        varThreshold=50,
                        detectShadows=False
                    )
                else:
                    # Mode Static: Update background reference
                    background_reference = blurred.copy()
                
                # Reset semua counter
                canny_roi_edge_counter = 0
                roi_occupied = False
                last_object_bbox_in_roi = None
                object_stationary_counter = 0
                movement_log_counter = 0
                
                # Reset indikator SETELAH reset (kotak berhenti berkedip SETELAH reset)
                indicator_on = False
                blink_state = False
                object_present = False
            else:
                # Canny counter belum mencapai threshold → ROI masih occupied, box tetap berkedip
                roi_occupied = True
                persistent_object_in_roi = True
        elif roi_occupied:
            # Tidak ada MOG2 dan tidak ada Canny edge → object pergi
            canny_roi_edge_counter = 0
            canny_detecting = False
            object_stationary_counter += 1
            object_moving = False
            
            # Grace period 60 frames (~2 detik)
            if object_stationary_counter > 60:
                roi_occupied = False
                last_object_bbox_in_roi = None
                persistent_object_in_roi = False  # Object benar-benar keluar
        
        # Log movement changes (hanya jika di ROI)
        if roi_occupied:
            if object_moving and not prev_object_moving:
                # Object mulai bergerak di ROI
                print(f"\n  🚀 [ROI] Object started MOVING")
                last_movement_time = time.time()
            elif not object_moving and prev_object_moving:
                # Object berhenti bergerak (mulai diam) di ROI
                print(f"\n  ⏸️ [ROI] Object stopped - now STATIONARY")
                last_movement_time = time.time()
            
            # Log periodic status (hanya jika di ROI)
            if object_moving and movement_log_counter % 100 == 0 and movement_log_counter > 0:
                print(f"  🟢 [ROI] Object MOVING - {movement_log_counter/30:.1f}s")
            elif not object_moving and canny_detecting and movement_log_counter % 100 == 0 and movement_log_counter > 0:
                print(f"  🟡 [ROI] Object STATIONARY (Canny) - {movement_log_counter/30:.1f}s")
        
        # Gunakan roi_occupied untuk auto reset logic
        persistent_object_in_roi = roi_occupied

        # === AUTO RESET LOGIC (ROI-BASED) ===
        # Logic baru: Auto reset HANYA jika ROI kosong selama NO_MOTION_THRESHOLD
        # Object di ROI TIDAK akan di-reset meskipun MOG2 sudah "belajar"
        
        if auto_reset_state:
            # Gunakan persistent_object_in_roi untuk auto reset logic
            if persistent_object_in_roi:
                # Ada object di ROI → Reset counter, JANGAN auto reset
                roi_empty_frames = 0
                object_in_roi_frames += 1
                
                # Debug: object masih di ROI
                if object_in_roi_frames % 100 == 0:
                    print(f"  🟢 [{object_in_roi_frames/30:.1f}s] Object still in ROI - no auto reset")
            else:
                # Tidak ada object di ROI → Increment counter untuk auto reset
                roi_empty_frames += 1
                object_in_roi_frames = 0
                
                # Hitung berapa detik ROI kosong
                roi_empty_seconds = int(roi_empty_frames / 30)
                
                # Log setiap 1 detik (30 frames)
                if roi_empty_seconds > last_log_second and roi_empty_seconds % 1 == 0:
                    remaining = NO_MOTION_THRESHOLD - roi_empty_frames
                    remaining_seconds = int(remaining / 30)
                    print(f"  ⏳ [{roi_empty_seconds}s] ROI empty: {roi_empty_frames}/{NO_MOTION_THRESHOLD} frames (remaining: ~{remaining_seconds}s)")
                    last_log_second = roi_empty_seconds
                
                # Cek apakah sudah mencapai threshold
                if roi_empty_frames >= NO_MOTION_THRESHOLD:
                    # AUTO RESET! ROI kosong selama threshold
                    if auto_reset_state:
                        # Mode MOG2: Reset background subtractor
                        bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                            history=500,
                            varThreshold=50,
                            detectShadows=False
                        )
                        preview_mog2 = cv2.createBackgroundSubtractorMOG2(
                            history=500,
                            varThreshold=50,
                            detectShadows=False
                        )
                    else:
                        # Mode Static: Update background reference
                        background_reference = blurred.copy()
                    
                    total_wait_seconds = roi_empty_frames / 30
                    roi_empty_frames = 0
                    indicator_on = False
                    blink_state = False
                    object_present = False
                    last_log_second = 0
                    
                    print(f"\n{'='*60}")
                    print(f"  🔄 [AUTO RESET] Background reset - frame {frame_count}")
                    print(f"  ⏱️  [AUTO RESET] ROI empty time: {total_wait_seconds:.1f} detik ({roi_empty_frames} frames)")
                    print(f"  📊 [AUTO RESET] Threshold: {NO_MOTION_THRESHOLD} frames")
                    print(f"{'='*60}\n")
        else:
            # Auto reset OFF → counter tidak jalan
            roi_empty_frames = 0
            last_log_second = 0

        # === STATE MANAGEMENT untuk ROI INDIKATOR ===
        # LOGIC DIPISAHKAN:
        # 1. Kotak ROI berkedip → Berdasarkan object di ROI (MOG2 atau Canny)
        # 2. Label "OBJECT IN ROI" → Sama dengan logic kotak biru
        
        # --- LOGIC 1: Kotak ROI Berkedip ---
        if persistent_object_in_roi and roi_occupied:
            # Ada object di ROI (MOG2 atau Canny) → kotak berkedip
            object_detected_frames += 1
            object_lost_frames = 0

            # Konfirmasi object ada setelah beberapa frame berturut-turut
            if object_detected_frames >= OBJECT_CONFIRM_THRESHOLD:
                object_present = True
                roi_box_blink = True  # Kotak berkedip
                
                # Efek berkedip: toggle ON/OFF setiap beberapa frame
                if frame_count % BLINK_INTERVAL == 0:
                    blink_state = not blink_state
        else:
            # Object TIDAK di ROI (keluar atau sudah reset) → kotak BERHENTI berkedip
            object_detected_frames = 0
            object_lost_frames = 0
            object_present = False
            roi_box_blink = False  # Kotak tidak berkedip
            blink_state = False
        
        # --- LOGIC 2: Label "OBJECT IN ROI" (SAMA dengan logic kotak biru) ---
        # Label muncul jika kotak biru berkedip (object di ROI)
        label_object_in_roi = roi_box_blink and object_present

        # 4. DISPLAY
        # Gambar ROI
        if roi_box_blink and blink_state:
            # Kotak biru berkedip (object di ROI)
            roi_color = (255, 0, 0)  # Blue (BGR)
            roi_thickness = 3
        else:
            # Kotak normal (abu-abu tipis)
            roi_color = (128, 128, 128)  # Gray
            roi_thickness = 2

        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height),
                     roi_color, roi_thickness)

        # Tampilkan status indikator
        if label_object_in_roi:
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
        reset_status = f"AUTO RESET: {'ON' if auto_reset_state else 'OFF'}"
        reset_color = (0, 255, 255) if auto_reset_state else (0, 128, 255)  # Yellow / Orange
        cv2.putText(frame, reset_status, (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, reset_color, 2)

        # Tampilkan mode deteksi
        mode_text = "MODE: MOG2 (Adaptive)" if auto_reset_state else "MODE: Static BG"
        mode_color = (255, 255, 0) if auto_reset_state else (255, 128, 0)  # Cyan / Orange
        cv2.putText(frame, mode_text, (10, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, mode_color, 2)

        # Tampilkan counter debug
        debug_text = f"Detected: {object_detected_frames} | Lost: {object_lost_frames}"
        cv2.putText(frame, debug_text, (10, height - 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        debug_text2 = f"ROI Empty: {roi_empty_frames}/{NO_MOTION_THRESHOLD}"
        cv2.putText(frame, debug_text2, (10, height - 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Debug: object detection status
        debug_text4 = f"Obj: {'YES' if has_detected_object else 'NO'} | ROI: {'YES' if persistent_object_in_roi else 'NO'}"
        cv2.putText(frame, debug_text4, (10, height - 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 255, 150), 1)
        
        # Debug: Movement status
        movement_status = "MOVING" if object_moving else "STATIONARY"
        movement_color = (0, 255, 255) if object_moving else (0, 128, 255)  # Cyan / Orange
        debug_text5 = f"Status: {movement_status} | Canny: {canny_roi_edge_counter}/{NO_MOTION_THRESHOLD}"
        cv2.putText(frame, debug_text5, (10, height - 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, movement_color, 2)

        # Debug: contour count dan total area
        debug_text3 = f"Contours: {len(contours)} | Mask: {cv2.countNonZero(fg_mask)}px"
        cv2.putText(frame, debug_text3, (10, height - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Tampilkan frame
        cv2.imshow('ROI Object Detection', frame)
        
        # =========================================
        # PREVIEW WINDOW (jika show_preview = True)
        # =========================================
        if show_preview:
            # Preprocessing untuk preview
            preview_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            preview_blurred = cv2.GaussianBlur(preview_gray, blur_kernel, 0)
            
            # Convert ke BGR untuk display
            current_bgr = cv2.cvtColor(preview_blurred, cv2.COLOR_GRAY2BGR)
            
            # Edge detection untuk preview
            preview_edges = cv2.Canny(preview_blurred, 50, 150)
            edges_bgr = cv2.cvtColor(preview_edges, cv2.COLOR_GRAY2BGR)
            
            # Highlight ROI di edge image
            edges_roi_color = edges_bgr.copy()
            cv2.rectangle(edges_roi_color, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)
            
            if auto_reset_state:
                # MOG2 Mode
                fg_mask_preview = preview_mog2.apply(preview_blurred, learningRate=0.005)
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
                cv2.putText(edges_resized, f"CANNY EDGE (ROI: {roi_edge_pixels}px)", (10, 30),
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
                bg_diff = cv2.absdiff(background_reference, preview_blurred)
                _, mask_bg = cv2.threshold(bg_diff, BG_DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
                
                if prev_frame_preview is not None:
                    frame_diff = cv2.absdiff(prev_frame_preview, preview_blurred)
                    _, mask_diff = cv2.threshold(frame_diff, FRAME_DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)
                else:
                    mask_diff = np.zeros_like(mask_bg)
                
                prev_frame_preview = preview_blurred.copy()
                
                fg_mask_preview = cv2.bitwise_or(mask_bg, mask_diff)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                fg_mask_preview = cv2.morphologyEx(fg_mask_preview, cv2.MORPH_OPEN, kernel)
                fg_mask_preview = cv2.dilate(fg_mask_preview, kernel, iterations=3)
                
                # Convert masks to BGR
                bg_bgr = cv2.cvtColor(background_reference, cv2.COLOR_GRAY2BGR)
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
                cv2.putText(mask_bg_resized, f"BG DIFF (>{BG_DIFF_THRESHOLD})", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.putText(mask_diff_resized, f"FRAME DIFF (>{FRAME_DIFF_THRESHOLD})", (10, 30),
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
                    f"BG Threshold: {BG_DIFF_THRESHOLD} | Frame Threshold: {FRAME_DIFF_THRESHOLD}",
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

        # 5. EXIT - Tekan 'q' untuk keluar
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        # Manual background reset dengan 'r'
        if key == ord('r'):
            if AUTO_RESET_ENABLED:
                bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                    history=500,
                    varThreshold=50,
                    detectShadows=False
                )
            else:
                background_reference = blurred.copy()
            roi_empty_frames = 0
            last_log_second = 0
            print("Manual background reset")

        # Toggle auto reset dengan 'o'
        if key == ord('o'):
            auto_reset_state = not auto_reset_state
            
            # Jika beralih ke mode Static BG, perlu capture background baru
            if not auto_reset_state:
                print("\n=== SWITCHING TO STATIC BG MODE ===")
                print(f"Capturing {INIT_CAPTURE_COUNT} frames for background reference...")
                print("Please ensure NO objects in the scene!\n")
                
                init_frames = []
                for i in range(INIT_CAPTURE_COUNT):
                    ret, frame = cap.read()
                    if not ret:
                        print("Error: Cannot read frame")
                        continue
                    
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray_blurred = cv2.GaussianBlur(gray, BLUR_KERNEL_SIZE, 0)
                    init_frames.append(gray_blurred)
                    
                    cv2.putText(frame, f"Capturing frame {i+1}/{INIT_CAPTURE_COUNT}",
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    cv2.imshow('ROI Object Detection', frame)
                    cv2.waitKey(300)
                
                background_reference = init_frames[-1].copy()
                print("Background reference captured! Mode: STATIC BG\n")
            else:
                # Beralih ke mode MOG2
                print("\n=== SWITCHING TO MOG2 MODE ===")
                bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                    history=500,
                    varThreshold=50,
                    detectShadows=False
                )
                preview_mog2 = cv2.createBackgroundSubtractorMOG2(
                    history=500,
                    varThreshold=50,
                    detectShadows=False
                )
                print("MOG2 initialized! Mode: AUTO RESET\n")
            
            print(f"Auto reset: {'ON (MOG2)' if auto_reset_state else 'OFF (Static BG)'}")

        # Toggle preview window dengan 'u'
        if key == ord('u'):
            show_preview = not show_preview
            if show_preview:
                print(f"\n[PREVIEW] ON - Press 'u' again to close")
            else:
                print(f"\n[PREVIEW] OFF")
                try:
                    cv2.destroyWindow('Threshold & Grayscale Preview')
                except:
                    pass

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


def is_intersecting(obj_x, obj_y, obj_w, obj_h, roi_x, roi_y, roi_w, roi_h):
    """
    Cek apakah bounding box objek bersinggungan dengan ROI
    """
    # Cek overlap
    if (obj_x < roi_x + roi_w and
        obj_x + obj_w > roi_x and
        obj_y < roi_y + roi_h and
        obj_y + obj_h > roi_y):
        return True
    return False


if __name__ == "__main__":
    main()
