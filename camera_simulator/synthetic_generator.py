import asyncio
import random
import uuid
from datetime import datetime, timezone, timedelta
import httpx

class SyntheticGenerator:
    """Generates realistic synthetic detection events for demo purposes.
    
    This produces DEMO/SYNTHETIC data clearly separated from production data.
    All generated data is labeled as synthetic.
    """
    
    DEMO_PLATES = [
        'CG04AB1234', 'CG04CD5678', 'CG07EF9012', 'CG10GH3456',
        'MH02AB1234', 'DL01CD5678', 'KA03EF9012', 'TN04GH3456',
        'UP16JK7890', 'RJ14LM2345', 'MP09NP6789', 'HR26QR0123',
    ]
    
    VEHICLE_TYPES = ['car', 'motorcycle', 'bus', 'truck', 'auto-rickshaw']
    VEHICLE_COLORS = ['white', 'black', 'silver', 'red', 'blue', 'grey']
    DIRECTIONS = ['north', 'south', 'east', 'west']
    
    def __init__(self, cameras: list, api_base_url: str = 'http://localhost:8000', token: str = None):
        self.cameras = cameras
        self.api_base_url = api_base_url
        self.token = token
        self.real_cameras = []
    
    async def init_cameras(self):
        """Fetch camera list from API if available to use real database IDs."""
        headers = {}
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{self.api_base_url}/api/cameras/", headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    self.real_cameras = data.get("cameras", [])
        except Exception as e:
            print(f"Could not load cameras from API: {e}")
    
    async def generate_demo_scenario(self):
        """Generate the full demo scenario:
        - Vehicle CG04AB1234 traverses all cameras
        - Multiple other vehicles with random patterns
        - Realistic timing between cameras
        - Varied vehicle types
        """
        await self.init_cameras()
        cams_to_use = self.real_cameras if self.real_cameras else self.cameras
        if not cams_to_use:
            print("No cameras available.")
            return

        print(f"Starting demo scenario generation across {len(cams_to_use)} cameras...")
        start_time = datetime.now(timezone.utc)
        
        # Trajectory 1: CG04AB1234 moving sequentially through all cameras
        await self.generate_trajectory('CG04AB1234', cams_to_use, start_time, speed_kmh=45)
        
        # Other random trajectories
        for _ in range(4):
            plate = self._random_plate()
            cam_sequence = random.sample(cams_to_use, min(2, len(cams_to_use)))
            delay_minutes = random.randint(1, 10)
            delayed_start = start_time + timedelta(minutes=delay_minutes)
            await self.generate_trajectory(plate, cam_sequence, delayed_start, speed_kmh=random.uniform(30, 60))
            
        print("Demo scenario generation complete.")
    
    async def generate_trajectory(self, plate: str, camera_sequence: list, 
                                   start_time: datetime, speed_kmh: float = 40):
        """Generate a realistic trajectory for a vehicle through cameras."""
        current_time = start_time
        vehicle_type = random.choice(self.VEHICLE_TYPES)
        
        for cam in camera_sequence:
            cam_id = cam.get("id") if isinstance(cam, dict) else cam.camera_id
            lat = cam.get("latitude") if isinstance(cam, dict) else cam.latitude
            lon = cam.get("longitude") if isinstance(cam, dict) else cam.longitude
            
            detection = {
                "camera_id": str(cam_id),
                "plate_number": plate,
                "timestamp": current_time.isoformat(),
                "ocr_confidence": round(random.uniform(0.85, 0.99), 2),
                "latitude": lat,
                "longitude": lon,
                "vehicle_type": vehicle_type,
                "direction": random.choice(self.DIRECTIONS),
                "speed": round(speed_kmh, 1)
            }
            
            await self.send_detection(detection)
            current_time += timedelta(minutes=random.randint(2, 5))
            await asyncio.sleep(0.5)
    
    async def send_detection(self, detection: dict):
        """Send detection to backend API."""
        headers = {}
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base_url}/api/detections/",
                    json=detection,
                    headers=headers
                )
                response.raise_for_status()
                print(f"[SIMULATOR] Detection recorded: {detection['plate_number']} at Camera {str(detection['camera_id'])[:8]} (Speed: {detection['speed']} km/h)")
            except Exception as e:
                print(f"[SIMULATOR] Error sending detection: {e}")
    
    def _random_plate(self) -> str:
        """Generate a random Indian license plate."""
        if random.random() < 0.4:
            return random.choice(self.DEMO_PLATES)
        state = random.choice(['CG', 'MH', 'DL', 'KA', 'TN', 'UP', 'RJ', 'MP', 'HR'])
        code = f"{random.randint(1, 99):02d}"
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
        nums = f"{random.randint(1000, 9999)}"
        return f"{state}{code}{letters}{nums}"
    
    async def run_continuous(self, detections_per_minute: int = 10):
        """Run continuous synthetic generation for real-time demo."""
        await self.init_cameras()
        cams_to_use = self.real_cameras if self.real_cameras else self.cameras
        print(f"Running continuous synthetic generation at {detections_per_minute} req/min...")
        sleep_interval = 60.0 / detections_per_minute
        while True:
            plate = self._random_plate()
            cam = random.choice(cams_to_use)
            cam_id = cam.get("id") if isinstance(cam, dict) else cam.camera_id
            lat = cam.get("latitude") if isinstance(cam, dict) else cam.latitude
            lon = cam.get("longitude") if isinstance(cam, dict) else cam.longitude
            
            detection = {
                "camera_id": str(cam_id),
                "plate_number": plate,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ocr_confidence": round(random.uniform(0.75, 0.99), 2),
                "latitude": lat,
                "longitude": lon,
                "vehicle_type": random.choice(self.VEHICLE_TYPES),
                "direction": random.choice(self.DIRECTIONS),
                "speed": round(random.uniform(25, 75), 1)
            }
            await self.send_detection(detection)
            await asyncio.sleep(sleep_interval)
