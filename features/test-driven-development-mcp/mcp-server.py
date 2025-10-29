#!/usr/bin/env python3
"""
TDD Pipeline MCP Server - Thin-Slice Phase 1

Barebones MCP server using the MCP Python SDK
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Setup logging to stderr (visible in MCP logs)
logging.basicConfig(
    level=logging.DEBUG,
    format='[MCP-Server] %(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

# Import delivery-pipeline from same directory
import importlib.util
spec = importlib.util.spec_from_file_location("delivery_pipeline", Path(__file__).parent / "delivery_pipeline.py")
delivery_pipeline = importlib.util.module_from_spec(spec)
sys.modules["delivery_pipeline"] = delivery_pipeline
spec.loader.exec_module(delivery_pipeline)

from delivery_pipeline import DeliveryPipeline

def handle_execute_next_step(feature_name):
    """Execute the next pipeline step"""
    try:
        pipeline = DeliveryPipeline(feature_name, Path("features") / feature_name)
        next_step = pipeline.get_next_step()
        
        if not next_step:
            return "Pipeline completed - no more steps"
        
        result = pipeline.execute_step(next_step['name'], next_step['func'])
        
        return json.dumps({
            "step_executed": next_step['name'],
            "success": result,
            "phase": pipeline.state.current_phase,
            "next_step": pipeline.get_next_step()['name'] if pipeline.get_next_step() else None
        }, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

def handle_get_current_step(feature_name):
    """Get current pipeline step"""
    logger.info(f"Getting current step for feature: {feature_name}")
    try:
        logger.debug(f"Creating DeliveryPipeline for {feature_name}")
        pipeline = DeliveryPipeline(feature_name, Path("features") / feature_name)
        logger.debug(f"Pipeline created successfully")
        
        # Format as human-readable text
        phase = pipeline.state.current_phase or "Not started"
        step = pipeline.state.current_step or "No step active"
        status = pipeline.state.status or "Unknown"
        
        # Check what's next
        next_step_info = pipeline.get_next_step()
        if next_step_info:
            next_step = next_step_info['name']
            next_phase = next_step_info.get('phase', 'Unknown')
            next_type = next_step_info.get('type', 'Unknown')
        else:
            next_step = "None - pipeline complete"
            next_phase = "N/A"
            next_type = "N/A"
        
        result = f"""Current Pipeline State for '{feature_name}'

Phase: {phase}
Current Step: {step}
Status: {status}

Next:
- Step: {next_step}
- Phase: {next_phase}
- Type: {next_type}
"""
        
        return result
    except Exception as e:
        return f"Error getting pipeline state: {str(e)}"

# MCP Server Main Loop following JSON-RPC over stdio
if __name__ == "__main__":
    logger.info("MCP Server starting up")
    
    # Handle MCP protocol
    for line in sys.stdin:
        try:
            logger.debug(f"Received: {line.strip()[:200]}")
            request = json.loads(line.strip())
            logger.debug(f"Parsed request: {request.get('method', 'unknown')}")
            
            # Initialize
            if request.get("method") == "initialize":
                logger.info("Handling initialize request")
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "tdd-pipeline",
                            "version": "0.1.0"
                        }
                    }
                }
                print(json.dumps(response))
                sys.stdout.flush()
            
            # Initialized
            elif request.get("method") == "notifications/initialized":
                continue
            
            # Tools list
            elif request.get("method") == "tools/list":
                logger.info("Handling tools/list request")
                tools = [
                    {
                        "name": "execute_next_step",
                        "description": "Execute the next pipeline step based on current state. Use this to continue the pipeline, proceed to next step, move forward, execute pipeline, or run next task in TDD workflow.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "feature_name": {
                                    "type": "string",
                                    "description": "Feature name to process"
                                }
                            },
                            "required": ["feature_name"]
                        }
                    },
                    {
                        "name": "get_current_step",
                        "description": "Get current pipeline step, phase, and status. Use this to check what step a feature is on in the TDD pipeline, get pipeline state, see current status, check what phase we're in, or find out what's next in the workflow.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "feature_name": {
                                    "type": "string",
                                    "description": "Feature name"
                                }
                            },
                            "required": ["feature_name"]
                        }
                    }
                ]
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": tools
                    }
                }
                print(json.dumps(response))
                sys.stdout.flush()
            
            # Tool call
            elif request.get("method") == "tools/call":
                tool_name = request.get("params", {}).get("name")
                logger.info(f"Handling tools/call for {tool_name}")
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "execute_next_step":
                    result = handle_execute_next_step(arguments.get("feature_name"))
                elif tool_name == "get_current_step":
                    result = handle_get_current_step(arguments.get("feature_name"))
                else:
                    result = f"Unknown tool: {tool_name}"
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
                print(json.dumps(response))
                sys.stdout.flush()
            
            else:
                logger.warning(f"Unknown method: {request.get('method')}")
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": "Unknown method"}
                }), file=sys.stderr)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            continue
        except Exception as e:
            logger.exception(f"Error handling request: {e}")
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            }), file=sys.stderr)
