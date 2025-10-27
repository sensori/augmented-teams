#!/usr/bin/env python3
"""
Base class for service-test.py files
Provides common functionality for loading URLs from config and running tests
"""

import sys
import io
import yaml  # pyright: ignore
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
    
    containerization_path = feature_path.parent / "containerization"
    sys.path.insert(0, str(containerization_path))
    
    import argparse
    from provisioner import Provisioner  # pyright: ignore
    
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
        max_attempts = 60  # Increase to 2 minutes
        for attempt in range(max_attempts):
            try:
                # Try root endpoint first (most reliable)
                response = requests.get(f"{base_url}/", timeout=10)
                if response.status_code in [200, 404, 405]:  # 404/405 means service is up but endpoint doesn't exist
                    print(f"✅ Service is ready!")
                    break
            except requests.exceptions.SSLError as e:
                # SSL errors might indicate service is still starting
                if attempt < max_attempts - 1:
                    print(f"⏳ Attempt {attempt + 1}/{max_attempts} - SSL error, waiting...")
                    time.sleep(2)
                else:
                    print(f"❌ SSL Error: {e}")
                    sys.exit(1)
            except requests.exceptions.Timeout:
                if attempt < max_attempts - 1:
                    print(f"⏳ Attempt {attempt + 1}/{max_attempts} - timeout, waiting...")
                    time.sleep(2)
                else:
                    print("❌ Service failed to respond after 2 minutes")
                    sys.exit(1)
            except requests.exceptions.ConnectionError as e:
                if attempt < max_attempts - 1:
                    print(f"⏳ Attempt {attempt + 1}/{max_attempts} - connection error: {e}")
                    time.sleep(2)
                else:
                    print(f"❌ Connection failed: {e}")
                    sys.exit(1)
            except Exception as e:
                if attempt < max_attempts - 1:
                    print(f"⏳ Attempt {attempt + 1}/{max_attempts} - error: {e}")
                    time.sleep(2)
                else:
                    print(f"❌ Service failed: {e}")
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
