import re
from typing import Tuple

VALID_STATE_CODES = [
    "AP", "AR", "AS", "BR", "CG", "CH", "DD", "DL", "GA", "GJ", "HP", "HR", "JH",
    "JK", "KA", "KL", "LA", "LD", "MH", "ML", "MN", "MP", "MZ", "NL", "OD", "PB",
    "PY", "RJ", "SK", "TN", "TR", "TS", "UK", "UP", "WB", "BH"
]

def normalize_plate(raw: str) -> str:
    """Strip spaces, hyphens, dots and convert to uppercase."""
    if not raw:
        return ""
    normalized = re.sub(r'[\s\-\.]', '', raw).upper()
    return re.sub(r'[^A-Z0-9]', '', normalized)

def is_valid_state_code(code: str) -> bool:
    return code in VALID_STATE_CODES

def validate_indian_plate(plate: str) -> Tuple[bool, str]:
    """
    Validate against standard Indian plate pattern and BH series.
    Returns (is_valid, normalized_plate)
    """
    normalized = normalize_plate(plate)
    
    # BH Series: BH [2 digits year] [1-3 letters] [4 digits]
    bh_pattern = r'^BH\d{2}[A-Z]{1,3}\d{4}$'
    if re.match(bh_pattern, normalized):
        return True, normalized
        
    # Standard: [2 letters] [2 digits] [1-3 letters] [1-4 digits]
    # Sometime the digits part can be 1 to 4 characters
    std_pattern = r'^([A-Z]{2})\d{2}[A-Z]{1,3}\d{1,4}$'
    match = re.match(std_pattern, normalized)
    if match:
        state_code = match.group(1)
        if is_valid_state_code(state_code):
            return True, normalized
            
    return False, normalized
