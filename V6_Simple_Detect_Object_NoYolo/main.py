"""
Simple Object Detection with ROI (Region of Interest)
Flow: OpenCV-based motion/contour detection without YOLO

Detection Mode:
- AUTO_RESET_ENABLED = True  → MOG2 Background Subtractor (adaptive, auto reset)
- AUTO_RESET_ENABLED = False → Background Reference (static, object diam tetap terdeteksi)
"""

import cv2
import numpy as np
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

    # Background subtractor (hanya untuk mode AUTO_RESET = True)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=500,
        varThreshold=50,
        detectShadows=False
    ) if INITIAL_AUTO_RESET_MODE else None

    # Preprocessing kernel untuk blur
    blur_kernel = (5, 5)

    # Tracking object presence
    object_detected_frames = 0
    object_lost_frames = 0
    object_present = False

    # Background reset counter
    no_motion_frames = 0

    # Auto reset state - ini yang di-toggle dengan tombol 'o'
    auto_reset_state = INITIAL_AUTO_RESET_MODE

    print("Press 'q' to quit")
    print("Press 'r' to manually reset background")
    print("Press 'o' to toggle auto reset (ON/OFF)")
    print(f"Initial auto reset state: {'ON' if auto_reset_state else 'OFF'}")
    if not INITIAL_AUTO_RESET_MODE:
        print(f"Thresholds - BG: {BG_DIFF_THRESHOLD}, Frame: {FRAME_DIFF_THRESHOLD}")
    print(f"Auto reset logic: Reset if NO object for {NO_MOTION_THRESHOLD} frames")

    # Minimum dimensions for bounding box display
    MIN_BOX_WIDTH = 120
    MIN_BOX_HEIGHT = 120
    
    # Minimum contour area
    MIN_CONTOUR_AREA = 500

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

        # =========================================
        # DETEKSI OBJEK - Mode tergantung auto_reset_state
        # =========================================
        if auto_reset_state:
            # Mode MOG2 Background Subtractor (adaptive)
            fg_mask = bg_subtractor.apply(blurred)
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

            # Filter visual: hanya tampilkan bounding box jika lebar DAN tinggi >= 120
            if w < MIN_BOX_WIDTH or h < MIN_BOX_HEIGHT:
                continue

            # Gambar bounding box objek (hijau) - hanya yang besar enough
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            has_green_box = True

        # === AUTO RESET LOGIC ===
        if auto_reset_state:
            if not has_detected_object:
                # Tidak ada object → increment counter
                no_motion_frames += 1

                # Cek apakah sudah mencapai threshold
                if no_motion_frames >= NO_MOTION_THRESHOLD:
                    # RESET!
                    if auto_reset_state:
                        # Mode MOG2: Reset background subtractor
                        bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                            history=500,
                            varThreshold=50,
                            detectShadows=False
                        )
                    else:
                        # Mode Static: Update background reference
                        background_reference = blurred.copy()
                    
                    no_motion_frames = 0
                    indicator_on = False
                    blink_state = False
                    object_present = False
                    print(f"[AUTO RESET] Background reset - frame {frame_count}")
            else:
                # Ada object terdeteksi → reset counter
                no_motion_frames = 0
        else:
            # Auto reset OFF → counter tidak jalan
            no_motion_frames = 0

        # === STATE MANAGEMENT untuk ROI INDIKATOR ===
        if not has_detected_object:
            # Tidak ada object sama sekali → matikan indikator
            object_detected_frames = 0
            object_lost_frames = 0
            object_present = False
            indicator_on = False
            blink_state = False
        elif object_in_roi:
            # Ada object di ROI
            object_detected_frames += 1
            object_lost_frames = 0

            # Konfirmasi object ada setelah beberapa frame berturut-turut
            if object_detected_frames >= OBJECT_CONFIRM_THRESHOLD:
                object_present = True
                indicator_on = True

                # Efek berkedip: toggle ON/OFF setiap beberapa frame
                if frame_count % BLINK_INTERVAL == 0:
                    blink_state = not blink_state
        else:
            # Ada object terdeteksi, tapi TIDAK di ROI
            object_detected_frames = 0
            object_lost_frames += 1

            # Object masih dianggap ada selama grace period
            if object_lost_frames >= OBJECT_LOST_THRESHOLD:
                object_present = False
                indicator_on = False
                blink_state = False

        # 4. DISPLAY
        # Gambar ROI
        if indicator_on and blink_state:
            # Kotak biru berkedip
            roi_color = (255, 0, 0)  # Blue (BGR)
            roi_thickness = 3
        else:
            # Kotak normal (abu-abu tipis)
            roi_color = (128, 128, 128)  # Gray
            roi_thickness = 2

        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height),
                     roi_color, roi_thickness)

        # Tampilkan status indikator
        if indicator_on:
            status_text = "OBJECT IN ROI"
            status_color = (0, 255, 0)  # Green
        else:
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

        debug_text2 = f"No Object: {no_motion_frames}/{NO_MOTION_THRESHOLD}"
        cv2.putText(frame, debug_text2, (10, height - 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Debug: object detection status
        debug_text4 = f"Obj Detect: {'YES' if has_detected_object else 'NO'} | Green Box: {'YES' if has_green_box else 'NO'}"
        cv2.putText(frame, debug_text4, (10, height - 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 255, 150), 1)

        # Debug: contour count dan total area
        debug_text3 = f"Contours: {len(contours)} | Mask: {cv2.countNonZero(fg_mask)}px"
        cv2.putText(frame, debug_text3, (10, height - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Tampilkan frame
        cv2.imshow('ROI Object Detection', frame)

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
            no_motion_frames = 0
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
                print("MOG2 initialized! Mode: AUTO RESET\n")
            
            print(f"Auto reset: {'ON (MOG2)' if auto_reset_state else 'OFF (Static BG)'}")

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
