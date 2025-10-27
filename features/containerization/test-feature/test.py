#!/usr/bin/env python3
"""
Test test-feature - plain Python tests
Tests the actual functions from main.py
"""

import sys
import io

# Fix encoding for Windows - allow emojis in output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

from main import hello, add_numbers

def test_hello_world():
    """Test hello with World"""
    result = hello("World")
    assert result == "Hello World!", f"Expected 'Hello World!', got '{result}'"
    print("✅ test_hello_world passed")

def test_hello_custom():
    """Test hello with custom name"""
    result = hello("Alice")
    assert result == "Hello Alice!", f"Expected 'Hello Alice!', got '{result}'"
    print("✅ test_hello_custom passed")

def test_add_numbers():
    """Test add_numbers function"""
    result = add_numbers(2, 3)
    assert result == 5, f"Expected 5, got {result}"
    print("✅ test_add_numbers passed")

def test_goodbye():
    """Test goodbye function"""
    from main import goodbye
    result = goodbye("World")
    assert result == "Goodbye World!", f"Expected 'Goodbye World!', got '{result}'"
    print("✅ test_goodbye passed")

if __name__ == "__main__":
    test_hello_world()
    test_hello_custom()
    test_add_numbers()
    test_goodbye()
    print("✅ All tests passed")
