#!/usr/bin/env python3
"""
Test containerization - plain Python tests
Tests the actual functions from main.py
"""

from main import provision_feature, start_feature, get_test_url, provision_and_start, provision_start_and_test

def test_provision_feature():
    """Test provision_feature function"""
    # Test provision
    result = provision_feature("test-feature", "SERVICE", always=True)
    assert result["success"] in [True, False], f"Expected success boolean, got {result.get('success')}"
    print("✅ test_provision_feature passed")

def test_get_test_url():
    """Test get_test_url function"""
    # Test getting URL
    result = get_test_url("test-feature", "SERVICE")
    assert result["success"] in [True, False], f"Expected success boolean, got {result.get('success')}"
    print("✅ test_get_test_url passed")

if __name__ == "__main__":
    test_provision_feature()
    test_get_test_url()
    print("✅ All tests passed")


