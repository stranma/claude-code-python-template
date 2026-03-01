# Implementation Plan

> **Status**: Phase 8 - Complete
> **Last Updated**: 2026-03-01

## Quick Status Summary

| Phase | Name | Status |
|-------|------|--------|
| 1 | Fix 5 Template Bugs | Complete |
| 2 | Permissions Modernization | Complete |
| 3 | Security Hooks | Complete |
| 4 | Productivity Hooks | Complete |
| 5 | Slash Commands | Complete |
| 6 | New Agents | Complete |
| 7 | Review Rules | Complete |
| 8 | GitHub Actions + Config + Documentation | Complete |

---

## Phase 1: Fix 5 Template Bugs

**Goal:** Fix critical setup script bugs preventing correct package customization and workspace builds.

**Acceptance Criteria:**
- [x] Bug 1: rename_packages() updates pyproject.toml package names after directory renames
- [x] Bug 2: rename_packages() updates __init__.py docstrings after directory renames
- [x] Bug 3: Additional packages use -name pattern to avoid false matches (e.g., "core" substring)
- [x] Bug 4: Root pyproject.toml does not include [build-system] section in workspace mode
- [x] Bug 5: Template packages include tests/ directories so pytest discovers package tests
- [x] All documentation uses uv sync --all-packages flag for workspace installs
- [x] PCC includes Step -1 for mandatory feature branch creation
- [x] settings.json allows uv run execution

**Tasks:**
- [x] Add _update_package_contents() helper to update renamed package internals
- [x] Call _update_package_contents() in rename_packages() after directory moves
- [x] Change additional package creation to use -name pattern replacements
- [x] Remove [build-system] from root pyproject.toml template
- [x] Add tests/ directory creation to rename_packages() for new packages
- [x] Update CLAUDE.md, README.md, and tests.yml to use --all-packages flag
- [x] Add PCC Step -1 documentation for feature branch requirement
- [x] Add settings.json with Claude Code server uv run permissions

**Decisions & Trade-offs:**

| Decision | Alternatives Considered | Why This Option |
|----------|------------------------|-----------------|
| Use -name pattern for package name replacements | Bare name replacement (e.g., "core" -> "engine") | Avoids false matches on substrings like "core" appearing in "pyproject" or other unrelated strings; more robust and predictable |

**Phase Completion Steps:**
> After this phase, follow the development process in `docs/DEVELOPMENT_PROCESS.md`: classify as Q/S/P, then execute the corresponding path (validate with agents, ship, document).

---

## Phase 2: Permissions Modernization

**Goal:** Eliminate unnecessary permission prompts, migrate deprecated syntax, and add a permissions management skill.

**Acceptance Criteria:**
- [x] CLAUDE.md instructs Claude to use absolute paths instead of `cd /path && command` chains
- [x] CLAUDE.md instructs Claude to use `TaskOutput` tool instead of `tail`/`cat` on task output files
- [x] All `:*` patterns in settings.json replaced with ` *` (deprecated syntax migration)
- [x] settings.json remains valid JSON
- [x] `.claude/skills/edit-permissions/SKILL.md` created with permission management instructions
- [x] `/edit-permissions` skill is user-invocable and includes pattern syntax, safety rules, and shell operator warnings
- [x] IMPLEMENTATION_PLAN.md updated with Phase 2
- [x] CHANGELOG.md updated with user-facing changes

**Tasks:**
- [x] Add shell command style rules to CLAUDE.md (absolute paths + TaskOutput guidance)
- [x] Modernize settings.json -- replace all `:*` patterns with ` *`
- [x] Create `.claude/skills/edit-permissions/SKILL.md` with permission management instructions
- [x] Update documentation (IMPLEMENTATION_PLAN.md and CHANGELOG.md)
- [x] Add automated permission tests (tests/test_permissions.py) validating structure, syntax, matching, conflicts, security, and evaluation order

**Decisions & Trade-offs:**

| Decision | Alternatives Considered | Why This Option |
|----------|------------------------|-----------------|
| Instruct absolute paths in CLAUDE.md instead of adding `Bash(cd *)` | Adding `Bash(cd *)` to allow list; using PreToolUse hooks to parse chained commands | `Bash(cd *)` doesn't solve the problem (shell operator protection still blocks `cd && cmd`). Hooks add complexity. Absolute paths are simpler and align with existing permission patterns |
| Instruct `TaskOutput` tool usage instead of adding `Read` allow rule for temp dir | Adding `Read(//c/Users/*/AppData/Local/Temp/claude/**)` to settings.json | The temp path is OS-specific and user-specific, making it non-portable for a template. `TaskOutput` is the dedicated built-in tool and needs no file permissions |
| Create custom `.claude/skills/` skill instead of installing `@otrebu/claude-permissions` | Installing community skill ZIP; using built-in `/permissions` command only | Community skill is for claude.ai web (ZIP upload), not Claude Code CLI. Custom skill lives in `.claude/skills/` and ships with the template automatically |

**Phase Completion Steps:**
> After this phase, follow the development process in `docs/DEVELOPMENT_PROCESS.md`: classify as Q/S/P, then execute the corresponding path (validate with agents, ship, document).

