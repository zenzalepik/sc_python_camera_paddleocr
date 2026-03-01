import cv2
from paddleocr import PaddleOCR
import tkinter as tk
from threading import Thread

# Inisialisasi PaddleOCR (CPU, bahasa Inggris)
ocr = PaddleOCR(lang='en')

# GUI Tkinter
root = tk.Tk()
root.title("Realtime OCR Camera")
root.geometry("600x400")

textbox = tk.Text(root, wrap="word", font=("Arial", 12))
textbox.pack(expand=True, fill="both")

def update_text(text):
    textbox.delete("1.0", tk.END)
    textbox.insert(tk.END, text)

def camera_loop():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Gunakan predict() bukan ocr()
        result = ocr.predict(frame_rgb)

        detected_texts = []
        for line in result[0]:
            detected_texts.append(line[1][0])

        if detected_texts:
            update_text("\n".join(detected_texts))

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

thread = Thread(target=camera_loop, daemon=True)
thread.start()

root.mainloop()
