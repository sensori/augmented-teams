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

# ============================================================================
# GIVEN/WHEN/THEN HELPER FUNCTIONS
# ============================================================================

def given_pycache_directories_exist(base_path: Path, cache_paths: list):
    """Given step: __pycache__ directories exist with .pyc files.
    
    Creates cache directories and .pyc files for testing.
    Returns list of created cache directories.
    """
    for cache_dir in cache_paths:
        cache_dir.mkdir(parents=True)
        (cache_dir / 'test.cpython-312.pyc').write_text('bytecode')
        (cache_dir / 'test2.cpython-312.pyc').write_text('bytecode')
    return cache_paths

def when_clear_python_cache_is_called(base_path: Path):
    """When step: clear_python_cache is called.
    
    Calls clear_python_cache function and returns cleared count.
    """
    from agile_bot.bots.base_bot.src.mcp.server_restart import clear_python_cache
    return clear_python_cache(base_path)

def then_all_pycache_directories_removed(cache_dirs: list):
    """Then step: All __pycache__ directories are removed."""
    assert not any(d.exists() for d in cache_dirs)

def then_all_pyc_files_deleted(cache_dirs: list):
    """Then step: All .pyc files are deleted."""
    for cache_dir in cache_dirs:
        pyc_files = list(cache_dir.glob('*.pyc'))
        assert len(pyc_files) == 0

def then_cache_cleared_count_matches(cached_count: int, expected_count: int):
    """Then step: Cache cleared count matches expected."""
    assert cached_count == expected_count

def when_find_mcp_server_processes_is_called(server_name: str):
    """When step: find_mcp_server_processes is called."""
    from agile_bot.bots.base_bot.src.mcp.server_restart import find_mcp_server_processes
    return find_mcp_server_processes(server_name)

def then_processes_list_is_valid(processes: list):
    """Then step: Processes list is valid."""
    assert isinstance(processes, list)
    for pid in processes:
        assert isinstance(pid, int)
        assert pid > 0


def test_clear_python_bytecode_cache(tmp_path):
    """
    Test that clear_python_cache removes all __pycache__ directories and .pyc files.
    
    Given __pycache__ directories exist with .pyc files
    When clear_python_cache is called
    Then all __pycache__ directories are removed
    And all .pyc files are deleted
    """
    # Given: __pycache__ directories exist with .pyc files
    cache_dirs = [
        tmp_path / 'agile_bot' / 'bots' / 'test_bot' / 'src' / '__pycache__',
        tmp_path / 'agile_bot' / 'bots' / 'test_bot' / 'src' / 'bot' / '__pycache__',
        tmp_path / 'agile_bot' / 'bots' / 'base_bot' / 'src' / '__pycache__',
    ]
    given_pycache_directories_exist(tmp_path, cache_dirs)
    assert all(d.exists() for d in cache_dirs)
    
    # When: clear_python_cache is called
    cleared_count = when_clear_python_cache_is_called(tmp_path / 'agile_bot')
    
    # Then: All __pycache__ directories are removed
    then_all_pycache_directories_removed(cache_dirs)
    # And: All .pyc files are deleted
    then_all_pyc_files_deleted(cache_dirs)
    # And: Cache cleared count matches expected
    then_cache_cleared_count_matches(cleared_count, 3)


def test_find_mcp_server_processes():
    """
    Test finding MCP server processes by name pattern.
    
    Note: This test requires actual MCP server to be running to be meaningful.
    For now, just tests the function doesn't crash.
    """
    # When: find_mcp_server_processes is called
    processes = when_find_mcp_server_processes_is_called('story_bot')
    
    # Then: Processes list is valid (may be empty if no servers running)
    then_processes_list_is_valid(processes)






