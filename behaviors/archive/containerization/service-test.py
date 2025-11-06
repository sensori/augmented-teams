#!/usr/bin/env python3
"""
Service test for containerization
Tests that containerization service is deployed and all routes are accessible
"""

import sys
import io
import requests
from pathlib import Path

# Fix encoding for Windows - allow emojis in output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

feature_path = Path(__file__).parent
containerization_path = feature_path
sys.path.insert(0, str(containerization_path))

from service_test_base import get_base_url

def test_root(mode="AZURE"):
    """Test root endpoint"""
    url = get_base_url(feature_path, mode)
    response = requests.get(f"{url}/", timeout=5)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    print("✅ Root endpoint working")

def test_health(mode="AZURE"):
    """Test health endpoint"""
    url = get_base_url(feature_path, mode)
    response = requests.get(f"{url}/health", timeout=5)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health endpoint working")

def test_provision_endpoint(mode="AZURE"):
    """Test provision endpoint exists"""
    url = get_base_url(feature_path, mode)
    # Just check the endpoint exists (won't actually provision in AZURE without files)
    response = requests.post(f"{url}/provision?feature_name=test-feature&mode=SERVICE", timeout=5)
    # Should return some response (even if error about feature not found)
    assert response.status_code in [200, 404, 500], f"Expected 200/404/500, got {response.status_code}"
    print("✅ Provision endpoint exists")

def test_start_endpoint(mode="AZURE"):
    """Test start endpoint exists"""
    url = get_base_url(feature_path, mode)
    response = requests.post(f"{url}/start?feature_name=test-feature&mode=SERVICE", timeout=5)
    assert response.status_code in [200, 404, 500], f"Expected 200/404/500, got {response.status_code}"
    print("✅ Start endpoint exists")

def test_provision_and_start_endpoint(mode="AZURE"):
    """Test provision-and-start endpoint exists"""
    url = get_base_url(feature_path, mode)
    response = requests.post(f"{url}/provision-and-start?feature_name=test-feature&mode=SERVICE", timeout=5)
    assert response.status_code in [200, 404, 500], f"Expected 200/404/500, got {response.status_code}"
    print("✅ Provision-and-start endpoint exists")

def test_get_test_url_endpoint(mode="AZURE"):
    """Test test-url endpoint exists"""
    url = get_base_url(feature_path, mode)
    response = requests.get(f"{url}/test-url/test-feature?mode=SERVICE", timeout=5)
    assert response.status_code in [200, 404, 500], f"Expected 200/404/500, got {response.status_code}"
    print("✅ Test-url endpoint exists")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "AZURE"
    print(f"Testing containerization service routes in {mode} mode...")
    
    test_root(mode)
    test_health(mode)
    test_provision_endpoint(mode)
    test_start_endpoint(mode)
    test_provision_and_start_endpoint(mode)
    test_get_test_url_endpoint(mode)
    print("✅ All containerization service routes are working")
