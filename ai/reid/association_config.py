from dataclasses import dataclass

@dataclass
class AssociationConfig:
    # Matching weights (must sum to 1.0)
    plate_match_weight: float = 0.50
    time_consistency_weight: float = 0.20
    location_distance_weight: float = 0.15
    vehicle_type_weight: float = 0.05
    vehicle_color_weight: float = 0.05
    appearance_weight: float = 0.05
    
    # Thresholds
    confirmed_threshold: float = 0.85
    probable_threshold: float = 0.65
    
    # Time constraints
    max_time_gap_minutes: float = 120.0
    min_time_gap_seconds: float = 30.0
    
    # Speed constraints
    max_speed_kmh: float = 120.0
    min_speed_kmh: float = 5.0
    
    # String matching
    max_plate_edit_distance: int = 2
