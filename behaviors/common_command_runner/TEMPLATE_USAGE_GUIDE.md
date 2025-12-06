# Template Usage Guide

## Overview

This guide explains how to create and use templates in the command infrastructure. Templates provide structure and formatting, while commands provide logic and orchestration, and prompts provide decision-making guidance.

---

## Division of Responsibility

### Templates (Structure & Formatting)
**What they define:**
- Document structure (section headings, order)
- Formatting (emojis, tree characters, markdown syntax)
- Static content (legends, instructions, examples)
- Placeholder locations

**What they DON'T define:**
- Business logic or decision-making
- What content to generate
- Which principles apply
- Workflow or orchestration

### Commands (Orchestration & Workflow)
**What they do:**
- Load templates
- Fill placeholders with generated content
- Coordinate workflow steps
- Handle file operations
- Call validation heuristics

**What they DON'T do:**
- Define document structure
- Make formatting decisions
- Duplicate content that belongs in templates

### Prompts (Logic & Decision-Making)
**What they guide:**
- Which principles to apply and HOW
- What decisions to make
- What content to include
- Where assumptions will be made
- What questions to ask users

**What they DON'T include:**
- Detailed formatting instructions
- Section heading specifications
- Emoji or syntax details

---

## Using Templates in Commands

### Base Template Methods

All `Command` classes have these methods available:

```python
def load_template(self, template_path: str) -> str:
    """Load template file content"""
    # Returns: template content as string
    
def fill_template(self, template_content: str, **kwargs) -> str:
    """Fill template placeholders using str.format()"""
    # Returns: filled content with placeholders replaced
    
def load_and_fill_template(self, template_path: str, **kwargs) -> str:
    """Load template and fill placeholders in one step"""
    # Returns: fully filled template content
```

### Example: Loading and Filling a Template

```python
class MyCommand(Command):
    def generate(self):
        # Load template
        template_path = Path(__file__).parent / "templates" / "my-template.md"
        
        # Fill placeholders
        result = self.load_and_fill_template(
            str(template_path),
            placeholder1="value1",
            placeholder2="value2",
            placeholder3="value3"
        )
        
        # Write to file or return to user
        output_path = Path("output/my-document.md")
        output_path.write_text(result, encoding='utf-8')
        
        return result
```

---

## Creating New Templates

### Step 1: Extract from Actual Output

**DO:**
1. Generate content using current command
2. Review actual output files
3. Extract common structure
4. Identify variable content → make placeholders

**DON'T:**
1. Create templates from scratch
2. Guess at structure without seeing real output
3. Copy outdated templates

### Step 2: Define Placeholders

**Placeholder syntax:** `{placeholder_name}`

**Naming conventions:**
- Use `snake_case` for multi-word names
- Be descriptive: `{feature_name}` not `{name}`
- Use consistent names across templates

**Common placeholder patterns:**
```python
# Entity names
{product_name}          # "MM3E Online Character Creator"
{product_name_slug}     # "mm3e-character-creator" (for filenames)
{epic_name}             # "Create Character"
{feature_name}          # "Allocate Abilities"
{story_name}            # "User increases ability rank"

# Content sections
{system_purpose}        # High-level purpose paragraph
{epic_hierarchy}        # Full epic/feature/story tree structure
{domain_concepts}       # Domain AC concepts section
{stories_with_ac}       # All stories with acceptance criteria

# Metadata
{story_count}           # Number of stories (e.g., "7")
{source_material}       # Source tracking section
{notes}                 # Additional notes section
```

### Step 3: Create Template File

**Template structure:**
```markdown
# {main_heading}

**File Name**: `{filename}`

## Section 1

{content_placeholder_1}

---

## Section 2

{content_placeholder_2}

---

## Section 3 (Static Content)

This section has static instructions that don't change.
- Static bullet point
- Another static point

---

## Section 4

{content_placeholder_3}
```

### Step 4: Update Command to Load Template

**In command's `__init__` or `generate()`:**
```python
generate_instructions = """Generate content using template.

TEMPLATE TO LOAD:
- behaviors/{feature}/templates/{template-name}.md

PLACEHOLDERS TO FILL:
- {placeholder1}: Description of what to generate
- {placeholder2}: Description of what to generate

APPLY PRINCIPLES:
- §X.Y Principle name and how to apply it

Template defines structure. YOU define content following principles."""
```

### Step 5: Test Template

**Create test:**
```python
def test_my_template():
    cmd = MyCommand(content, rule)
    result = cmd.load_and_fill_template(
        "path/to/template.md",
        placeholder1="test value 1",
        placeholder2="test value 2"
    )
    
    # Verify structure
    assert "# Main Heading" in result
    assert "## Section 1" in result
    assert "test value 1" in result
```

---

## Template Locations

### Standard Locations

```
behaviors/
└── {feature}/
    └── templates/
        ├── {feature}-{document-type}-template.md
        ├── {feature}-{another-type}-template.md
        └── ...
```

### Stories Templates

```
behaviors/stories/templates/
├── story-doc-template.md              # Individual story files
├── story-map-decomposition-template.md # Story map hierarchical view
├── story-map-increments-template.md   # Story map increments view
├── feature-overview-template.md       # Feature-level Domain AC + stories
├── epic-overview-template.md          # Epic-level shared Domain AC
└── sub-epic-overview-template.md      # Sub-epic-level shared Domain AC
```

### Specification Templates

```
behaviors/stories/specification/
└── scenario-template.md               # Given/When/Then scenarios
```

---

## Best Practices

