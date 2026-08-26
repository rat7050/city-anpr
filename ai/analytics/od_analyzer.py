import numpy as np
from typing import List, Dict, Any, Tuple
import math

class ODAnalyzer:
    """Origin-Destination analysis."""
    
    def build_od_matrix(self, trajectories: List[List[Dict[str, Any]]], zones: List[str]) -> np.ndarray:
        """Build OD matrix (rows: origin, cols: dest). No PII exposed."""
        matrix = np.zeros((len(zones), len(zones)), dtype=int)
        zone_to_idx = {z: i for i, z in enumerate(zones)}
        
        for trajectory in trajectories:
            if len(trajectory) >= 2:
                origin_d = trajectory[0]
                dest_d = trajectory[-1]
                
                o_zone = origin_d.get('zone_id')
                d_zone = dest_d.get('zone_id')
                
                if o_zone in zone_to_idx and d_zone in zone_to_idx:
                    matrix[zone_to_idx[o_zone]][zone_to_idx[d_zone]] += 1
                    
        return matrix
        
    def get_top_routes(self, od_matrix: np.ndarray, zones: List[str], n: int = 10) -> List[Tuple[str, str, int]]:
        routes = []
        for i in range(len(zones)):
            for j in range(len(zones)):
                count = int(od_matrix[i, j])
                if count > 0:
                    routes.append((zones[i], zones[j], count))
                    
        routes.sort(key=lambda x: x[2], reverse=True)
        return routes[:n]
        
    def get_zone_for_camera(self, camera_lat: float, camera_lon: float, zone_definitions: Dict[str, Dict[str, float]]) -> str:
        """Find closest zone center for camera."""
        best_zone = "unknown"
        min_dist = float('inf')
        
        for zone_id, center in zone_definitions.items():
            dist = self._haversine(camera_lat, camera_lon, center['lat'], center['lon'])
            if dist < min_dist:
                min_dist = dist
                best_zone = zone_id
                
        return best_zone

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0 
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
