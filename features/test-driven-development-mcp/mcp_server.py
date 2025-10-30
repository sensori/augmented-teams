#!/usr/bin/env python3
"""
TDD Pipeline MCP Server - Complete Implementation

TABLE OF CONTENTS:
1. MCP SERVER SETUP
   1.1 Logging Configuration
   1.2 Pipeline Import and Initialization
2. TOOL HANDLERS
   2.1 Generic Tools (Context-Independent)
      2.1.1 get_current_step - Get current pipeline step
      2.1.2 start_next_step - Execute next step in pipeline
      2.1.3 repeat_current_step - Retry current step
      2.1.4 get_workflow_status - Show all phases and status
      2.1.5 resume_pipeline - Resume from human activity
      2.1.6 reset_pipeline - Reset to beginning
   2.2 Step Navigation Tools
      2.2.1 skip_to_step - Skip to any step by name
   2.3 Workflow Discovery
      2.3.1 list_workflow_phases - List all phases
      2.3.2 get_phase_details - Get specific phase info
3. MCP PROTOCOL HANDLER
   3.1 Initialize and Tools List
   3.2 Tool Execution Router
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

# Import delivery_pipeline from same directory
sys.path.insert(0, str(Path(__file__).parent))
from delivery_pipeline import DeliveryPipeline

# 1. MCP SERVER SETUP
# 1.1 Logging Configuration - Setup complete above

# 1.2 Pipeline Import and Initialization
def normalize_feature_name(raw: str) -> str:
    """Normalize feature name to lowercase with hyphens (e.g., 'Test Example' -> 'test-example')"""
    import re
    # Convert to lowercase and replace spaces/special chars with hyphens
    s = re.sub(r'[^a-zA-Z0-9\s_-]', '', raw)  # strip special chars
    s = s.lower().replace(' ', '-').replace('_', '-')
    # Remove duplicate hyphens
    s = re.sub(r'-+', '-', s)
    # Remove leading/trailing hyphens
    return s.strip('-')

def get_project_root() -> Path:
    """Get project root directory (where 'features' folder is located)"""
    # MCP server is in features/test-driven-development-mcp/
    # Go up 2 levels to get to project root
    mcp_file = Path(__file__).resolve()
    project_root = mcp_file.parent.parent.parent
    return project_root

def get_pipeline(feature_name):
    """Create DeliveryPipeline instance for a feature and save state"""
    normalized_name = normalize_feature_name(feature_name)
    project_root = get_project_root()
    feature_path = project_root / "features" / normalized_name
    pipeline = DeliveryPipeline(normalized_name, feature_path)
    # Ensure state is saved to disk
    pipeline.state_mgr.save_state(pipeline.state)
    return pipeline

# 2. TOOL HANDLERS
# 2.1 Generic Tools (Context-Independent)
# 2.1.0 Dev start - Initialize new feature for development
def handle_dev_start(feature_name):
    """Start development for a new feature when user initiates new feature"""
    logger.info(f"Starting development for feature: {feature_name}")
    try:
        # Normalize feature name for filesystem
        normalized_name = normalize_feature_name(feature_name)
        project_root = get_project_root()
        feature_path = project_root / "features" / normalized_name
        
        # Create feature directory if it doesn't exist
        feature_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize pipeline (this sets up all steps including START)
        pipeline = DeliveryPipeline(normalized_name, feature_path)
        
        # Ensure state is saved
        pipeline.state_mgr.save_state(pipeline.state)
        
        # Get summary of what was initialized
        total_steps = len(pipeline.state.steps)
        pipeline_id = pipeline.state.pipeline_id
        started_at = pipeline.state.started_at
        
        result = f"""Development started for '{feature_name}'

Initialized:
- Pipeline ID: {pipeline_id}
- Started: {started_at}
- Total Steps: {total_steps} (all pending)
- Normalized name: {normalized_name}

