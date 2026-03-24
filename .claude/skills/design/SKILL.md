---
name: design
description: Crystallize brainstorming into a structured implementation plan. Reads DECISIONS.md for conflicts, auto-classifies scope (Q/S/P), and outputs an actionable plan. Optionally loads a specialist agent for domain expertise.
argument-hint: "[topic] [using <agent-name>]"
allowed-tools: Read, Glob, Grep, Bash, Edit
---

# Design

Crystallize brainstorming into a structured implementation plan. Use at the start or end of brainstorming to formalize an approach. Optionally reference a specialist agent from the catalog for domain-specific expertise.

## Steps

### 0. Load Specialist Agent (optional)

Parse the user's input for a `using <agent-name>` pattern (e.g., `/design build login page using engineering-frontend-developer`).

**If an agent name is provided:**

1. Search for `<agent-name>.md` in `.claude/agents/` first (installed agents)
2. If not found, search in `.claude/agent-catalog/**/` (catalog agents)
3. Read the agent file and extract these sections as domain context:
   - **Core Mission** -- what this specialist focuses on
   - **Critical Rules** -- domain constraints to respect
   - **Workflow Process** -- recommended approach for this domain
4. Keep this context loaded for Steps 1-5 below

**If no agent name is provided but `.claude/agent-catalog/manifest.json` exists:**

1. Read the manifest to get available categories and agents
2. Based on the topic keywords, suggest 1-3 relevant specialist agents. Examples:
   - Frontend/UI/CSS/React -> `engineering-frontend-developer`, `design-ui-designer`
   - Backend/API/database -> `engineering-backend-architect`, `engineering-database-optimizer`
   - DevOps/CI/deploy -> `engineering-devops-automator`, `engineering-sre`
   - Testing/QA -> `testing-api-tester`, `testing-performance-benchmarker`
   - Security -> `engineering-security-engineer`, `specialized-blockchain-security-auditor`
3. Present suggestions: "Specialist agents available for this topic: `<name>` -- <description>. Re-run with `using <name>` to load domain expertise, or proceed without."

### 1. Check for Conflicts

- Read `docs/DECISIONS.md` -- scan for entries that conflict with or overlap the proposed work
- Read `docs/IMPLEMENTATION_PLAN.md` -- check for active phases or overlapping planned work
- If conflicts found: present the contradiction to the user before proceeding

### 2. Auto-Classify Scope

This is a planning-time estimate based on conversation context. `/done` will later auto-detect actual scope from workspace signals (branch, files changed, diff size, plan state) at completion time.

| Scope | Criteria |
|-------|----------|
| **Q** (Quick) | Trivial, obvious, single-location change (typo, config tweak, one-liner) |
| **S** (Standard) | Fits in one session, clear scope (new feature, multi-file refactor, investigation) |
| **P** (Project) | Needs phased execution across sessions (multi-phase feature, architecture change) |

### 3. Output Structured Plan

When a specialist agent was loaded in Step 0, incorporate its expertise:
- Add a `**Specialist**: <agent-name>` line to the plan header
- Use the agent's **Workflow Process** to inform the Approach steps
- Include the agent's **Critical Rules** as items in the Risks section
- Apply the agent's **Core Mission** priorities when ordering and scoping work

The plan format varies by scope:

#### Q (Quick)
```
## Plan (Quick)
**Fix**: <what to change>
**File**: <target file>
**Recommendation**: Proceed directly -- this is a single-location change.
```

#### S (Standard)
```
## Plan (Standard)
**Scope**: <1-2 sentence summary>
**Branch**: `<fix|feat|refactor>/<short-name>`

### Files to Modify
- <file> -- <what changes>

### Approach
<numbered steps>

### Test Strategy
<what to test and how>

### Risks
- <potential issues>
```

#### P (Project)
```
## Plan (Project)
**Scope**: <1-2 sentence summary>

### Phase 1: <name>
**Acceptance Criteria**:
- [ ] <criterion>
**Files**: <list>
**Approach**: <summary>

### Phase 2: <name>
...
```

For P-scoped plans: write the phase breakdown to `docs/IMPLEMENTATION_PLAN.md` using the same structure shown above (phase name, acceptance criteria, files, approach). The `.claude/agents/implementation-tracker.md` agent validates this format.

### 4. Decision Candidates

List any decisions that should be recorded in `docs/DECISIONS.md`:
- Architectural choices made during planning
- Alternatives considered and rejected
- Constraints or assumptions

### 5. User Confirmation

Present the plan and wait for user approval before implementation begins.
