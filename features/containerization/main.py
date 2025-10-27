#!/usr/bin/env python3
"""
Containerization Service - Core Business Logic
Routes provisioning, starting, and testing operations
"""

from pathlib import Path
from typing import Optional
import sys

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from provisioner import Provisioner

def find_repo_root(start_path: Path) -> Path:
    """Find the repository root by looking for .git or features/ directory"""
    current = start_path.resolve()
    
    # Walk up the directory tree looking for repo indicators
    while current != current.parent:
        # Check for .git directory (git repository)
        if (current / ".git").exists():
            return current
        # Check for features/ directory (our repo structure)
        if (current / "features").exists() and (current / "features" / "containerization").exists():
            return current
        current = current.parent
    
    # If no repo root found, return start_path's parent
    return start_path.parent.parent

def provision_feature(feature_name: str, mode: str = "SERVICE", always: bool = False) -> dict:
    """Provision a feature in the specified mode"""
    # Find repo root first
    repo_root = find_repo_root(Path(__file__))
    
    # Now find the feature relative to repo root
    feature_path = repo_root / "features" / feature_name
    containerization_path = repo_root / "features" / "containerization"
    
    if not feature_path.exists():
        return {"success": False, "error": f"Feature '{feature_name}' not found"}
    
    provisioner = Provisioner.create(mode, feature_path, containerization_path)
    
    try:
        result = provisioner.provision(always)
        return {
            "success": result,
            "mode": mode,
            "feature": feature_name,
            "action": "provision"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def start_feature(feature_name: str, mode: str = "SERVICE", always: bool = False) -> dict:
    """Start a feature in the specified mode"""
    # Find repo root first
    repo_root = find_repo_root(Path(__file__))
    
    # Now find the feature relative to repo root
    feature_path = repo_root / "features" / feature_name
    containerization_path = repo_root / "features" / "containerization"
    
    if not feature_path.exists():
        return {"success": False, "error": f"Feature '{feature_name}' not found"}
    
    provisioner = Provisioner.create(mode, feature_path, containerization_path)
    
    try:
        result = provisioner.start(always)
        return {
            "success": result,
            "mode": mode,
            "feature": feature_name,
            "action": "start"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_test_url(feature_name: str, mode: str = "SERVICE") -> dict:
    """Get the test URL for a feature in the specified mode"""
    # Find repo root first
    repo_root = find_repo_root(Path(__file__))
    
    # Now find the feature relative to repo root
    feature_path = repo_root / "features" / feature_name
    containerization_path = repo_root / "features" / "containerization"
    
    if not feature_path.exists():
        return {"success": False, "error": f"Feature '{feature_name}' not found"}
    
    provisioner = Provisioner.create(mode, feature_path, containerization_path)
    
    try:
        url = provisioner.get_test_url()
        return {
            "success": True,
            "mode": mode,
            "feature": feature_name,
            "url": url
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def provision_and_start(feature_name: str, mode: str = "SERVICE", always: bool = False) -> dict:
    """Provision and start a feature"""
    provision_result = provision_feature(feature_name, mode, always)
    if not provision_result.get("success"):
        return provision_result
    
    start_result = start_feature(feature_name, mode, always)
    return start_result

def provision_start_and_test(feature_name: str, mode: str = "SERVICE", always: bool = False) -> dict:
    """Full pipeline: provision, start, and test a feature"""
    # Provision and start
    start_result = provision_and_start(feature_name, mode, always)
    if not start_result.get("success"):
        return start_result
    
    # Get test URL
    url_result = get_test_url(feature_name, mode)
    if not url_result.get("success"):
        return url_result
    
    return {
        "success": True,
        "mode": mode,
        "feature": feature_name,
        "action": "provision_start_and_test",
        "url": url_result.get("url"),
        "message": f"Feature '{feature_name}' provisioned, started, and ready for testing at {url_result.get('url')}"
    }

if __name__ == "__main__":
    # Test the functions
    print("Containerization Service - Core Logic")
    print("Available functions:")
    print("  - provision_feature(feature_name, mode, always)")
    print("  - start_feature(feature_name, mode, always)")
    print("  - get_test_url(feature_name, mode)")
    print("  - provision_and_start(feature_name, mode, always)")

