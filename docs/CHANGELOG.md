# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Security model simplified to 2-layer exfiltration defense: iptables firewall (primary) blocks non-approved network domains; `dangerous-actions-blocker.sh` (narrowed) blocks exfiltration via trusted channels (gh gist, gh issue --body, package publishing, secrets in args) -- local destruction (rm -rf, sudo, etc.) is no longer blocked since devcontainer is disposable
- CLAUDE.md Security section rewritten to describe the 2-layer defense model instead of listing individual hooks
- Devcontainer simplified: permission tiers removed, single settings.json baseline for all environments

### Removed
- Permission tier system (`.devcontainer/permissions/tier1-assisted.json`, `tier2-autonomous.json`, `tier3-full-trust.json`) and `PERMISSION_TIER` env var -- single settings.json baseline replaces graduated tiers
- `devcontainer-policy-blocker.sh` hook -- tier-dependent policy enforcement no longer needed
- `output-secrets-scanner.sh` hook -- conversation leaks to Anthropic are accepted risk
- `unicode-injection-scanner.sh` hook -- exotic threat with low practical risk
- `test-on-change.sh` hook -- informational-only hook that added latency without preventing issues
- All slash commands (`/cove`, `/cove-isolated`, `/security-audit`) -- niche utilities that added complexity without proportional value
- 6 agents: `agent-auditor`, `security-auditor`, `output-evaluator`, `acceptance-criteria-validator`, `implementation-tracker`, `refactoring-specialist` -- pruned to the 6 agents directly used by the QSP workflow
- `/edit-permissions` skill -- permission tier system removed
- `docs/ARCHITECTURE_GUIDE.md`, `docs/DEVCONTAINER_PERMISSIONS.md`, `docs/community/` -- supporting docs for removed features
- Local destruction patterns from `dangerous-actions-blocker.sh` (`rm -rf`, `sudo`, `DROP DATABASE`, `git push --force`, etc.) -- devcontainer is disposable, these blocks added friction without security value

### Added
- Architecture Deep Dive guide (`docs/ARCHITECTURE_GUIDE.md`) explains why each component exists, what it does under the hood, and what happens if you remove or modify it -- covers all hooks, agents, skills, rules, configuration files, devcontainer layers, and CI/CD workflows with a defense-in-depth diagram and customization guide
- `/landed` skill for post-merge lifecycle -- verifies merge CI, optionally checks deployments (via `.claude/deploy.json`), cleans up feature branches, and identifies the next phase for P-scope work
- `.claude/deploy.json.example` template for configuring deployment verification in `/landed`
- Chain-of-Verification (CoVe) commands (`/cove`, `/cove-isolated`) for high-stakes accuracy -- 4-step self-verification process based on Meta's CoVe paper, with an isolated variant that runs verification in a separate agent to prevent confirmation bias
- Template sync workflow (`.github/workflows/template-sync.yml`) for downstream projects to auto-sync upstream template improvements -- runs weekly or on manual trigger, creates PRs with changed template-managed files while preserving project-specific code
- Python-specific SOLID checklist in `refactoring-specialist` agent -- checks for mutable default arguments, ABC/Protocol misuse, missing dependency injection, god classes, `@property` overuse, and circular imports
- Template integration CI pipeline (`template-integration.yml`) tests `setup_project.py` across 5 configurations (mono-default, mono-renamed, mono-extra-pkgs, single-package, mono-postgres) -- verifies each produces a valid project that installs, lints, type-checks, and passes tests
- Reusable `scripts/test_template_integration.sh` for local template validation with the same 9-step verification as CI
- Workflow skill `/sync` checks workspace readiness before starting work (git fetch, status, branch info, warnings)
- Workflow skill `/design` crystallizes brainstorming into structured plans with conflict detection against DECISIONS.md
- Workflow skill `/done` auto-detects scope (Q/S/P) and runs the full validate-ship-document pipeline, including the former `/ship` checklist
- Three graduated permission tiers (Assisted, Autonomous, Full Trust) for devcontainer environments -- container isolation (firewall, non-root, hooks) enables safely expanding Claude Code permissions, reducing unnecessary prompts from dozens per session to zero in Tier 2/3 while blocking tool installation, package publishing, and container escape vectors via curated deny lists and a policy-enforcement hook
- 5 hook scripts in `.claude/hooks/` run automatically during Claude Code sessions -- 3 security hooks block destructive commands, secret leaks, and invisible Unicode attacks in real time; 2 productivity hooks auto-format Python files and auto-run associated tests after every edit
- 3 slash commands (`/cove`, `/cove-isolated`, `/security-audit`) provide chain-of-verification for accuracy and a 6-phase security posture scan with A-F grading
- 3 new specialized agents: `security-auditor` (OWASP-based vulnerability analysis, read-only), `refactoring-specialist` (SOLID/code smell detection, read-only), `output-evaluator` (LLM-as-Judge quality scoring for automated pipelines)
- 4 review rules in `.claude/rules/` auto-loaded as project context -- cover architecture, code quality, performance, and test quality concerns that linters cannot catch
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

