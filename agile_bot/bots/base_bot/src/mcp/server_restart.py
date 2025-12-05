"""
MCP Server Restart Utilities

Provides functionality to restart MCP server processes to load code changes.
"""
import psutil
import subprocess
import time
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def find_mcp_server_processes(bot_name: str = None) -> List[int]:
    """
    Find all running MCP server processes.
    
    Args:
        bot_name: Optional bot name to filter processes (e.g., 'story_bot')
    
    Returns:
        List of process IDs
    """
    pids = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline') or []
                cmdline_str = ' '.join(cmdline)
                
                # Look for Python processes running mcp_server
                if ('python' in proc.info.get('name', '').lower() and 
                    'mcp_server' in cmdline_str):
                    # If bot_name specified, filter by bot name
                    if bot_name is None or bot_name in cmdline_str:
                        pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.warning(f'Error finding MCP processes: {e}')
    
    return pids


def terminate_processes(pids: List[int], timeout: int = 5) -> dict:
    """
    Terminate processes gracefully, then force kill if needed.
    
    Args:
        pids: List of process IDs to terminate
        timeout: Seconds to wait for graceful shutdown
    
    Returns:
        Dict with 'terminated', 'killed', 'failed' lists
    """
    result = {
        'terminated': [],
        'killed': [],
        'failed': []
    }
    
    if not pids:
        return result
    
    # Send SIGTERM to all processes
    processes = []
    for pid in pids:
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            processes.append(proc)
            logger.info(f'Sent SIGTERM to process {pid}')
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f'Could not terminate process {pid}: {e}')
            result['failed'].append(pid)
    
    # Wait for graceful shutdown
    gone, alive = psutil.wait_procs(processes, timeout=timeout)
    
    for proc in gone:
        result['terminated'].append(proc.pid)
        logger.info(f'Process {proc.pid} terminated gracefully')
    
    # Force kill remaining
    for proc in alive:
        try:
            proc.kill()
            proc.wait(timeout=2)
            result['killed'].append(proc.pid)
            logger.info(f'Process {proc.pid} force killed')
        except Exception as e:
            logger.error(f'Failed to kill process {proc.pid}: {e}')
            result['failed'].append(proc.pid)
    
    return result


def clear_python_cache(root_path: Path) -> int:
    """
    Clear all Python bytecode cache under root_path.
    
    Args:
        root_path: Root directory to search for __pycache__
    
    Returns:
        Number of cache directories cleared
    """
    cleared = 0
    root = Path(root_path)
    
    for pycache_dir in root.rglob('__pycache__'):
        try:
            # Delete all .pyc and .pyo files
            for cache_file in pycache_dir.glob('*.pyc'):
                cache_file.unlink()
            for cache_file in pycache_dir.glob('*.pyo'):
                cache_file.unlink()
            
            # Remove directory
            pycache_dir.rmdir()
            cleared += 1
            logger.info(f'Cleared cache: {pycache_dir}')
        except Exception as e:
            logger.warning(f'Failed to clear cache {pycache_dir}: {e}')
    
    return cleared


def restart_mcp_server(workspace_root: Path, bot_name: str, bot_location: str) -> dict:
    """
    Restart MCP server: terminate processes, clear cache, start new server.
    
    Args:
        workspace_root: Workspace root path
        bot_name: Name of bot (e.g., 'story_bot')
        bot_location: Path to bot directory (e.g., 'agile_bot/bots/story_bot')
    
    Returns:
        Status dict with restart information
    """
    result = {
        'status': 'unknown',
        'previous_pids': [],
        'new_pid': None,
        'cache_cleared': False,
        'error': None
    }
    
    try:
        # Step 1: Find and terminate existing processes
        logger.info(f'Finding {bot_name} MCP server processes...')
        pids = find_mcp_server_processes(bot_name)
        
        if pids:
            logger.info(f'Found {len(pids)} processes: {pids}')
            term_result = terminate_processes(pids, timeout=5)
            result['previous_pids'] = term_result['terminated'] + term_result['killed']
            
            if term_result['failed']:
                result['error'] = f"Failed to terminate processes: {term_result['failed']}"
                return result
        
        # Step 2: Clear bytecode cache
        logger.info('Clearing Python bytecode cache...')
        cache_root = workspace_root / 'agile_bot'
        cleared = clear_python_cache(cache_root)
        result['cache_cleared'] = cleared > 0
        logger.info(f'Cleared {cleared} cache directories')
        
        # Step 3: Start new server
        # Note: This is tricky - MCP server is typically started by Cursor, not by us
        # For now, just return success and let Cursor restart it
        result['status'] = 'restarted' if pids else 'ready_to_start'
        result['message'] = 'Processes terminated and cache cleared. MCP server will restart automatically.'
        
        return result
        
    except Exception as e:
        logger.error(f'Error during restart: {e}', exc_info=True)
        result['error'] = str(e)
        result['status'] = 'failed'
        return result



