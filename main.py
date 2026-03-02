import os
import cv2
import warnings
import time
from dotenv import load_dotenv
from paddleocr import PaddleOCR

# Load konfigurasi dari file .env
load_dotenv()

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'


def main():
    # Load konfigurasi dari environment
    # Kamera
    camera_width = int(os.getenv('CAMERA_WIDTH', '640'))
    camera_height = int(os.getenv('CAMERA_HEIGHT', '480'))
    camera_fps = int(os.getenv('CAMERA_FPS', '30'))
    
    # OCR
    ocr_interval = int(os.getenv('OCR_INTERVAL', '5'))
    ocr_scale = float(os.getenv('OCR_SCALE', '0.5'))
    
    # Display
    textbox_height = int(os.getenv('TEXTBOX_HEIGHT', '150'))
    text_color = tuple(map(int, os.getenv('TEXT_COLOR', '0,255,0').split(',')))
    text_size = float(os.getenv('TEXT_SIZE', '0.5'))
    text_thickness = int(os.getenv('TEXT_THICKNESS', '1'))
    
    # PaddleOCR
    paddle_lang = os.getenv('PADDLE_LANG', 'en')
    paddle_use_angle_cls = os.getenv('PADDLE_USE_ANGLE_CLS', 'True') == 'True'
    
    # Performa
    show_fps = os.getenv('SHOW_FPS', 'True') == 'True'

    # Inisialisasi PaddleOCR
    ocr = PaddleOCR(use_angle_cls=paddle_use_angle_cls, lang=paddle_lang)

    # Inisialisasi kamera
    cap = cv2.VideoCapture(0)
    
    # Set resolusi kamera sesuai konfigurasi
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

    # Cek apakah kamera berhasil dibuka
    if not cap.isOpened():
        print("Error: Tidak dapat membuka kamera")
        return

    print(f"Menampilkan live camera view dengan OCR. Tekan 'q' untuk keluar.")
    print(f"Konfigurasi: {camera_width}x{camera_height}@{camera_fps}fps, OCR interval={ocr_interval}, scale={ocr_scale}")
    print(f"Target: ~{camera_fps} FPS, OCR update ~{camera_fps/ocr_interval:.1f}x/detik")
    
    # Frame skipping untuk mengurangi beban CPU
    frame_count = 0
    last_text_display = "Waiting for OCR..."
    
    # Untuk membatasi FPS - delay minimum per frame
    fps_delay = 1.0 / camera_fps  # Delay per frame dalam detik

    while True:
        frame_start = time.time()
        start_time = frame_start
        ret, frame = cap.read()

        if not ret:
            print("Gagal membaca frame dari kamera")
            break

        frame_count += 1
        
        # Hanya proses OCR setiap N frame
        if frame_count % ocr_interval == 0:
            # Resize frame untuk OCR (lebih kecil = lebih cepat)
            h, w = frame.shape[:2]
            small_frame = cv2.resize(frame, (int(w * ocr_scale), int(h * ocr_scale)))
            
            # Lakukan OCR pada frame yang di-resize
            result = ocr.ocr(small_frame)

            # Ekstrak teks yang terdeteksi
            detected_texts = []
            if result:
                for res in result:
                    if isinstance(res, dict):
                        rec_texts = res.get('rec_texts', [])
                        rec_scores = res.get('rec_scores', [])
                        for text, score in zip(rec_texts, rec_scores):
                            detected_texts.append(f"{text} ({score:.2f})")

            # Gabungkan teks untuk ditampilkan
            last_text_display = "\n".join(detected_texts) if detected_texts else "No text detected"
        
        text_display = last_text_display

        # Buat area teks (textbox) di bagian bawah frame
        overlay = frame.copy()
        frame_height, frame_width = frame.shape[:2]

        # Gambar rectangle untuk background teks
        cv2.rectangle(
            overlay,
            (0, frame_height - textbox_height),
            (frame_width, frame_height),
            (0, 0, 0),
            cv2.FILLED
        )

        # Blend overlay dengan frame asli
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Tampilkan teks yang terdeteksi
        y_offset = frame_height - textbox_height + 25
        for line in text_display.split("\n"):
            if y_offset < frame_height:
                cv2.putText(
                    frame,
                    line,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    text_size,
                    text_color,
                    text_thickness,
                    cv2.LINE_AA
                )
                y_offset += 20
        
        # Tampilkan FPS untuk monitoring performa
        if show_fps:
            elapsed = time.time() - start_time
            fps = 1.0 / elapsed if elapsed > 0 else 0
            fps_color = (0, 255, 0) if fps < camera_fps * 1.5 else (0, 255, 255)
            cv2.putText(
                frame,
                f"FPS: {fps:.0f} (target: {camera_fps})",
                (frame_width - 180, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                fps_color,
                1,
                cv2.LINE_AA
            )

        # Menampilkan frame dari kamera dengan teks OCR
        cv2.imshow('Live Camera View - OCR', frame)

        # Hitung delay untuk maintain FPS target
        frame_elapsed = time.time() - frame_start
        frame_remaining = fps_delay - frame_elapsed
        
        # Delay untuk maintain FPS (gunakan waitKey untuk responsif)
        if frame_remaining > 0:
            delay_ms = int(frame_remaining * 1000)
            if cv2.waitKey(delay_ms) & 0xFF == ord('q'):
                break
        else:
            # Frame processing lebih lama dari target, langsung lanjut
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Melepaskan resource
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()