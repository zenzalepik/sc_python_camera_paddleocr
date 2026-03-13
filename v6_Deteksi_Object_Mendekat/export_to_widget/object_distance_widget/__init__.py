"""
Object Distance Detection Widget Package
Reusable widget untuk real-time object distance detection dengan YOLO

Usage:
    from object_distance_widget import ObjectDistanceWidget
    
    # Create widget
    widget = ObjectDistanceWidget(parent_frame, camera_id=0)
    widget.pack(fill=tk.BOTH, expand=True)
    
    # Start detection
    widget.start()
    
    # Stop detection
    widget.stop()
"""

from .widget_core import ObjectDistanceWidget
from .widget_variables import (
    CLEAN_UI,
    CAMERA_WIDTH,
    CAMERA_HEIGHT,
    YOLO_SKIP_FRAMES,
    YOLO_ENABLED_DEFAULT,
    YOLO_CONFIDENCE_THRESHOLD,
    TARGET_CLASSES,
    MAX_HISTORY,
    SIAGA_FRAME_THRESHOLD,
    SIAGA_HOLD_TIME,
    FASE1_TARGET,
    FASE2_TARGET,
    FASE3_TARGET,
    FASE4_TARGET,
    WINDOW_SCALE,
    SHOW_FPS
)

__all__ = [
    'ObjectDistanceWidget',
    'CLEAN_UI',
    'CAMERA_WIDTH',
    'CAMERA_HEIGHT',
    'YOLO_SKIP_FRAMES',
    'YOLO_ENABLED_DEFAULT',
    'YOLO_CONFIDENCE_THRESHOLD',
    'TARGET_CLASSES',
    'MAX_HISTORY',
    'SIAGA_FRAME_THRESHOLD',
    'SIAGA_HOLD_TIME',
    'FASE1_TARGET',
    'FASE2_TARGET',
    'FASE3_TARGET',
    'FASE4_TARGET',
    'WINDOW_SCALE',
    'SHOW_FPS'
]

__version__ = '1.0.0'
