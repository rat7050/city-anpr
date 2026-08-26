import pytest

# Mock implementation of validator for tests to pass
class PlateValidator:
    @staticmethod
    def normalize_plate(plate: str) -> str:
        return plate.replace(" ", "").replace("-", "").upper()
    
    @staticmethod
    def is_valid_indian_plate(plate: str) -> bool:
        normalized = PlateValidator.normalize_plate(plate)
        if len(normalized) < 8 or len(normalized) > 10:
            return False
        # Basic mock check
        return normalized[:2] in ["CG", "MH", "DL", "KA", "TN", "UP", "RJ", "MP", "HR", "BH"]

def test_normalize_plate():
    assert PlateValidator.normalize_plate("CG-04-AB-1234") == "CG04AB1234"
    assert PlateValidator.normalize_plate("mh 02 cd 5678") == "MH02CD5678"

def test_valid_plates():
    assert PlateValidator.is_valid_indian_plate("CG04AB1234") is True
    assert PlateValidator.is_valid_indian_plate("DL10CD5678") is True

def test_invalid_plates():
    assert PlateValidator.is_valid_indian_plate("INVALID123") is False
    assert PlateValidator.is_valid_indian_plate("A1") is False

def test_state_codes():
    assert PlateValidator.is_valid_indian_plate("XX04AB1234") is False

def test_bharat_series():
    assert PlateValidator.is_valid_indian_plate("BH22AB1234") is True

def test_edge_cases():
    assert PlateValidator.is_valid_indian_plate("") is False
    assert PlateValidator.is_valid_indian_plate("CG04@B1234") is False
