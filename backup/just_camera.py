import cv2


def main():
    # Inisialisasi kamera
    cap = cv2.VideoCapture(0)
    
    # Cek apakah kamera berhasil dibuka
    if not cap.isOpened():
        print("Error: Tidak dapat membuka kamera")
        return
    
    print("Menampilkan live camera view. Tekan 'q' untuk keluar.")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Gagal membaca frame dari kamera")
            break
        
        # Menampilkan frame dari kamera
        cv2.imshow('Live Camera View', frame)
        
        # Tekan tombol 'q' untuk keluar dari loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Melepaskan resource
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()