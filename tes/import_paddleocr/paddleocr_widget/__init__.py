"""
PaddleOCR Widget - Reusable OCR Text Detection

Widget reusable untuk deteksi teks dengan PaddleOCR v5 Mobile.

Fitur:
- OCR dengan PaddleOCR v5 Mobile
- Support multi-language
- Bounding box detection
- Confidence score
- Group by line
- Delete space option
- Export ke TXT/JSON
- Copy to clipboard

CARA PAKAI:
    from paddleocr_widget import PaddleOCRWidget
    
    widget = PaddleOCRWidget(lang='id', conf_threshold=0.5)
    result = widget.process_image('path/to/image.jpg')
    texts = widget.get_texts()
    widget.export_to_txt('output.txt')
"""

from .widget_wrapper import PaddleOCRWidget

__all__ = ['PaddleOCRWidget']