---

## Phase 3: Security Hooks

**Goal:** Add 3 security hooks -- the template previously had zero hooks.

**Acceptance Criteria:**
- [x] All 3 hook scripts exist, are executable, have `#!/bin/bash` shebang
- [x] dangerous-actions-blocker exits 2 for blocked patterns, 0 otherwise
- [x] unicode-injection-scanner exits 2 for blocked Unicode, 0 otherwise
- [x] output-secrets-scanner exits 0 always (PostToolUse), emits systemMessage JSON for warnings
- [x] settings.json has hooks section with correct nested structure
- [x] setup_project.py processes .sh files for placeholders
- [x] tests/test_hooks.py passes

**Tasks:**
- [x] Create `.claude/hooks/dangerous-actions-blocker.sh` -- PreToolUse(Bash) blocker
- [x] Create `.claude/hooks/output-secrets-scanner.sh` -- PostToolUse(Bash) scanner
- [x] Create `.claude/hooks/unicode-injection-scanner.sh` -- PreToolUse(Edit|Write) blocker
- [x] Add hooks section to `.claude/settings.json`
- [x] Add `.sh` to `TEXT_EXTENSIONS` in setup_project.py
- [x] Create tests/test_hooks.py

**Decisions & Trade-offs:**

| Decision | Alternatives Considered | Why This Option |
|----------|------------------------|-----------------|
| Hook directory `.claude/hooks/` | Root-level `hooks/` dir; inline scripts in settings.json | Official Claude Code convention for project-scoped hooks |
| Path resolution via `$CLAUDE_PROJECT_DIR` | Hardcoded paths; relative paths | Official env var, works across different checkout locations |
| jq for JSON parsing with graceful degradation | Python JSON parsing; no JSON validation | jq is lightweight and standard for shell JSON; graceful exit 0 if missing avoids blocking developer work |

**Phase Completion Steps:**
> After this phase, follow the development process in `docs/DEVELOPMENT_PROCESS.md`: classify as Q/S/P, then execute the corresponding path (validate with agents, ship, document).

---

## Phase 4: Productivity Hooks

**Goal:** Add auto-format and test-on-change hooks.

**Acceptance Criteria:**
- [x] auto-format.sh runs ruff format and ruff check --fix on edited .py files
- [x] test-on-change.sh discovers and runs associated test file
- [x] Both hooks registered in settings.json PostToolUse for Edit|Write
- [x] tests/test_hooks.py updated with new hook tests

**Tasks:**
- [x] Create `.claude/hooks/auto-format.sh` -- PostToolUse(Edit|Write) formatter
- [x] Create `.claude/hooks/test-on-change.sh` -- PostToolUse(Edit|Write) test runner
- [x] Add PostToolUse hooks to settings.json
- [x] Add tests for new hooks

**Decisions & Trade-offs:**

| Decision | Alternatives Considered | Why This Option |
|----------|------------------------|-----------------|
| auto-format is synchronous (no systemMessage) | Async with systemMessage reporting | Claude must see formatted code before next edit to avoid fighting the formatter |
| test-on-change is informational (systemMessage) | Blocking (exit 2 on test failure) | Failing tests should inform, not block -- developer may be mid-refactor |

**Phase Completion Steps:**
> After this phase, follow the development process in `docs/DEVELOPMENT_PROCESS.md`: classify as Q/S/P, then execute the corresponding path (validate with agents, ship, document).

---

## Phase 5: Slash Commands

**Goal:** Add 3 slash commands for context restoration, security auditing, and pre-deployment checks.

**Acceptance Criteria:**
- [x] `/catchup` command restores context after /clear
- [x] `/security-audit` command runs 6-phase security scan with A-F grading
- [x] `/ship` command runs 3-tier pre-deployment checklist
- [x] All commands have frontmatter with `allowed-tools` and `description`
- [x] tests/test_commands.py passes

**Tasks:**
- [x] Create `.claude/commands/catchup.md`
- [x] Create `.claude/commands/security-audit.md`
- [x] Create `.claude/commands/ship.md`
- [x] Create tests/test_commands.py

**Decisions & Trade-offs:**

| Decision | Alternatives Considered | Why This Option |
|----------|------------------------|-----------------|
| Use `.claude/commands/` not `.claude/skills/` | Skills directory | Commands are simpler (single file) and correct for instruction-set-style content; skills are for more complex multi-file capabilities |
| All commands set `allowed-tools` | No tool restrictions | Scoping tools prevents commands from accidentally modifying code when they should only read |

**Phase Completion Steps:**
> After this phase, follow the development process in `docs/DEVELOPMENT_PROCESS.md`: classify as Q/S/P, then execute the corresponding path (validate with agents, ship, document).

---

## Phase 6: New Agents

**Goal:** Add 3 specialized agents (security-auditor, refactoring-specialist, output-evaluator).

