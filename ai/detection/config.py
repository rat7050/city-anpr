from dataclasses import dataclass, field

@dataclass
class DetectionConfig:
    # Vehicle detection
    vehicle_model_path: str = 'yolov8n.pt'
    vehicle_confidence: float = 0.5
    vehicle_iou: float = 0.45
    vehicle_classes: list[int] = field(default_factory=lambda: [2, 3, 5, 7])  # car, motorcycle, bus, truck in COCO
    vehicle_class_names: dict[int, str] = field(default_factory=lambda: {
        2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'
    })
    
    # Plate detection
    plate_model_path: str = 'models/plate_detector.pt'  # Custom trained or downloaded
    plate_confidence: float = 0.4
    plate_iou: float = 0.3
    
    # General
    device: str = 'cpu'  # 'cpu' or 'cuda' or 'cuda:0'
    input_size: int = 640
    half_precision: bool = False  # FP16 for GPU
    max_detections: int = 50
