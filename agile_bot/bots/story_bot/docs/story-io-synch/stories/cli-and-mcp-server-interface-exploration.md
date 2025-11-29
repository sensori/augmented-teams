# CLI and MCP Server Interface - Increment Exploration

**Navigation:** [📋 Story Map](../map/story-graph.json) | [📊 Increments](../increments/story-io-story-map-increments.md)

**File Name**: `cli-and-mcp-server-interface-exploration.md`
**Location**: `agile_bot/bots/story_bot/docs/stories/increments/cli-and-mcp-server-interface-exploration.md`

**Priority:** High
**Relative Size:** Medium

## Increment Purpose

Story IO CLI and MCP Server provide command-line and programmatic interfaces for rendering and synchronizing story maps so that users and AI agents can interact with story graph operations through both CLI commands and MCP tool calls.

---

## Domain AC (Increment Level)

### Core Domain Concepts

- **Story IO CLI**: Command-line interface that parses user commands and delegates to StoryIODiagram methods
- **Story IO MCP Server**: Multi-agent communication protocol server that exposes story map operations as tools
- **StoryIODiagram**: Core domain model that orchestrates story map lifecycle operations (load, render, synchronize, save)
- **Argument Parser**: CLI component that parses command-line arguments into structured args objects
- **MCP Tool**: Wrapper function that handles tool requests, loads diagrams, executes operations, and returns JSON responses

### Domain Behaviors

- **Story IO CLI parses commands**: Converts command-line arguments into structured args objects with Path attributes
- **Story IO CLI delegates to StoryIODiagram**: Command handlers load diagrams and call diagram methods to perform operations
- **Story IO MCP Server receives tool requests**: MCP tools accept parameters, validate inputs, and execute operations
- **Story IO MCP Server returns JSON responses**: Tools wrap results in JSON strings with success status and operation results
- **StoryIODiagram loads from story graph**: Reads JSON story graph files and constructs in-memory domain model
- **StoryIODiagram renders to DrawIO**: Generates DrawIO XML from story graph and saves to file
- **StoryIODiagram synchronizes from DrawIO**: Extracts story graph from DrawIO XML and optionally compares with original

### Domain Rules

- **CLI commands require story graph path**: Render commands must have --story-graph or --json argument provided
- **MCP tools validate required parameters**: Tools raise ValueError when required parameters (e.g., story_graph_path) are None
- **Layout preservation is optional**: Layout files can be auto-detected by CLI or explicitly provided via layout_json parameter
- **Error handling returns structured responses**: MCP tools catch exceptions and return JSON with success=False and error message
- **CLI commands return exit codes**: Successful operations return 0, errors return 1
- **MCP tools return JSON strings**: All tool responses are JSON-serialized strings with success status and result data

---

## Stories (8 total)

### 📝 Handle Render Outline

**Acceptance Criteria:**
- **When** MCP tool receives render_outline request with story_graph_path, drawio_path, output_path, and layout_json parameters, **then** tool validates that story_graph_path is provided
- **When** story_graph_path is None, **then** tool raises ValueError('story_graph_path is required')
- **When** story_graph_path is provided, **then** tool calls StoryIODiagram.load_from_story_graph(Path(story_graph_path), Path(drawio_path) if drawio_path else None)
- **When** layout_json parameter is provided, **then** tool parses layout_json string using json.loads() to create layout_data dict
- **When** layout_json is None, **then** tool sets layout_data to None
- **When** diagram.render_outline(output_path=Path(output_path), layout_data=layout_data) is called, **then** renderer generates DrawIO XML and saves to output_path
- **When** render completes successfully, **then** tool returns JSON string with success=True, output_path, and summary containing epics count
- **When** render raises exception, **then** tool catches exception and returns JSON string with success=False and error message

### 📝 Invoke Render Outline from CLI

