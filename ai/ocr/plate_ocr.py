import logging
import numpy as np
import re
from typing import Tuple

from .config import OCRConfig
from .preprocessor import PlatePreprocessor

logger = logging.getLogger(__name__)

class PlateOCR:
    """License plate OCR using PaddleOCR (primary) or Tesseract (fallback).
    
    PaddleOCR: Apache-2.0 license
    Tesseract: Apache-2.0 license
    """
    
    def __init__(self, config: OCRConfig):
        self.config = config
        self.preprocessor = PlatePreprocessor(config)
        self.ocr = None
        self._init_engine()
    
    def _init_engine(self):
        """Initialize OCR engine."""
        if self.config.engine == 'paddleocr':
            try:
                from paddleocr import PaddleOCR
                self.ocr = PaddleOCR(use_angle_cls=True, lang=self.config.language, show_log=False)
                logger.info("PaddleOCR initialized.")
            except ImportError:
                logger.warning("PaddleOCR not available, falling back to Tesseract")
                self.config.engine = 'tesseract'
                self._init_tesseract()
        else:
            self._init_tesseract()
    
    def _init_tesseract(self):
        try:
            import pytesseract
            self.ocr = pytesseract
            logger.info("Tesseract initialized.")
        except ImportError:
            logger.error("Tesseract not available either.")
            self.ocr = None
    
    def read_plate(self, plate_image: np.ndarray) -> Tuple[str, float]:
        """Read text from plate image.
        
        Returns: (text, confidence)
        """
        if plate_image is None or plate_image.size == 0 or self.ocr is None:
            return "", 0.0
            
        # 1. Preprocess
        processed = self.preprocessor.process(plate_image)
        
        # 2. Run OCR
        if self.config.engine == 'paddleocr':
            text, conf = self._run_paddleocr(processed)
        else:
            text, conf = self._run_tesseract(processed)
            
        # 3. Normalize result
        text = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # 4. Return text + confidence
        if conf >= self.config.confidence_threshold:
            return text, conf
        return "", 0.0
    
    def _run_paddleocr(self, image: np.ndarray) -> Tuple[str, float]:
        try:
            result = self.ocr.ocr(image, cls=True)
            if not result or not result[0]:
                return "", 0.0
            
            # Get the result with highest confidence
            best_res = max(result[0], key=lambda x: x[1][1])
            return best_res[1][0], best_res[1][1]
        except Exception as e:
            logger.error(f"PaddleOCR error: {e}")
            return "", 0.0
    
    def _run_tesseract(self, image: np.ndarray) -> Tuple[str, float]:
        try:
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            data = self.ocr.image_to_data(image, config=custom_config, output_type=self.ocr.Output.DICT)
            
            texts = data['text']
            confs = data['conf']
            
            valid_texts = []
            for t, c in zip(texts, confs):
                if str(c) != '-1' and t.strip():
                    valid_texts.append((t.strip(), float(c) / 100.0))
                    
            if not valid_texts:
                return "", 0.0
                
            best_res = max(valid_texts, key=lambda x: x[1])
            return best_res[0], best_res[1]
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return "", 0.0
