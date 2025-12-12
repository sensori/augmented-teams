# Story Bot CLI Wrapper (PowerShell)

    # Get script directory
    $SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

    # Prefer setting WORKING_DIR explicitly for runtime file I/O. If not set,
    # derive a sensible default from the script location.
    if (-not $env:WORKING_DIR) {
        $env:WORKING_DIR = (Resolve-Path "$SCRIPT_DIR\..\..\..").Path
    }

    # Run Python CLI script (it resolves WORKING_AREA itself)
    python "$SCRIPT_DIR\src\story_bot_cli.py" $args
    