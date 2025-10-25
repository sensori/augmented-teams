#!/usr/bin/env python3
"""
Start the Git Integration Service
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    print("🚀 Starting Git Integration Service")
    print("=" * 40)
    
    # Change to the feature directory
    feature_dir = Path(__file__).parent
    
    try:
        # Start the service directly
        print("Starting service...")
        subprocess.run([sys.executable, "main.py"], cwd=feature_dir, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Service failed to start: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
        return 0

if __name__ == "__main__":
    sys.exit(main())
