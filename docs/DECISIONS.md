# Decision Log

Running log of feature requests and user decisions. Append new entries during Standard and Project paths. Consistency-checked and pruned during Project analysis (P.1). Quick-path tasks are exempt.

When a decision is superseded or obsolete, delete it (git history preserves the record).

---

## 2026-02-14: Fix 5 Template Bugs

**Request**: Fix critical setup script bugs preventing correct package customization and workspace builds.

**Decisions**:
- Use `-name` pattern for package name replacements instead of bare name replacement (avoids false substring matches like "core" in "pyproject")

## 2026-02-16: Permissions Modernization

**Request**: Eliminate unnecessary permission prompts, migrate deprecated syntax, add permissions management skill.

**Decisions**:
- Absolute paths in CLAUDE.md instead of adding `Bash(cd *)` allow rule -- shell operator protection blocks chained commands regardless
- `TaskOutput` tool instead of Read allow rule for temp dirs -- temp path is OS-specific and non-portable for a template
- Custom `.claude/skills/` skill instead of community `@otrebu/claude-permissions` -- community skill is for claude.ai web (ZIP upload), not Claude Code CLI

## 2026-02-24: CLAUDE.md Three-Path Restructuring

**Request**: Replace monolithic Phase Completion Checklist with complexity-aware development process.

**Decisions**:
- Three paths: Quick (trivial), Standard (one-session), Project (multi-phase) -- task complexity determines process depth
- Acceptance criteria and implementation tracking agents moved to Project-only -- Standard tasks don't need them
- Shell Command Style and Allowed Operations sections removed -- redundant with settings.json
- "PCC now" shorthand preserved -- triggers S.5 Validate + S.6 Ship + S.7 Document

## 2026-02-24: Devcontainer Setup

**Request**: Add `.devcontainer/` with Claude Code CLI, network firewall, and docker-compose profiles for common service stacks (inspired by official Claude Code devcontainer and okruh project adaptation).

**Decisions**:
- Python base image (`python:{{python_version}}-bookworm`) with Node.js 20 added for Claude Code CLI -- not Node base image, since this is a Python project
- `vscode` user (UID 1000) with restricted sudoers (firewall-only) instead of `NOPASSWD:ALL` -- follows principle of least privilege from the official reference
- No docker-compose.yml by default (simple build) -- compose only generated when user selects a services profile during setup
- Three compose profiles embedded as Python string constants in `setup_project.py` rather than separate template files -- keeps the repo clean, compose files only appear when needed
- `zsh-in-docker` script instead of manual oh-my-zsh installation -- cleaner single-step setup, matches official Claude Code reference
- Firewall uses `aggregate` tool for GitHub CIDR consolidation -- more robust than resolving individual domains, matches official reference
- Non-critical domain resolution failures log WARNING and continue instead of exit 1 -- DNS blips should not prevent container startup

## 2026-02-26: Trim CLAUDE.md Based on "Evaluating AGENTS.md" Paper

**Request**: Reduce CLAUDE.md size based on findings from ETH Zurich paper (Feb 2026) showing that large context files reduce agent task success rates by ~3% and increase cost by 20%+.

**Decisions**:
- Keep only non-discoverable constraints in CLAUDE.md (security rules, dev commands, ASCII requirement, version sync rule) -- agents can read pyproject.toml for discoverable config
- Move full development process (Q/S/P paths, agent reference, changelog format, PCC shorthand, context recovery rule) to `docs/DEVELOPMENT_PROCESS.md` -- still accessible but not loaded into every context window
- Remove repository structure and testing sections entirely -- proven unhelpful by the paper, fully discoverable from project files
- CLAUDE.md must contain a mandatory directive to classify every task as Q/S/P before starting work

## 2026-02-24: Decision Log

**Request**: Create persistent decision log tracking every feature request and user decision.

**Decisions**:
- Dedicated `docs/DECISIONS.md` rather than only per-phase tables in IMPLEMENTATION_PLAN.md -- long-lived, cross-phase visibility
- No status field; prune by deletion (git preserves history) -- simpler than Active/Superseded/Obsolete tracking
- Integrated into S.2 (log), S.7 (update), P.1 (consistency check + prune) -- Quick path exempt

## 2026-03-01: Hooks, Commands, Agents, Rules, CI

**Request**: Add hooks (5), slash commands (3), agents (3), review rules (4), and AI-powered CI to bring the template to a comprehensive state.

**Decisions**:
- Hook scripts in `.claude/hooks/` using `$CLAUDE_PROJECT_DIR` for path resolution -- official Claude Code convention
- jq required for JSON parsing in hooks with graceful degradation (exit 0 + stderr warning) if missing -- avoids blocking dev work
- auto-format hook is synchronous (no systemMessage) so Claude sees formatted code; test-on-change is informational only
- Commands in `.claude/commands/` not `.claude/skills/` -- simpler single-file format for instruction-set content
- security-auditor and refactoring-specialist agents are read-only (permissionMode: plan) -- analyze, not modify
- output-evaluator uses haiku + dontAsk -- designed for automated pipeline integration, scoring is formulaic
- Review rules have no `paths:` frontmatter (apply globally) and stay under 80 lines -- loaded into every context window
- CLAUDE.md kept compact per ETH Zurich paper decision; detailed hooks/commands/rules tables added to DEVELOPMENT_PROCESS.md instead
- CI review workflow uses claude-sonnet-4-6 with read-only tools (Read, Glob, Grep) -- security principle of least privilege
