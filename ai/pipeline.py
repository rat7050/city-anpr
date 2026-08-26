import logging
import cv2
import numpy as np
from typing import List, Dict, Any, Callable

from .detection.config import DetectionConfig
from .detection.vehicle_detector import VehicleDetector
from .detection.plate_detector import PlateDetector
from .ocr.config import OCRConfig
from .ocr.plate_ocr import PlateOCR
from .tracking.byte_tracker import SimpleByteTracker
from .tracking.track_manager import TrackManager

logger = logging.getLogger(__name__)

class ANPRPipeline:
    """Complete ANPR processing pipeline.
    
    Video/Frame -> Vehicle Detection -> Plate Detection -> 
    Preprocessing -> OCR -> Validation -> Tracking -> Detection Event
    """
    
    def __init__(self, det_config: DetectionConfig = None, ocr_config: OCRConfig = None):
        if det_config is None:
            det_config = DetectionConfig()
        if ocr_config is None:
            ocr_config = OCRConfig()
            
        self.vehicle_detector = VehicleDetector(det_config)
        self.plate_detector = PlateDetector(det_config)
        self.ocr = PlateOCR(ocr_config)
        self.tracker = SimpleByteTracker()
        self.track_manager = TrackManager()
        self.plate_validator = None  # Set externally if needed
    
    def process_frame(self, frame: np.ndarray, camera_id: str, timestamp: Any) -> List[Dict[str, Any]]:
        """Process a single frame through the full pipeline."""
        events = []
        
        # 1. Detect vehicles
        vehicle_detections = self.vehicle_detector.detect(frame)
        
        # 2. Update tracker
        active_tracks = self.tracker.update(vehicle_detections)
        
        # Maps bounding box string to track id for easy lookup
        box_to_track = {}
        for trk in active_tracks:
            box_to_track[tuple(trk['bbox'])] = trk['track_id']
            
        # Extract vehicle boxes for plate detection
        vehicle_boxes = [d['bbox'] for d in vehicle_detections]
        
        # 3. Detect plates
        plate_detections = self.plate_detector.detect_plates(frame, vehicle_boxes)
        
        for pd in plate_detections:
            v_box = tuple(pd['vehicle_bbox'])
            if v_box not in box_to_track:
                continue
                
            track_id = box_to_track[v_box]
            px1, py1, px2, py2 = pd['bbox']
            
            # Crop plate
            h, w = frame.shape[:2]
            px1, py1, px2, py2 = max(0, px1), max(0, py1), min(w, px2), min(h, py2)
            if px2 <= px1 or py2 <= py1:
                continue
                
            plate_crop = frame[py1:py2, px1:px2]
            
            # Run OCR
            text, conf = self.ocr.read_plate(plate_crop)
            
            if text:
                # Add to track manager
                v_type = next((d['class_name'] for d in vehicle_detections if tuple(d['bbox']) == v_box), "unknown")
                self.track_manager.add_ocr_result(track_id, text, conf, v_type)
                
                if self.track_manager.is_track_ready(track_id):
                    res = self.track_manager.finalize_track(track_id)
                    if res:
                        events.append({
                            "camera_id": camera_id,
                            "timestamp": timestamp,
                            "track_id": track_id,
                            "plate_number": res.get("plate_number"),
                            "confidence": res.get("confidence"),
                            "vehicle_type": res.get("vehicle_type"),
                            "bbox": v_box
                        })
                        
        return events
    
    def process_video(self, video_path: str, camera_id: str, callback: Callable = None) -> List[Dict[str, Any]]:
        """Process a complete video file."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Cannot open video {video_path}")
            return []
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_idx = 0
        all_events = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Simulate timestamp
            timestamp = frame_idx / fps
            
            events = self.process_frame(frame, camera_id, timestamp)
            all_events.extend(events)
            
            if callback and events:
                callback(events)
                
            frame_idx += 1
            
        cap.release()
        return all_events
