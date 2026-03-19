# Decision Log

Running log of feature requests and user decisions. Append new entries during Standard and Project paths. Consistency-checked and pruned during Project analysis (P.1). Quick-path tasks are exempt.

When a decision is superseded or obsolete, delete it (git history preserves the record).

---

## 2026-02-14: Fix 5 Template Bugs

**Request**: Fix critical setup script bugs preventing correct package customization and workspace builds.

**Decisions**:
- Use `-name` pattern for package name replacements instead of bare name replacement (avoids false substring matches like "core" in "pyproject")

## 2026-02-24: CLAUDE.md Three-Path Restructuring

**Request**: Replace monolithic Phase Completion Checklist with complexity-aware development process.

**Decisions**:
- Three paths: Quick (trivial), Standard (one-session), Project (multi-phase) -- task complexity determines process depth
- Acceptance criteria and implementation tracking agents moved to Project-only -- Standard tasks don't need them
- Shell Command Style and Allowed Operations sections removed -- redundant with settings.json
- "PCC now" shorthand preserved -- triggers S.5 Validate + S.6 Ship + S.7 Document

## 2026-02-24: Devcontainer Setup

**Request**: Add `.devcontainer/` with Claude Code CLI and network firewall.

**Decisions**:
- Python base image (`python:{{python_version}}-bookworm`) with Claude Code native binary installer -- not Node base image, since this is a Python project
- `vscode` user (UID 1000) with restricted sudoers (firewall-only) instead of `NOPASSWD:ALL` -- follows principle of least privilege
- No docker-compose.yml by default (simple build) -- compose only generated when user selects a services profile during setup

## 2026-02-26: Trim CLAUDE.md Based on "Evaluating AGENTS.md" Paper

**Request**: Reduce CLAUDE.md size based on findings from ETH Zurich paper (Feb 2026) showing that large context files reduce agent task success rates by ~3% and increase cost by 20%+.

**Decisions**:
- Keep only non-discoverable constraints in CLAUDE.md (security rules, dev commands, ASCII requirement, version sync rule) -- agents can read pyproject.toml for discoverable config
- Move full development process (Q/S/P paths, agent reference, changelog format, PCC shorthand, context recovery rule) to `docs/DEVELOPMENT_PROCESS.md` -- still accessible but not loaded into every context window
- Remove repository structure and testing sections entirely -- proven unhelpful by the paper, fully discoverable from project files
- CLAUDE.md must contain a mandatory directive to classify every task as Q/S/P before starting work

## 2026-03-01: Hooks, Commands, Agents, Rules

**Request**: Add hooks, agents, and review rules to bring the template to a comprehensive state.

**Decisions**:
- Hook scripts in `.claude/hooks/` using `$CLAUDE_PROJECT_DIR` for path resolution -- official Claude Code convention
- jq required for JSON parsing in hooks with graceful degradation (exit 0 + stderr warning) if missing -- avoids blocking dev work
- auto-format hook is synchronous (no systemMessage) so Claude sees formatted code
- Review rules have no `paths:` frontmatter (apply globally) and stay under 80 lines -- loaded into every context window
- CLAUDE.md kept compact per ETH Zurich paper decision; detailed tables in DEVELOPMENT_PROCESS.md

## 2026-03-02: QSP Enforcement and Pre-flight Sync

**Request**: Fix three process failures: QSP classification ignored until reminded, no git sync before work (caused push rejection), no branch confirmation.

**Decisions**:
- QSP classification moved to first section in CLAUDE.md -- being last made it easy to skip
- New "Pre-flight (all paths)" section in DEVELOPMENT_PROCESS.md with mandatory git sync and explicit classification -- applies before Q, S, or P begins
- Redundant `git fetch` removed from S.3 -- now centralized in pre-flight

## 2026-03-04: Devcontainer Native Installer and Firewall Hardening

**Request**: Port devcontainer fixes from Vizier repository -- migrate Claude Code CLI from npm to native binary installer, enforce LF line endings, and harden the iptables firewall script.

**Decisions**:
- Native binary installer for Claude Code CLI instead of npm + Node.js 20 -- Node.js added no value to a Python project
- .gitattributes enforcing LF line endings for shell scripts (`*.sh`), Dockerfiles, and `.devcontainer` files -- CRLF-corrupted shell scripts fail silently on Linux
- iptables-legacy backend instead of the default nftables -- nftables is unreliable inside Docker due to missing kernel module support
- iptables pre-check with graceful degradation (log warning, skip firewall) instead of hard exit 1
- DROP policies added after all ACCEPT rules -- prevents partial-failure lockout

## 2026-03-09: Workflow Skills (/sync, /design, /done)

