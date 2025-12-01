# Story Map Validation Summary

## Analysis: Story Graph → DrawIO Mapping According to Rules

This document validates that `story-map-outline.drawio` correctly represents `story-graph.json` according to `story-map-construction-rules.mdc`.

---

## Epic 1: "Build Agile Bots" (sequential_order: 1)

### Expected Position
- **X**: 20
- **Y**: 130
- **Width**: Should span all sub-epics
- **Height**: 60
- **Style**: Purple/lavender (#e1d5e7)

### Sub-Epic 1: "Generate Bot Server And Tools" (sequential_order: 1)

**Expected Position:**
- **X**: 20 (epic x + 0, or epic x + 10 per rules)
- **Y**: 200
- **Width**: Should span all stories
- **Height**: 70
- **Style**: Green (#d5e8d4)

**Stories in Graph (in sequential_order):**

1. **"Provides Context of New Bot"** (sequential_order: 1, connector: "and", users: ["Human"])
   - **Expected**: x=32, y=337 (yellow, user story)
   - **User "Human"**: x=30, y=277 (above first story)

2. **"Generate MCP Bot Server"** (sequential_order: 2, connector: "or", users: [])
   - **Expected**: Below sequential stories, y=402+ (OR story)
   - **User**: None (empty users array)

3. **"Drop Bot Builder Behavior into Chat"** (sequential_order: 3, connector: "and", users: ["Human"])
   - **Expected**: x=92, y=337 (horizontal flow, 60px spacing)
   - **User "Human"**: Should NOT appear again (same user as story 1)

4. **"Creates Bot Scaffolding"** (sequential_order: 4, connector: "and", users: ["AI Chat"])
   - **Expected**: x=152, y=337 (horizontal flow)
   - **User "AI Chat"**: x=150, y=277 (new user, show above this story)

5. **"Generate Bot Tools"** (sequential_order: 5, connector: "and", users: ["Human"])
   - **Expected**: x=212, y=337 (horizontal flow)
   - **User "Human"**: Should appear again (user changed from "AI Chat" back to "Human")

6. **"Generate Behavior Tools"** (sequential_order: 6, connector: "and", users: ["Human"])
   - **Expected**: x=272, y=337 (horizontal flow)
   - **User "Human"**: Should NOT appear (same user as story 5)

7. **"Generate Behavior Action Tools"** (sequential_order: 7, connector: "and", users: ["Human"])
   - **Expected**: x=332, y=337 (horizontal flow)
   - **User "Human"**: Should NOT appear (same user as story 6)

8. **"Deploy MCP BOT Server"** (sequential_order: 8, connector: "and", users: ["Human"])
   - **Expected**: x=392, y=337 (horizontal flow)
   - **User "Human"**: Should NOT appear (same user as story 7)

---

## Epic 2: "Invoke MCP Bot Server" (sequential_order: 2)

### Expected Position
- **X**: 540 (after Epic 1 width + spacing)
- **Y**: 130
- **Width**: Should span all sub-epics
- **Height**: 60

### Sub-Epic 1: "Init Project" (sequential_order: 1)

**Expected Position:**
- **X**: 550 (epic x + 10)
- **Y**: 200
- **Width**: Should span all stories
- **Height**: 70

**Stories in Graph:**

1. **"Shares Context and Project Location"** (sequential_order: 1, connector: "and", users: ["Human"], **has nested stories**)
   - **Expected**: x=562, y=337 (AND story at top)
   - **User "Human"**: x=560, y=277 (new user context, show above)
   - **Nested Stories** (parent has nested stories, so they're considered together):
     - "Drops Behavior Folder in Chat w/ relevant Bot Config" (sequential_order: 1, connector: "and", users: ["Human"])
     - "Determine Working Area From Current Dir" (sequential_order: 2, connector: "and", users: ["AI Chat"])
     - "Confirm Location" (sequential_order: 3, connector: "and", users: ["Human"])
   - **Note**: According to rules, nesting has no impact on positioning - nested stories follow normal connector rules. Since all nested stories are "and", they should flow horizontally at y=337, not below.

2. **"Speaks Trigger Words For Bot Tool"** (sequential_order: 2, connector: "or", users: ["Human"], **has nested stories**)
   - **Expected**: Below sequential stories, y=404.75 (OR story)
   - **User "Human"**: x=550, y=290 (user changed, show above)
   - **Nested Story**: "Intercept Tool Call With Project Check" (sequential_order: 1, connector: "and", users: ["AI Chat"])
     - **Exception Rule**: AND nested in OR - should start to the right of OR story, not at y=337
     - **Expected**: x=612, y=404.75 (to right of OR story at x=562)

3. **"Locate Existing Project State"** (sequential_order: 2, connector: "and", users: ["Bot Project"], **has nested stories**)
   - **Expected**: x=612, y=337 (AND story, horizontal flow)
   - **User "Bot Project"**: x=610, y=277 (new user)
   - **Nested Stories**:
     - "Confirm Location" (sequential_order: 1, connector: "and")
     - "Move to Project" (sequential_order: 2, connector: "and")
   - **Note**: Nested stories follow normal positioning - both are "and", so should be at y=337

4. **"Generates Project Scaffold"** (sequential_order: 3, connector: "or", users: ["Bot Project"], **has nested stories**)
   - **Expected**: Below sequential stories, y=404.75+ (OR story)
   - **User "Bot Project"**: Should NOT appear (same user as story 3)
   - **Nested Stories**:
     - "Confirm Location" (sequential_order: 1, connector: "and")
     - "Create Project Folder" (sequential_order: 2, connector: "and")
   - **Exception Rule**: AND nested in OR - nested stories should start to right of OR story

5. **"Save Project State to Agent State File"** (sequential_order: 4, connector: "opt", users: ["Bot Project"])
   - **Expected**: Below sequential stories, y=402+ (OPT story)
   - **User "Bot Project"**: Should NOT appear (same user as story 4)

6. **"Update Project Area and Create Directory Structure"** (sequential_order: 5, connector: "opt", users: ["Bot Project"])
   - **Expected**: Below, stacked vertically, y=402+55px = 457+ (OPT story, according to sequential_order)
   - **User "Bot Project"**: Should NOT appear (same user)

---

## Key Validation Points

### ✅ Correct Mappings
1. Epics at y=130
2. Sub-epics at y=200
3. Users positioned above stories (y=277-290)
4. Sequential AND stories at y=337
5. OR/OPT stories below (y=402+)

### ⚠️ Potential Issues to Verify

1. **User Deduplication**: 
   - Multiple AND stories with "Human" should only show user above first story
   - User should appear again when user changes

2. **Nested Stories Positioning**:
   - Stories with nested stories are considered together as a unit
   - Nesting itself doesn't affect positioning - nested stories follow normal connector rules
   - **Exception**: AND nested in OR starts to right of OR story

3. **OR Story Positioning**:
   - "Generate MCP Bot Server" (connector: "or") should be below, not at y=337
   - All OR stories should appear below sequential stories

4. **Story Spacing**:
   - Horizontal: 60px between story centers
   - Vertical for OPT/OR: ~55px spacing according to sequential_order

---

## Recommendations

1. Verify all stories from graph are present in DrawIO
2. Verify user circles follow deduplication rule (only show when user changes)
3. Verify OR/OPT stories are below, not at top level
4. Verify nested AND stories in OR stories start to right of OR story
5. Verify all story types have correct colors (user=yellow, system=dark blue, technical=black)
