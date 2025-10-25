#!/usr/bin/env python3
"""
Shared Provisioning Script
Performs complete provisioning for any feature

Usage: python src/features/containerization/provision-service.py src/features/[feature-name]
"""

import subprocess
import sys
import time
import requests
import yaml
from pathlib import Path

def load_config(feature_path):
    """Load centralized configuration from feature's config/config.yaml"""
    config_file = feature_path / "config" / "config.yaml"
    if not config_file.exists():
        print(f"❌ Error: config/config.yaml not found in {feature_path}")
        return None
    
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return result
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return None

def validate_environment(feature_path):
    """Validate system environment and prerequisites"""
    print("🔍 Validating environment...")
    
    # Check Python version (3.8+)
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check required files exist
    required_files = [
        "main.py",
        "config/config.yaml", 
        "requirements.txt",
        "test-service.py"
    ]
    
    for file_path in required_files:
        if not (feature_path / file_path).exists():
            print(f"❌ Required file missing: {file_path}")
            return False
    
    print("✅ Environment validation passed")
    return True

def install_dependencies(feature_path):
    """Install dependencies from requirements.txt"""
    print("📦 Installing dependencies...")
    
    requirements_file = feature_path / "requirements.txt"
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    result = run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
    
    if result and result.returncode == 0:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Dependency installation failed")
        return False

def setup_service_configuration(feature_path):
    """Setup service configuration and validate modules"""
    print("⚙️ Setting up service configuration...")
    
    # Test module imports
    try:
        # Change to feature directory and test imports
        result = run_command([sys.executable, "-c", "import main"], cwd=feature_path)
        if result and result.returncode == 0:
            print("✅ Module imports validated")
            return True
        else:
            print("❌ Module import validation failed")
            return False
    except Exception as e:
        print(f"❌ Configuration setup failed: {e}")
        return False

def run_tests(feature_path):
    """Run the comprehensive test suite"""
    print("🧪 Running test suite...")
    
    test_file = feature_path / "test-service.py"
    if not test_file.exists():
        print("❌ test-service.py not found")
        return False
    
    result = run_command([sys.executable, str(test_file)], cwd=feature_path)
    
    if result and result.returncode == 0:
        print("✅ All tests passed")
        return True
    else:
        print("❌ Tests failed")
        return False

def production_readiness_check(feature_path):
    """Perform production readiness validation"""
    print("🚀 Production readiness check...")
    
    config = load_config(feature_path)
    if not config:
        return False
    
    # Start service in background
    print("Starting service for testing...")
    service_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=feature_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Wait for service to start
        time.sleep(5)
        
        # Test health endpoint
        service_url = config['service']['url']
        health_path = config['health_check']['path']
        
        try:
            response = requests.get(f"{service_url}{health_path}", timeout=10)
            if response.status_code == 200:
                print("✅ Service health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    finally:
        # Clean up service process
        service_process.terminate()
        service_process.wait()

def main():
    """Main provisioning function"""
    if len(sys.argv) != 2:
        print("Usage: python provision-service.py <feature-path>")
        print("Example: python provision-service.py src/features/vector-search")
        sys.exit(1)
    
    feature_path = Path(sys.argv[1])
    
    if not feature_path.exists():
        print(f"❌ Error: Feature path {feature_path} does not exist")
        sys.exit(1)
    
    print(f"🚀 Provisioning {feature_path.name}...")
    print("=" * 60)
    
    # Step 1: Validate environment
    if not validate_environment(feature_path):
        print("❌ Environment validation failed")
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not install_dependencies(feature_path):
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Step 3: Setup service configuration
    if not setup_service_configuration(feature_path):
        print("❌ Service configuration failed")
        sys.exit(1)
    
    # Step 4: Run tests
    if not run_tests(feature_path):
        print("❌ Tests failed")
        sys.exit(1)
    
    # Step 5: Production readiness check
    if not production_readiness_check(feature_path):
        print("❌ Production readiness check failed")
        sys.exit(1)
    
    print("🎉 Provisioning completed successfully!")
    print(f"✅ {feature_path.name} is ready for deployment")

if __name__ == "__main__":
    main()
