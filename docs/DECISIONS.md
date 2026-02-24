# Decision Log

Running log of feature requests and user decisions. Append new entries during Standard and Project paths. Consistency-checked and pruned during Project analysis (P.1). Quick-path tasks are exempt.

When a decision is superseded or obsolete, delete it (git history preserves the record).

---

### 2026-02-14: Fix 5 Template Bugs

**Request**: Fix critical setup script bugs preventing correct package customization and workspace builds.

**Decisions**:
- Use `-name` pattern for package name replacements instead of bare name replacement (avoids false substring matches like "core" in "pyproject")

### 2026-02-16: Permissions Modernization

**Request**: Eliminate unnecessary permission prompts, migrate deprecated syntax, add permissions management skill.

**Decisions**:
- Absolute paths in CLAUDE.md instead of adding `Bash(cd *)` allow rule -- shell operator protection blocks chained commands regardless
- `TaskOutput` tool instead of Read allow rule for temp dirs -- temp path is OS-specific and non-portable for a template
- Custom `.claude/skills/` skill instead of community `@otrebu/claude-permissions` -- community skill is for claude.ai web (ZIP upload), not Claude Code CLI

### 2026-02-24: CLAUDE.md Three-Path Restructuring

**Request**: Replace monolithic Phase Completion Checklist with complexity-aware development process.

**Decisions**:
- Three paths: Quick (trivial), Standard (one-session), Project (multi-phase) -- task complexity determines process depth
- Acceptance criteria and implementation tracking agents moved to Project-only -- Standard tasks don't need them
- Shell Command Style and Allowed Operations sections removed -- redundant with settings.json
- "PCC now" shorthand preserved -- triggers S.5 Validate + S.6 Ship + S.7 Document

### 2026-02-24: Decision Log

**Request**: Create persistent decision log tracking every feature request and user decision.

**Decisions**:
- Dedicated `docs/DECISIONS.md` rather than only per-phase tables in IMPLEMENTATION_PLAN.md -- long-lived, cross-phase visibility
- No status field; prune by deletion (git preserves history) -- simpler than Active/Superseded/Obsolete tracking
- Integrated into S.2 (log), S.7 (update), P.1 (consistency check + prune) -- Quick path exempt
