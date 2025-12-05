# Story Map: Mob/Minion Management for Foundry VTT

**File Name**: `story-map.md`  
**Location**: `demo/mob_minion/docs/stories/story-map.md`

> **CRITICAL MARKDOWN FORMATTING**: All tree structure lines MUST end with TWO SPACES (  ) for proper line breaks. Without two spaces, markdown will wrap lines together into one long line, breaking the visual tree structure.

## System Purpose
Enable Game Masters to group minions into mobs that act together, reducing the need to click on every individual minion token. Mobs execute coordinated actions based on selected strategies, allowing unified control of multiple minions through a single interaction.

---

## Legend
- 🎯 **Epic** - High-level capability
- ⚙️ **Sub-Epic** - Sub-capability
- 📝 **Story** - Small increment of behavior

---

## Story Map Structure

🎯 **Group Minions into Mobs** (2 sub-epics, ~10 stories)  
│  
├─ ⚙️ **Create and Edit Mobs** (5 stories)  
│  ├─ 📝 Story: Select multiple minion tokens on canvas when preparing for combat  
│  │  *Game Master selects multiple minion tokens on canvas when preparing for combat*  
│  ├─ 📝 Story: Create mob with selected tokens and assign random leader  
│  │  *Game Master creates mob with selected tokens and system assigns random leader*  
│  ├─ 📝 Story: Display mob grouping in combat tracker showing all members  
│  │  *System displays mob grouping in combat tracker showing all members*  
│  ├─ 📝 Story: Edit mob membership by adding or removing minion tokens  
│  │  *Game Master edits mob membership by adding or removing minion tokens*  
│  └─ 📝 Story: Delete mob and return minions to individual control  
│     *Game Master deletes mob and system returns minions to individual control*  
│  
└─ ⚙️ **Spawn Mobs from Actors** (5 stories)  
   ├─ 📝 Story: Select actor templates when creating mob from library  
   │  *Game Master selects actor templates when creating mob from library*  
   ├─ 📝 Story: Spawn mob from selected actor templates on canvas  
   │  *Game Master spawns mob from selected actor templates on canvas*  
   ├─ 📝 Story: Create reusable mob template from selected actors and configuration  
   │  *Game Master creates reusable mob template from selected actors and configuration*  
   ├─ 📝 Story: Save mob template to library for future use  
   │  *Game Master saves mob template to library for future use*  
   └─ 📝 Story: Load saved mob template and spawn mob on canvas  
      *Game Master loads saved mob template and spawns mob on canvas*  

🎯 **Select and Configure Mob Strategies** (2 sub-epics, ~8 stories)  
│  
├─ ⚙️ **Select Strategy Type** (5 stories)  
│  ├─ 📝 Story: Select attack most powerful target strategy when mob needs to eliminate strongest threat  
│  │  *Game Master selects attack most powerful target strategy when mob needs to eliminate strongest threat*  
│  ├─ 📝 Story: Select attack weakest target strategy when mob needs quick eliminations  
│  │  *Game Master selects attack weakest target strategy when mob needs quick eliminations*  
│  ├─ 📝 Story: Select defend leader strategy when mob leader is under threat  
│  │  *Game Master selects defend leader strategy when mob leader is under threat*  
│  ├─ 📝 Story: Select attack most damaged target strategy when mob needs to finish off wounded enemies  
│  │  *Game Master selects attack most damaged target strategy when mob needs to finish off wounded enemies*  
│  └─ 📝 Story: Select attack common target strategy when mob needs coordinated focus fire  
│     *Game Master selects attack common target strategy when mob needs coordinated focus fire*  
│  
└─ ⚙️ **Configure Strategy Settings** (3 stories)  
   ├─ 📝 Story: Open mob configuration panel when clicking on mob leader token or combat tracker entry  
   │  *Game Master opens mob configuration panel when clicking on mob leader token or combat tracker entry*  
   ├─ 📝 Story: Display current strategy and available options in configuration panel  
   │  *System displays current strategy and available options in configuration panel*  
   └─ 📝 Story: Save strategy configuration and apply to mob for future actions  
      *Game Master saves strategy configuration and system applies to mob for future actions*  

