from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import math

class TrafficAnalyzer:
    """Traffic analytics engine."""
    
    def vehicle_count_by_interval(self, detections: List[Dict[str, Any]], interval_minutes: int) -> Dict[str, int]:
        counts = {}
        for d in detections:
            ts: datetime = d.get('timestamp')
            if not ts:
                continue
            # Round down to interval
            rounded = ts - timedelta(minutes=ts.minute % interval_minutes,
                                     seconds=ts.second,
                                     microseconds=ts.microsecond)
            key = rounded.isoformat()
            counts[key] = counts.get(key, 0) + 1
        return counts
        
    def calculate_density(self, detections: List[Dict[str, Any]], grid_size_km: float) -> List[Dict[str, Any]]:
        grids = {}
        for d in detections:
            loc = d.get('location')
            if not loc:
                continue
            lat, lon = loc
            # Rough approximation: 1 deg lat ~ 111 km, 1 deg lon ~ 111 * cos(lat) km
            lat_step = grid_size_km / 111.0
            lon_step = grid_size_km / (111.0 * math.cos(math.radians(lat)))
            
            grid_x = int(lon / lon_step)
            grid_y = int(lat / lat_step)
            
            key = (grid_x, grid_y)
            grids[key] = grids.get(key, 0) + 1
            
        return [{"grid": k, "count": v} for k, v in grids.items()]
        
    def estimate_speed(self, detection1: Dict[str, Any], detection2: Dict[str, Any]) -> float:
        """Estimate speed in km/h between two detections."""
        loc1 = detection1.get('location')
        loc2 = detection2.get('location')
        ts1 = detection1.get('timestamp')
        ts2 = detection2.get('timestamp')
        
        if not (loc1 and loc2 and ts1 and ts2):
            return 0.0
            
        distance = self._haversine(loc1[0], loc1[1], loc2[0], loc2[1])
        time_diff = abs((ts2 - ts1).total_seconds())
        
        if time_diff == 0:
            return 0.0
            
        return (distance / (time_diff / 3600.0))
        
    def congestion_score(self, current_count: int, baseline_count: int) -> Tuple[float, str]:
        """Calculate congestion score and level (PROTOTYPE THRESHOLDS)."""
        if baseline_count == 0:
            score = 1.0 if current_count > 0 else 0.0
        else:
            score = current_count / float(baseline_count)
            
        if score < 1.0:
            level = "NORMAL"
        elif score < 1.5:
            level = "MODERATE"
        elif score < 2.0:
            level = "HEAVY"
        else:
            level = "SEVERE"
            
        return score, level
        
    def aggregate_by_camera(self, detections: List[Dict[str, Any]]) -> Dict[str, int]:
        counts = {}
        for d in detections:
            cam = d.get('camera_id', 'unknown')
            counts[cam] = counts.get(cam, 0) + 1
        return counts
        
    def aggregate_by_zone(self, detections: List[Dict[str, Any]]) -> Dict[str, int]:
        counts = {}
        for d in detections:
            zone = d.get('zone_id', 'unknown')
            counts[zone] = counts.get(zone, 0) + 1
        return counts

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0 
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
