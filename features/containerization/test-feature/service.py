#!/usr/bin/env python3
"""
Test Containerization Feature - Service
Wraps main functions in FastAPI service
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

@app.get("/hello")
def hello_endpoint(name: str = "World"):
    """Hello endpoint"""
    return {"message": main.hello(name)}

@app.get("/add")
def add_endpoint(a: int, b: int):
    """Add endpoint"""
    return {"result": main.add_numbers(a, b)}

@app.get("/goodbye")
def goodbye_endpoint(param: str = "Farewell"):
    """Goodbye endpoint"""
    return {"message": main.goodbye(param)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("service:app", host="0.0.0.0", port=8000)

