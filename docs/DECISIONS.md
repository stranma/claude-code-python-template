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

## 2026-03-02: QSP Enforcement and Pre-flight Sync

**Request**: Fix three process failures: QSP classification ignored until reminded, no git sync before work (caused push rejection), no branch confirmation.

**Decisions**:
- QSP classification moved to first section in CLAUDE.md -- being last made it easy to skip
- New "Pre-flight (all paths)" section in DEVELOPMENT_PROCESS.md with mandatory git sync and explicit classification -- applies before Q, S, or P begins
- Redundant `git fetch` removed from S.3 -- now centralized in pre-flight

## 2026-03-04: Devcontainer Native Installer and Firewall Hardening

**Request**: Port devcontainer fixes from Vizier repository -- migrate Claude Code CLI from npm to native binary installer, enforce LF line endings, and harden the iptables firewall script.

**Decisions**:
- Native binary installer for Claude Code CLI instead of npm + Node.js 20 -- Node.js added no value to a Python project; the official native installer is the recommended path and removes a large runtime dependency
- .gitattributes enforcing LF line endings for shell scripts (`*.sh`), Dockerfiles, and `.devcontainer` files -- CRLF-corrupted shell scripts fail silently on Linux, and Windows developers check out these files by default with CRLF
- iptables-legacy backend instead of the default nftables -- nftables is unreliable inside Docker due to missing kernel module support; iptables-legacy is stable and widely supported across host kernels
- iptables pre-check with graceful degradation (log warning, skip firewall) instead of hard exit 1 -- a missing iptables binary should degrade to an open network rather than block container startup entirely
- Suppress stderr on iptables -X (chain flush) -- Docker pre-populates chains (DOCKER, DOCKER-USER, etc.) that cannot be deleted; the errors are expected and misleading
- Skip lines starting with `#` during DNS rule restoration -- comment lines in the allowlist were being passed to iptables as hostnames, causing spurious errors
- DROP policies added after all ACCEPT rules -- reordering prevents a partial-failure scenario where DROP is installed before the ACCEPT rules complete, locking out the container
- Replaced registry.npmjs.org with claude.ai in the firewall allowlist -- npmjs.org is no longer contacted now that the native installer is used; claude.ai is required for Claude Code authentication

## 2026-03-09: Workflow Skills (/sync, /design, /done)

**Request**: Replace rigid QSP upfront classification with three entry-point skills that auto-detect scope at completion time.

**Decisions**:
- Three skills (`/sync`, `/design`, `/done`) replace mandatory upfront QSP classification -- scope is now auto-detected by `/done` based on branch, diff size, and plan state
- `/plan` renamed to `/design` because `/plan` is a built-in Claude Code command (enters read-only plan mode) -- `/design` is distinct and forms a natural arc: sync -> design -> done
- `/ship` command absorbed into `/done` Phase 2 -- the 3-tier checklist (Blockers/High Priority/Recommended) is preserved in `/done`'s validate phase
- `/sync` and `/done` have `disable-model-invocation: true` (side effects: git fetch, git commit/push, PR creation); `/design` is intentionally model-invocable so Claude can suggest it during brainstorming
- QSP paths (Q/S/P) and their step descriptions preserved in DEVELOPMENT_PROCESS.md -- skills orchestrate the paths, they don't replace them

## 2026-03-10: Template Integration CI Pipeline

**Request**: Create a CI pipeline that applies the template in various settings to catch template bugs before merge.

**Decisions**:
- New workflow `template-integration.yml` (not extending `tests.yml`) -- `tests.yml` has `{{base_branch}}` in its trigger and never fires on the raw template repo
- GitHub Actions matrix (5 configs) + reusable shell script (`scripts/test_template_integration.sh`) -- matrix defines WHAT to test, script defines HOW to verify; script also runnable locally
- Copy template to temp dir before applying -- `setup_project.py` modifies in-place, would destroy the checkout
- 5 matrix configs cover all major code paths: default monorepo, package renaming, additional packages, single-package conversion, Docker Compose services
- Unit tests gate job runs first -- fail fast if setup_project.py functions are broken before spending matrix resources
- Placeholder check uses named pattern matching (`{{project_name}}` etc.) not generic `{{` -- avoids false positives from GitHub Actions `${{ }}` expressions
- `test_setup_project.py` excluded from integration pytest runs -- tests setup script internals (already covered by unit-tests job), fails on single-package layout

## 2026-03-04: Devcontainer Permission Tiers

**Request**: Expand Claude Code permissions for devcontainer usage, taking advantage of container isolation (firewall, non-root user, hooks) to reduce unnecessary permission prompts.

**Decisions**:
- Three graduated tiers (Assisted, Autonomous, Full Trust) stored as JSON in `.devcontainer/permissions/` -- copied to `.claude/settings.local.json` at container creation via build arg
- `settings.local.json` (gitignored) for devcontainer-specific expansions, NOT modifying shared `settings.json` -- base settings remain the universal bare-metal baseline
- Tier 2 (Autonomous, recommended default) uses `Bash(*)` allow with curated deny list -- zero prompts for bash, denied commands fail immediately instead of prompting
- Deny list targets three categories: shared external state (gh pr merge, workflow triggers, issue mutations), irreversible actions (package publishing to npm/PyPI), and container escape vectors (docker --privileged)
- Tool installation comprehensively denied in Tier 2 (pip, npm -g, cargo, go, gem, uv tool, apt, snap, brew) -- toolchain defined by Dockerfile, project deps via `uv add`
- Separate `devcontainer-policy-blocker.sh` hook (not modifying existing hooks) catches denied patterns in chained commands (`cd && pip install`) that bypass glob-based deny rules
- Single hook script with `$PERMISSION_TIER` env var for tier awareness -- fail-closed (if unset, blocks everything)
- Each tier file is fully self-contained (permissions + ALL hooks) to survive settings.local.json replace-not-merge semantics
- Template guard in onCreateCommand: skips `uv sync` if pyproject.toml still has `{{project_name}}` placeholders
- `docs/DEVCONTAINER_PERMISSIONS.md` maps every denied command to its approved alternative -- CLAUDE.md references this doc so Claude checks alternatives before attempting blocked commands
- Full implementation recorded in `docs/IMPLEMENTATION_PLAN.md` Phase 9

**Accepted Risks**:

| Risk | Why accepted | Mitigation |
|------|-------------|------------|
| Grep-based hook bypass via obfuscation (`p\ip install`, `alias p=pip; p install`) | Grep hooks are a UX layer to prevent Claude from wasting turns on naive mistakes. They cannot stop deliberate bash obfuscation from prompt injection. | Actual security boundaries are non-root user (installs fail) + firewall (limits exfiltration). The hook catches the 99% case. |
| GitHub API via curl (`curl -H "Authorization: ..." https://api.github.com/.../merge`) | Blocking curl to github.com is fragile and breaks legitimate web fetching. The hook already blocks commands containing `GH_TOKEN=` as a literal argument. | Use fine-grained PATs with minimal scopes. CLAUDE.md instructs Claude to use `gh` CLI, not raw API calls. Token scoping is the real control. |
| Docker not present but deny rules exist | Docker is not installed in the current template container. Deny rules exist as defense-in-depth for users who add Docker-in-Docker later. | If Docker-in-Docker is added, the deny list should be revisited (add `-v` and `--mount` volume escape patterns). |
| Whitelisted domains as exfil channels | `github.com` is whitelisted for git/gh operations. A compromised agent could theoretically exfiltrate via gist creation or issue comments. | Token scoping (no gist/issue create permission) + GH mutation deny rules in Tier 2. Tier 3 accepts this risk explicitly. |
