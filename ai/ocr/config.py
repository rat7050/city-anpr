from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class OCRConfig:
    engine: str = 'paddleocr'  # 'paddleocr' or 'tesseract'
    language: str = 'en'
    confidence_threshold: float = 0.6
    
    # Preprocessing pipeline (order matters, not all applied)
    preprocessing_steps: List[str] = field(default_factory=lambda: [
        'resize', 'grayscale', 'denoise', 'clahe', 'sharpen'
    ])
    
    # Resize
    target_height: int = 64
    target_width: int = 200
    
    # CLAHE
    clahe_clip_limit: float = 2.0
    clahe_tile_size: Tuple[int, int] = (8, 8)
    
    # Sharpening
    sharpen_kernel_size: int = 3
    sharpen_strength: float = 1.5
    
    # Multi-frame voting
    voting_window: int = 5
    min_votes: int = 3
