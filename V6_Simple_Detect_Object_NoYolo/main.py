"""
Simple Object Detection with ROI (Region of Interest)
Flow: OpenCV-based motion/contour detection without YOLO
Uses background reference image for stationary object detection
"""

import cv2
import numpy as np
from variables import (
    AUTO_RESET_ENABLED,
    NO_MOTION_THRESHOLD,
    OBJECT_CONFIRM_THRESHOLD,
    OBJECT_LOST_THRESHOLD,
    MIN_CONTOUR_AREA,
    ROI_WIDTH_FRACTION,
    ROI_HEIGHT_FRACTION,
    BLINK_INTERVAL,
    CAMERA_INDEX,
    BLUR_KERNEL_SIZE,
    BG_SUBTRACTOR_HISTORY,
    BG_SUBTRACTOR_VAR_THRESHOLD,
    BG_SUBTRACTOR_DETECT_SHADOWS,
    INIT_CAPTURE_COUNT,
    INIT_SIMILARITY_THRESHOLD,
    INIT_SELECTION_METHOD,
    INIT_STRICT_MIN_VOTES,
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
    # FASE INISIALISASI - CAPTURE BACKGROUND REFERENCE
    # =========================================
    print(f"\n=== INITIALIZING BACKGROUND REFERENCE ===")
    print(f"Capturing {INIT_CAPTURE_COUNT} frames...")
    print(f"Selection method: {INIT_SELECTION_METHOD}")
    print(f"Please ensure NO objects in the scene!\n")

    init_frames = []
    init_frames_original = []  # Simpan original frames untuk preview
    for i in range(INIT_CAPTURE_COUNT):
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame during initialization")
            return

        # Simpan original frame
        init_frames_original.append(frame.copy())

        # Convert ke grayscale dan blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.GaussianBlur(gray, BLUR_KERNEL_SIZE, 0)
        init_frames.append(gray_blurred)

        # Tampilkan progress
        progress_frame = frame.copy()
        cv2.putText(progress_frame, f"Capturing frame {i+1}/{INIT_CAPTURE_COUNT}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(progress_frame, "Please stay still...",
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.imshow('ROI Object Detection', progress_frame)
        cv2.waitKey(300)  # Tunggu 300ms antar frame

    # Pilih frame paling stabil dengan metode yang dipilih
    print("Selecting best reference frame...")
    best_frame_idx = select_best_reference_frame(
        init_frames,
        method=INIT_SELECTION_METHOD,
        threshold=INIT_SIMILARITY_THRESHOLD,
        min_votes=INIT_STRICT_MIN_VOTES
    )
    background_reference = init_frames[best_frame_idx].copy()
    
    # Simpan untuk preview
    init_frames_storage = {
        'original': init_frames_original,
        'grayscale': init_frames,
        'best_idx': best_frame_idx
    }
    background_reference_original = init_frames_original[best_frame_idx].copy()

    print(f"Background reference selected (frame #{best_frame_idx + 1})")
    print(f"=== INITIALIZATION COMPLETE ===\n")

    # Tampilkan background reference
    cv2.imshow('Background Reference', background_reference)
    cv2.waitKey(1000)
    cv2.destroyWindow('Background Reference')

    # =========================================
    # VARIABEL UNTUK MAIN LOOP
    # =========================================

    # Status indikator
    indicator_on = False

    # Untuk efek berkedip
    blink_state = False
    frame_count = 0

    # Background subtractor untuk deteksi gerakan (opsional, backup)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=BG_SUBTRACTOR_HISTORY,
        varThreshold=BG_SUBTRACTOR_VAR_THRESHOLD,
        detectShadows=BG_SUBTRACTOR_DETECT_SHADOWS
    )

    # Tracking object presence - untuk handle object diam
    object_detected_frames = 0
    object_lost_frames = 0
    object_present = False

    # Background reset - untuk handle kondisi kosong
    no_motion_frames = 0
    background_reset = False
    
    # Cooldown setelah reset (untuk mencegah false detection)
    reset_cooldown_frames = 0
    RESET_COOLDOWN = 30  # Frame cooldown setelah reset (~1 detik)

    # Frame sebelumnya untuk frame differencing
    prev_frame = None

    # Auto reset state (bisa di-toggle)
    auto_reset_state = AUTO_RESET_ENABLED  # Initial state dari variables.py

    # Storage untuk init frames (untuk preview dengan Ctrl+Shift+I)
    init_frames_storage = None
    background_reference_original = None

    print("Press 'q' to quit")
    print("Press 'r' to manually reset background reference")
    print("Press 't' to toggle auto reset (ON/OFF)")
    print("Press 'p' to show initialization preview")
    print(f"Initial auto reset state: {'ON' if auto_reset_state else 'OFF'}")

    # 2. LOOP
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read frame")
            break

        frame_count += 1

        # Preprocessing: grayscale dan blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, BLUR_KERNEL_SIZE, 0)

        # =========================================
        # DETEKSI OBJEK (BERGERAK DAN DIAM)
        # =========================================
        # 1. Background Reference Differencing (utama untuk object diam)
        bg_diff = cv2.absdiff(background_reference, blurred)
        _, fg_mask_bg = cv2.threshold(bg_diff, 25, 255, cv2.THRESH_BINARY)

        # 2. Frame Differencing (untuk object bergerak)
        if prev_frame is not None:
            frame_diff = cv2.absdiff(prev_frame, blurred)
            _, fg_mask_diff = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
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

        # 3. CHECK ROI
        object_in_roi = False
        detected_contours = []
        has_motion = False

        for contour in contours:
            # Filter contour kecil
            if cv2.contourArea(contour) < MIN_CONTOUR_AREA:
                continue

            has_motion = True

            # Ambil bounding box
            x, y, w, h = cv2.boundingRect(contour)
            detected_contours.append((x, y, w, h))

            # Gambar bounding box objek (hijau)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Cek apakah bounding box bersinggungan dengan ROI
            if is_intersecting(x, y, w, h, roi_x, roi_y, roi_width, roi_height):
                object_in_roi = True

        # === BACKGROUND RESET LOGIC ===
        # Reset hanya jika: tidak ada object di ROI DAN tidak ada motion cukup lama
        # Ini lebih strict untuk mencegah false reset
        if not has_motion and not object_in_roi and not object_present:
            no_motion_frames += 1
            # Auto reset background jika tidak ada gerakan cukup lama
            if auto_reset_state and no_motion_frames >= NO_MOTION_THRESHOLD:
                # Re-capture background reference
                background_reference = blurred.copy()
                no_motion_frames = 0
                background_reset = True
                reset_cooldown_frames = RESET_COOLDOWN  # Activate cooldown
                print("Background reference updated - scene kosong")
        else:
            no_motion_frames = 0
            background_reset = False
        
        # Decrement cooldown counter
        if reset_cooldown_frames > 0:
            reset_cooldown_frames -= 1
            # Selama cooldown, skip deteksi untuk mencegah false positive
            if reset_cooldown_frames > 0:
                has_motion = False
                object_in_roi = False

        # === STATE MANAGEMENT untuk object diam ===
        if object_in_roi:
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
            object_detected_frames = 0
            object_lost_frames += 1

            # Object masih dianggap ada selama grace period
            if object_lost_frames >= OBJECT_LOST_THRESHOLD:
                object_present = False
                indicator_on = False
                blink_state = False
            # else: tetap anggap object masih ada (handle object diam)

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

        # Tampilkan counter debug (opsional)
        debug_text = f"Detected: {object_detected_frames} | Lost: {object_lost_frames}"
        cv2.putText(frame, debug_text, (10, height - 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        debug_text2 = f"No Motion: {no_motion_frames}/{NO_MOTION_THRESHOLD}"
        cv2.putText(frame, debug_text2, (10, height - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Tampilkan frame
        cv2.imshow('ROI Object Detection', frame)

        # 5. EXIT - Tekan 'q' untuk keluar
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break

        # Manual background reset dengan 'r'
        if key == ord('r'):
            background_reference = blurred.copy()
            no_motion_frames = 0
            print("Manual background reference reset")

        # Toggle auto reset dengan 't'
        if key == ord('t'):
            auto_reset_state = not auto_reset_state
            print(f"Auto reset: {'ON' if auto_reset_state else 'OFF'}")

        # Show initialization preview dengan 'p'
        if key == ord('p'):
            if init_frames_storage is not None:
                show_initialization_preview(
                    init_frames_storage,
                    background_reference_original,
                    BLUR_KERNEL_SIZE
                )
            else:
                print("No initialization frames stored")

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Camera released and windows destroyed")


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


def select_best_reference_frame(frames, method="average", threshold=0.85, min_votes=10):
    """
    Pilih frame paling stabil (paling mirip dengan frame lainnya)
    dari sekumpulan frame inisialisasi.

    Args:
        frames: List of grayscale frames
        method: Selection method ("average", "majority", "strict")
        threshold: Similarity threshold for voting (0-1)
        min_votes: Minimum votes required for "strict" method

    Returns:
        Index frame terbaik untuk background reference
    """
    n = len(frames)
    if n <= 1:
        return 0

    # Hitung pair-wise similarity matrix
    similarity_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                score = cv2.matchTemplate(frames[i], frames[j], cv2.TM_CCOEFF_NORMED)[0][0]
                similarity_matrix[i, j] = score

    print(f"  Similarity matrix ({n}x{n} frames):")

    if method == "average":
        # Metode 1: Pilih frame dengan rata-rata similarity tertinggi
        avg_scores = []
        for i in range(n):
            scores = [similarity_matrix[i, j] for j in range(n) if i != j]
            avg_similarity = np.mean(scores)
            avg_scores.append(avg_similarity)
            print(f"    Frame {i+1:2d}: avg = {avg_similarity:.4f}")

        best_idx = int(np.argmax(avg_scores))
        print(f"\n  ✓ Selected: Frame {best_idx + 1} (avg similarity = {avg_scores[best_idx]:.4f})")
        return best_idx

    elif method == "majority":
        # Metode 2: Voting - pilih frame yang paling banyak punya similarity di atas threshold
        vote_counts = []
        for i in range(n):
            votes = sum(1 for j in range(n) if i != j and similarity_matrix[i, j] >= threshold)
            vote_counts.append(votes)
            print(f"    Frame {i+1:2d}: {votes}/{n-1} votes (similarity >= {threshold})")

        # Pilih frame dengan votes terbanyak
        best_idx = int(np.argmax(vote_counts))
        print(f"\n  ✓ Selected: Frame {best_idx + 1} ({vote_counts[best_idx]}/{n-1} votes)")
        return best_idx

    elif method == "strict":
        # Metode 3: Strict - pilih frame yang SEMUA pair-wise similarity-nya di atas threshold
        # Jika tidak ada, fallback ke majority
        qualified_frames = []
        for i in range(n):
            all_above = all(similarity_matrix[i, j] >= threshold for j in range(n) if i != j)
            min_sim = min(similarity_matrix[i, j] for j in range(n) if i != j)
            print(f"    Frame {i+1:2d}: min = {min_sim:.4f} {'✓' if all_above else '✗'}")

            if all_above:
                qualified_frames.append(i)

        if len(qualified_frames) >= min_votes:
            # Jika ada cukup frame yang qualified, pilih yang min similarity tertinggi
            best_idx = max(qualified_frames,
                          key=lambda i: min(similarity_matrix[i, j] for j in range(n) if i != j))
            print(f"\n  ✓ Selected: Frame {best_idx + 1} (strict mode, {len(qualified_frames)} qualified)")
            return best_idx
        else:
            # Fallback ke majority
            print(f"\n  ! Not enough qualified frames ({len(qualified_frames)} < {min_votes})")
            print(f"  ! Falling back to majority voting...")
            return select_best_reference_frame(frames, method="majority", threshold=threshold)

    else:
        print(f"  ! Unknown method '{method}', using 'average'")
        return select_best_reference_frame(frames, method="average", threshold=threshold)


def show_initialization_preview(init_frames_data, background_ref_original, blur_kernel):
    """
    Tampilkan popup preview initialization frames dengan 3 versi:
    1. Original (color)
    2. Grayscale + Blur
    3. Threshold (binary)
    """
    import math

    original_frames = init_frames_data['original']
    grayscale_frames = init_frames_data['grayscale']
    best_idx = init_frames_data['best_idx']
    n = len(original_frames)

    print(f"\n=== INITIALIZATION PREVIEW (Frame #{best_idx + 1} selected) ===")

    # Tampilkan frame terbaik (original, grayscale, threshold)
    best_original = original_frames[best_idx].copy()
    best_gray = grayscale_frames[best_idx].copy()

    # Threshold untuk visualisasi
    bg_diff = cv2.absdiff(best_gray, grayscale_frames[0])
    _, best_threshold = cv2.threshold(bg_diff, 30, 255, cv2.THRESH_BINARY)

    # Resize untuk fit screen
    target_width = 400
    h, w = best_original.shape[:2]
    scale = target_width / w
    new_size = (int(w * scale), int(h * scale))

    original_resized = cv2.resize(best_original, new_size)
    gray_resized = cv2.resize(best_gray, new_size)
    threshold_resized = cv2.resize(best_threshold, new_size)

    # Convert grayscale ke BGR untuk display
    gray_bgr = cv2.cvtColor(gray_resized, cv2.COLOR_GRAY2BGR)
    threshold_bgr = cv2.cvtColor(threshold_resized, cv2.COLOR_GRAY2BGR)

    # Add labels
    cv2.putText(original_resized, "ORIGINAL", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(gray_bgr, "GRAYSCALE + BLUR", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(threshold_bgr, "THRESHOLD", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Stack horizontal
    combined = np.hstack([original_resized, gray_bgr, threshold_bgr])

    # Tampilkan info
    info_text = [
        f"Frame Selected: #{best_idx + 1} / {n}",
        f"Resolution: {w}x{h}",
        "",
        "Close window or press any key to continue..."
    ]

    # Buat panel info
    info_panel = np.zeros((200, target_width * 3, 3), dtype=np.uint8)
    for i, text in enumerate(info_text):
        color = (200, 200, 200) if text else (100, 100, 100)
        cv2.putText(info_panel, text, (10, 40 + i * 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

    # Gabungkan
    full_preview = np.vstack([combined, info_panel])

    cv2.imshow('Initialization Preview', full_preview)
    print("Preview window opened. Press any key in the preview window to close.")

    # Wait hingga user tekan key di preview window
    cv2.waitKey(0)
    cv2.destroyWindow('Initialization Preview')
    print("=== PREVIEW CLOSED ===\n")


if __name__ == "__main__":
    main()