**Acceptance Criteria:**
- [x] security-auditor is read-only (permissionMode: plan, no Bash/Edit/Write)
- [x] refactoring-specialist is read-only (permissionMode: plan, no Bash)
- [x] output-evaluator uses haiku model and dontAsk permissionMode
- [x] All 3 agents follow existing frontmatter pattern
- [x] tests/test_agents.py validates all 12 agents

**Tasks:**
- [x] Create `.claude/agents/security-auditor.md`
- [x] Create `.claude/agents/refactoring-specialist.md`
- [x] Create `.claude/agents/output-evaluator.md`
- [x] Create tests/test_agents.py

**Decisions & Trade-offs:**

| Decision | Alternatives Considered | Why This Option |
|----------|------------------------|-----------------|
| security-auditor and refactoring-specialist are read-only (permissionMode: plan) | acceptEdits or dontAsk | These agents analyze, not modify -- principle of least privilege |
| output-evaluator uses dontAsk | plan or acceptEdits | Designed for automated pipeline integration where prompting would block |
| output-evaluator uses haiku model | sonnet | Scoring is structured and formulaic, doesn't need sonnet's reasoning depth |

**Phase Completion Steps:**
> After this phase, follow the development process in `docs/DEVELOPMENT_PROCESS.md`: classify as Q/S/P, then execute the corresponding path (validate with agents, ship, document).

---

## Phase 7: Review Rules

**Goal:** Add 4 review rules auto-loaded as project context.

**Acceptance Criteria:**
- [x] All 4 rule files exist in `.claude/rules/`
- [x] Rules have frontmatter with `description` field, no `paths:` field
- [x] Each rule is under 80 lines, checklist format
- [x] Rules cover architecture, code quality, performance, test quality
- [x] tests/test_rules.py passes

**Tasks:**
- [x] Create `.claude/rules/architecture-review.md`
- [x] Create `.claude/rules/code-quality-review.md`
- [x] Create `.claude/rules/performance-review.md`
- [x] Create `.claude/rules/test-review.md`
- [x] Create tests/test_rules.py

**Decisions & Trade-offs:**

| Decision | Alternatives Considered | Why This Option |
|----------|------------------------|-----------------|
| No `paths:` frontmatter -- rules apply globally | Path-scoped rules (e.g., only `libs/`) | Rules cover universal concerns (architecture, quality, performance, tests) that apply to all code |
| Concise checklist format (<80 lines each) | Detailed prose explanations | Rules are loaded into every context window; brevity matters per ETH Zurich paper findings |
| No overlap with ruff/pyright | Including style/type rules | Rules should cover what linters cannot: architecture, design, and logic-level concerns |

**Phase Completion Steps:**
> After this phase, follow the development process in `docs/DEVELOPMENT_PROCESS.md`: classify as Q/S/P, then execute the corresponding path (validate with agents, ship, document).

---

## Phase 8: GitHub Actions + Config + Documentation

**Goal:** AI-powered PR review, local config template, and comprehensive doc updates.

**Acceptance Criteria:**
- [x] claude-code-review.yml workflow created with `anthropics/claude-code-action@v1`
- [x] settings.local.json.example created as local override template
- [x] .gitignore updated with `.claude/settings.local.json`, `.claude/hooks/*.log`, `CLAUDE.local.md`
- [x] setup_project.py adds `chmod +x` for hook scripts after placeholder substitution
- [x] CLAUDE.md updated with security hooks reference (kept compact per ETH Zurich paper decision)
- [x] README.md updated with full feature list (12 agents, 5 hooks, 3 commands, 4 rules)
- [x] DEVELOPMENT_PROCESS.md updated with hooks, commands, rules, and new agent references

**Tasks:**
- [x] Create `.github/workflows/claude-code-review.yml`
- [x] Create `.claude/settings.local.json.example`
- [x] Update `.gitignore`
- [x] Update `setup_project.py` with chmod +x for hooks and .sh in TEXT_EXTENSIONS
- [x] Update `CLAUDE.md` (compact -- security hooks only)
- [x] Update `README.md` (full feature list, project structure, agent table)
- [x] Update `docs/DEVELOPMENT_PROCESS.md` (hooks, commands, rules tables + new agents)

**Decisions & Trade-offs:**

| Decision | Alternatives Considered | Why This Option |
|----------|------------------------|-----------------|
| Keep CLAUDE.md compact, put detailed tables in DEVELOPMENT_PROCESS.md | Add Hooks/Commands/Rules sections to CLAUDE.md | Respects the ETH Zurich paper decision (D48) to keep CLAUDE.md under ~40 lines |
| claude-code-review.yml uses `claude-sonnet-4-6` model | opus or haiku | Best balance of review quality and cost for automated PR review |
| Read-only tools (Read, Glob, Grep) for CI review action | Including Edit/Bash | CI review should analyze, not modify -- matches security principle of least privilege |

**Phase Completion Steps:**
> After this phase, follow the development process in `docs/DEVELOPMENT_PROCESS.md`: classify as Q/S/P, then execute the corresponding path (validate with agents, ship, document).

---

## Implementation Notes

<!-- Record architectural insights and learnings as the project progresses.
     For specific decisions, use the per-phase "Decisions & Trade-offs" tables above. -->
