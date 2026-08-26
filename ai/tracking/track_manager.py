from collections import Counter
from typing import Dict, List, Tuple, Any

class TrackManager:
    """Manages track lifecycle and OCR result aggregation.
    
    Associates plate OCR results with track IDs using
    multi-frame voting for robust plate identification.
    """
    
    def __init__(self, voting_window: int = 5, min_votes: int = 3):
        self.voting_window = voting_window
        self.min_votes = min_votes
        self.track_ocr_results: Dict[int, List[Tuple[str, float]]] = {}
        self.track_meta: Dict[int, Dict[str, Any]] = {}
        self.finalized_tracks: Dict[int, Dict[str, Any]] = {}
    
    def add_ocr_result(self, track_id: int, plate_text: str, confidence: float, vehicle_type: str = None):
        """Add OCR reading for a track."""
        if not plate_text:
            return
            
        if track_id not in self.track_ocr_results:
            self.track_ocr_results[track_id] = []
            self.track_meta[track_id] = {"vehicle_type": vehicle_type}
            
        self.track_ocr_results[track_id].append((plate_text, confidence))
        
        # Keep window size
        if len(self.track_ocr_results[track_id]) > self.voting_window:
            self.track_ocr_results[track_id].pop(0)
    
    def get_best_plate(self, track_id: int) -> Tuple[str, float]:
        """Multi-frame voting: most common plate text weighted by confidence."""
        if track_id not in self.track_ocr_results or not self.track_ocr_results[track_id]:
            return "", 0.0
            
        votes = Counter()
        conf_sums = Counter()
        
        for text, conf in self.track_ocr_results[track_id]:
            votes[text] += 1
            conf_sums[text] += conf
            
        best_plate = votes.most_common(1)[0][0]
        avg_conf = conf_sums[best_plate] / votes[best_plate]
        
        return best_plate, avg_conf
    
    def finalize_track(self, track_id: int) -> Dict[str, Any]:
        """Called when track ends, returns final detection event."""
        if track_id in self.finalized_tracks:
            return self.finalized_tracks[track_id]
            
        plate, conf = self.get_best_plate(track_id)
        if not plate:
            return {}
            
        meta = self.track_meta.get(track_id, {})
        
        result = {
            "track_id": track_id,
            "plate_number": plate,
            "confidence": conf,
            "vehicle_type": meta.get("vehicle_type", "unknown")
        }
        self.finalized_tracks[track_id] = result
        
        # Cleanup
        if track_id in self.track_ocr_results:
            del self.track_ocr_results[track_id]
        if track_id in self.track_meta:
            del self.track_meta[track_id]
            
        return result
    
    def is_track_ready(self, track_id: int) -> bool:
        """Check if track has enough OCR readings."""
        if track_id not in self.track_ocr_results:
            return False
        return len(self.track_ocr_results[track_id]) >= self.min_votes
