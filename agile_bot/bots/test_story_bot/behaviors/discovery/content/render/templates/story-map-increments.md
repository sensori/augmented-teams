# Story Map Increments: {product_name}

**Navigation:** [📋 Story Map](../map/{product_name_slug}-story-map.md)

**File Name**: `{product_name_slug}-story-map-increments.md`
**Location**: `{solution_folder}/docs/stories/{product_name_slug}-story-map-increments.md`

> **CRITICAL MARKDOWN FORMATTING**: All tree structure lines MUST end with TWO SPACES (  ) for proper line breaks. Without two spaces, markdown will wrap lines together into one long line, breaking the visual tree structure.

## Increment Planning Philosophy

**🎯 VERTICAL SLICES - NOT Horizontal Layers**

Each increment should deliver a **thin end-to-end working flow** across multiple features/epics, NOT complete one feature/epic at a time.

- ✅ **DO**: Include PARTIAL features from MULTIPLE epics in each increment
- ✅ **DO**: Ensure each increment demonstrates complete flow: input → process → validate → persist → display
- ✅ **DO**: Layer complexity across increments (simple first, then add users/scenarios/edge cases)
- ❌ **DON'T**: Complete entire Epic A, then Epic B, then Epic C
- ❌ **DON'T**: Build increments that can't demonstrate working end-to-end flow

**Layering Strategy:**
- **Increment 1**: Simplest user + simplest scenario + happy path → Full end-to-end
- **Increment 2**: Add complexity (more options, validations) + Additional users → Full end-to-end  
- **Increment 3**: Add edge cases + Error handling + Advanced features → Full end-to-end

## Legend
- 🎯 **Epic** - High-level capability
- 📂 **Sub-Epic** - Sub-capability (when epic has > 9 features)
- ⚙️ **Feature** - Cohesive set of functionality
- 📝 **Story** - Small increment of behavior (3-12d)

---

## Increment <number>: <increment_name>

<increment_description>

### Stories Included:

- 🎯 **Epic**: <Epic Name>
  - ⚙️ **Feature**: <Feature Name>
    - 📝 <Story Name>
    - 📝 <Story Name>
  - ⚙️ **Feature**: <Feature Name>
    - 📝 <Story Name>
- 🎯 **Epic**: <Another Epic Name>
  - ⚙️ **Feature**: <Feature Name>
    - 📝 <Story Name>

**Example:**
## Increment 1: Initialize Behavior and Workflow

Delivers complete end-to-end flow for initializing a project and starting the first behavior.

### Stories Included:

- 🎯 **Epic**: Initialize Behavior and Workflow
  - ⚙️ **Feature**: Initialize Project
    - 📝 User provides project path in chat window
    - 📝 Project loads agent configuration from agent.json
  - ⚙️ **Feature**: Start First Behavior
    - 📝 Workflow creates first behavior state
    - 📝 Behavior presents clarification questions

{increments_organized}

---

## Source Material

{source_material}
