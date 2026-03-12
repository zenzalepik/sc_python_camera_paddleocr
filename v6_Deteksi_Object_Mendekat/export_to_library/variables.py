"""
Configuration Variables for Object Distance Detection - Parking System
Edit file ini untuk mengubah pengaturan aplikasi
"""

# ============================================
# CLEAN_UI Mode Configuration
# ============================================
# True  = Hide all UI elements, only camera view
# False = Show full UI with all visual elements
# CLEAN_UI = True
CLEAN_UI = False

# ============================================
# CAMERA OPTIMIZATION Settings
# ============================================
# Resolution - Lower = smoother, Higher = better quality
# Recommended: 320x240 (smooth) or 640x480 (quality)
# CAMERA_WIDTH = 320
# CAMERA_HEIGHT = 240
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# YOLO Frame Skipping:
# 0 = Detect every frame (most accurate, less smooth)
# 1 = Skip 1 frame (balanced - RECOMMENDED)
# 2 = Skip 2 frames (very smooth, less accurate)
YOLO_SKIP_FRAMES = 0

# YOLO Enabled by Default
# True = YOLO running on startup
# False = YOLO disabled on startup (use Toggle Y with Y key to enable)
YOLO_ENABLED_DEFAULT = True

# ============================================
# YOLO Detection Settings
# ============================================
# Confidence threshold (0.0 - 1.0)
YOLO_CONFIDENCE_THRESHOLD = 0.5

# Target classes untuk tracking (COCO dataset):
# 0=person, 1=bicycle, 2=car, 3=motorcycle, 5=bus, 7=truck, 67=cell phone
TARGET_CLASSES = [0, 67, 1, 2, 3, 5, 7]

# ============================================
# Tracker Settings
# ============================================
# Frame history untuk tracking
MAX_HISTORY = 30

# Frame berturut-turut untuk trigger SIAGA
SIAGA_FRAME_THRESHOLD = 3

# Detik SIAGA tetap aktif setelah object hilang
SIAGA_HOLD_TIME = 3.0

# ============================================
# Parking System Settings
# ============================================
# Target capture frames per fase
FASE1_TARGET = 3  # SIAGA - approaching
FASE2_TARGET = 5  # TETAP - stopped
FASE3_TARGET = 3  # LOOP detector
FASE4_TARGET = 3  # TAP card

# ============================================
# Display Settings
# ============================================
# Window scale (1.0 = original, 2.0 = 2x zoom)
WINDOW_SCALE = 2.0

# Show FPS counter
SHOW_FPS = True
