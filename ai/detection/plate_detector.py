import logging
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple

from .config import DetectionConfig

logger = logging.getLogger(__name__)

class PlateDetector:
    """License plate detector.
    
    Uses a YOLO model trained/fine-tuned for plate detection.
    Falls back to OpenCV cascade or contour-based detection if model is unavailable.
    """
    
    def __init__(self, config: DetectionConfig):
        self.config = config
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model."""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.config.plate_model_path)
            if self.config.device != 'cpu':
                self.model.to(self.config.device)
            logger.info(f"Plate detector loaded: {self.config.plate_model_path} on {self.config.device}")
        except Exception as e:
            logger.warning(f"Failed to load plate detector YOLO model, falling back to OpenCV: {e}")
            self.model = None
    
    def detect_plates(self, frame: np.ndarray, vehicle_boxes: List[List[int]]) -> List[Dict[str, Any]]:
        """Detect plates within vehicle regions.
        
        Args:
            frame: Full BGR image
            vehicle_boxes: List of [x1, y1, x2, y2]
        Returns:
            List of plate detections: {bbox, confidence, vehicle_bbox}
        """
        plate_detections = []
        for v_box in vehicle_boxes:
            x1, y1, x2, y2 = v_box
            # Ensure valid box
            h, w = frame.shape[:2]
            x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
            
            if x2 <= x1 or y2 <= y1:
                continue
                
            crop = frame[y1:y2, x1:x2]
            
            if self.model is not None:
                results = self.model(
                    crop,
                    conf=self.config.plate_confidence,
                    iou=self.config.plate_iou,
                    verbose=False
                )
                
                for result in results:
                    boxes = result.boxes.cpu().numpy()
                    for box in boxes:
                        px1, py1, px2, py2 = map(int, box.xyxy[0])
                        conf = float(box.conf[0])
                        
                        # Translate to full frame coordinates
                        global_bbox = [x1 + px1, y1 + py1, x1 + px2, y1 + py2]
                        
                        plate_detections.append({
                            "bbox": global_bbox,
                            "confidence": conf,
                            "vehicle_bbox": v_box
                        })
            else:
                fallback_plates = self.detect_plates_fallback(crop)
                for f_box, conf in fallback_plates:
                    px1, py1, px2, py2 = f_box
                    global_bbox = [x1 + px1, y1 + py1, x1 + px2, y1 + py2]
                    plate_detections.append({
                        "bbox": global_bbox,
                        "confidence": conf,
                        "vehicle_bbox": v_box
                    })
                    
        return plate_detections

    def detect_plates_fallback(self, image: np.ndarray) -> List[Tuple[List[int], float]]:
        """OpenCV contour-based plate detection fallback."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(bfilter, 30, 200)
        
        contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
        
        plates = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 10, True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                if 2.0 <= aspect_ratio <= 5.5:
                    plates.append(([x, y, x+w, y+h], 0.5))
                    break # Usually one plate per vehicle
        return plates
