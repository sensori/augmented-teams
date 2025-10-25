#!/usr/bin/env python3
"""
Git Integration Service Test Suite

Tests all endpoints and functionality of the Git Integration Service.
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path
import tempfile
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SERVICE_URL = os.getenv("CODESPACE_URL", "http://localhost:8001")
SERVICE_TIMEOUT = 30
TEST_FILE_CONTENT = "# Test Document\nThis is a test file created by the test suite."
TEST_FILE_PATH = "test/test-file.md"

# Authentication
SERVICE_TOKEN = os.getenv("GITHUB_TOKEN")

class GitIntegrationTester:
    def __init__(self):
        self.service_url = SERVICE_URL
        self.test_results = []
        self.session = requests.Session()
        
        # Add authentication headers if token is available
        if SERVICE_TOKEN:
            self.session.headers.update({
                "Authorization": f"Bearer {SERVICE_TOKEN}"
            })
            print(f"Using authentication token: {SERVICE_TOKEN[:10]}...")
        else:
            print("ERROR: No GITHUB_TOKEN found - authentication is mandatory!")
            print("Please set GITHUB_TOKEN in your .env file")
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "PASS" if success else "FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        
    def start_service(self):
        """Start the service, kill existing if running"""
        import subprocess
        import time
        
        # Kill any existing service
        try:
            print("Killing existing service...")
            subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                         capture_output=True, text=True)
            time.sleep(1)
        except:
            pass
        
        try:
            print("Starting Git Integration Service...")
            process = subprocess.Popen(["python", "service.py"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            time.sleep(3)  # Give service time to start
            print("Service started successfully")
            return True
        except Exception as e:
            print(f"Failed to start service: {e}")
            return False

    def check_service_running(self) -> bool:
        """Check if the service is running, start if needed"""
        try:
            response = self.session.get(f"{self.service_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                github_auth = data.get("github_auth", False)
                self.log_test("Service Health Check", True, f"Service is running, GitHub auth: {github_auth}")
                return True
            else:
                self.log_test("Service Health Check", False, f"HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Service not running: {e}")
            print("Starting service automatically...")
            if self.start_service():
                # Try again after starting
                try:
                    response = self.session.get(f"{self.service_url}/", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        github_auth = data.get("github_auth", False)
                        self.log_test("Service Health Check", True, f"Service started and running, GitHub auth: {github_auth}")
                        return True
                except Exception as e2:
                    self.log_test("Service Health Check", False, f"Still can't connect: {e2}")
            return False
    
    def test_authentication(self):
        """Test authentication endpoints"""
        try:
            # Test GitHub auth status
            response = self.session.get(f"{self.service_url}/auth/github")
            if response.status_code == 200:
                data = response.json()
                self.log_test("GitHub Auth Status", True, f"GitHub auth: {data.get('authenticated', False)}")
            else:
                self.log_test("GitHub Auth Status", False, f"HTTP {response.status_code}")
            
            # Test client auth status
            response = self.session.get(f"{self.service_url}/auth/client")
            if response.status_code == 200:
                data = response.json()
                auth_required = data.get("authentication_required", False)
                self.log_test("Client Auth Status", True, f"Auth required: {auth_required}")
            else:
                self.log_test("Client Auth Status", False, f"HTTP {response.status_code}")
            
            # Test auth verification
            response = self.session.get(f"{self.service_url}/auth/verify")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Auth Verification", True, f"Authenticated: {data.get('authenticated', False)}")
            else:
                self.log_test("Auth Verification", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Authentication Tests", False, str(e))
    
    def test_status_endpoint(self):
        """Test the /status endpoint"""
        try:
            response = self.session.get(f"{self.service_url}/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Status Endpoint", True, f"Has changes: {data.get('has_changes', False)}")
            else:
                self.log_test("Status Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Status Endpoint", False, str(e))
    
    def test_tree_endpoint(self):
        """Test the /tree endpoint"""
        try:
            response = self.session.get(f"{self.service_url}/tree")
            if response.status_code == 200:
                data = response.json()
                file_count = data.get('total_files', 0)
                self.log_test("Tree Endpoint", True, f"Found {file_count} files")
            else:
                self.log_test("Tree Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Tree Endpoint", False, str(e))
    
    def test_search_files_endpoint(self):
        """Test the /search/files endpoint"""
        try:
            response = self.session.get(f"{self.service_url}/search/files?pattern=*.py")
            if response.status_code == 200:
                data = response.json()
                file_count = data.get('total_files', 0)
                self.log_test("Search Files Endpoint", True, f"Found {file_count} Python files")
            else:
                self.log_test("Search Files Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Search Files Endpoint", False, str(e))
    
    def test_search_content_endpoint(self):
        """Test the /search/content endpoint"""
        try:
            payload = {
                "query": "def ",
                "file_pattern": "*.py"
            }
            response = self.session.post(f"{self.service_url}/search/content", json=payload)
            if response.status_code == 200:
                data = response.json()
                match_count = data.get('total_matches', 0)
                self.log_test("Search Content Endpoint", True, f"Found {match_count} matches")
            else:
                self.log_test("Search Content Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Search Content Endpoint", False, str(e))
    
    def test_commit_text_endpoint(self):
        """Test the /commit/text endpoint"""
        try:
            payload = {
                "content": TEST_FILE_CONTENT,
                "file_path": TEST_FILE_PATH,
                "commit_message": "test: add test file via API"
            }
            response = self.session.post(f"{self.service_url}/commit/text", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    self.log_test("Commit Text Endpoint", True, f"Committed {data.get('file_path')}")
                else:
                    self.log_test("Commit Text Endpoint", False, data.get('message', 'Unknown error'))
            else:
                self.log_test("Commit Text Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Commit Text Endpoint", False, str(e))
    
    def test_get_file_endpoint(self):
        """Test the /file/{path} endpoint"""
        try:
            response = self.session.get(f"{self.service_url}/file/{TEST_FILE_PATH}")
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', '')
                if TEST_FILE_CONTENT in content:
                    self.log_test("Get File Endpoint", True, "File content matches")
                else:
                    self.log_test("Get File Endpoint", False, "File content doesn't match")
            else:
                self.log_test("Get File Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Get File Endpoint", False, str(e))
    
    def test_folder_endpoint(self):
        """Test the /folder/{path} endpoint"""
        try:
            response = self.session.get(f"{self.service_url}/folder/test")
            if response.status_code == 200:
                data = response.json()
                file_count = data.get('total_files', 0)
                self.log_test("Folder Endpoint", True, f"Found {file_count} files in test folder")
            else:
                self.log_test("Folder Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Folder Endpoint", False, str(e))

    def test_extract_file_endpoint(self):
        """Test the GET /extract/{path} endpoint"""
        try:
            # Test extracting content from a text file (.gitignore in root)
            response = self.session.get(f"{self.service_url}/extract/.gitignore")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('file_type') == 'text':
                    content_length = len(data.get('content', ''))
                    self.log_test("Extract File Endpoint (Text)", True, f"Extracted {content_length} chars from .gitignore")
                else:
                    self.log_test("Extract File Endpoint (Text)", False, f"Unexpected response format: {data}")
            else:
                error_detail = response.json().get('detail', 'No detail') if response.headers.get('content-type') == 'application/json' else response.text
                self.log_test("Extract File Endpoint (Text)", False, f"HTTP {response.status_code}: {error_detail}")
        except Exception as e:
            self.log_test("Extract File Endpoint (Text)", False, str(e))

    def test_extract_powerpoint_endpoint(self):
        """Test extracting content from PowerPoint files"""
        try:
            # Test extracting content from the actual PowerPoint file
            pptx_file = "assets/AI Workforce Enablement Proposal/AI Transformation Slides 2.pptx"
            
            response = self.session.get(f"{self.service_url}/extract/{pptx_file}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('file_type') == 'binary':
                    extracted_length = len(data.get('extracted_content', ''))
                    extension = data.get('extension', 'unknown')
                    self.log_test(f"Extract PowerPoint ({extension})", True, f"Extracted {extracted_length} chars from {pptx_file}")
                else:
                    self.log_test(f"Extract PowerPoint ({pptx_file})", False, f"Unexpected response format: {data}")
            else:
                error_detail = response.json().get('detail', 'No detail') if response.headers.get('content-type') == 'application/json' else response.text
                self.log_test(f"Extract PowerPoint ({pptx_file})", False, f"HTTP {response.status_code}: {error_detail}")
        except Exception as e:
            self.log_test("Extract PowerPoint Endpoint", False, str(e))
    
    def test_sync_endpoint(self):
        """Test the /sync endpoint"""
        try:
            response = self.session.post(f"{self.service_url}/sync")
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    self.log_test("Sync Endpoint", True, "Repository synced successfully")
                else:
                    self.log_test("Sync Endpoint", False, data.get('message', 'Unknown error'))
            else:
                self.log_test("Sync Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Sync Endpoint", False, str(e))
    
    def test_workflows_copy_endpoint(self):
        """Test the /workflows/copy endpoint"""
        try:
            response = self.session.post(f"{self.service_url}/workflows/copy")
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    self.log_test("Workflows Copy Endpoint", True, "Workflow files copied successfully")
                else:
                    self.log_test("Workflows Copy Endpoint", False, data.get('message', 'Unknown error'))
            else:
                self.log_test("Workflows Copy Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Workflows Copy Endpoint", False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("Starting Git Integration Service Test Suite")
        print("=" * 50)
        
        # Check if service is running
        if not self.check_service_running():
            print("\nService is not running. Please start the service first:")
            print("   cd src/integration/git")
            print("   .\\start-git-integration-service.ps1")
            return False
        
        print("\n Running endpoint tests...")
        
        # Run all tests
        self.test_authentication()
        self.test_status_endpoint()
        self.test_tree_endpoint()
        self.test_search_files_endpoint()
        self.test_search_content_endpoint()
        self.test_commit_text_endpoint()
        self.test_get_file_endpoint()
        self.test_folder_endpoint()
        self.test_extract_file_endpoint()
        self.test_extract_powerpoint_endpoint()
        self.test_sync_endpoint()
        self.test_workflows_copy_endpoint()
        
        # Summary
        print("\n" + "=" * 50)
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        print(f"Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("All tests passed!")
            return True
        else:
            print("  Some tests failed. Check the output above.")
            return False

def main():
    tester = GitIntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
