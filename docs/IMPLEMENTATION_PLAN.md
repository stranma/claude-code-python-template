# Implementation Plan

> **Status**: Phase 1 - Complete
> **Last Updated**: 2026-02-15

## Quick Status Summary

| Phase | Name | Status |
|-------|------|--------|
| 1 | Fix 5 Template Bugs | Complete |

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
> After this phase, execute the Phase Completion Checklist (steps 0-10 from CLAUDE.md): sync remote, pre-commit hygiene, commit & push, parallel validation (code-quality-validator + test-coverage-validator + acceptance criteria agents), Plan agent for implementation check, docs-updater agent for documentation verification + changelog, create PR with pr-writer agent, verify CI, review-responder agent for code review (optional), phase handoff note. Consult the Failure & Rollback Protocol if any step fails.

---

## Implementation Notes

<!-- Record architectural insights and learnings as the project progresses.
     For specific decisions, use the per-phase "Decisions & Trade-offs" tables above. -->
