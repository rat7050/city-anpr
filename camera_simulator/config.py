from dataclasses import dataclass

@dataclass
class SimulatorCamera:
    camera_id: str
    camera_name: str
    latitude: float
    longitude: float
    road_name: str
    zone: str
    video_file: str = ''  # Optional video file path

DEMO_CAMERAS = [
    SimulatorCamera('c01', 'C01 - VIP Road', 21.2514, 81.6296, 'VIP Road', 'Zone A'),
    SimulatorCamera('c08', 'C08 - Ring Road', 21.2350, 81.6100, 'Ring Road', 'Zone B'),
    SimulatorCamera('c15', 'C15 - GE Road', 21.2200, 81.5950, 'GE Road', 'Zone C'),
    SimulatorCamera('c22', 'C22 - Pandri', 21.2100, 81.6350, 'Pandri Main Road', 'Zone D'),
]
