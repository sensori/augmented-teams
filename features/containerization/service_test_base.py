#!/usr/bin/env python3
"""
Base class for service-test.py files
Provides common functionality for loading URLs from config and running tests
"""

import sys
import io
import yaml
import time
import requests
from pathlib import Path

# Fix encoding for Windows - allow emojis in output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

def get_base_url(feature_path, mode=None):
    """Get base URL from config based on mode"""
    # Use global mode if not explicitly provided
    if mode is None:
        mode = _mode
    
    config_file = feature_path / "config" / "feature-config.yaml"
    
    if not config_file.exists():
        return 'http://localhost:8000'  # fallback
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    if mode == 'AZURE':
        return config.get('environment', {}).get('production', {}).get('url', 'http://localhost:8000')
    else:  # SERVICE or CONTAINER - both use development URL (local)
        return config.get('environment', {}).get('development', {}).get('url', 'http://localhost:8000')

# Global mode variable for get_base_url
_mode = 'SERVICE'

def run_service_tests(test_functions):
    """Common runner for service tests"""
    global _mode
    
    # Get feature_path from the caller's file
    import inspect
    caller_frame = inspect.currentframe().f_back
    caller_file = Path(caller_frame.f_globals['__file__'])
    feature_path = caller_file.parent
    
    containerization_path = feature_path.parent.parent / "containerization"
    sys.path.insert(0, str(containerization_path))
    
    import argparse
    from provisioner import Provisioner
    
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['SERVICE', 'CONTAINER', 'AZURE'])
    parser.add_argument('--always-provision', action='store_true')
    args = parser.parse_args()
    
    # Store mode globally
    _mode = args.mode
    
    # Provision and start (skip for AZURE since it's already deployed)
    if args.mode == 'AZURE':
        print("ℹ️  AZURE mode - skipping local provision/start, using production URL")
        # Wait for service to be ready
        base_url = get_base_url(feature_path, args.mode)
        print(f"⏳ Waiting for service at {base_url} to be ready...")
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{base_url}/hello?name=HealthCheck", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Service is ready!")
                    break
            except:
                if attempt < max_attempts - 1:
                    print(f"⏳ Attempt {attempt + 1}/{max_attempts} - waiting for service...")
                    time.sleep(2)
                else:
                    print("❌ Service failed to become ready after 60 seconds")
                    sys.exit(1)
    else:
        provisioner = Provisioner.create(args.mode, feature_path, containerization_path)
        if not provisioner.provision(args.always_provision):
            sys.exit(1)
        if not provisioner.start(args.always_provision):
            sys.exit(1)
    
    # Run all test functions
    for test_func in test_functions:
        test_func()
    
    print("✅ All service tests passed")
