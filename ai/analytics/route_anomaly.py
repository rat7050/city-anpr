from typing import List, Dict, Any, Tuple

class RouteAnomalyDetector:
    """Route anomaly detection based on camera sequence patterns."""
    
    def build_baseline(self, historical_trajectories: List[List[Dict[str, Any]]]) -> Dict[Tuple[str, str], List[List[str]]]:
        """Build dictionary of common routes: (origin, dest) -> list of camera sequences."""
        baseline = {}
        for trajectory in historical_trajectories:
            if len(trajectory) < 2:
                continue
                
            cams = [d.get('camera_id') for d in trajectory if d.get('camera_id')]
            if len(cams) < 2:
                continue
                
            o, d = cams[0], cams[-1]
            key = (o, d)
            if key not in baseline:
                baseline[key] = []
            
            baseline[key].append(cams)
        return baseline
        
    def detect_anomaly(self, trajectory: List[Dict[str, Any]], baseline: Dict[Tuple[str, str], List[List[str]]]) -> Tuple[bool, float, str]:
        """Compare camera sequence against known patterns.
        
        Returns: (is_anomaly, anomaly_score, reason)
        DECISION-SUPPORT signal, not definitive evidence.
        """
        cams = [d.get('camera_id') for d in trajectory if d.get('camera_id')]
        if len(cams) < 3:
            return False, 0.0, "Trajectory too short for anomaly detection"
            
        o, d = cams[0], cams[-1]
        key = (o, d)
        
        if key not in baseline or not baseline[key]:
            return True, 1.0, "Unknown origin-destination pair"
            
        max_sim = 0.0
        for base_route in baseline[key]:
            sim = self._jaccard(cams, base_route)
            if sim > max_sim:
                max_sim = sim
                
        anomaly_score = 1.0 - max_sim
        is_anomaly = anomaly_score > 0.7  # PROTOTYPE THRESHOLD
        
        reason = f"Low route similarity ({max_sim:.2f}) compared to historical patterns" if is_anomaly else "Normal route"
        return is_anomaly, anomaly_score, reason
        
    def _jaccard(self, list1: List[str], list2: List[str]) -> float:
        set1, set2 = set(list1), set(list2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        if union == 0:
            return 0.0
        return intersection / float(union)
