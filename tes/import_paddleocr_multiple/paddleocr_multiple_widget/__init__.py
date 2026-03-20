"""
PaddleOCR Multiple Widget
Reusable widget untuk OCR multiple images.

Usage:
    from paddleocr_multiple_widget import PaddleOCRMultipleWidget
    
    widget = PaddleOCRMultipleWidget(root=tkinter_root)
    widget.add_images(['img1.jpg', 'img2.jpg', 'img3.jpg'])
    results = widget.process_all()
    widget.export_batch()
"""

from .widget_wrapper import PaddleOCRMultipleWidget

__all__ = ['PaddleOCRMultipleWidget']
