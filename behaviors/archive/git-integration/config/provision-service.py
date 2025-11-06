#!/usr/bin/env python3
"""
Provisions the git-integration feature
This calls the shared containerization scripts
"""

import subprocess
import sys
from pathlib import Path

def main():
    feature_path = Path(__file__).parent.parent
    containerization_path = Path(__file__).parent.parent.parent / "containerization"
    
    print(f"Provisioning {feature_path.name}...")
    
    # Step 1: Inject configuration
    result = subprocess.run([
        sys.executable, 
        str(containerization_path / "inject-config.py"),
        str(feature_path)
    ])
    if result.returncode != 0:
        return 1
    
    # Step 2: Run shared provisioning
    result = subprocess.run([
        sys.executable,
        str(containerization_path / "provision-service.py"), 
        str(feature_path)
    ])
    if result.returncode != 0:
        return 1
    
    print(f"SUCCESS: {feature_path.name} provisioned and deployed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
