#!/usr/bin/env python3
"""
Test Containerization Feature - Core Business Logic
"""

# Plain Python functions - no service dependencies
def hello(name: str) -> str:
    """Greet someone"""
    return f"Hello {name}!"

def add_numbers(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def goodbye(param: str) -> str:
    """Say goodbye"""
    return f"Goodbye {param}!"

def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b
   
if __name__ == '__main__':
    # Simple test when run directly
    print(hello("World"))
    print(add_numbers(2, 3))
    print(goodbye("Farewell"))