Phases:
"""
        for phase in DeliveryPipeline.PHASES:
            result += f"- {phase['name']}: {len(phase['steps'])} steps\n"
        
        result += f"""
Feature directory: features/{normalized_name}
State file: features/{normalized_name}/.deployment-state.json

Next step: PROMPT_CREATE (describe feature requirements)
"""
        return result
    except Exception as e:
        logger.exception(f"Error starting development: {e}")
        return f"Error: {str(e)}"

# 2.1 Generic Tools (Context-Independent)
# 2.1.1 Get current step when user asks status
def handle_get_current_step(feature_name):
    """Get current pipeline step when user wants to know status"""
    logger.info(f"Getting current step for feature: {feature_name}")
    try:
        pipeline = get_pipeline(feature_name)
        
        step = pipeline.state.get_current_step_display()
        status = pipeline.state.get_status_display()
        
        # Check if current step is still active
        current_step_name = pipeline.state.current_step
        current_step_completed = False
        if current_step_name:
            current_step_state = pipeline.state.steps.get(current_step_name)
            current_step_completed = current_step_state and current_step_state.status == 'completed'
        
        # Get next step after current one (or actual next if current is completed/None)
        next_step_obj = pipeline.get_next_step()
        if next_step_obj:
            next_step = next_step_obj.name
            next_type = next_step_obj.type
        elif current_step_name and not current_step_completed:
            # Current step is active, need to complete it first
            # Find what would be next after current step
            next_step = "Complete current step first"
            next_type = "N/A"
        else:
            next_step = "None - pipeline complete"
            next_type = "N/A"
        
        return f"""Current Pipeline State for '{feature_name}'

Current Step: {step}
Status: {status}

Next:
- Step: {next_step}
- Type: {next_type}
"""
    except Exception as e:
        logger.exception(f"Error getting current step: {e}")
        return f"Error: {str(e)}"

# 2.1.2 Start next step when user says continue or proceed
def handle_start_next_step(feature_name):
    """Start the next pipeline step when user wants to proceed"""
    try:
        pipeline = get_pipeline(feature_name)
        
        # Complete current step and start next step
        execution_result = pipeline.start_next_step()
        
        if not execution_result:
            return "Pipeline completed - no more steps"
        
        next_step = execution_result['step']
        result = execution_result['result']
        
        return f"""Next step to execute: {next_step.name}

Type: {next_step.type}
Phase: {next_step.phase}

Result: {result}

Note: Step execution will be implemented in Phase 2.
Currently only state management and reporting are active.
"""
    except Exception as e:
        logger.exception(f"Error executing step: {e}")
        return f"Error: {str(e)}"

# 2.1.3 Repeat current step when user wants to retry
def handle_repeat_current_step(feature_name):
    """Repeat current step when user wants to retry with feedback"""
    try:
        pipeline = get_pipeline(feature_name)
        current = pipeline.state.current_step
        
        if not current:
            return "No current step to repeat"
        
        return f"""Repeating step: {current}
       
This will restart the current step for '{feature_name}'.
Feedback/refinements from previous attempt will be incorporated.
"""
    except Exception as e:
        logger.exception(f"Error repeating step: {e}")
        return f"Error: {str(e)}"

# 2.1.4 Get workflow status when user wants overview
def handle_get_workflow_status(feature_name):
    """Show all phases and their status when user wants overview"""
    try:
        pipeline = get_pipeline(feature_name)
        
        summary = pipeline.get_status_summary()
        completed = summary['completed']
        pending = summary['pending']
        total = summary['total_steps']
        
        result = f"""Pipeline Workflow Status for '{feature_name}'

Overall Status: {summary['status']}
Current Step: {summary['current_step'] or 'None'}

Progress:
- Completed: {completed}/{total}
- Pending: {pending}