### Fixed
- CI badge in README now points to `template-integration.yml` (the actual CI) instead of `tests.yml` (template placeholder that never runs)

### Changed

- Development workflow expanded from sync-design-done to sync-design-done-landed, closing the post-merge gap
- QSP scope classification is now auto-detected by `/done` based on branch, diff size, and IMPLEMENTATION_PLAN.md state -- users no longer classify manually before starting work
- PCC shorthand now triggers `/done` instead of manually executing S.5-S.7
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

- CI-based AI code review workflow (`claude-code-review.yml`) -- the local `code-reviewer` agent (run by `/done` at step S.6.5) already provides equivalent pre-PR review coverage, making the CI workflow redundant and removing the need to manage an `ANTHROPIC_API_KEY` secret in GitHub
- `/catchup` command -- its context restoration role overlaps with `/sync`, which already covers pre-flight workspace state
- `/ship` slash command -- its 3-tier validation checklist (Blockers, High Priority, Recommended) is preserved in `/done` Phase 2
- Shell Command Style and Allowed Operations sections from CLAUDE.md -- absolute path preferences and read-only command lists are now handled by settings.json permission rules rather than prose instructions

### Fixed

- Quick (Q) path now ships changes to production -- previously ended at local commit with no push or CI verification, so fixes never reached the remote
- QSP task classification is now the first section in CLAUDE.md -- previously buried at the bottom where it was easily skipped
- All development paths (Q, S, P) now require a pre-flight git sync before starting work -- prevents push rejections from stale local branches

- Setup script now correctly renames package names inside pyproject.toml and __init__.py files when customizing packages beyond the defaults
- Additional packages created by setup script now get correct project-prefixed names instead of inheriting the template source package name (e.g., vizier-engine instead of vizier-core when adding engine package)
- Root pyproject.toml no longer includes a [build-system] section that caused hatchling build failures in workspace mode
- Devcontainer now installs Claude Code CLI via the official native binary installer, removing the Node.js 20 dependency -- reduces image size and eliminates a runtime that served no purpose in a Python project
- Devcontainer firewall hardened: switched to iptables-legacy backend (nftables is unreliable inside Docker), added a pre-check with graceful degradation so container startup is never blocked by missing iptables support, suppressed Docker-internal chain errors on iptables -X, skipped comment lines in DNS rule restoration, and moved DROP policies after ACCEPT rules to prevent access lockout on partial failure
- Devcontainer firewall allowlist updated: replaced registry.npmjs.org with claude.ai now that npm is no longer used
- Shell scripts, Dockerfiles, and .devcontainer files now enforce LF line endings via .gitattributes -- prevents CRLF corruption on Windows checkouts that caused silent script failures
