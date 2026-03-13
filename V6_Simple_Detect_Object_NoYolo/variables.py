"""
Configuration Variables for ROI Object Detection
"""

# ============================================
# AUTO RESET BACKGROUND
# ============================================
# Aktifkan auto reset background saat tidak ada gerakan
AUTO_RESET_ENABLED = True
# AUTO_RESET_ENABLED = False

# Durasi tanpa gerakan sebelum auto reset (dalam frames)
# 60 frames ≈ 2 detik pada 30 FPS
# 120 frames ≈ 4 detik pada 30 FPS
# 180 frames ≈ 6 detik pada 30 FPS
NO_MOTION_THRESHOLD = 300  # frames

# ============================================
# INITIALIZATION - BACKGROUND REFERENCE
# ============================================
# Jumlah frame yang di-capture saat inisialisasi untuk background reference
# INIT_CAPTURE_COUNT = 15
INIT_CAPTURE_COUNT = 1

# Threshold similarity untuk memilih background reference (0-1)
# Frame dengan similarity rata-rata tertinggi akan dipilih
INIT_SIMILARITY_THRESHOLD = 0.85

# Metode seleksi background reference:
# "majority" = Pilih frame yang paling banyak mirip dengan frame lainnya (voting)
# "average"  = Pilih frame dengan rata-rata similarity tertinggi (default)
# "strict"   = Pilih frame yang semua pair-wise similarity-nya di atas threshold
INIT_SELECTION_METHOD = "majority"

# Minimum frame yang harus lolos threshold untuk metode "strict"
INIT_STRICT_MIN_VOTES = 10  # Dari total INIT_CAPTURE_COUNT

# ============================================
# OBJECT DETECTION
# ============================================
# Frame untuk konfirmasi object ada
OBJECT_CONFIRM_THRESHOLD = 3

# Frame sebelum object dianggap pergi
OBJECT_LOST_THRESHOLD = 30

# Minimum area contour untuk dianggap object
MIN_CONTOUR_AREA = 800

# ============================================
# ROI (REGION OF INTEREST)
# ============================================
# ROI dimensions sebagai fraksi dari frame size
ROI_WIDTH_FRACTION = 0.75  # 3/4 dari width
ROI_HEIGHT_FRACTION = 0.5  # 1/2 dari height

# ============================================
# DISPLAY
# ============================================
# Interval kedipan indikator (frames)
BLINK_INTERVAL = 10

# ============================================
# CAMERA
# ============================================
# Camera index (0 = default camera)
CAMERA_INDEX = 0

# Gaussian blur kernel size
BLUR_KERNEL_SIZE = (5, 5)

# ============================================
# BACKGROUND SUBTRACTOR
# ============================================
BG_SUBTRACTOR_HISTORY = 200
BG_SUBTRACTOR_VAR_THRESHOLD = 30
BG_SUBTRACTOR_DETECT_SHADOWS = True
