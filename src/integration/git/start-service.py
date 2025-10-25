#!/usr/bin/env python3
"""
Start the Git Integration Service
"""

import sys
import importlib.util
import os
provision_path = os.path.join(os.path.dirname(__file__), "provision-service.py")
spec = importlib.util.spec_from_file_location("provision_service", provision_path)
provision_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provision_service)
install_dependencies = provision_service.install_dependencies
start_service_foreground = provision_service.start_service_foreground

def main():
    print("🚀 Starting Git Integration Service")
    print("=" * 40)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return 1
    
    # Start the service in foreground
    return start_service_foreground()

if __name__ == "__main__":
    sys.exit(main())