### 1. Keep Templates Simple
- ✅ Use simple `{placeholder}` syntax
- ✅ Static structure, variable content
- ❌ Don't put logic in templates (use code for that)
- ❌ Don't put conditional content (templates are filled once)

### 2. Maintain Consistency
- ✅ Use same placeholder names across related templates
- ✅ Follow same section ordering patterns
- ✅ Use consistent heading levels

### 3. Document Placeholders
- ✅ List all placeholders in command instructions
- ✅ Describe what content goes in each placeholder
- ✅ Provide examples of filled content

### 4. Test Templates
- ✅ Create test script for each new template
- ✅ Verify filled output matches expected format
- ✅ Compare against actual generated files

### 5. Version Control
- ✅ Keep templates in git
- ✅ Review template changes like code changes
- ✅ Document why structure changed

---

## Examples from Stories Behavior

### Example 1: Story Document Template

**Template:** `behaviors/stories/templates/story-doc-template.md`

```markdown
# 📝 {story_name}

**Epic:** {epic_name}
**Feature:** {feature_name}

## Story Description

{story_name}

## Acceptance Criteria

- [ ] 

## Notes

---

## Source Material

**Inherited From**: Story Map
- See story map "Source Material" section for primary source
- Additional source references will be added during Exploration phase
```

**Usage in StoryArrangeCommand:**
```python
story_content = self.load_and_fill_template(
    str(template_path),
    story_name=story_name,
    epic_name=epic_name,
    feature_name=feature_name
)
```

**Result:**
```markdown
# 📝 User increases ability rank

**Epic:** Create Character
**Feature:** Allocate Abilities

## Story Description

User increases ability rank

## Acceptance Criteria

- [ ] 

...
```

### Example 2: Feature Overview Template

**Template:** `behaviors/stories/templates/feature-overview-template.md`

**Placeholders:**
- `{feature_name}`: "Allocate Abilities"
- `{epic_name}`: "Create Character"
- `{feature_purpose}`: "Enable users to allocate ability ranks..."
- `{domain_concepts}`: Full Domain AC concepts section
- `{domain_behaviors}`: Full Domain AC behaviors section
- `{domain_rules}`: Full Domain AC rules section
- `{stories_with_ac}`: All stories with their acceptance criteria
- `{consolidation_decisions}`: Consolidation rationale
- `{source_material}`: Source tracking

**Usage:** AI generates content for each placeholder following principles, then fills template

---

## Migrating Existing Commands to Templates

### Step-by-Step Migration

**1. Identify Hardcoded Content**
Look for:
- f-strings with document structure
- Long instruction strings with formatting details
- Repeated structure across multiple commands

**2. Extract to Template**
- Copy actual output to new template file
- Replace variable content with `{placeholders}`
- Keep static structure intact

**3. Update Command Code**
- Remove hardcoded content
- Add `load_and_fill_template()` call
- Map variables to placeholder names

**4. Simplify Instructions**
- Remove formatting details from instructions
- Keep logic and decision-making
- Reference template in instructions
- Document placeholder meanings

**5. Test Migration**
- Run command with template
- Compare output to previous version
- Verify structure identical
- Check all content present

---

## Troubleshooting

### Problem: Template not found
```
FileNotFoundError: Template not found: path/to/template.md
```

**Solution:** Verify path is correct relative to command file
```python
# Correct: relative to command file
template_path = Path(__file__).parent / "templates" / "my-template.md"

# Also correct: absolute from workspace
template_path = Path("behaviors/feature/templates/my-template.md")
```

### Problem: KeyError when filling template
```
KeyError: 'placeholder_name'
```

**Solution:** Ensure all placeholders in template are provided in `fill_template()` call
```python
# Template has: {name}, {description}, {author}
# Must provide all three:
result = cmd.fill_template(template, 
    name="value",
    description="value",
    author="value"  # Don't forget any!
)
```

### Problem: Placeholder not replaced
**Symptom:** Output still contains `{placeholder}` text

**Solution:** Check placeholder syntax - must match exactly
```markdown
❌ { placeholder }  # spaces not allowed
❌ {{placeholder}}  # double braces not supported (yet)
✅ {placeholder}    # correct syntax
```

### Problem: Output doesn't match expected format

**Solution:** Compare template to actual generated files
1. Generate file with old method
2. Generate file with template
3. Use diff tool to compare
4. Update template to match exactly

---

## Future Enhancements

### Possible Improvements

**1. Conditional Logic (Jinja2)**
If templates need conditional sections:
```jinja2
{% if has_sub_epics %}
## Sub-Epics
{{ sub_epic_content }}
{% endif %}
```

**2. Loops (Jinja2)**
If templates need repeated sections:
```jinja2
{% for story in stories %}
### {{ story.name }}
{{ story.content }}
{% endfor %}
```

**3. Template Validation**
Create validator script:
- Check placeholder syntax
- Verify section structure
- Validate against schema

**4. Template Library**
Reusable templates across behaviors:
- `common_templates/document-base.md`
- `common_templates/validation-report.md`
- `common_templates/command-doc.md`

---

## Reference

**Implementation Examples:**
- `behaviors/stories/stories_runner.py` - StoryArrangeCommand (line 372)
- `behaviors/stories/templates/` - All story templates
- `behaviors/common_command_runner/common_command_runner.py` - Base template methods (line 872)

**Plans:**
- `behaviors/common_command_runner/TEMPLATE_DRIVEN_STORIES_PLAN.md` - Full refactoring plan
- `behaviors/common_command_runner/REFACTORING_COMPLETE_SUMMARY.md` - What was accomplished

**Tests:**
- Run: `python behaviors/stories/test_template_integration.py`

