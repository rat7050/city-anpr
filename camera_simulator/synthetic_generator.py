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
    
    async def generate_demo_scenario(self):
        """Generate the full demo scenario:
        - Vehicle CG04AB1234 traverses all 4 cameras
        - Multiple other vehicles with random patterns
        - Realistic timing between cameras
        - Varied vehicle types
        """
        print("Starting demo scenario generation...")
        start_time = datetime.now(timezone.utc)
        
        tasks = []
        # Trajectory 1: CG04AB1234 moving through all 4 cameras
        tasks.append(self.generate_trajectory('CG04AB1234', self.cameras, start_time, speed_kmh=45))
        
        # Other random trajectories
        for _ in range(5):
            plate = self._random_plate()
            # Select 2 random cameras
            cam_sequence = random.sample(self.cameras, min(2, len(self.cameras)))
            delay_minutes = random.randint(1, 10)
            delayed_start = start_time + timedelta(minutes=delay_minutes)
            tasks.append(self.generate_trajectory(plate, cam_sequence, delayed_start, speed_kmh=random.uniform(30, 60)))
            
        await asyncio.gather(*tasks)
        print("Demo scenario generation complete.")
    
    async def generate_trajectory(self, plate: str, camera_sequence: list, 
                                   start_time: datetime, speed_kmh: float = 40):
        """Generate a realistic trajectory for a vehicle through cameras."""
        current_time = start_time
        vehicle_type = random.choice(self.VEHICLE_TYPES)
        vehicle_color = random.choice(self.VEHICLE_COLORS)
        
        for cam in camera_sequence:
            detection = {
                "plate_number": plate,
                "camera_id": cam.camera_id,
                "timestamp": current_time.isoformat(),
                "confidence": round(random.uniform(0.75, 0.99), 2),
                "vehicle_type": vehicle_type,
                "vehicle_color": vehicle_color,
                "direction": random.choice(self.DIRECTIONS),
                "is_synthetic": True
            }
            
            # Add a slight random delay to wait for real-world playback simulation
            # (In a real simulator, we'd sleep until current_time, but here we just send)
            await self.send_detection(detection)
            
            # Advance time for next camera (simulate travel time)
            # Roughly 2-5 minutes between cameras
            current_time += timedelta(seconds=random.randint(120, 300))
            await asyncio.sleep(1) # Small sleep to avoid overwhelming server
    
    async def send_detection(self, detection: dict):
        """Send detection to backend API."""
        headers = {}
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base_url}/api/v1/detections",
                    json=detection,
                    headers=headers
                )
                response.raise_for_status()
                print(f"Sent synthetic detection: {detection['plate_number']} at {detection['camera_id']}")
            except Exception as e:
                print(f"Error sending detection: {e}")
    
    def _random_plate(self) -> str:
        """Generate a random Indian license plate or pick from list."""
        if random.random() < 0.5:
            return random.choice(self.DEMO_PLATES)
        else:
            state = random.choice(['CG', 'MH', 'DL', 'KA', 'TN', 'UP', 'RJ', 'MP', 'HR'])
            code = f"{random.randint(1, 99):02d}"
            letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
            nums = f"{random.randint(1, 9999):04d}"
            return f"{state}{code}{letters}{nums}"
    
    async def run_continuous(self, detections_per_minute: int = 10):
        """Run continuous synthetic generation for real-time demo."""
        print(f"Running continuous synthetic generation at {detections_per_minute} req/min...")
        sleep_interval = 60.0 / detections_per_minute
        while True:
            plate = self._random_plate()
            cam = random.choice(self.cameras)
            detection = {
                "plate_number": plate,
                "camera_id": cam.camera_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "vehicle_type": random.choice(self.VEHICLE_TYPES),
                "vehicle_color": random.choice(self.VEHICLE_COLORS),
                "direction": random.choice(self.DIRECTIONS),
                "is_synthetic": True
            }
            await self.send_detection(detection)
            await asyncio.sleep(sleep_interval)
