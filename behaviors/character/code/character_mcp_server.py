"""
MCP Server for Character Behavior

Exposes character agent methods as MCP tools.
Character commands use Agent classes directly, not Command classes with generate/validate/correct actions.
"""

import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Literal

# Set up file-based logging for debugging
_log_file = None
_log_file_path = None

def _init_log_file():
    """Initialize log file for debugging"""
    global _log_file, _log_file_path
    try:
        # Create logs directory in workspace root
        workspace_root = Path(__file__).parent.parent.parent.parent
        log_dir = workspace_root / "behaviors" / "character" / "code" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        _log_file_path = log_dir / f"character_mcp_server_{timestamp}.log"
        _log_file = open(_log_file_path, "w", encoding="utf-8")
        return True
    except Exception:
        # If we can't create log file, continue without it
        return False

def _debug_log(message: str):
    """Log debug messages to both stderr and log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [CHARACTER-MCP] {message}"
    
    # Always write to stderr (visible in Cursor MCP logs)
    print(log_message, file=sys.stderr, flush=True)
    
    # Also write to log file if available
    if _log_file:
        try:
            _log_file.write(log_message + "\n")
            _log_file.flush()
        except Exception:
            pass  # Ignore file write errors

# Initialize logging immediately
_log_initialized = _init_log_file()
if _log_initialized:
    _debug_log(f"Log file initialized: {_log_file_path}")
else:
    _debug_log("WARNING: Could not initialize log file, using stderr only")

_debug_log("Starting MCP server initialization...")
_debug_log(f"Python executable: {sys.executable}")
_debug_log(f"Python version: {sys.version}")

# Add workspace root to path
# This file is in behaviors/character/code/, so go up 4 levels to workspace root
try:
    workspace_root = Path(__file__).parent.parent.parent.parent
    _debug_log(f"Workspace root: {workspace_root}")
    _debug_log(f"Current file: {__file__}")
    _debug_log(f"Current directory (before change): {Path.cwd()}")
    
    # Change working directory to workspace root so relative paths resolve correctly
    import os
    os.chdir(workspace_root)
    _debug_log(f"Changed working directory to: {Path.cwd()}")
    
    sys.path.insert(0, str(workspace_root))
    sys.path.insert(0, str(Path(__file__).parent))  # Also add code/ directory for local imports
    _debug_log(f"Python path updated: {sys.path[:3]}")
except Exception as e:
    _debug_log(f"ERROR setting up paths: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

try:
    _debug_log("Importing MCP SDK...")
    from mcp.server.fastmcp import FastMCP
    _debug_log("MCP SDK imported successfully")
except ImportError as e:
    _debug_log(f"ERROR: MCP SDK import failed: {e}")
    traceback.print_exc(file=sys.stderr)
    print(f"MCP SDK import error: {e}. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

try:
    _debug_log("Importing character agent modules...")
    from character_agent_runner import (
        CharacterSheetAgent,
        CharacterRollAgent,
        CharacterChatAgent,
        validate_character_name,
        create_character_folder_structure,
        copy_character_profile_template,
        create_episode_file,
        list_episodes,
        set_current_episode,
        get_current_episode_path,
        write_response_to_episode,
        undo_last_episode_entry,
        edit_last_episode_entry
    )
    _debug_log("Character agent modules imported successfully")
except ImportError as e:
    _debug_log(f"ERROR: Character agent import failed: {e}")
    traceback.print_exc(file=sys.stderr)
    print(f"Character agent import error: {e}", file=sys.stderr)
    sys.exit(1)

try:
    _debug_log("Creating FastMCP instance...")
    mcp = FastMCP("mutants-and-masterminds-character-helper")
    _debug_log("FastMCP instance created successfully")
except Exception as e:
    _debug_log(f"ERROR: FastMCP creation failed: {e}")
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

def _serialize_result(result) -> dict:
    """
    Convert a result object to a dictionary for JSON serialization.
    Handles various result types from character_agent_runner.
    """
    if result is None:
        return {"error": "Result is None"}
    
    # If it's already a dict, return it
    if isinstance(result, dict):
        return result
    
    # If it's a result object, convert to dict
    if hasattr(result, '__dict__'):
        return {k: v for k, v in result.__dict__.items() if not k.startswith('_')}
    
    # Fallback: convert to string representation
    return {"result": str(result)}

def _extract_capabilities_from_sheet(agent: CharacterSheetAgent) -> str:
    """
    Extract capabilities from a character sheet and convert to foe description string.
    This allows the tactics tool to work with character sheets directly.
    """
    try:
        # Get defenses
        defenses = agent._get_defenses()
        defense_parts = []
        
        # Extract defense values
        for defense_name, defense_value in defenses.items():
            if isinstance(defense_value, (int, float)):
                # Convert numeric values to descriptive levels
                if defense_value >= 15:
                    defense_parts.append(f"high {defense_name}")
                elif defense_value >= 10:
                    defense_parts.append(f"medium {defense_name}")
                else:
                    defense_parts.append(f"low {defense_name}")
            elif isinstance(defense_value, str):
                defense_parts.append(f"{defense_value} {defense_name}")
        
        # Get abilities for additional context
        abilities = agent._get_abilities()
        ability_parts = []
        high_ability_threshold = 3  # Assuming +3 or higher is "high"
        
        for ability_name, ability_value in abilities.items():
            if isinstance(ability_value, (int, float)):
                if ability_value >= high_ability_threshold:
                    ability_parts.append(f"high {ability_name}")
                elif ability_value <= -high_ability_threshold:
                    ability_parts.append(f"low {ability_name}")
        
        # Combine into description
        parts = defense_parts + ability_parts
        if parts:
            return ", ".join(parts)
        else:
            # Fallback if we can't extract much
            return "character from sheet data"
    except Exception as e:
        # Fallback on error
        return f"character from sheet data (extraction error: {str(e)})"

# Character Sheet Tools
@mcp.tool()
def character_sheet(
    character_name: str,
    category: Literal["powers", "abilities", "skills", "defenses", "attacks"],
    name_or_index: str | int | None = None
) -> str:
    """
    Load character sheet from XML or Foundry and query data by category.
    
    Args:
        character_name: Character name (e.g., 'Roach-Boy', 'Atom')
        category: Category to query: 'powers', 'abilities', 'skills', 'defenses', 'attacks'
        name_or_index: Optional: specific power/skill name or index to query
    """
    try:
        agent = CharacterSheetAgent()
        
        # Load sheet
        load_result = agent.load_character_sheet(character_name)
        if not load_result.loaded:
            return f"Error loading character sheet: {load_result.error_message}"
        
        # Query based on category
        import json
        if category == "powers":
            powers = agent._get_powers()
            if name_or_index:
                # Return specific power
                if isinstance(name_or_index, int):
                    power = powers[name_or_index] if name_or_index < len(powers) else None
                else:
                    power = next((p for p in powers if p.get('name') == name_or_index), None)
                if power:
                    result = {"power": power, "found": True}
                else:
                    result = {"error": f"Power not found: {name_or_index}", "found": False}
            else:
                result = {"powers": powers, "count": len(powers)}
        elif category == "abilities":
            abilities = agent._get_abilities()
            if name_or_index:
                ability_value = abilities.get(str(name_or_index).lower())
                if ability_value is not None:
                    result = {"ability": {str(name_or_index).lower(): ability_value}, "found": True}
                else:
                    result = {"error": f"Ability not found: {name_or_index}", "found": False}
            else:
                result = {"abilities": abilities, "count": len(abilities)}
        elif category == "skills":
            skills = agent._get_skills()
            if name_or_index:
                skill_value = skills.get(str(name_or_index).lower())
                if skill_value is not None:
                    result = {"skill": {str(name_or_index).lower(): skill_value}, "found": True}
                else:
                    result = {"error": f"Skill not found: {name_or_index}", "found": False}
            else:
                result = {"skills": skills, "count": len(skills)}
        elif category == "defenses":
            defenses = agent._get_defenses()
            result = {"defenses": defenses}
        else:
            result = {"error": f"Unknown category: {category}"}
        
        # Return as JSON string for structured data
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error executing character_sheet: {str(e)}"

# Character Tactics Tool
@mcp.tool()
def character_tactics(
    character_name: str | None = None,
    foe_description: str | None = None,
    attacker_character_name: str | None = None,
    target_character_name: str | None = None,
    character_sheet_data: dict | None = None,
    foe_sheet_data: dict | None = None
) -> str:
    """
    Recommend optimal tactics, powers, and abilities based on foe capabilities.
    Can use character sheet data, foe description, or attacker/target character sheets.
    
    Args:
        character_name: Character name whose sheet to use for recommendations
        foe_description: Natural language description of foe (e.g., 'high dodge, high parry, low toughness')
        attacker_character_name: Optional: Attacker character name (alternative to character_name)
        target_character_name: Optional: Target character name (alternative to foe_description)
        character_sheet_data: Optional: Pre-loaded character sheet data (if not using character_name)
        foe_sheet_data: Optional: Pre-loaded foe/target character sheet data
    """
    try:
        agent = CharacterSheetAgent()
        
        # Determine character sheet source
        char_name = character_name or attacker_character_name
        
        if char_name:
            # Load sheet from character name
            load_result = agent.load_character_sheet(char_name)
            if not load_result.loaded:
                return f"Error loading character sheet: {load_result.error_message}"
        elif character_sheet_data:
            # Use provided sheet data
            agent.sheet_data = character_sheet_data
        else:
            return "Error: Must provide character_name, attacker_character_name, or character_sheet_data"
        
        # Determine foe/target information
        if target_character_name:
            # Load target character sheet and extract capabilities
            target_agent = CharacterSheetAgent()
            target_load = target_agent.load_character_sheet(target_character_name)
            if not target_load.loaded:
                return f"Error loading target character sheet: {target_load.error_message}"
            # Extract capabilities from target sheet and convert to description
            foe_desc = _extract_capabilities_from_sheet(target_agent)
        elif foe_sheet_data:
            # Extract capabilities from provided foe sheet data
            temp_agent = CharacterSheetAgent()
            temp_agent.sheet_data = foe_sheet_data
            foe_desc = _extract_capabilities_from_sheet(temp_agent)
        elif foe_description:
            foe_desc = foe_description
        else:
            return "Error: Must provide foe_description, target_character_name, or foe_sheet_data"
        
        # Get recommendations
        result = agent.recommend_tactic(foe_desc)
        # Convert result object to structured dict
        result_dict = _serialize_result(result)
        import json
        return json.dumps(result_dict, indent=2)
    except Exception as e:
        return f"Error executing character_tactics: {str(e)}"

# Character Roll Tools
@mcp.tool()
def character_roll_execute(
    character_name: str,
    roll_command: str,
    episode_id: str | None = None
) -> str:
    """
    Execute game mechanics roll (abilities, skills, attacks) using character statistics.
    
    Args:
        character_name: Character name
        roll_command: Roll command in natural language (e.g., 'roll STR check', 'roll Blast power attack')
        episode_id: Optional episode ID to write roll results to
    """
    try:
        agent = CharacterRollAgent()
        agent.character_name = character_name
        result = agent.execute_roll(roll_command)
        
        # Write to episode if provided
        if episode_id and result.roll_executed:
            episode_path = workspace_root / f"behaviors/character/characters/{character_name}/episodes/{episode_id}.md"
            agent.write_roll_results_to_episode(character_name, episode_path, result.roll_results)
        
        # Convert result object to structured dict
        result_dict = _serialize_result(result)
        import json
        return json.dumps(result_dict, indent=2)
    except Exception as e:
        return f"Error executing character_roll_execute: {str(e)}"

# Character Chat Tools
@mcp.tool()
def character_chat(
    character_name: str,
    user_input: str,
    mode: Literal["combat", "non-combat"] | None = None,
    output_type: Literal["speak", "act", "both"] | None = None,
    identity: str | None = None,
    context_files: list[str] | None = None
) -> str:
    """
    Build prompt for character chat interaction from template and character profile.
    
    Args:
        character_name: Character name
        user_input: User input/message to the character
        mode: Mode: 'combat' or 'non-combat'
        output_type: Output type: 'speak', 'act', or 'both'
        identity: Identity to use: 'costumed', 'secret', or other identity name
        context_files: Optional list of context file names to include
    """
    try:
        agent = CharacterChatAgent()
        
        # Load profile
        agent.character_name = character_name
        agent.character_profile = agent.load_character_profile(character_name)
        
        # Set identity if provided
        if identity:
            agent.set_identity(identity)
        
        # Build prompt
        prompt = agent.build_prompt(
            user_input,
            mode=mode,
            output_type=output_type,
            context_files=context_files
        )
        
        return prompt
    except Exception as e:
        return f"Error executing character_chat: {str(e)}"

@mcp.tool()
def character_chat_write_response(
    character_name: str,
    user_input: str,
    response: str,
    mode: Literal["combat", "non-combat"] = "non-combat",
    output_type: Literal["speak", "act", "both"] = "speak"
) -> str:
    """
    Write character chat response to current episode file.
    
    Args:
        character_name: Character name
        user_input: Original user input/message to the character
        response: Generated character response
        mode: Mode: 'combat' or 'non-combat' (default: 'non-combat')
        output_type: Output type: 'speak', 'act', or 'both' (default: 'speak')
    """
    try:
        # Get current episode path
        episode_path = get_current_episode_path(character_name)
        if not episode_path:
            return f"Error: No current episode for {character_name}. Use character_episodes with action='start' to create an episode first."
        
        # Write response to episode
        write_response_to_episode(
            episode_path=episode_path,
            character_name=character_name,
            user_input=user_input,
            response=response,
            mode=mode,
            output_type=output_type
        )
        
        return f"Response written to episode: {episode_path}"
    except Exception as e:
        _debug_log(f"Error in character_chat_write_response: {e}")
        traceback.print_exc(file=sys.stderr)
        return f"Error executing character-chat-write-response: {str(e)}"

# Episode Management Tools
@mcp.tool()
def character_episodes(
    character_name: str,
    action: Literal["start", "summarize", "update-plot", "set-current", "list", "undo", "edit"],
    episode_title: str | None = None,
    episode_number: str | int | None = None,
    episode_filename: str | None = None,
    new_user_input: str | None = None,
    new_response: str | None = None
) -> str:
    """
    Manage episodes - set current episode, start new episodes, summarize, update plot, list episodes, undo last entry, or edit last entry.
    
    Args:
        character_name: Character name
        action: Action to perform: 'start', 'summarize', 'update-plot', 'set-current', 'list', 'undo', 'edit'
        episode_title: Episode title (required for 'start' action)
        episode_number: Optional episode number/ID
        episode_filename: Episode filename for 'set-current' action (e.g., "roach-boyt-loves-anticipator.md")
        new_user_input: New user input for 'edit' action (required for 'edit')
        new_response: New response for 'edit' action (required for 'edit')
    """
    try:
        episodes_dir = workspace_root / f"behaviors/character/characters/{character_name}/episodes"
        episodes_dir.mkdir(parents=True, exist_ok=True)
        
        if action == "start":
            # Create new episode - require title
            if not episode_title:
                return "ERROR: episode_title is required for 'start' action. Please provide an episode title."
            
            # Create new episode file with proper name
            creation_result = create_episode_file(
                character_name=character_name,
                episode_title=episode_title,
                episode_description=""
            )
            
            if not creation_result.episode_created:
                return f"Error creating episode: {creation_result.error_message}"
            
            # Set the newly created episode as current
            episode_filename = creation_result.episode_path.name
            set_result = set_current_episode(character_name, episode_filename)
            
            if not set_result['success']:
                return f"Episode created but failed to set as current: {set_result['message']}"
            
            return f"Episode started: {creation_result.episode_path} (title: {episode_title})"
        
        elif action == "list":
            # List all episodes
            episodes = list_episodes(character_name)
            
            if not episodes:
                return f"No episodes found for {character_name}"
            
            result_lines = [f"Episodes for {character_name}:"]
            for ep in episodes:
                current_marker = " [CURRENT]" if ep['is_current'] else ""
                result_lines.append(f"  - {ep['title']} ({ep['filename']}){current_marker}")
            
            return "\n".join(result_lines)
        
        elif action == "set-current":
            # Set an existing episode as current
            if not episode_filename:
                return "ERROR: episode_filename is required for 'set-current' action. Use 'list' action to see available episodes."
            
            set_result = set_current_episode(character_name, episode_filename)
            
            if not set_result['success']:
                return f"Error setting current episode: {set_result['message']}"
            
            return set_result['message']
        
        elif action == "summarize":
            # Summarize episode
            current_episode = get_current_episode_path(character_name)
            if not current_episode:
                return "No current episode to summarize. Start an episode first."
            return f"Episode summary (implementation needed) for: {current_episode}"
        
        elif action == "update-plot":
            # Update plot
            current_episode = get_current_episode_path(character_name)
            if not current_episode:
                return "No current episode to update plot for. Start an episode first."
            return f"Plot updated (implementation needed) for: {current_episode}"
        
        elif action == "undo":
            # Undo last entry
            result = undo_last_episode_entry(character_name)
            if result['success']:
                return f"{result['message']}"
            else:
                return f"Error: {result['message']}"
        
        elif action == "edit":
            # Edit last entry
            if not new_user_input or not new_response:
                return "ERROR: new_user_input and new_response are required for 'edit' action."
            
            result = edit_last_episode_entry(character_name, new_user_input, new_response)
            if result['success']:
                return f"{result['message']}"
            else:
                return f"Error: {result['message']}"
        
        else:
            return f"Unknown action: {action}. Valid actions: start, list, set-current, summarize, update-plot, undo, edit"
    
    except Exception as e:
        _debug_log(f"Error in character_episodes: {e}")
        traceback.print_exc(file=sys.stderr)
        return f"Error executing character_episodes: {str(e)}"

# Character Generate Tool
@mcp.tool()
def character_profile_generate(character_name: str) -> str:
    """
    Generate character profile template structure and interactively populate it.
    
    Args:
        character_name: Character name used for folder and file naming
    """
    try:
        # Validate name
        validation = validate_character_name(character_name)
        if not validation.is_valid:
            return f"Invalid character name: {validation.error_message}"
        
        # Create folder structure
        folder_result = create_character_folder_structure(
            validation.trimmed_name,
            workspace_root / "behaviors/character/characters"
        )
        
        # Copy templates
        template_path = workspace_root / "behaviors/character/behaviors/generate/templates/character_profile_template.md"
        copy_result = copy_character_profile_template(
            validation.trimmed_name,
            workspace_root / "behaviors/character/characters",
            template_path
        )
        
        return f"Character profile generated: {folder_result}, {copy_result}"
    except Exception as e:
        return f"Error executing character-generate-profile: {str(e)}"

if __name__ == "__main__":
    # Run MCP server over stdio (Cursor's preferred method)
    try:
        _debug_log("Starting FastMCP server with stdio transport...")
        mcp.run()
        _debug_log("FastMCP server completed (this should not happen unless server is shutting down)")
    except KeyboardInterrupt:
        _debug_log("Server interrupted by user (KeyboardInterrupt)")
    except Exception as e:
        _debug_log(f"ERROR: server startup failed: {e}")
        traceback.print_exc(file=sys.stderr)
        if _log_file:
            traceback.print_exc(file=_log_file)
        sys.exit(1)
    finally:
        if _log_file:
            _debug_log(f"Closing log file: {_log_file_path}")
            _log_file.close()

