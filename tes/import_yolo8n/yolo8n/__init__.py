"""
YOLOv8n Module - Reusable Components
Export semua components yang bisa di-import

Usage:
    from yolo8n import YOLODetector, YOLOFullDetector, ObjectDistanceTracker, ParkingSession
    
    # Simple detector
    detector = YOLODetector(camera_id=0)
    frame, detections = detector.get_frame()
    
    # Full detector dengan semua fitur
    full_detector = YOLOFullDetector(camera_id=0)
    frame, state = full_detector.get_frame()
"""

from .detector import (
    YOLOFullDetector,
    ObjectDistanceTracker,
    ParkingSession,
    ParkingPhase,
    DEFAULT_CONFIG,
    create_detector as create_full_detector,
)

# Simple YOLODetector (basic detection only)
import cv2
import numpy as np
from ultralytics import YOLO
import os
import time


class YOLODetector:
    """Simple YOLO Detector - basic detection only."""

    def __init__(self, camera_id=0, confidence_threshold=0.5, model_path=None):
        self.camera_id = camera_id
        self.confidence_threshold = confidence_threshold
        
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "yolov8n.pt")
        self.model_path = model_path
        
        self.model = None
        self._load_model()
        
        self.cap = None
        self._init_camera()
        
        self.target_classes = [0]
        self.last_detections = []
        self.current_frame_count = 0
        self.yolo_skip_frames = 2

    def _load_model(self):
        if os.path.exists(self.model_path):
            self.model = YOLO(self.model_path)
        else:
            self.model = None

    def _init_camera(self):
        self.cap = cv2.VideoCapture(self.camera_id)

    def detect_objects(self, frame):
        if self.model is None:
            return []

        results = self.model(frame, verbose=False, conf=self.confidence_threshold)
        
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
                
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                
                detections.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': conf,
                    'class_id': class_id,
                    'class_name': class_name
                })
        
        return detections

    def get_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return None, []

        ret, frame = self.cap.read()
        if not ret:
            return None, []

        self.current_frame_count += 1

        if self.yolo_skip_frames > 0 and self.current_frame_count % (self.yolo_skip_frames + 1) != 0:
            detections = self.last_detections
        else:
            detections = self.detect_objects(frame)
            self.last_detections = detections

        return frame, detections

    def release(self):
        if self.cap is not None:
            self.cap.release()


def create_detector(camera_id=0, confidence_threshold=0.5):
    """Create YOLODetector instance."""
    return YOLODetector(camera_id=camera_id, confidence_threshold=confidence_threshold)


__all__ = [
    'YOLODetector',
    'YOLOFullDetector',
    'ObjectDistanceTracker',
    'ParkingSession',
    'ParkingPhase',
    'DEFAULT_CONFIG',
    'create_detector',
    'create_full_detector',
]