🎯 **Choose Targets for Mob Actions** (2 sub-epics, ~6 stories)  
│  
├─ ⚙️ **Apply Strategy-Based Target Selection** (4 stories)  
│  ├─ 📝 Story: System queries combat tracker for available enemy targets when mob's turn begins  
│  │  *System queries combat tracker for available enemy targets when mob's turn begins*  
│  ├─ 📝 Story: System calculates power levels for each available target based on combat stats  
│  │  *System calculates power levels for each available target based on combat stats*  
│  ├─ 📝 Story: System applies selected strategy rules to determine optimal target  
│  │  *System applies selected strategy rules to determine optimal target*  
│  └─ 📝 Story: Display selected target in combat tracker with visual indicator  
│     *System displays selected target in combat tracker with visual indicator*  
│  
└─ ⚙️ **Manual Target Override** (2 stories)  
   ├─ 📝 Story: Override strategy-selected target when manual control is needed  
   │  *Game Master overrides strategy-selected target when manual control is needed*  
   └─ 📝 Story: Manually select target token for mob action from available enemies  
      *Game Master manually selects target token for mob action from available enemies*  

🎯 **Execute Mob Actions** (3 sub-epics, ~10 stories)  
│  
├─ ⚙️ **Execute Unified Mob Action** (3 stories)  
│  ├─ 📝 Story: Click on any mob member token when ready to execute mob action  
│  │  *Game Master clicks on any mob member token when ready to execute mob action*  
│  ├─ 📝 Story: System forwards selected action to all mob members simultaneously  
│  │  *System forwards selected action to all mob members simultaneously*  
│  └─ 📝 Story: System executes same action for all mob members with selected target  
│     *System executes same action for all mob members with selected target*  
│  
├─ ⚙️ **Execute Attack Types** (5 stories)  
│  ├─ 📝 Story: Execute ranged attack for all mob members against selected target  
│  │  *Game Master executes ranged attack for all mob members against selected target*  
│  ├─ 📝 Story: Execute melee attack with automatic movement when target is out of range  
│  │  *Game Master executes melee attack with automatic movement when target is out of range*  
│  ├─ 📝 Story: Execute area attack affecting multiple targets within range  
│  │  *Game Master executes area attack affecting multiple targets within range*  
│  ├─ 📝 Story: Attack fleeing targets when enemies attempt to retreat  
│  │  *Game Master attacks fleeing targets when enemies attempt to retreat*  
│  └─ 📝 Story: Move mob members to target location when melee attack requires positioning  
│     *System moves mob members to target location when melee attack requires positioning*  
│  
└─ ⚙️ **Display Action Results** (2 stories)  
   ├─ 📝 Story: Display formatted attack results in chat showing hits, misses, and damage for all mob members  
   │  *System displays formatted attack results in chat showing hits, misses, and damage for all mob members*  
   └─ 📝 Story: Update combat tracker with damage dealt and status changes for all participants  
      *System updates combat tracker with damage dealt and status changes for all participants*  

---

## Domain Concepts

### Core Domain Concepts

**Mob**: Collection of minions that act together for unified control. Maintains membership and executes coordinated actions based on strategies.

**Minion**: Individual token/actor that can be grouped into a mob. Belongs to Foundry VTT Token and Actor systems.

**Strategy**: Defines target selection rules and attack behavior patterns. Configures mob behavior for coordinated actions.

**Target Selection**: Determines target based on strategy, evaluates available targets, and applies strategy rules.

**Attack Execution**: Executes attacks for all mob members, handles different attack types (ranged, melee, area), and coordinates movement.

**Mob Template**: Defines mob configuration for spawning, stores actor references and spawn parameters.

---

## Source Material

- Input: User requirements for minion/mob management in Foundry VTT
- Technical specifications: Foundry VTT system integration requirements
- Planning decisions: Business capability grouping, deep user workflow focus, end-to-end user-system behavior