**Acceptance Criteria:**
- **When** argparse parses 'render-outline' command with --story-graph and --output arguments, **then** argparse creates args object with story_graph Path and output Path attributes
- **When** render_outline_command function receives args object, **then** function calls StoryIODiagram.load_from_story_graph(args.story_graph, args.drawio_file)
- **When** layout file is not provided in args, **then** function auto-detects layout by checking output_path.stem-layout.json, story-graph-drawio-extracted-layout.json, and output_path.stem-drawio-extracted-layout.json patterns
- **When** layout file exists, **then** function loads layout_data from JSON file
- **When** diagram.render_outline(output_path, layout_data) is called, **then** renderer generates DrawIO XML and saves to output_path
- **When** render completes, **then** function prints 'Generated DrawIO diagram: {output_path}' and 'Epics: {count}' to stdout
- **When** render succeeds, **then** function returns exit code 0

### 📝 Invoke Render Increments from CLI

**Acceptance Criteria:**
- **When** argparse parses 'render-increments' command with --story-graph and --output arguments, **then** argparse creates args object with story_graph Path and output Path attributes
- **When** render_increments_command function receives args object, **then** function calls StoryIODiagram.load_from_story_graph(args.story_graph, args.drawio_file)
- **When** layout file is provided in args.layout, **then** function loads layout_data from JSON file
- **When** layout file is not provided, **then** function sets layout_data to None
- **When** diagram.render_increments(output_path, layout_data) is called, **then** renderer generates DrawIO XML with increments and saves to output_path
- **When** render completes, **then** function prints 'Generated DrawIO diagram: {output_path}', 'Epics: {count}', and 'Increments: {count}' to stdout
- **When** render succeeds, **then** function returns exit code 0

### 📝 Handle Render Increments

**Acceptance Criteria:**
- **When** MCP tool receives render_increments request with story_graph_path, drawio_path, output_path, and layout_json parameters, **then** tool validates that story_graph_path is provided
- **When** story_graph_path is None, **then** tool raises ValueError('story_graph_path is required')
- **When** story_graph_path is provided, **then** tool calls StoryIODiagram.load_from_story_graph(Path(story_graph_path), Path(drawio_path) if drawio_path else None)
- **When** layout_json parameter is provided, **then** tool parses layout_json string using json.loads() to create layout_data dict
- **When** layout_json is None, **then** tool sets layout_data to None
- **When** diagram.render_increments(output_path=Path(output_path), layout_data=layout_data) is called, **then** renderer generates DrawIO XML with increments and saves to output_path
- **When** render completes successfully, **then** tool returns JSON string with success=True, output_path, and summary containing epics count and increments count
- **When** render raises exception, **then** tool catches exception and returns JSON string with success=False and error message

### 📝 Handle Synchronize Outline

**Acceptance Criteria:**
- **When** MCP tool receives synchronize_outline request with drawio_path, original_path, and output_path parameters, **then** tool creates StoryIODiagram instance with drawio_file=Path(drawio_path)
- **When** original_path parameter is provided, **then** tool sets original to Path(original_path)
- **When** original_path is None, **then** tool sets original to None
- **When** diagram.synchronize_outline(drawio_path=Path(drawio_path), original_path=original) is called, **then** synchronizer extracts story graph from DrawIO XML and compares with original if provided
- **When** output_path parameter is provided, **then** tool calls diagram.save_story_graph(Path(output_path)) to save synchronized graph
- **When** synchronize completes successfully, **then** tool returns JSON string with success=True, epics_count from result, and output_path
- **When** synchronize raises exception, **then** tool catches exception and returns JSON string with success=False and error message

### 📝 Invoke Synchronize Outline from CLI

**Acceptance Criteria:**
- **When** argparse parses 'sync-outline' command with --drawio-file, --original, --output, --generate-report, and --report arguments, **then** argparse creates args object with drawio_file Path, original Path, output Path, generate_report boolean, and report Path attributes
- **When** synchronize_outline_command function receives args object, **then** function creates StoryIODiagram instance with drawio_file=args.drawio_file
- **When** args.original is provided, **then** function sets original_path to Path(args.original)
- **When** args.original is None, **then** function sets original_path to None
- **When** diagram.synchronize_outline(drawio_path, original_path, generate_report) is called, **then** synchronizer extracts story graph from DrawIO and compares with original if provided
- **When** args.output is provided, **then** function calls diagram.save_story_graph(args.output) to save synchronized graph
- **When** args.generate_report is True and args.report is provided, **then** function saves sync_report to args.report JSON file
- **When** synchronize completes, **then** function prints 'Saved story graph to: {output}' or 'Synchronized story graph (use --output to save)' to stdout
- **When** synchronize succeeds, **then** function returns exit code 0

