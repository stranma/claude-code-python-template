# Implementation Plan

> **Status**: Phase 2 - Complete
> **Last Updated**: 2026-02-16

## Quick Status Summary

| Phase | Name | Status |
|-------|------|--------|
| 1 | Fix 5 Template Bugs | Complete |
| 2 | Permissions Modernization | Complete |

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

## Implementation Notes

<!-- Record architectural insights and learnings as the project progresses.
     For specific decisions, use the per-phase "Decisions & Trade-offs" tables above. -->
