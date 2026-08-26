import logging
from typing import Optional, List, Dict, Any
import numpy as np

from .config import DetectionConfig

logger = logging.getLogger(__name__)

class VehicleDetector:
    """YOLO-based vehicle detector.
    
    Uses YOLOv8 (Ultralytics, AGPL-3.0) for vehicle detection.
    Detects: car, motorcycle, bus, truck from COCO classes.
    """
    
    def __init__(self, config: DetectionConfig):
        self.config = config
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model. Falls back to download if not found locally."""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.config.vehicle_model_path)
            if self.config.device != 'cpu':
                self.model.to(self.config.device)
            logger.info(f"Vehicle detector loaded: {self.config.vehicle_model_path} on {self.config.device}")
        except Exception as e:
            logger.error(f"Failed to load vehicle detector: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect vehicles in a frame.
        
        Args:
            frame: BGR image as numpy array (H, W, 3)
            
        Returns:
            List of detections, each containing:
            - bbox: [x1, y1, x2, y2] in pixel coordinates
            - confidence: float
            - class_id: int (COCO class ID)
            - class_name: str (car, motorcycle, bus, truck)
        """
        if self.model is None:
            logger.error("Model not loaded.")
            return []
            
        results = self.model(
            frame,
            conf=self.config.vehicle_confidence,
            iou=self.config.vehicle_iou,
            classes=self.config.vehicle_classes,
            imgsz=self.config.input_size,
            half=self.config.half_precision,
            max_det=self.config.max_detections,
            verbose=False
        )
        
        detections = []
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                
                cls_name = self.config.vehicle_class_names.get(cls_id, "unknown")
                
                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": conf,
                    "class_id": cls_id,
                    "class_name": cls_name
                })
                
        return detections
