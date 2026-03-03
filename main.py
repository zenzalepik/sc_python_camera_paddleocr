import os
import cv2
import warnings
import time
import threading
import numpy as np
from queue import Queue
from dotenv import load_dotenv
from paddleocr import PaddleOCR

# Load konfigurasi dari file .env
load_dotenv()

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'


def calculate_blur_score(frame):
    """
    Menghitung blur score menggunakan Laplacian variance.
    Score tinggi = gambar tajam, Score rendah = gambar blur.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


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
    debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'

    # Smart OCR Mode
    smart_ocr_mode = os.getenv('SMART_OCR_MODE', 'False') == 'True'
    focus_wait_time = float(os.getenv('FOCUS_WAIT_TIME', '2'))
    display_duration = float(os.getenv('DISPLAY_DURATION', '5'))
    blur_threshold = float(os.getenv('BLUR_THRESHOLD', '100'))
    min_confidence = float(os.getenv('MIN_CONFIDENCE', '0.8'))

    # Inisialisasi PaddleOCR
    ocr = PaddleOCR(use_angle_cls=paddle_use_angle_cls, lang=paddle_lang)

    # Inisialisasi kamera
    cap = cv2.VideoCapture(0)

    # Set resolusi kamera sesuai konfigurasi
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

    # Set FPS kamera sesuai konfigurasi
    cap.set(cv2.CAP_PROP_FPS, camera_fps)

    # Cek apakah kamera berhasil dibuka
    if not cap.isOpened():
        print("Error: Tidak dapat membuka kamera")
        return

    # Verifikasi FPS yang di-set (beberapa webcam tidak support)
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    print(f"Menampilkan live camera view dengan OCR. Tekan 'q' untuk keluar.")
    print(f"Konfigurasi: {camera_width}x{camera_height}@{camera_fps}fps, OCR interval={ocr_interval}, scale={ocr_scale}")
    print(f"Target: ~{camera_fps} FPS, OCR update ~{camera_fps/ocr_interval:.1f}x/detik")
    print(f"---")
    print(f"FPS yang di-set kamera: {actual_fps} (requested: {camera_fps})")
    print(f"Resolusi kamera: {actual_width}x{actual_height} (requested: {camera_width}x{camera_height})")
    
    if debug_mode:
        print(f"🐛 DEBUG MODE: AKTIF")
        print(f"   • Logging detail untuk OCR dan state transitions")
    
    if smart_ocr_mode:
        print(f"---")
        print(f"🧠 SMART OCR MODE: AKTIF")
        print(f"   • Focus wait: {focus_wait_time} detik")
        print(f"   • Display duration: {display_duration} detik")
        print(f"   • Blur threshold: {blur_threshold}")
        print(f"   • Min confidence: {min_confidence}")
    print(f"---")
    
    if actual_fps != camera_fps and actual_fps > 0:
        print(f"⚠️  PERHATIAN: Webcam tidak support set FPS manual. FPS aktual: {actual_fps}")
    elif actual_fps == 0:
        print(f"⚠️  PERHATIAN: Webcam tidak melaporkan FPS (default driver)")
    print(f"---")

    # State machine untuk Smart OCR Mode
    # STATE: FOCUSING → SCANNING → DISPLAY_ONLY → repeat
    STATE_FOCUSING = 0
    STATE_SCANNING = 1
    STATE_DISPLAY_ONLY = 2

    current_state = STATE_FOCUSING
    state_start_time = time.time()
    last_text_display = "Waiting for focus..."
    last_confidence = 0.0
    ocr_active = True

    # OCR result storage
    ocr_result_queue = Queue(maxsize=1)
    ocr_confidence_queue = Queue(maxsize=1)

    # OCR Worker thread
    ocr_request_queue = Queue(maxsize=1)
    ocr_stop_event = threading.Event()

    def ocr_worker():
        """Background thread untuk OCR processing"""
        ocr_count = 0
        while not ocr_stop_event.is_set():
            if not ocr_request_queue.empty():
                frame_for_ocr = ocr_request_queue.get()
                if frame_for_ocr is not None:
                    ocr_count += 1
                    ocr_start = time.time()
                    
                    if debug_mode:
                        print(f"\n[OCR-{ocr_count}] Mulai OCR...")
                        print(f"  Frame size: {frame_for_ocr.shape[1]}x{frame_for_ocr.shape[0]}")
                    
                    # Lakukan OCR
                    result = ocr.ocr(frame_for_ocr)
                    ocr_time = time.time() - ocr_start

                    # Ekstrak teks yang terdeteksi
                    detected_texts = []
                    max_confidence = 0.0
                    all_raw_results = []
                    
                    if debug_mode:
                        print(f"  OCR time: {ocr_time*1000:.1f}ms")
                        print(f"  Raw result type: {type(result)}")
                    
                    if result:
                        for res in result:
                            if debug_mode:
                                print(f"  Result item type: {type(res)}")
                                print(f"  Result item: {res}")
                            
                            # Handle berbagai format result PaddleOCR
                            if isinstance(res, dict):
                                rec_texts = res.get('rec_texts', [])
                                rec_scores = res.get('rec_scores', [])
                                dt_boxes = res.get('dt_boxes', [])
                                
                                if debug_mode:
                                    print(f"  Dict format - rec_texts: {rec_texts}")
                                    print(f"  Dict format - rec_scores: {rec_scores}")
                                
                                for i, (text, score) in enumerate(zip(rec_texts, rec_scores)):
                                    detected_texts.append(f"{text} ({score:.2f})")
                                    all_raw_results.append({'text': text, 'score': score, 'box': dt_boxes[i] if i < len(dt_boxes) else None})
                                    if score > max_confidence:
                                        max_confidence = score
                            elif isinstance(res, (list, tuple)):
                                # Format lama: [[box], (text, score)]
                                if len(res) >= 2:
                                    box = res[0]
                                    rec_result = res[1]
                                    if isinstance(rec_result, (list, tuple)) and len(rec_result) >= 2:
                                        text = rec_result[0]
                                        score = rec_result[1]
                                        detected_texts.append(f"{text} ({score:.2f})")
                                        all_raw_results.append({'text': text, 'score': score, 'box': box})
                                        if score > max_confidence:
                                            max_confidence = score
                                        
                                        if debug_mode:
                                            print(f"  List format - text: {text}, score: {score}")
                    
                    if debug_mode:
                        print(f"  Detected texts count: {len(detected_texts)}")
                        print(f"  Max confidence: {max_confidence:.2f}")
                        if detected_texts:
                            print(f"  Texts: {detected_texts}")
                        else:
                            print(f"  [OCR-{ocr_count}] ⚠️  TIDAK ADA TEKS TERDETEKSI")
                    
                    # Update result
                    text_result = "\n".join(detected_texts) if detected_texts else "No text detected"

                    # Masukkan ke queue (overwrite jika penuh)
                    try:
                        while not ocr_result_queue.empty():
                            ocr_result_queue.get_nowait()
                        ocr_result_queue.put_nowait(text_result)

                        while not ocr_confidence_queue.empty():
                            ocr_confidence_queue.get_nowait()
                        ocr_confidence_queue.put_nowait(max_confidence)
                        
                        if debug_mode:
                            print(f"  [OCR-{ocr_count}] Result queued: {text_result[:50]}...")
                    except Exception as e:
                        if debug_mode:
                            print(f"  [OCR-{ocr_count}] Queue error: {e}")
                        pass  # Queue penuh, skip

            else:
                time.sleep(0.001)  # Idle sebentar

    # Start OCR worker thread
    ocr_thread = threading.Thread(target=ocr_worker, daemon=True)
    ocr_thread.start()

    # Frame skipping untuk mengurangi beban CPU
    frame_count = 0

    # FPS counter untuk monitoring
    fps_counter = 0
    fps_start_time = time.time()
    current_fps = 0

    # Frame timing control
    target_frame_delay = 1.0 / camera_fps

    while True:
        loop_start = time.time()

        # Baca frame dari kamera (non-blocking dengan waitKey(1))
        ret, frame = cap.read()

        if not ret:
            print("Gagal membaca frame dari kamera")
            break

        frame_count += 1

        # Hitung blur score untuk frame ini
        blur_score = calculate_blur_score(frame)
        is_sharp = blur_score > blur_threshold

        # Smart OCR Mode logic
        if smart_ocr_mode:
            elapsed_in_state = time.time() - state_start_time

            if current_state == STATE_FOCUSING:
                # State 1: FOCUSING - tunggu kamera fokus dan gambar jernih
                last_text_display = f"Focusing... ({focus_wait_time - elapsed_in_state:.1f}s)"

                if elapsed_in_state >= focus_wait_time and is_sharp:
                    # Gambar sudah jernih, lanjut ke scanning
                    if debug_mode:
                        print(f"\n[STATE] FOCUSING → SCANNING (blur_score: {blur_score:.0f} > {blur_threshold})")
                    current_state = STATE_SCANNING
                    state_start_time = time.time()
                    last_text_display = "Scanning..."
                    ocr_active = True

            elif current_state == STATE_SCANNING:
                # State 2: SCANNING - OCR aktif mencari teks dengan confidence tinggi
                # Kirim frame ke OCR
                if frame_count % ocr_interval == 0:
                    h, w = frame.shape[:2]
                    small_frame = cv2.resize(frame, (int(w * ocr_scale), int(h * ocr_scale)))

                    if debug_mode:
                        print(f"\n[SCANNING] Kirim frame ke OCR (frame #{frame_count})...")
                    
                    try:
                        while not ocr_request_queue.empty():
                            ocr_request_queue.get_nowait()
                        ocr_request_queue.put_nowait(small_frame)
                    except Exception as e:
                        if debug_mode:
                            print(f"  Queue error: {e}")
                        pass

                # Ambil hasil OCR terbaru
                try:
                    while not ocr_result_queue.empty():
                        last_text_display = ocr_result_queue.get_nowait()
                        last_confidence = ocr_confidence_queue.get_nowait()
                except:
                    pass

                # Cek apakah dapat teks dengan confidence tinggi
                if last_confidence >= min_confidence:
                    # Dapat teks bagus, istirahat
                    if debug_mode:
                        print(f"\n[STATE] SCANNING → DISPLAY_ONLY (confidence: {last_confidence:.2f} >= {min_confidence})")
                    current_state = STATE_DISPLAY_ONLY
                    state_start_time = time.time()
                    last_text_display = f"✓ {last_text_display}"

            elif current_state == STATE_DISPLAY_ONLY:
                # State 3: DISPLAY_ONLY - tampilkan hasil, OCR istirahat
                ocr_active = False

                # Tampilkan countdown
                remaining = display_duration - elapsed_in_state
                if remaining > 0:
                    last_text_display = f"{last_text_display} | Next: {remaining:.1f}s"
                else:
                    # Waktu display habis, ulang dari focusing
                    if debug_mode:
                        print(f"\n[STATE] DISPLAY_ONLY → FOCUSING (reset cycle)")
                    current_state = STATE_FOCUSING
                    state_start_time = time.time()
                    last_text_display = "Refocusing..."
                    ocr_active = True
        else:
            # Mode normal (tanpa Smart OCR)
            if frame_count % ocr_interval == 0:
                h, w = frame.shape[:2]
                small_frame = cv2.resize(frame, (int(w * ocr_scale), int(h * ocr_scale)))
                
                try:
                    while not ocr_request_queue.empty():
                        ocr_request_queue.get_nowait()
                    ocr_request_queue.put_nowait(small_frame)
                except:
                    pass

            # Ambil hasil OCR terbaru
            try:
                while not ocr_result_queue.empty():
                    last_text_display = ocr_result_queue.get_nowait()
            except:
                pass

        text_display = last_text_display

        # Tampilkan status Smart OCR Mode
        if smart_ocr_mode:
            state_names = ["FOCUSING", "SCANNING", "DISPLAY"]
            state_color = (0, 255, 255) if current_state == STATE_SCANNING else (0, 255, 0)
            cv2.putText(
                frame,
                f"State: {state_names[current_state]}",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                state_color,
                1,
                cv2.LINE_AA
            )
            
            # Tampilkan blur score
            blur_color = (0, 255, 0) if is_sharp else (0, 0, 255)
            cv2.putText(
                frame,
                f"Sharp: {blur_score:.0f}/{blur_threshold}",
                (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                blur_color,
                1,
                cv2.LINE_AA
            )

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

        # Hitung FPS aktual untuk monitoring
        fps_counter += 1
        if show_fps:
            fps_elapsed = time.time() - fps_start_time
            if fps_elapsed >= 1.0:  # Update FPS setiap 1 detik
                current_fps = fps_counter / fps_elapsed
                fps_counter = 0
                fps_start_time = time.time()

            fps_color = (0, 255, 0) if current_fps <= camera_fps * 1.1 else (0, 255, 255)
            cv2.putText(
                frame,
                f"FPS: {current_fps:.1f} (target: {camera_fps})",
                (frame_width - 200, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                fps_color,
                1,
                cv2.LINE_AA
            )

        # Menampilkan frame dari kamera dengan teks OCR
        cv2.imshow('Live Camera View - OCR', frame)

        # Frame rate control: tunggu sesuai target FPS
        processing_time = time.time() - loop_start
        time_to_wait = target_frame_delay - processing_time

        if time_to_wait > 0:
            wait_ms = max(1, int(time_to_wait * 1000))
        else:
            wait_ms = 1

        if cv2.waitKey(wait_ms) & 0xFF == ord('q'):
            break

    # Cleanup
    ocr_stop_event.set()
    ocr_thread.join(timeout=1.0)

    # Melepaskan resource
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
