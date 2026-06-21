import pytest
from app.routes.calculator import calculate_power

def test_calculate_power_valid_integers():
    # Test with typical integer values
    # (0.5 * 10**3) + (0.8 * 100) = 500 + 80 = 580
    assert calculate_power(10, 100) == pytest.approx(580.0)

def test_calculate_power_valid_floats():
    # Test with floating-point values
    # (0.5 * 12.5**3) + (0.8 * 75.5) = (0.5 * 1953.125) + 60.4 = 976.5625 + 60.4 = 1036.9625
    assert calculate_power(12.5, 75.5) == pytest.approx(1036.9625)

def test_calculate_power_zero_inputs():
    # Test with zero values
    assert calculate_power(0, 0) == pytest.approx(0.0)
    # (0.5 * 0**3) + (0.8 * 50) = 40
    assert calculate_power(0, 50) == pytest.approx(40.0)
    # (0.5 * 10**3) + (0.8 * 0) = 500
    assert calculate_power(10, 0) == pytest.approx(500.0)

def test_calculate_power_negative_inputs():
    # Test with negative inputs. The formula should still calculate a value.
    # (0.5 * (-5)**3) + (0.8 * -20) = (0.5 * -125) + (-16) = -62.5 - 16 = -78.5
    assert calculate_power(-5, -20) == pytest.approx(-78.5)

def test_calculate_power_invalid_string_input():
    # Test with non-numeric string input
    assert calculate_power("abc", 100) is None
    assert calculate_power(10, "xyz") is None
    assert calculate_power("abc", "xyz") is None

def test_calculate_power_empty_string_input():
    # Test with empty string input
    assert calculate_power("", 100) is None
    assert calculate_power(10, "") is None

def test_calculate_power_none_input():
    # Test with None input
    assert calculate_power(None, 100) is None
    assert calculate_power(10, None) is None
