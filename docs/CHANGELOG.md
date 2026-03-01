# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 5 hook scripts in `.claude/hooks/` run automatically during Claude Code sessions -- 3 security hooks block destructive commands, secret leaks, and invisible Unicode attacks in real time; 2 productivity hooks auto-format Python files and auto-run associated tests after every edit
- 3 slash commands (`/catchup`, `/security-audit`, `/ship`) provide one-command context restoration after `/clear`, a 6-phase security posture scan with A-F grading, and a 3-tier pre-deployment checklist
- 3 new specialized agents: `security-auditor` (OWASP-based vulnerability analysis, read-only), `refactoring-specialist` (SOLID/code smell detection, read-only), `output-evaluator` (LLM-as-Judge quality scoring for automated pipelines)
- 4 review rules in `.claude/rules/` auto-loaded as project context -- cover architecture, code quality, performance, and test quality concerns that linters cannot catch
- AI-powered PR review via GitHub Actions (`claude-code-review.yml`) using `anthropics/claude-code-action@v1` -- automatically reviews PRs with read-only tools on open/sync/ready_for_review
- Local config template (`.claude/settings.local.json.example`) for developer-specific hook overrides, extra permissions, and MCP server configuration
- Tests for hooks (test_hooks.py), commands (test_commands.py), agents (test_agents.py), and rules (test_rules.py) validating existence, structure, frontmatter, and behavioral contracts
- New `docs/DEVELOPMENT_PROCESS.md` contains the full Q/S/P development workflow, agent reference, failure protocol, changelog format, and PCC shorthand -- accessible on demand instead of always loaded into context
- Development container (`.devcontainer/`) with Claude Code CLI, network security firewall, and Python tooling pre-installed -- developers can open the project in VS Code and get a sandboxed, reproducible environment with one click
- Docker Compose service profiles selectable during project setup (`--services postgres`, `--services postgres-redis`, `--services custom`) -- common stacks are ready to use without writing compose files from scratch
- Architectural decisions and feature requests are now captured in `docs/DECISIONS.md`, so trade-offs are never lost between sessions (maintained during Standard/Project paths, consistency-checked during Project analysis)
- Automated permission tests (53 tests) validate settings.json structure, pattern syntax, matching semantics, conflict detection, security invariants, and deny > ask > allow evaluation order -- catches misconfigurations before they cause unexpected prompts or weaken security
- Template packages now include tests/ directories so pytest discovers package tests immediately after setup
- Phase Completion Checklist now includes Step -1 requiring feature branch creation before starting work
- Added settings.json to enable uv run execution in Claude Code server environment
- New `/edit-permissions` skill for managing Claude Code permission rules in settings.json -- invocable via slash command, includes pattern syntax reference, shell operator protection warnings, and safety guardrails

### Changed

- Setup script now makes `.claude/hooks/*.sh` files executable after placeholder substitution -- hook scripts work immediately after project setup without manual `chmod`
- Agent count increased from 9 to 12 with security-auditor, refactoring-specialist, and output-evaluator
- `docs/DEVELOPMENT_PROCESS.md` expanded with hooks, commands, rules reference tables and 4 new agent entries
- CLAUDE.md trimmed from ~200 lines to ~40 lines -- keeps only non-discoverable constraints (security, dev commands, code style, version sync) and a mandatory Q/S/P task classification directive, reducing agent context overhead
- Permission patterns in settings.json migrated from deprecated `:*` syntax to ` *` -- no behavior change, follows current Claude Code documentation
- CLAUDE.md restructured from monolithic Phase Completion Checklist to three-path development process tree (Quick/Standard/Project) -- task complexity now determines process depth, reducing overhead for small changes while maintaining rigor for large projects
- All documentation and CI workflows now use `uv sync --all-packages --group dev` to correctly install all workspace members
- Default base branch from "main" to "master" -- new projects created from this template will use "master" as the default branch name
- Claude Code permissions moved from settings.local.json to settings.json -- projects created from this template will automatically inherit tool permissions at the project level, reducing approval prompts

### Removed

- Shell Command Style and Allowed Operations sections from CLAUDE.md -- absolute path preferences and read-only command lists are now handled by settings.json permission rules rather than prose instructions

### Fixed

- Setup script now correctly renames package names inside pyproject.toml and __init__.py files when customizing packages beyond the defaults
- Additional packages created by setup script now get correct project-prefixed names instead of inheriting the template source package name (e.g., vizier-engine instead of vizier-core when adding engine package)
- Root pyproject.toml no longer includes a [build-system] section that caused hatchling build failures in workspace mode
