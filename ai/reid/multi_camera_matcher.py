import math
from datetime import datetime
from typing import Dict, Any, List

from .association_config import AssociationConfig

class MultiCameraMatcher:
    """Multi-Camera Vehicle Association Engine.
    
    Connects vehicle observations from different cameras using:
    - Primary: Plate number matching
    - Secondary: Time consistency, location distance, vehicle type/color
    
    Match states: CONFIRMED, PROBABLE, UNCERTAIN
    """
    
    def __init__(self, config: AssociationConfig):
        self.config = config
    
    def match(self, detection1: Dict[str, Any], detection2: Dict[str, Any]) -> Dict[str, Any]:
        """Score match between two detections from different cameras."""
        d1_plate = detection1.get('plate_number', '')
        d2_plate = detection2.get('plate_number', '')
        d1_time = detection1.get('timestamp')
        d2_time = detection2.get('timestamp')
        d1_loc = detection1.get('location', (0.0, 0.0))
        d2_loc = detection2.get('location', (0.0, 0.0))
        d1_type = detection1.get('vehicle_type', 'unknown')
        d2_type = detection2.get('vehicle_type', 'unknown')
        d1_color = detection1.get('color', 'unknown')
        d2_color = detection2.get('color', 'unknown')

        # Distance
        distance = self._haversine(d1_loc[0], d1_loc[1], d2_loc[0], d2_loc[1])
        if d1_time and d2_time:
            time_diff = abs((d2_time - d1_time).total_seconds())
        else:
            time_diff = 0

        # Calculate individual scores
        plate_score = self._plate_similarity(d1_plate, d2_plate)
        time_score = self._time_consistency(time_diff, distance)
        location_score = self._location_score(distance, time_diff)
        type_score = self._vehicle_type_score(d1_type, d2_type)
        color_score = self._color_score(d1_color, d2_color)
        
        # Weighted total
        total = (
            plate_score * self.config.plate_match_weight +
            time_score * self.config.time_consistency_weight +
            location_score * self.config.location_distance_weight +
            type_score * self.config.vehicle_type_weight +
            color_score * self.config.vehicle_color_weight
        )
        # Assuming appearance weight is not used fully if we lack features, we'll normalize
        used_weight = self.config.plate_match_weight + self.config.time_consistency_weight + \
                      self.config.location_distance_weight + self.config.vehicle_type_weight + \
                      self.config.vehicle_color_weight
        total /= used_weight

        # Classify
        if total >= self.config.confirmed_threshold:
            state = 'CONFIRMED'
        elif total >= self.config.probable_threshold:
            state = 'PROBABLE'
        else:
            state = 'UNCERTAIN'
            
        breakdown = {
            'plate_score': plate_score,
            'time_score': time_score,
            'location_score': location_score,
            'type_score': type_score,
            'color_score': color_score
        }
        
        return {'score': total, 'state': state, 'breakdown': breakdown}
    
    def find_matches(self, new_detection: Dict[str, Any], existing_detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find matching detections for a new detection."""
        results = []
        for d in existing_detections:
            match_res = self.match(new_detection, d)
            if match_res['state'] in ('CONFIRMED', 'PROBABLE'):
                match_res['matched_detection'] = d
                results.append(match_res)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def _plate_similarity(self, plate1: str, plate2: str) -> float:
        if not plate1 or not plate2:
            return 0.0
        if plate1 == plate2:
            return 1.0
        
        # Levenshtein distance
        def levenshtein(s1, s2):
            if len(s1) < len(s2):
                return levenshtein(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]
            
        dist = levenshtein(plate1, plate2)
        if dist <= self.config.max_plate_edit_distance:
            return 1.0 - (dist / float(max(len(plate1), len(plate2))))
        return 0.0
    
    def _time_consistency(self, time_diff_sec: float, distance_km: float) -> float:
        if time_diff_sec < self.config.min_time_gap_seconds:
            return 0.0
        if time_diff_sec > self.config.max_time_gap_minutes * 60:
            return 0.5 # Neutral if too long
            
        speed = (distance_km / (time_diff_sec / 3600.0)) if time_diff_sec > 0 else 0
        if self.config.min_speed_kmh <= speed <= self.config.max_speed_kmh:
            return 1.0
        return 0.2
    
    def _location_score(self, distance_km: float, time_diff_sec: float) -> float:
        if distance_km == 0.0:
            return 1.0
        expected_distance = (self.config.max_speed_kmh / 3600.0) * time_diff_sec
        if distance_km <= expected_distance:
            return 1.0
        return max(0.0, 1.0 - (distance_km / (expected_distance + 0.1)))
    
    def _vehicle_type_score(self, type1: str, type2: str) -> float:
        if type1 == 'unknown' or type2 == 'unknown':
            return 0.5
        return 1.0 if type1 == type2 else 0.0
    
    def _color_score(self, color1: str, color2: str) -> float:
        if color1 == 'unknown' or color2 == 'unknown':
            return 0.5
        return 1.0 if color1 == color2 else 0.0

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0 # Radius of the Earth in km
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance
