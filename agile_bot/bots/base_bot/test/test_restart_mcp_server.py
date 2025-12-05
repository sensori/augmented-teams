"""
Test MCP Server Restart Functionality

Tests the automatic restart of MCP server to load code changes.
"""
import pytest
import json
import psutil
import subprocess
import time
from pathlib import Path


def test_clear_python_bytecode_cache(tmp_path):
    """
    Test that clear_python_cache removes all __pycache__ directories and .pyc files.
    
    Given __pycache__ directories exist with .pyc files
    When clear_python_cache is called
    Then all __pycache__ directories are removed
    And all .pyc files are deleted
    """
    # Create mock cache structure
    cache_dirs = [
        tmp_path / 'agile_bot' / 'bots' / 'test_bot' / 'src' / '__pycache__',
        tmp_path / 'agile_bot' / 'bots' / 'test_bot' / 'src' / 'bot' / '__pycache__',
        tmp_path / 'agile_bot' / 'bots' / 'base_bot' / 'src' / '__pycache__',
    ]
    
    for cache_dir in cache_dirs:
        cache_dir.mkdir(parents=True)
        (cache_dir / 'test.cpython-312.pyc').write_text('bytecode')
        (cache_dir / 'test2.cpython-312.pyc').write_text('bytecode')
    
    # Verify setup
    assert all(d.exists() for d in cache_dirs)
    
    # Execute
    from agile_bot.bots.base_bot.src.mcp.server_restart import clear_python_cache
    cleared_count = clear_python_cache(tmp_path / 'agile_bot')
    
    # Verify all caches cleared
    assert cleared_count == 3
    assert not any(d.exists() for d in cache_dirs)


def test_find_mcp_server_processes():
    """
    Test finding MCP server processes by name pattern.
    
    Note: This test requires actual MCP server to be running to be meaningful.
    For now, just tests the function doesn't crash.
    """
    from agile_bot.bots.base_bot.src.mcp.server_restart import find_mcp_server_processes
    
    # Execute (may return empty list if no servers running)
    processes = find_mcp_server_processes('story_bot')
    
    # Should return list (empty or with PIDs)
    assert isinstance(processes, list)
    for pid in processes:
        assert isinstance(pid, int)
        assert pid > 0



