import cv2
import numpy as np
import logging

from .config import OCRConfig

logger = logging.getLogger(__name__)

class PlatePreprocessor:
    """Configurable image preprocessing pipeline for license plate OCR.
    
    Applies a sequence of OpenCV transformations to improve OCR accuracy.
    Not all transformations are applied — the pipeline is configurable.
    Excessive preprocessing can REDUCE OCR accuracy.
    """
    
    def __init__(self, config: OCRConfig):
        self.config = config
        self.steps = {
            'resize': self._resize,
            'grayscale': self._grayscale,
            'denoise': self._denoise,
            'clahe': self._clahe,
            'contrast': self._enhance_contrast,
            'sharpen': self._sharpen,
            'threshold': self._threshold,
            'perspective': self._perspective_correct,
        }
    
    def process(self, image: np.ndarray) -> np.ndarray:
        """Apply the configured preprocessing pipeline."""
        if image is None or image.size == 0:
            return image
            
        processed = image.copy()
        for step_name in self.config.preprocessing_steps:
            if step_name in self.steps:
                try:
                    processed = self.steps[step_name](processed)
                except Exception as e:
                    logger.warning(f"Error in preprocessing step '{step_name}': {e}")
            else:
                logger.warning(f"Unknown preprocessing step: {step_name}")
        return processed
    
    def _resize(self, image: np.ndarray) -> np.ndarray:
        """Resize maintaining aspect ratio to target height."""
        h, w = image.shape[:2]
        ratio = self.config.target_height / float(h)
        new_w = int(w * ratio)
        return cv2.resize(image, (new_w, self.config.target_height), interpolation=cv2.INTER_CUBIC)
    
    def _grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert to grayscale if not already."""
        if len(image.shape) == 3 and image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def _denoise(self, image: np.ndarray) -> np.ndarray:
        """fastNlMeansDenoising or fastNlMeansDenoisingColored."""
        if len(image.shape) == 2:
            return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    
    def _clahe(self, image: np.ndarray) -> np.ndarray:
        """CLAHE contrast enhancement."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        clahe = cv2.createCLAHE(clipLimit=self.config.clahe_clip_limit, tileGridSize=self.config.clahe_tile_size)
        res = clahe.apply(gray)
        if len(image.shape) == 3:
            return cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)
        return res
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Simple contrast/brightness adjustment."""
        alpha = 1.2 # Contrast control
        beta = 0    # Brightness control
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    def _sharpen(self, image: np.ndarray) -> np.ndarray:
        """Unsharp mask sharpening."""
        blurred = cv2.GaussianBlur(image, (self.config.sharpen_kernel_size, self.config.sharpen_kernel_size), 0)
        return cv2.addWeighted(image, self.config.sharpen_strength + 1.0, blurred, -self.config.sharpen_strength, 0)
    
    def _threshold(self, image: np.ndarray) -> np.ndarray:
        """Adaptive thresholding."""
        gray = self._grayscale(image)
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    def _perspective_correct(self, image: np.ndarray) -> np.ndarray:
        """4-point perspective correction (placeholder if simple crop)."""
        return image
