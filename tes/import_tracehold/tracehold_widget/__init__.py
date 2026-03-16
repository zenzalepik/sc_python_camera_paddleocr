"""
TraceHold Widget - ROI Object Detection
Widget reusable untuk deteksi object dengan Region of Interest (ROI).

Fitur:
- Object Detection (OpenCV-based, tanpa YOLO)
- Dual Mode: MOG2 Adaptive vs Static Background
- ROI (Region of Interest) tracking
- Auto Reset setelah ROI kosong
- Canny Edge backup detection

CARA PAKAI:
    from tracehold_widget import TraceHoldWidget
    
    widget = TraceHoldWidget(camera_id=0)
    frame, state = widget.get_frame()
"""

from .widget_wrapper import TraceHoldWidget

__all__ = ['TraceHoldWidget']
