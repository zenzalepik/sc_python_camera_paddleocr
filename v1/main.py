import cv2
import os
import time
from dotenv import load_dotenv
from paddleocr import PaddleOCR

# Suppress model source check
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

# Load konfigurasi dari .env
load_dotenv()

# Inisialisasi PaddleOCR (API v3.x)
ocr = PaddleOCR(
    use_textline_orientation=True,
    lang=os.getenv('PADDLE_LANG', 'en')
)

# Buka kamera
cap = cv2.VideoCapture(0)

# Set resolusi kamera
width = int(os.getenv('CAMERA_WIDTH', '640'))
height = int(os.getenv('CAMERA_HEIGHT', '480'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

if not cap.isOpened():
    print("Error: Tidak dapat membuka kamera")
    exit()

print("Live Camera OCR - Tekan 'q' untuk keluar")

# OCR interval (proses setiap N frame)
ocr_interval = int(os.getenv('OCR_INTERVAL', '5'))
frame_count = 0
last_text = "Waiting for OCR..."

while True:
    ret, frame = cap.read()
    if not ret:
        print("Gagal membaca frame")
        break

    frame_count += 1

    # Proses OCR setiap N frame
    if frame_count % ocr_interval == 0:
        result = ocr.predict(frame)

        # Ekstrak teks dari hasil OCR (format PaddleOCR 3.x)
        detected_texts = []
        if result:
            for res in result:
                if isinstance(res, dict):
                    # Format v3.x: dict dengan rec_texts, rec_scores
                    rec_texts = res.get('rec_texts', [])
                    rec_scores = res.get('rec_scores', [])
                    for text, score in zip(rec_texts, rec_scores):
                        detected_texts.append(f"{text} ({score:.2f})")

        last_text = "\n".join(detected_texts) if detected_texts else "No text detected"

    # Tampilkan hasil OCR di layar (background hitam semi-transparan)
    h, w = frame.shape[:2]
    overlay = frame.copy()
    textbox_h = 150
    cv2.rectangle(overlay, (0, h - textbox_h), (w, h), (0, 0, 0), cv2.FILLED)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    # Render teks hasil deteksi
    y_offset = h - textbox_h + 25
    for line in last_text.split("\n"):
        if y_offset < h:
            cv2.putText(frame, line, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            y_offset += 20

    # Tampilkan FPS
    elapsed = time.time()
    fps = 1.0 / (time.time() - elapsed + 0.001)
    cv2.putText(frame, f"FPS: {fps:.0f}", (w - 80, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

    # Tampilkan frame
    cv2.imshow('Live Camera OCR', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