All Phases:
"""
        for phase in DeliveryPipeline.PHASES:
            result += f"\n{phase['name']}:\n"
            for step_def in phase['steps']:
                step_name = step_def['name']
                step_status = 'pending'
                if step_name in pipeline.state.steps:
                    step_status = pipeline.state.steps[step_name].status
                status_icon = {'completed': '✓', 'failed': '✗', 'started': '→', 'pending': '○'}.get(step_status, '?')
                result += f"  {status_icon} {step_name} ({step_status})\n"
        
        return result
    except Exception as e:
        logger.exception(f"Error getting workflow status: {e}")
        return f"Error: {str(e)}"

# 2.1.5 Resume pipeline when human approves
def handle_resume_pipeline(feature_name, approval=True):
    """Resume pipeline when human approves or rejects work"""
    try:
        pipeline = get_pipeline(feature_name)
        
        if approval:
            return f"""Pipeline resumed for '{feature_name}'

Human approval received. Continuing from current step.
"""
        else:
            return f"""Pipeline paused for '{feature_name}'

Human rejection received. Pipeline stopped.
"""
    except Exception as e:
        logger.exception(f"Error resuming pipeline: {e}")
        return f"Error: {str(e)}"

# 2.1.6 Reset pipeline when user wants to start over
def handle_reset_pipeline(feature_name):
    """Reset pipeline to beginning when user wants fresh start"""
    try:
        pipeline = get_pipeline(feature_name)
        
        # Reset all steps to pending
        for step in pipeline.state.steps.values():
            step.status = 'pending'
        
        pipeline.state.current_step = None
        pipeline.state.status = 'pending'
        pipeline.state_mgr.save_state(pipeline.state)
        
        return f"""Pipeline reset for '{feature_name}'

All steps have been reset to pending. Ready to start from beginning.
"""
    except Exception as e:
        logger.exception(f"Error resetting pipeline: {e}")
        return f"Error: {str(e)}"

# 2.2 Step Navigation Tools
# Generic tool to skip to any step

def handle_skip_to_step(feature_name, step_name):
    """Skip to a specific step by name. Use this to jump to any step like CREATE_STRUCTURE, BUILD_SCAFFOLDING, etc."""
    return _handle_step_jump(feature_name, step_name)

def _handle_step_jump(feature_name, step_or_phase_name, **kwargs):
    """Generic handler for step/phase jumps - tries skip_to_step then skip_to_phase"""
    try:
        pipeline = get_pipeline(feature_name)
        
        # Try step name first (exact match)
        current_step_obj = pipeline.skip_to_step(step_or_phase_name)
        
        # If not found as step, try as phase name
        if not current_step_obj:
            current_step_obj = pipeline.skip_to_phase(step_or_phase_name)
        
        if not current_step_obj:
            return f"{step_or_phase_name} step/phase not found for '{feature_name}'"
        
        # Execute to get skipped steps info
        result = current_step_obj.execute()
        
        response = f"""Jumped to {step_or_phase_name} for '{feature_name}'

Current step: {current_step_obj.name}
Type: {current_step_obj.type}
Phase: {current_step_obj.phase}

