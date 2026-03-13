"""
Simple Object Detection with ROI (Region of Interest)
Flow: OpenCV-based motion/contour detection without YOLO
"""

import cv2
import numpy as np
import time


def main():
    # 1. INIT
    # Buka kamera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
    
    # Tentukan ukuran frame
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Definisikan ROI (Region of Interest)
    # tinggi = height/2, lebar = width*3/4, posisi = center frame
    roi_width = int(width * 3 / 4)
    roi_height = int(height / 2)
    roi_x = (width - roi_width) // 2
    roi_y = (height - roi_height) // 2
    
    # Status indikator
    indicator_on = False
    
    # Untuk efek berkedip
    blink_state = False
    blink_interval = 10  # frame interval untuk toggle
    frame_count = 0
    
    # Background subtractor untuk deteksi gerakan
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50)
    
    # Preprocessing kernel untuk blur
    blur_kernel = (5, 5)
    
    print("Press 'q' to quit")
    
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
        
        # Deteksi gerakan/objek menggunakan background subtraction
        fg_mask = bg_subtractor.apply(blurred)
        
        # Morphological operations untuk membersihkan noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)
        
        # Cari contour untuk mendapatkan bounding box objek
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 3. CHECK ROI
        object_in_roi = False
        
        for contour in contours:
            # Filter contour kecil
            if cv2.contourArea(contour) < 500:
                continue
            
            # Ambil bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Gambar bounding box objek (hijau)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Cek apakah bounding box bersinggungan dengan ROI
            if is_intersecting(x, y, w, h, roi_x, roi_y, roi_width, roi_height):
                object_in_roi = True
        
        # Update status indikator
        if object_in_roi:
            indicator_on = True
            # Efek berkedip: toggle ON/OFF setiap beberapa frame
            if frame_count % blink_interval == 0:
                blink_state = not blink_state
        else:
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
        status_text = "OBJECT IN ROI" if indicator_on else "NO OBJECT"
        status_color = (0, 255, 0) if indicator_on else (0, 0, 255)
        cv2.putText(frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        
        # Tampilkan frame
        cv2.imshow('ROI Object Detection', frame)
        
        # 5. EXIT - Tekan 'q' untuk keluar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
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


if __name__ == "__main__":
    main()
