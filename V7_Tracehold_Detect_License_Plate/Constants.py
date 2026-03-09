"""
Constants and configuration for ANPR detection
"""

import cv2
import numpy as np

# Color constants
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)
SCALAR_CYAN = (255.0, 223.0, 10.0)  # Cyan border color (#0ADFFF in BGR)
BORDER_OPACITY = 0.5  # 50% opacity for border

# Debug mode
showStep = False