"""
        
        # Display skipped steps
        if result.get('skipped_steps'):
            response += f"Skipped {len(result['skipped_steps'])} steps:\n"
            for skipped in result['skipped_steps']:
                response += f"- {skipped['name']} ({skipped['type']}) in {skipped['phase']}\n"
            response += "\n"
        
        return response
    except Exception as e:
        logger.exception(f"Error in step/phase jump: {e}")
        return f"Error: {str(e)}"

# 2.3 Workflow Discovery
# 2.3.1 List workflow phases when user wants phase list
def handle_list_workflow_phases(feature_name):
    """List all workflow phases when user wants to see structure"""
    try:
        pipeline = get_pipeline(feature_name)
        
        result = f"""All Workflow Phases for '{feature_name}'\n\n"""
        
        for phase in DeliveryPipeline.PHASES:
            # Count step statuses in this phase
            phase_steps = [s['name'] for s in phase['steps']]
            total = len(phase_steps)
            completed = sum(1 for s in phase_steps if s in pipeline.state.steps and pipeline.state.steps[s].status == 'completed')
            
            result += f"{phase['name']}: {completed}/{total} completed\n"
            for step_def in phase['steps']:
                step_name = step_def['name']
                step_status = 'pending'
                if step_name in pipeline.state.steps:
                    step_status = pipeline.state.steps[step_name].status
                status_icon = {'completed': '✓', 'failed': '✗', 'started': '→', 'pending': '○'}.get(step_status, '?')
                result += f"  {status_icon} {step_name} ({step_status})\n"
            result += "\n"
        
        return result
    except Exception as e:
        logger.exception(f"Error listing phases: {e}")
        return f"Error: {str(e)}"

# 2.3.2 Get phase details when user wants specific phase info
def handle_get_phase_details(feature_name, phase_name):
    """Get specific phase details when user wants phase info"""
    try:
        pipeline = get_pipeline(feature_name)
        
        for phase in DeliveryPipeline.PHASES:
            if phase['name'] == phase_name:
                result = f"""Phase Details: {phase_name}\n\n"""
                result += f"Steps ({len(phase['steps'])} total):\n"
                
                for step_def in phase['steps']:
                    step_name = step_def['name']
                    step_type = step_def['type']
                    reason = step_def.get('reason', 'No reason specified')
                    
                    step_status = 'pending'
                    if step_name in pipeline.state.steps:
                        step_state = pipeline.state.steps[step_name]
                        step_status = step_state.status
                        result += f"  - {step_name}: {step_status} (Type: {step_type})\n"
                    else:
                        result += f"  - {step_name}: {step_status} (Type: {step_type})\n"
                    if 'reason' in step_def:
                        result += f"    Reason: {reason}\n"
                
                return result
        
        return f"Phase '{phase_name}' not found for '{feature_name}'"
    except Exception as e:
        logger.exception(f"Error getting phase details: {e}")
        return f"Error: {str(e)}"

# 3. MCP PROTOCOL HANDLER
# 3.1 Initialize and Tools List - Define all available tools
def get_all_tools():
    """Get list of all 13 tools for TDD pipeline"""
    return [
        # Generic Tools (7)
        {
            "name": "dev_start",
            "description": "Start development for a new feature. Use this to initialize a new feature, start tracking a feature, begin development, create a new feature, or set up feature tracking.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name to initialize"}
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
                    "feature_name": {"type": "string", "description": "Feature name"}
                },
                "required": ["feature_name"]
            }
        },
        {
            "name": "start_next_step",
            "description": "Strt the next pipeline step based on current state. Use this to continue the pipeline, proceed to next step, move forward, execute pipeline, or run next task in TDD workflow.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name to process"}
                },
                "required": ["feature_name"]
            }
        },
        {
            "name": "repeat_current_step",
            "description": "Repeat the current pipeline step with feedback. Use this to retry, retry current step, redo current step, or rerun current step in the TDD workflow.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"}
                },
                "required": ["feature_name"]
            }
        },
        {
            "name": "get_workflow_status",
            "description": "Show all phases and their status. Use this to get an overview of the pipeline, see all phases, check workflow status, view all steps, or get pipeline overview.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"}
                },
                "required": ["feature_name"]
            }
        },
        {
            "name": "resume_pipeline",
            "description": "Resume pipeline from human activity. Use this to approve work, reject work, continue after review, or proceed after approval.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "approval": {"type": "boolean", "description": "True to approve, False to reject"}
                },
                "required": ["feature_name", "approval"]
            }
        },
        {
            "name": "reset_pipeline",
            "description": "Reset pipeline to beginning. Use this to start over, reset pipeline, restart from beginning, or clear all progress.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"}
                },
                "required": ["feature_name"]
            }
        },
        {
            "name": "skip_to_step",
            "description": "Skip to a specific step by name. Use this to jump to any step like CREATE_STRUCTURE, BUILD_SCAFFOLDING, DEVELOP_TEST, WRITE_CODE, REFACTOR, or START_FEATURE.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "step_name": {"type": "string", "description": "Name of the step to skip to (e.g., CREATE_STRUCTURE, BUILD_SCAFFOLDING, DEVELOP_TEST, WRITE_CODE, REFACTOR)"}
                },
                "required": ["feature_name", "step_name"]
            }
        },
        # Workflow Discovery (2)
        {
            "name": "list_workflow_phases",
            "description": "List all workflow phases with their status. Use this to see all phases, list workflow phases, show phase structure, or view all phases.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"}
                },
                "required": ["feature_name"]
            }
        },
        {
            "name": "get_phase_details",
            "description": "Get details for a specific phase. Use this to get phase info, show phase details, or view phase information.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "feature_name": {"type": "string", "description": "Feature name"},
                    "phase_name": {"type": "string", "description": "Name of the phase"}
                },
                "required": ["feature_name", "phase_name"]
            }
        }
    ]

# 3.2 Tool Execution Router - Route tool calls to appropriate handlers
def handle_tool_call(tool_name, arguments):
    """Route tool calls to appropriate handlers"""
    if tool_name == "dev_start":
        return handle_dev_start(arguments.get("feature_name"))
    
    elif tool_name == "get_current_step":
        return handle_get_current_step(arguments.get("feature_name"))
    
    elif tool_name == "start_next_step":
        return handle_start_next_step(arguments.get("feature_name"))
    
    elif tool_name == "repeat_current_step":
        return handle_repeat_current_step(arguments.get("feature_name"))
    
    elif tool_name == "get_workflow_status":
        return handle_get_workflow_status(arguments.get("feature_name"))
    
    elif tool_name == "resume_pipeline":
        return handle_resume_pipeline(arguments.get("feature_name"), arguments.get("approval", True))
    
    elif tool_name == "reset_pipeline":
        return handle_reset_pipeline(arguments.get("feature_name"))
    
    elif tool_name == "skip_to_step":
        return handle_skip_to_step(arguments.get("feature_name"), arguments.get("step_name"))
    
    elif tool_name == "list_workflow_phases":
        return handle_list_workflow_phases(arguments.get("feature_name"))
    
    elif tool_name == "get_phase_details":
        return handle_get_phase_details(arguments.get("feature_name"), arguments.get("phase_name"))
    
    else:
        return f"Unknown tool: {tool_name}"

# 3. MCP PROTOCOL HANDLER
# MCP Server Main Loop following JSON-RPC over stdio
if __name__ == "__main__":
    logger.info("MCP Server starting up")
    
    for line in sys.stdin:
        try:
            if not line.strip():
                continue
            
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
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "tdd-pipeline", "version": "2.0.0"}
                    }
                }
                print(json.dumps(response))
                sys.stdout.flush()
            
            # Initialized
            elif request.get("method") == "notifications/initialized":
                continue
            
            # Prompts list (empty for now)
            elif request.get("method") == "prompts/list":
                response = {"jsonrpc": "2.0", "id": request.get("id"), "result": {"prompts": []}}
                print(json.dumps(response))
                sys.stdout.flush()
            
            # Resources list (empty for now)
            elif request.get("method") == "resources/list":
                response = {"jsonrpc": "2.0", "id": request.get("id"), "result": {"resources": []}}
                print(json.dumps(response))
                sys.stdout.flush()
            
            # Tools list - return all 12 tools
            elif request.get("method") == "tools/list":
                logger.info("Handling tools/list request")
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"tools": get_all_tools()}
                }
                print(json.dumps(response))
                sys.stdout.flush()
            
            # Tool call - route to appropriate handler
            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                logger.info(f"Handling tools/call for {tool_name}")
                
                result = handle_tool_call(tool_name, arguments)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [{"type": "text", "text": str(result)}]
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
