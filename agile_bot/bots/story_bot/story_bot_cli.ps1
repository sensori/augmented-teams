# Story Bot CLI Wrapper (PowerShell)

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$WORKSPACE_ROOT = (Resolve-Path "$SCRIPT_DIR\..\..\..").Path

# Run Python CLI script with all arguments passed through
python "$SCRIPT_DIR\src\story_bot_cli.py" $args
