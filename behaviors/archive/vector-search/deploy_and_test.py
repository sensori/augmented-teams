#!/usr/bin/env python3
"""
Comprehensive deployment and testing script for vector search system.

This script:
1. Stops and starts the Codespace server
2. Runs all tests and confirms they pass
3. Reindexes to create the database
4. Tests all connections and services
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path
from typing import List, Tuple

# Configuration
REPO_PATH = Path(__file__).resolve().parents[3]  # augmented-teams/
VECTOR_SEARCH_PATH = REPO_PATH / "src" / "features" / "vector-search"
SERVER_URL = "https://psychic-goggles-vx5qxgprpcww4p-8000.app.github.dev"
LOCAL_SERVER_URL = "http://127.0.0.1:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(message: str, status: str = "INFO"):
    """Print colored status messages"""
    color = Colors.BLUE
    if status == "SUCCESS":
        color = Colors.GREEN
    elif status == "ERROR":
        color = Colors.RED
    elif status == "WARNING":
        color = Colors.YELLOW
    
    print(f"{color}[{status}]{Colors.END} {message}")

def run_command(command: str, cwd: Path = None) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        print_status(f"Running: {command}")
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print_status(f"✅ Command succeeded", "SUCCESS")
            return True, result.stdout
        else:
            print_status(f"❌ Command failed: {result.stderr}", "ERROR")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print_status(f"❌ Command timed out", "ERROR")
        return False, "Command timed out"
    except Exception as e:
        print_status(f"❌ Command error: {e}", "ERROR")
        return False, str(e)

def install_dependencies():
    """Install required dependencies"""
    print_status("📦 Installing dependencies...")
    
    success, output = run_command(
        "pip install -r requirements.txt",
        cwd=VECTOR_SEARCH_PATH
    )
    
    if not success:
        print_status("❌ Failed to install dependencies", "ERROR")
        print_status(f"Dependency installation output: {output}", "ERROR")
        return False
    
    print_status("✅ Dependencies installed successfully!", "SUCCESS")
    return True

def stop_server():
    """Stop any running server processes"""
    print_status("🛑 Stopping existing server processes...")
    
    # Kill any Python processes on port 8000
    commands = [
        "netstat -ano | findstr :8000",
        "taskkill /F /IM python.exe 2>nul || echo No Python processes to kill"
    ]
    
    for cmd in commands:
        run_command(cmd)
    
    time.sleep(2)

def start_server():
    """Start the FastAPI server"""
    print_status("🚀 Starting FastAPI server...")
    
    # Start server in background
    success, output = run_command(
        "python -m uvicorn api:app --reload --port 8000",
        cwd=VECTOR_SEARCH_PATH
    )
    
    if not success:
        print_status("❌ Failed to start server", "ERROR")
        return False
    
    # Wait for server to start
    print_status("⏳ Waiting for server to start...")
    time.sleep(5)
    
    return True

def run_tests():
    """Run all tests and confirm they pass"""
    print_status("🧪 Running all tests...")
    
    success, output = run_command(
        "python test_setup.py",
        cwd=VECTOR_SEARCH_PATH
    )
    
    if not success:
        print_status("❌ Tests failed!", "ERROR")
        print_status(f"Test output: {output}", "ERROR")
        return False
    
    print_status("✅ All tests passed!", "SUCCESS")
    return True

def reindex_database():
    """Reindex to create/update the database"""
    print_status("📚 Reindexing database...")
    
    success, output = run_command(
        "python vector_search.py index",
        cwd=VECTOR_SEARCH_PATH
    )
    
    if not success:
        print_status("❌ Indexing failed!", "ERROR")
        print_status(f"Indexing output: {output}", "ERROR")
        return False
    
    print_status("✅ Database indexed successfully!", "SUCCESS")
    return True

def test_endpoint(url: str, endpoint: str, expected_status: int = 200) -> bool:
    """Test a specific endpoint"""
    try:
        full_url = f"{url}{endpoint}"
        print_status(f"🔍 Testing: {full_url}")
        
        response = requests.get(full_url, timeout=10)
        
        if response.status_code == expected_status:
            print_status(f"✅ {endpoint} - Status: {response.status_code}", "SUCCESS")
            return True
        else:
            print_status(f"❌ {endpoint} - Expected: {expected_status}, Got: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ {endpoint} - Error: {e}", "ERROR")
        return False

def test_search_functionality():
    """Test search functionality"""
    print_status("🔍 Testing search functionality...")
    
    test_queries = [
        "augmented teams",
        "AI transformation",
        "agile methodologies"
    ]
    
    all_passed = True
    
    for query in test_queries:
        success = test_endpoint(SERVER_URL, f"/search?query={query}")
        if not success:
            all_passed = False
    
    # Test enhanced search
    success = test_endpoint(SERVER_URL, "/search-detailed?query=augmented teams")
    if not success:
        all_passed = False
    
    return all_passed

def test_file_operations():
    """Test file operations"""
    print_status("📁 Testing file operations...")
    
    endpoints = [
        "/files",
        "/files?path=assets",
        "/files?path=instructions",
        "/stats"
    ]
    
    all_passed = True
    
    for endpoint in endpoints:
        success = test_endpoint(SERVER_URL, endpoint)
        if not success:
            all_passed = False
    
    return all_passed

def test_all_services():
    """Test all connections and services"""
    print_status("🔧 Testing all services...")
    
    # Test basic endpoints
    basic_tests = [
        ("/", 200),
        ("/health", 200),
        ("/docs", 200)
    ]
    
    all_passed = True
    
    for endpoint, expected_status in basic_tests:
        success = test_endpoint(SERVER_URL, endpoint, expected_status)
        if not success:
            all_passed = False
    
    # Test search functionality
    if not test_search_functionality():
        all_passed = False
    
    # Test file operations
    if not test_file_operations():
        all_passed = False
    
    return all_passed

def main():
    """Main deployment and testing workflow"""
    print_status("🚀 Starting comprehensive deployment and testing...")
    
    # Change to vector search directory
    os.chdir(VECTOR_SEARCH_PATH)
    
    # Step 1: Install dependencies
    print_status("=" * 60)
    print_status("STEP 1: Installing dependencies")
    print_status("=" * 60)
    
    if not install_dependencies():
        print_status("❌ Dependency installation failed! Stopping deployment.", "ERROR")
        sys.exit(1)
    
    # Step 2: Stop existing server
    stop_server()
    
    # Step 3: Run all tests
    print_status("=" * 60)
    print_status("STEP 2: Running all tests")
    print_status("=" * 60)
    
    if not run_tests():
        print_status("❌ Tests failed! Stopping deployment.", "ERROR")
        sys.exit(1)
    
    # Step 4: Start server
    print_status("=" * 60)
    print_status("STEP 3: Starting server")
    print_status("=" * 60)
    
    if not start_server():
        print_status("❌ Failed to start server! Stopping deployment.", "ERROR")
        sys.exit(1)
    
    # Step 5: Reindex database
    print_status("=" * 60)
    print_status("STEP 4: Reindexing database")
    print_status("=" * 60)
    
    if not reindex_database():
        print_status("❌ Database indexing failed! Stopping deployment.", "ERROR")
        sys.exit(1)
    
    # Step 6: Test all services
    print_status("=" * 60)
    print_status("STEP 5: Testing all services")
    print_status("=" * 60)
    
    if not test_all_services():
        print_status("❌ Service tests failed!", "ERROR")
        sys.exit(1)
    
    # Success!
    print_status("=" * 60)
    print_status("🎉 DEPLOYMENT SUCCESSFUL!", "SUCCESS")
    print_status("=" * 60)
    print_status(f"✅ Server running at: {SERVER_URL}")
    print_status("✅ All tests passed")
    print_status("✅ Database indexed")
    print_status("✅ All services tested")
    print_status("=" * 60)
    print_status("🚀 Ready for GPT Action integration!")

if __name__ == "__main__":
    main()
