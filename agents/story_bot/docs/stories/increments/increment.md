# Story Map: Story Agent

**Navigation:** [📊 Increments](../increments/story-agent-story-map-increments.md)

**File Name**: `story-agent-story-map.md`
**Location**: `{solution_folder}/docs/stories/map/story-agent-story-map.md`

> **CRITICAL MARKDOWN FORMATTING**: All tree structure lines MUST end with TWO SPACES (  ) for proper line breaks. Without two spaces, markdown will wrap lines together into one long line, breaking the visual tree structure.

> **CRITICAL HIERARCHY FORMATTING**: The {epic_hierarchy} section MUST use tree structure characters to show hierarchy:
> - Use `│` (vertical line) for continuing branches
> - Use `├─` (branch) for items that have siblings below them
> - Use `└─` (end branch) for the last item in a group
> - Epic format: `🎯 **Epic Name** (X features, ~Y stories)  `
> - Feature format: `├─ ⚙️ **Feature Name** (~Z stories)  ` or `└─ ⚙️ **Feature Name** (~Z stories)  ` for last feature
> - Story format (when present): `│  ├─ 📝 Story: [Verb-Noun Name]  ` followed by `│  │  *[Component interaction description]*  ` on the next line, or `│  └─ 📝 Story: [Verb-Noun Name]  ` for last story
> - **MANDATORY STORY NAMING FORMAT**: All story names MUST follow Actor-Verb-Noun format:
>   - Story name: Concise Verb-Noun format (e.g., "Create Mob from Selected Tokens", "Display Mob Grouping in Combat Tracker", "Execute Mob Attack with Strategy")
>   - Description: Italicized component interaction description showing component-to-component interactions (e.g., "*GM selects multiple minion tokens on canvas and Mob manager creates mob with selected tokens and assigns random leader*")
> - Example structure:
>   ```
>   🎯 **Epic Name** (2 features, ~8 stories)  
>   │  
>   ├─ ⚙️ **Feature 1** (~5 stories)  
>   │  ├─ 📝 Story: Create Mob from Selected Tokens  
>   │  │  *GM selects multiple minion tokens on canvas and Mob manager creates mob*  
>   │  └─ 📝 Story: Display Mob Grouping  
>   │     *Combat Tracker receives mob creation notification and updates display*  
>   │  
>   └─ ⚙️ **Feature 2** (~3 stories)  
>      └─ 📝 Story: Execute Mob Attack  
>         *Combat Tracker moves to mob leader's turn and Mob manager forwards action*  
>   ```

## System Purpose
Enable product owners, business analysts, and developers to use AI in a structured way for story shaping, discovery, exploration, and specification following Agile by Design practices. Accelerate story development from weeks/months to hours by providing structured AI assistance integrated into Cursor/VS Code environment.

---

## Legend
- 🎯 **Epic** - High-level capability
- 📂 **Sub-Epic** - Sub-capability (when epic has > 9 features)
- ⚙️ **Feature** - Cohesive set of functionality
- 📝 **Story** - Small increment of behavior (3-12d)

---

## Story Map Structure

🎯 **Start Story Development Session** (9 features, ~40 stories)  

├─ ⚙️ **Initialize Story Agent Workflow** (~5 stories)  
│  ├─ 📝 Story: User Adds Context to Chat  
│  │  *User adds documents, models, text descriptions, diagrams to Cursor/VS Code chat window and requests to start shaping/planning/building a new project*  
│  ├─ 📝 Story: AI Chat Invokes Story Agent MCP  
│  │  *AI Chat detects story shaping request and calls Story Agent MCP Server via agent_get_state or agent_get_instructions tool*  
│  ├─ 📝 Story: Initialize Agent  
│  │  *MCP Server receives tool call from AI Chat and requests Agent instance from AgentStateManager, which creates and initializes Agent with agent_name='stories', sets up configuration file paths*  
│  ├─ 📝 Story: Initialize Project  
│  │  *Agent creates Project instance and delegates project area determination to Project. Project determines project_area for new project, presents to user for confirmation, saves to agent_state.json, and completes initialization*  
│  └─ 📝 Story: Initialize Behavior and Workflow  
│     *After Project initialization, Agent loads base and Story Agent configurations (instruction templates, trigger words, Rules, Behaviors), connects Workflow to Project, Workflow sets up stages, and Agent starts workflow at first behavior and action*  

[Rest of the story map continues with other features...]

---

## Source Material

**Shape Phase:**
- Primary source: Story Agent requirements and architecture
- Sections referenced: Initialize Story Agent Workflow feature
- Date generated: [Current date]
- Context: Initial story shaping for workflow initialization
