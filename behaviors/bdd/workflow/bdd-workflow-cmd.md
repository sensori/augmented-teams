### Command: `/bdd-workflow`

**[Purpose]:** Orchestrate BDD workflow phases from start to finish. This is a lightweight orchestrator that delegates to phase-specific commands and manages workflow state.

**[Phases]:**
- **Phase 0: Domain Scaffolding** - Generate plain English hierarchy from domain maps (delegates to `/bdd-scaffold`)
- **Phase 1: Build Test Signatures** - Convert scaffold to code structure with empty bodies (delegates to `/bdd-signature`)
- **Phase 2: Write Tests** - Implement tests with Arrange-Act-Assert (delegates to `/bdd-test`)
- **Phase 3: Write Code** - Implement production code to make tests pass (delegates to `/bdd-code`)

**[Operations]:**
- `generate` - Execute current phase generation (delegates to current phase command)
- `validate` - Execute current phase validation (delegates to current phase command)
- `approve` - Approve current phase and advance to next phase
- `jump-to [phase-number]` - Jump to specific phase (0-3)
- `status` - Show current phase and workflow progress
- `restart` - Restart workflow from Phase 0

**Runner:**
* CLI: `python behaviors/bdd/bdd-runner.py workflow [test-file] [framework] [phase] --no-guard`

**Workflow Flow:**
1. **Initialize**: Start workflow with test file and framework
2. **Phase 0** → Generate scaffold → Validate → Approve → **Phase 1**
3. **Phase 1** → Generate signatures → Validate → Approve → **Phase 2**
4. **Phase 2** → Generate tests → Validate → Approve → **Phase 3**
5. **Phase 3** → Generate code → Validate → Approve → **Complete**

**Phase-Specific Details:**
- For detailed requirements of each phase, see phase-specific commands:
  - `/bdd-scaffold` - Domain scaffolding details
  - `/bdd-signature` - Test signature details
  - `/bdd-test` - Test implementation details
  - `/bdd-code` - Code implementation details

**Note:** This orchestrator is VERY LIGHTWEIGHT - it manages state and routes to phase commands. All actual work is done by phase-specific commands.

