"""
YOLO Widget - Parking System
Widget reusable untuk deteksi object dengan parking system.

Fitur lengkap sama dengan non_widget:
- Object Detection (YOLOv8n)
- Distance Tracking (mendekat/menjauh)
- SIAGA System
- Parking Session (4 Fase: SIAGA → TETAP → LOOP → TAP)
- UI Overlays lengkap

CARA PAKAI:
    from yolo_widget import YOLOWidget
    
    widget = YOLOWidget(camera_id=0)
    frame, state = widget.get_frame()
    # Frame sudah ada UI lengkap, siap ditampilkan!
"""

from .widget_wrapper import (
    YOLOWidget,
    ParkingPhase,
    ParkingSession,
    ObjectDistanceTracker,
    CaptureManager,
    DEFAULT_CONFIG,
)

__all__ = [
    'YOLOWidget',
    'ParkingPhase',
    'ParkingSession',
    'ObjectDistanceTracker',
    'CaptureManager',
    'DEFAULT_CONFIG',
]