**Request**: Replace rigid QSP upfront classification with three entry-point skills that auto-detect scope at completion time.

**Decisions**:
- Three skills (`/sync`, `/design`, `/done`) replace mandatory upfront QSP classification -- scope is now auto-detected by `/done` based on branch, diff size, and plan state
- `/plan` renamed to `/design` because `/plan` is a built-in Claude Code command (enters read-only plan mode) -- `/design` is distinct and forms a natural arc: sync -> design -> done
- `/ship` command absorbed into `/done` Phase 2 -- the 3-tier checklist (Blockers/High Priority/Recommended) is preserved in `/done`'s validate phase
- `/sync` and `/done` have `disable-model-invocation: true` (side effects: git fetch, git commit/push, PR creation); `/design` is intentionally model-invocable so Claude can suggest it during brainstorming
- QSP paths (Q/S/P) and their step descriptions preserved in DEVELOPMENT_PROCESS.md -- skills orchestrate the paths, they don't replace them

## 2026-03-10: Post-merge /landed Skill

**Request**: Close the post-merge gap in the sync-design-done workflow. After `/done` creates a PR and it merges, nothing verifies merge CI, checks deployments, cleans up branches, or identifies the next phase.

**Decisions**:
- New `/landed` skill (not command) -- follows same pattern as `/sync` and `/done` with `disable-model-invocation: true`
- `/catchup` removed -- its context restoration overlaps with `/sync` which already covers pre-flight state
- Optional deployment verification via `.claude/deploy.json` (gitignored) -- not all projects have deployments, so it's opt-in with an example file
- Phase detection uses "Quick Status Summary" table in IMPLEMENTATION_PLAN.md, not `- [ ]` checkboxes -- matches actual file structure

## 2026-03-16: WebFetch Firewall Integration

**Request**: Connect the devcontainer iptables firewall to Claude Code's WebFetch permission settings so users don't need to manually edit the firewall script when working with external services.

**Decisions**:
- Firewall reads `WebFetch(domain:...)` patterns from settings.json and settings.local.json at container startup -- single source of truth for domain whitelisting
- Only `allow` and `ask` lists are scanned (not `deny`) -- denied domains should never be whitelisted
- Bare `WebFetch` (no domain qualifier) is ignored -- it grants tool permission but has no domain to resolve
- Wildcard domains (e.g., `*.example.com`) are skipped with a warning -- DNS cannot resolve wildcard patterns to IPs
- WebFetch settings changes take effect on container restart (`init-firewall.sh` runs from `postStartCommand`)

## 2026-03-18: Subagent CLAUDE.md Limitation

**Observation**: Spawned subagents (via the Agent tool) do not read CLAUDE.md or project instructions. They only follow what the parent agent includes in the prompt. This means directives like "use `uv run` for all commands" are silently ignored by subagents unless explicitly passed through.

**Decisions**:
- Known template limitation -- subagents must receive key directives in their spawn prompt
- Agent `.md` files could include critical directives (e.g., "use `uv run`") but this duplicates CLAUDE.md and creates drift risk
- For this template repo specifically, `uv run` fails due to `{{project_name}}` placeholders, so `python -m pytest` is the correct fallback
- No code change for now; document as a known limitation

## 2026-03-18: Security Model Simplification

**Request**: Prune security infrastructure to essentials. Remove permission tiers,
most hooks, commands, and niche agents. Refocus on exfiltration prevention.

**Decisions**:
- Two exfiltration channels: network (firewall) and trusted-channel abuse (hook)
- Firewall is primary defense -- iptables whitelist blocks all non-approved domains
- dangerous-actions-blocker.sh narrowed to: GitHub API exfil, publishing, secrets in args
- Local destruction (rm -rf, sudo, etc.) not blocked -- devcontainer is disposable
- output-secrets-scanner removed -- conversation leaks to Anthropic are accepted
- Permission tiers removed -- single settings.json baseline for all environments
- unicode-injection-scanner removed -- exotic threat, low practical risk

## 2026-03-15: Devcontainer Firewall Inbound Relaxation

**Request**: Strict inbound filtering blocks legitimate dev server use cases unnecessarily.

**Decisions**:
- Default to permissive inbound (`FIREWALL_ALLOW_INBOUND=true`) -- the primary threat model is egress (data exfiltration), not inbound; Docker's network stack provides inbound isolation depending on port publishing and network mode
- Opt-in strict inbound via `FIREWALL_ALLOW_INBOUND=false` preserves the original INPUT DROP behavior for users who need it
- Firewall deny rules (iptables, ip6tables, ipset, nft, init-firewall) added to settings.json -- prevents Claude from tampering with the firewall, which is the primary security boundary