### 📝 Handle Synchronize Increments

**Acceptance Criteria:**
- **When** MCP tool receives synchronize_increments request with drawio_path, original_path, and output_path parameters, **then** tool creates StoryIODiagram instance with drawio_file=Path(drawio_path)
- **When** original_path parameter is provided, **then** tool sets original to Path(original_path)
- **When** original_path is None, **then** tool sets original to None
- **When** diagram.synchronize_increments(drawio_path=Path(drawio_path), original_path=original) is called, **then** synchronizer extracts story graph with increments from DrawIO XML and compares with original if provided
- **When** output_path parameter is provided, **then** tool calls diagram.save_story_graph(Path(output_path)) to save synchronized graph
- **When** synchronize completes successfully, **then** tool returns JSON string with success=True, epics_count and increments_count from result, and output_path
- **When** synchronize raises exception, **then** tool catches exception and returns JSON string with success=False and error message

### 📝 Invoke Synchronize Increments from CLI

**Acceptance Criteria:**
- **When** argparse parses 'sync-increments' command with --drawio-file, --original, --output, --generate-report, and --report arguments, **then** argparse creates args object with drawio_file Path, original Path, output Path, generate_report boolean, and report Path attributes
- **When** synchronize_increments_command function receives args object, **then** function creates StoryIODiagram instance with drawio_file=args.drawio_file
- **When** args.original is provided, **then** function sets original_path to Path(args.original)
- **When** args.original is None, **then** function sets original_path to None
- **When** diagram.synchronize_increments(drawio_path, original_path, generate_report) is called, **then** synchronizer extracts story graph with increments from DrawIO and compares with original if provided
- **When** args.output is provided, **then** function calls diagram.save_story_graph(args.output) to save synchronized graph
- **When** args.generate_report is True and args.report is provided, **then** function saves sync_report to args.report JSON file
- **When** synchronize completes, **then** function prints 'Saved story graph to: {output}' or 'Synchronized story graph (use --output to save)' to stdout
- **When** synchronize succeeds, **then** function returns exit code 0

---

## Consolidation Decisions

- **CLI and MCP stories kept separate**: CLI stories document argument parsing and command delegation, while MCP stories document tool request handling and JSON response formatting. These represent different atomic units of behavior (CLI vs MCP protocol).
- **Render Outline and Render Increments kept separate**: Different render methods (render_outline vs render_increments) have different parameters and outputs, representing distinct atomic behaviors.
- **Synchronize Outline and Synchronize Increments kept separate**: Different synchronization methods extract different structures (outline vs increments), representing distinct atomic behaviors.

---

## Domain Rules Referenced

- **Error handling pattern**: All MCP tools follow consistent error handling - catch exceptions and return JSON with success=False
- **Path conversion pattern**: All file paths are converted to Path objects before passing to StoryIODiagram methods
- **Optional parameter pattern**: Original path and layout data are optional parameters that default to None when not provided
- **Output generation pattern**: CLI commands print to stdout, MCP tools return JSON strings

---

## Source Material

**Shape phase:**
- Primary source: `agile_bot/bots/story_bot/src/story_io/story_io_cli.py` - CLI command implementations
- Primary source: `agile_bot/bots/story_bot/src/story_io/story_io_mcp_server.py` - MCP tool implementations
- Primary source: `agile_bot/bots/story_bot/src/story_io/story_io_diagram.py` - Core domain model methods
- Date generated: 2025-11-29
- Context: Focused exploration on CLI and MCP Server interface stories to document technical interaction points

**Discovery phase:**
- Reads source from Shape phase
- Discovery Refinements: Identified 8 key stories (4 CLI, 4 MCP) covering render and synchronize operations
- Additional sections referenced: Command parsing logic, tool request handling, error handling patterns

**Exploration phase:**
- Inherits source from story map
- Specific sections for acceptance criteria: Technical interaction points documented at Inner System granularity
- Focus: Document atomic units of behavior in code (CLI argument parsing → diagram loading → method calls → output generation)

