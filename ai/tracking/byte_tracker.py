import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any
from scipy.optimize import linear_sum_assignment

@dataclass
class Track:
    id: int
    bbox: List[int]
    confidence: float
    class_name: str
    age: int = 0
    hits: int = 1
    unmatched_age: int = 0
    active: bool = False

def iou(box1: List[int], box2: List[int]) -> float:
    """Calculate Intersection over Union (IoU) of two bounding boxes."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union = area1 + area2 - intersection
    if union <= 0:
        return 0.0
    return intersection / union

class SimpleByteTracker:
    """Simplified ByteTrack-style multi-object tracker.
    
    Based on ByteTrack (MIT license) concepts.
    Tracks vehicles across frames within a single camera.
    Associates track IDs with plate OCR results.
    """
    
    def __init__(self, max_age: int = 30, min_hits: int = 3, iou_threshold: float = 0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.tracks: Dict[int, Track] = {}
        self.next_id = 1
    
    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update tracks with new detections."""
        
        if not detections:
            for t in self.tracks.values():
                t.unmatched_age += 1
                t.age += 1
            self._cleanup_tracks()
            return self._get_active_tracks()
            
        high_confs = [d for d in detections if d['confidence'] >= 0.6]
        low_confs = [d for d in detections if d['confidence'] < 0.6]
        
        unmatched_tracks = list(self.tracks.values())
        
        # 1. Match high conf detections
        matched_high, unmatched_high, unmatched_tracks = self._match(high_confs, unmatched_tracks)
        
        # 2. Match low conf detections with remaining tracks
        matched_low, unmatched_low, unmatched_tracks = self._match(low_confs, unmatched_tracks)
        
        # 3. Create new tracks for unmatched high conf detections
        for det in unmatched_high:
            self.tracks[self.next_id] = Track(
                id=self.next_id,
                bbox=det['bbox'],
                confidence=det['confidence'],
                class_name=det['class_name']
            )
            self.next_id += 1
            
        # 4. Update unmatched tracks
        for t in unmatched_tracks:
            t.unmatched_age += 1
            t.age += 1
            
        self._cleanup_tracks()
        
        return self._get_active_tracks()
        
    def _match(self, detections: List[Dict[str, Any]], tracks: List[Track]):
        if len(detections) == 0 or len(tracks) == 0:
            return [], detections, tracks
            
        cost_matrix = np.zeros((len(detections), len(tracks)), dtype=np.float32)
        for d, det in enumerate(detections):
            for t, trk in enumerate(tracks):
                cost_matrix[d, t] = 1 - iou(det['bbox'], trk.bbox)
                
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        matched_detections = []
        unmatched_detections = []
        unmatched_tracks_idx = set(range(len(tracks)))
        
        for d, t in zip(row_ind, col_ind):
            if cost_matrix[d, t] > 1 - self.iou_threshold:
                unmatched_detections.append(detections[d])
            else:
                track = tracks[t]
                det = detections[d]
                track.bbox = det['bbox']
                track.confidence = det['confidence']
                track.class_name = det['class_name']
                track.hits += 1
                track.age += 1
                track.unmatched_age = 0
                if track.hits >= self.min_hits:
                    track.active = True
                matched_detections.append(det)
                unmatched_tracks_idx.remove(t)
                
        for i in range(len(detections)):
            if i not in row_ind:
                unmatched_detections.append(detections[i])
                
        unmatched_tracks = [tracks[i] for i in unmatched_tracks_idx]
        return matched_detections, unmatched_detections, unmatched_tracks

    def _cleanup_tracks(self):
        to_delete = []
        for tid, t in self.tracks.items():
            if t.unmatched_age > self.max_age:
                to_delete.append(tid)
        for tid in to_delete:
            del self.tracks[tid]
            
    def _get_active_tracks(self):
        res = []
        for t in self.tracks.values():
            if t.active:
                res.append({
                    "track_id": t.id,
                    "bbox": t.bbox,
                    "confidence": t.confidence,
                    "class_name": t.class_name,
                    "age": t.age,
                    "hits": t.hits
                })
        return res
