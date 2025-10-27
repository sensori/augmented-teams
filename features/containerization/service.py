#!/usr/bin/env python3
"""
Containerization Service - FastAPI Service Layer
"""

from fastapi import FastAPI
from pathlib import Path
import yaml
import main

# Load configuration
def load_config():
    """Load configuration from feature-config.yaml"""
    config_file = Path(__file__).parent / "config" / "feature-config.yaml"
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# FastAPI service
app = FastAPI(
    title=config['feature']['name'],
    description=config['feature']['description'],
    version=config['feature']['version']
)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "status": "healthy",
        "service": config['feature']['name'],
        "version": config['feature']['version']
    }

@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}

@app.post("/provision")
def provision(feature_name: str, mode: str = "SERVICE", always: bool = False):
    """Provision a feature"""
    return main.provision_feature(feature_name, mode, always)

@app.post("/start")
def start(feature_name: str, mode: str = "SERVICE", always: bool = False):
    """Start a feature"""
    return main.start_feature(feature_name, mode, always)

@app.post("/provision-and-start")
def provision_and_start(feature_name: str, mode: str = "SERVICE", always: bool = False):
    """Provision and start a feature"""
    return main.provision_and_start(feature_name, mode, always)

@app.post("/provision-start-and-test")
def provision_start_and_test(feature_name: str, mode: str = "SERVICE", always: bool = False):
    """Full pipeline: provision, start, and get test URL"""
    return main.provision_start_and_test(feature_name, mode, always)

@app.get("/test-url/{feature_name}")
def get_test_url(feature_name: str, mode: str = "SERVICE"):
    """Get test URL for a feature"""
    return main.get_test_url(feature_name, mode)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("service:app", host="0.0.0.0", port=8000)


