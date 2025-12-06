#!/usr/bin/env python3
"""Test Azure deployment for test-feature"""

import sys
from pathlib import Path

if __name__ == "__main__":
    feature_path = Path(__file__).parent.parent
    containerization_path = feature_path.parent.parent / "containerization"
    
    sys.path.insert(0, str(containerization_path))
    from provisioner import Provisioner
    
    print("🧪 Testing AZURE deployment...")
    
    provisioner = Provisioner.create('AZURE', feature_path, containerization_path)
    
    # Provision (generates Dockerfile)
    if not provisioner.provision(always=True):
        print("❌ Provisioning failed")
        sys.exit(1)
    
    # Start (deploys to Azure)
    if not provisioner.start(always=True):
        print("❌ Deployment failed")
        sys.exit(1)
    
    print("✅ AZURE deployment successful!")



