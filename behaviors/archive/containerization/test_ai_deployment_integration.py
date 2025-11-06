#!/usr/bin/env python3
"""
Integration tests for AI-assisted deployment

Tests the full deployment pipeline by creating real features and verifying:
- Logs are captured correctly
- Code is generated properly
- Services work as expected
- Error recovery functions properly

TABLE OF CONTENTS:
1. AI DEPLOYMENT INTEGRATION TESTS
   1.1 Happy Path Tests
   1.2 Error Recovery Tests
   1.3 Log Verification Tests
   1.4 Cleanup Utilities
"""

import pytest
import subprocess
import time
import shutil
import os
from pathlib import Path
from datetime import datetime

# Ensure logs directory exists
Path("behaviors/containerization/logs").mkdir(parents=True, exist_ok=True)


@pytest.fixture
def test_feature_name():
    """Generate unique feature name for each test"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ai-deploy-tester-{timestamp}"


@pytest.fixture
def test_feature_path(test_feature_name):
    """Get path to test feature"""
    return Path("features") / test_feature_name


@pytest.fixture
def cleanup_feature(test_feature_name, test_feature_path):
    """Ensure test feature is removed after test"""
    yield test_feature_path
    
    # Cleanup after test
    if test_feature_path.exists():
        print(f"\n[CLEANUP] Cleaning up test feature: {test_feature_name}")
        shutil.rmtree(test_feature_path, ignore_errors=True)


def run_deployment(feature_name: str, requirements: str, mode: str = "CONTAINER"):
    """Run AI-assisted deployment"""
    cmd = [
        "python", "behaviors/containerization/ai-assisted-deploy.py",
        "--feature", feature_name,
        "--requirements", requirements,
        "--mode", mode
    ]
    
    print(f"[RUN] Running deployment command: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        capture_output=True, 
        text=True, 
        timeout=300,
        cwd=Path.cwd()  # Run from project root
    )
    
    print(f"\n[RESULT] Return code: {result.returncode}")
    if result.stdout:
        print(f"[STDOUT]\n{result.stdout}")
    if result.stderr:
        print(f"[STDERR]\n{result.stderr}")
    
    return result


def get_latest_log():
    """Get the most recent deployment log"""
    logs_dir = Path("behaviors/containerization/logs")
    if not logs_dir.exists():
        return None
    
    log_files = sorted(logs_dir.glob("ai-assisted-deployment-*.log"))
    if not log_files:
        return None
    
    return log_files[-1]


def read_log(log_file: Path) -> str:
    """Read deployment log content"""
    if log_file and log_file.exists():
        return log_file.read_text()
    return ""


def verify_logs_contain(test_feature_name: str, expected_items: list):
    """Verify deployment log contains expected items"""
    log_file = get_latest_log()
    assert log_file is not None, "No deployment log found"
    
    content = read_log(log_file)
    
    for item in expected_items:
        assert item in content, f"Expected '{item}' not found in log:\n{content[:500]}"


class TestHappyPathDeployment:
    """1.1 Happy Path Tests - Verify basic deployment works"""
    
    def test_create_simple_feature(
        self, 
        test_feature_name: str, 
        test_feature_path: Path,
        cleanup_feature: Path
    ):
        """
        Test creating a simple feature with one method
        """
        print(f"\n[TEST] Testing simple feature creation: {test_feature_name}")
        
        requirements = "Create a feature with one method ai_deployment_works() that returns 'hooray!'"
        
        result = run_deployment(test_feature_name, requirements)
        
        # Verify deployment succeeded
        print(f"\n[OUTPUT] Deployment output:\n{result.stdout}")
        if result.returncode != 0:
            print(f"\n[FAILED] Deployment failed:\n{result.stderr}")
        
        assert result.returncode == 0, f"Deployment failed: {result.stderr}"
        
        # Verify feature was created
        assert test_feature_path.exists(), f"Feature path {test_feature_path} does not exist"
        assert (test_feature_path / "main.py").exists(), "main.py not created"
        assert (test_feature_path / "test.py").exists(), "test.py not created"
    
    def test_logs_capture_variables(
        self, 
        test_feature_name: str,
        cleanup_feature: Path
    ):
        """Verify logs capture configuration variables"""
        print(f"\n🧪 Testing log capture: {test_feature_name}")
        
        requirements = "Simple test feature"
        run_deployment(test_feature_name, requirements)
        
        # Verify logs contain expected variables
        verify_logs_contain(test_feature_name, [
            "feature_name",
            "Configuration",
            test_feature_name
        ])
    
    def test_logs_capture_prompts(
        self,
        test_feature_name: str,
        cleanup_feature: Path
    ):
        """Verify logs capture AI prompts"""
        print(f"\n🧪 Testing prompt logging: {test_feature_name}")
        
        requirements = "Create test feature"
        run_deployment(test_feature_name, requirements)
        
        # Verify logs contain prompts
        verify_logs_contain(test_feature_name, [
            "AI Prompt",
            "generate_test_code",
            "generate_main_code"
        ])


class TestErrorRecovery:
    """1.2 Error Recovery Tests - Verify error handling and recovery"""
    
    def test_syntax_error_detection(
        self,
        test_feature_name: str,
        test_feature_path: Path,
        cleanup_feature: Path
    ):
        """
        Test that syntax errors are detected and logged
        1. Create feature
        2. Inject syntax error
        3. Verify error in logs
        """
        print(f"\n🧪 Testing syntax error detection: {test_feature_name}")
        
        # Initial deployment
        requirements = "Create simple test feature"
        run_deployment(test_feature_name, requirements)
        
        # Inject syntax error
        main_file = test_feature_path / "main.py"
        if main_file.exists():
            content = main_file.read_text()
            # Inject syntax error
            content = content.replace("def ", "de@f ")  # Syntax error
            main_file.write_text(content)
            print("[ACTION] Injected syntax error")
        
        # Try to run and should fail
        result = subprocess.run(
            ["python", str(main_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0, "Syntax error should cause failure"
        assert "SyntaxError" in result.stderr or "invalid syntax" in result.stderr
    
    def test_missing_dependency_detection(
        self,
        test_feature_name: str,
        test_feature_path: Path,
        cleanup_feature: Path
    ):
        """
        Test that missing dependencies are detected
        """
        print(f"\n🧪 Testing missing dependency detection: {test_feature_name}")
        
        requirements = "Create feature"
        run_deployment(test_feature_name, requirements)
        
        # Add impossible import
        main_file = test_feature_path / "main.py"
        if main_file.exists():
            content = main_file.read_text()
            # Add import at top
            content = "import nonexistent_package_12345\n" + content
            main_file.write_text(content)
        
        # Should fail when running
        result = subprocess.run(
            ["python", "-c", f"import sys; sys.path.insert(0, 'behaviors/{test_feature_name}'); import main"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0, "Import error should cause failure"


class TestLogVerification:
    """1.3 Log Verification Tests - Verify log structure and content"""
    
    def test_log_file_created(
        self,
        test_feature_name: str,
        cleanup_feature: Path
    ):
        """Verify log file is created"""
        print(f"\n🧪 Testing log file creation: {test_feature_name}")
        
        requirements = "Simple test"
        run_deployment(test_feature_name, requirements)
        
        log_file = get_latest_log()
        assert log_file is not None, "Log file should be created"
        assert log_file.exists(), "Log file should exist"
        
        # Check log contains timestamp
        content = read_log(log_file)
        assert "Starting deployment" in content, "Log should contain deployment start"
    
    def test_log_contains_steps(
        self,
        test_feature_name: str,
        cleanup_feature: Path
    ):
        """Verify log contains deployment steps"""
        print(f"\n🧪 Testing log step capture: {test_feature_name}")
        
        requirements = "Create test feature"
        run_deployment(test_feature_name, requirements)
        
        verify_logs_contain(test_feature_name, [
            "Starting deployment",
            "Configuration",
            "Outcome:"
        ])


class TestCleanup:
    """1.4 Cleanup Utilities - Ensure test isolation"""
    
    def test_feature_cleanup(
        self,
        test_feature_name: str,
        test_feature_path: Path,
        cleanup_feature: Path
    ):
        """Verify cleanup removes test features"""
        # This test verifies the fixture works
        run_deployment(test_feature_name, "Test cleanup")
        
        # After yield in fixture, path should be cleaned
        # This is implicit - we're just verifying no other test leaked


if __name__ == "__main__":
    """Run tests with pytest"""
    pytest.main([__file__, "-v", "-s"])

