#!/usr/bin/env python3
"""
Git Integration Provision Script
Tiny wrapper that calls shared containerization script
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Get feature path (parent of config folder)
    feature_path = Path(__file__).parent.parent
    
    # Call shared containerization script
    containerization_script = Path(__file__).parent.parent.parent / "containerization" / "provision-service.py"
    
    result = subprocess.run([sys.executable, str(containerization_script), str(feature_path)])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
