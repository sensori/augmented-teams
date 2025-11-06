# Behavior Consistency Feature

The **Behavior Consistency** feature identifies and summarizes overlapping, inconsistent, or contradictory AI behaviors. It helps keep your AI's behavior library semantically coherent as it grows.

## Implementation

The behavior consistency is implemented in `code-agent-runner.py` via the `behavior_consistency()` function according to `code-agent-consistency-rule.mdc`.

### Rule Compliance

**Always:**
- ✅ Scan all active rules and commands for similar intent or wording
- ✅ Flag overlaps (same purpose, different approach)
- ✅ Flag contradictions (opposite guidance for the same context)
- ✅ Flag inconsistencies (naming, tone, or scope mismatch)
- ✅ Summarize issues for human review, not automatic enforcement
- ✅ Use OpenAI function calling for semantic analysis

**Never:**
- ❌ Edit, merge, or delete files automatically
- ❌ Treat stylistic differences as inconsistencies
- ❌ Override intentional divergence (e.g., feature-specific exceptions)

### Semantic Analysis

The consistency check uses OpenAI function calling to perform semantic analysis of behavior content. It compares behaviors for:

1. **Overlaps** - Behaviors with similar purpose but different approaches
2. **Contradictions** - Behaviors with opposite guidance for the same context
3. **Inconsistencies** - Behaviors with naming, tone, or scope mismatches

### Configuration

**Environment Setup:**
- Requires `OPENAI_API_KEY` environment variable
- Loads from `behaviors/.env`, `.env`, or system environment
- Install dependencies: `pip install openai python-dotenv`

**Function Schema:**
The implementation uses OpenAI function calling with a predefined schema for analyzing:
- Overlaps (behavior1, behavior2, similarity, difference, recommendation)
- Contradictions (behavior1, behavior2, context, contradiction, recommendation)
- Summary of findings

### Usage

```bash
# Check all behaviors
python behaviors/code-agent/code-agent-runner.py consistency

# Check specific feature
python behaviors/code-agent/code-agent-runner.py consistency <feature>
```

### Current Status

The consistency check is currently a **placeholder implementation** that:
- Validates OpenAI package installation
- Checks for API key configuration
- Defines the analysis schema
- Prints a placeholder message

**To fully implement:**
1. Load behavior files from deployed features
2. Extract content from rules and commands
3. Call OpenAI API with function calling
4. Parse and format the analysis results
5. Generate a markdown report

### Output

When fully implemented, the script will generate a report with:
- Summary of behaviors analyzed
- List of overlaps with similarity descriptions
- List of contradictions with conflict descriptions
- List of inconsistencies with issue descriptions
- Recommendations for each issue

### When to Run

* After behaviors are created, updated, changed, or deleted
* As part of the behavior maintenance workflow (after sync and index)
* Before committing behavior changes to catch inconsistencies early
* Periodically to maintain semantic coherence as the behavior library grows

### Integration with Workflow

The consistency check integrates with your existing behavior workflow:

```
1. Edit behavior file → File change detected
2. Run sync: python behaviors/code-agent/code-agent-runner.py sync
3. Run index: python behaviors/code-agent/code-agent-runner.py index
4. Run consistency: python behaviors/code-agent/code-agent-runner.py consistency
5. Review findings and resolve issues
```

### Future Enhancements

Potential improvements:
- Auto-trigger on file changes (watch mode)
- Integration with VS Code tasks for automatic checks
- Caching of analysis results to avoid redundant API calls
- Severity levels for different types of issues
- Interactive resolution workflow

## Related Files

- `code-agent-consistency-rule.mdc` - The rule definition
- `code-agent-consistency-cmd.md` - Command documentation
- `code-agent-runner.py` - Implementation (`behavior_consistency()` function)
