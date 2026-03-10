# Architecture Deep Dive

This guide explains **why** each component exists, **what** it does under the hood, and **what happens if** you remove or modify it. It is for developers who want to customize the template, strip parts out, or understand the design decisions behind it.

For setup instructions, see [Getting Started](GETTING_STARTED.md). For the workflow reference, see [Development Process](DEVELOPMENT_PROCESS.md). For permission tier details, see [Devcontainer Permissions](DEVCONTAINER_PERMISSIONS.md).

---

## System Architecture

The template uses defense-in-depth: multiple independent layers that each catch different problems. No single layer is the whole story.

```text
+-----------------------------------------------------------------------+
|  Devcontainer (optional, recommended)                                 |
|  +------------------------------------------------------------------+ |
|  | Network firewall (init-firewall.sh)                              | |
|  | Blocks all egress except ~10 whitelisted domains                 | |
|  +------------------------------------------------------------------+ |
|  | Non-root user (vscode, uid 1000)                                 | |
|  | Cannot install system packages or modify system files            | |
|  +------------------------------------------------------------------+ |
|  | Policy blocker (devcontainer-policy-blocker.sh)                   | |
|  | Tier-aware: blocks pip install, publishing, supply-chain piping  | |
|  +------------------------------------------------------------------+ |
+-----------------------------------------------------------------------+
|  Claude Code Runtime (always active)                                  |
|  +------------------------------------------------------------------+ |
|  | settings.json permissions (allow / deny / ask)                   | |
|  | First gate: controls which tools and commands Claude can invoke  | |
|  +------------------------------------------------------------------+ |
|  | PreToolUse hooks                                                 | |
|  | dangerous-actions-blocker  |  unicode-injection-scanner          | |
|  +------------------------------------------------------------------+ |
|  | PostToolUse hooks                                                | |
|  | output-secrets-scanner | auto-format | test-on-change            | |
|  +------------------------------------------------------------------+ |
|  | security-guidance plugin (real-time warnings during editing)     | |
|  +------------------------------------------------------------------+ |
|  | Review rules (architecture, code-quality, performance, test)     | |
|  | Loaded as context -- influence Claude's decisions, not enforced  | |
|  +------------------------------------------------------------------+ |
+-----------------------------------------------------------------------+
```

### What runs during a typical workflow

```text
/sync           /design          write code          /done              /landed
  |                |                 |                  |                  |
  git fetch        read DECISIONS   [your work]        lint+format        verify merge CI
  branch state     scope classify                      tests+coverage     deploy check
  dirty files      plan output                         code review        branch cleanup
  recent commits                    auto-format.sh     PR creation        next phase
                                    test-on-change.sh  changelog update
                                    (after each edit)
```

---

## Security Layers

### Permissions: settings.json

<details>
<summary>Why / What / Remove / Connects</summary>

**Why it exists.** Controls which shell commands Claude can run without asking. Without this, Claude either prompts for every command (slow) or runs everything unchecked (risky).

**What it does.** Three lists evaluated in order: **deny** (always blocked, no prompt), **ask** (user must approve), **allow** (runs without prompt). Each entry is a glob pattern matched against the command. The deny list blocks secret management commands (`gh secret`, `gh auth`, `git config`). The ask list covers destructive or stateful operations (`docker`, `terraform`, `gh pr merge`, `git reset`). The allow list covers safe read/build operations (`pytest`, `ruff`, `git status`, `ls`).

**What happens if you remove it.** Claude falls back to its default behavior: prompting for most commands. The workflow still works but requires constant approval clicks. No security risk -- just friction.

**How it connects.** Devcontainer tiers override these permissions by copying a tier-specific file to `settings.local.json`, which takes precedence over `settings.json`. The hooks (below) provide a second layer that catches commands the permission patterns miss.

</details>

### PreToolUse Hooks

These run **before** Claude executes a command or file edit. They can block the action (exit code 2) or allow it (exit code 0).

#### dangerous-actions-blocker.sh

<details>
<summary>Why / What / Remove / Connects</summary>

**Why it exists.** Permissions use glob patterns, which cannot catch every dangerous command variant. This hook uses substring and regex matching against the full command string to block destructive patterns that slip through.

**What it does.** Triggers on every `Bash` tool invocation. Checks the command against three categories:

1. **Destructive commands** (23 literal patterns): `rm -rf /`, `sudo rm -rf`, `dd if=/dev/zero`, fork bombs, `chmod -R 777 /`, `shutdown`, `reboot`, `halt`, `poweroff`, `git push --force`, `git push -f`, `git push origin +master`, `git push origin +main`, `DROP DATABASE`, `DROP TABLE`, `TRUNCATE TABLE`
2. **Filesystem format** (regex): `mkfs.*`, `DELETE FROM .* WHERE 1`
3. **Secrets in commands** (9 literal + 1 regex): any command containing `ANTHROPIC_API_KEY=`, `OPENAI_API_KEY=`, `AWS_SECRET_ACCESS_KEY=`, `GITHUB_TOKEN=`, `GH_TOKEN=`, `password=`, `passwd=`, `secret=`, `token=`, or database URLs with embedded credentials

Uses `grep -qiF` (case-insensitive, literal) for exact patterns and `grep -qiE` for regex. Returns a JSON decision object to stdout with exit code 2 to block.

**What happens if you remove it.** No pre-execution safety net. A command like `git push --force origin main` would execute if it passes the settings.json permissions. The devcontainer policy blocker (if present) covers some patterns but not all.

**How it connects.** Complements the settings.json permissions (which use glob patterns, not substring matching). In devcontainers, the `devcontainer-policy-blocker.sh` adds tier-aware blocking on top.

**Dependencies:** `jq` (degrades gracefully -- exits 0 with warning if missing).

</details>

#### unicode-injection-scanner.sh

<details>
<summary>Why / What / Remove / Connects</summary>

**Why it exists.** Invisible Unicode characters can make code appear different from what it actually does. A zero-width character in a variable name creates a visually identical but semantically different identifier. RTL override characters can make `if (isAdmin)` display as `if (isUser)` in code review. These are real attack vectors (CVE-2025-53109, CVE-2025-53110).

**What it does.** Triggers on every `Edit` and `Write` tool invocation. Scans the content being written for:

1. **Zero-width characters**: U+200B (zero-width space), U+200C (zero-width non-joiner), U+200D (zero-width joiner), U+FEFF (byte-order mark)
2. **Bidirectional overrides**: U+202A-E, U+2066-2069 (left-to-right/right-to-left embedding, override, isolate)
3. **ANSI escape sequences**: `\x1B[` (terminal injection)
4. **Null bytes**: U+0000 (can truncate strings in C-based parsers)
5. **Unicode tag characters**: U+E0001-E007F (invisible instruction embedding)

Uses `grep -P` (PCRE) for Unicode-aware matching.

**What happens if you remove it.** Code files could contain invisible characters that alter behavior without being visible in code review. This is a supply-chain attack vector.

**How it connects.** Only scans Edit/Write (not Bash output). The `output-secrets-scanner.sh` covers Bash output separately. Requires GNU grep with PCRE support -- on macOS or Alpine (no PCRE by default), the hook disables itself with a warning.

**Dependencies:** `jq`, `grep -P` (PCRE). Fails open on macOS/Alpine where PCRE is unavailable.

</details>

### PostToolUse Hooks

These run **after** a command or edit completes. They cannot block -- they can only warn via `systemMessage`.

#### output-secrets-scanner.sh

<details>
<summary>Why / What / Remove / Connects</summary>

**Why it exists.** A developer might run `cat .env` or `env | grep API` and accidentally expose secrets in the conversation log. This hook warns when that happens.

**What it does.** Triggers after every `Bash` command. Scans the command output for:

1. AWS Access Key IDs (`AKIA[0-9A-Z]{16}`)
2. AWS Secret Access Keys (40-char base64 near `aws_secret` context)
3. Anthropic API keys (`sk-ant-*`)
4. OpenAI API keys (`sk-*`)
5. GitHub PATs (`ghp_*`) and OAuth tokens (`gho_*`)
6. JWT tokens (`eyJ*.eyJ*.*`)
7. Private key material (`-----BEGIN ... PRIVATE KEY-----`)
8. Database URLs with embedded credentials (`postgres://user:pass@host`)

Emits a `systemMessage` warning to stderr if any match is found. Always exits 0 -- PostToolUse hooks cannot block.

**What happens if you remove it.** Secrets can appear in conversation output without any warning. They may end up in logs or screenshots.

**How it connects.** Complements the `dangerous-actions-blocker.sh` (which blocks secrets in *commands*). This hook catches secrets in *output*.

**Dependencies:** `jq`, `grep -E`.

</details>

### Productivity Hooks

#### auto-format.sh

<details>
<summary>Why / What / Remove / Connects</summary>

**Why it exists.** Without it, Claude writes code, then you (or CI) run the formatter, then Claude sees the diff and gets confused about what changed. Auto-formatting after each edit means Claude always sees correctly formatted code.

**What it does.** Triggers after every `Edit` or `Write` on `*.py` files. Runs `uv run ruff format <file>` followed by `uv run ruff check --fix <file>`. Runs synchronously so Claude's next read of the file sees formatted code.

**What happens if you remove it.** Code style drifts during a session. The CI lint step (`ruff check`) still catches formatting issues, but later -- after commit and push. Claude may also produce inconsistent style if it reads its own unformatted output.

**How it connects.** Runs before `test-on-change.sh` (both are registered on the same PostToolUse/Edit|Write event, in array order). This means tests run against formatted code.

**Dependencies:** `jq`, `uv`, `ruff`. Degrades gracefully if uv is not found.

</details>

#### test-on-change.sh

<details>
<summary>Why / What / Remove / Connects</summary>

**Why it exists.** Immediate feedback. Without it, Claude writes code, moves on, and only discovers test failures when `/done` runs validation -- potentially after many edits. With it, Claude sees failures right after the edit that caused them.

**What it does.** Triggers after every `Edit` or `Write` on `*.py` files. Discovers the associated test file using two strategies:

1. Walk up from the edited file looking for `tests/test_<basename>.py` adjacent to the package
2. Check the project root `tests/test_<basename>.py`

Skips test files themselves, `__init__.py`, and `conftest.py`. Runs `uv run pytest <test_file> -x -q` (stop on first failure, quiet output). On failure, emits a `systemMessage` with the last 20 lines of test output. Always exits 0.

**What happens if you remove it.** No instant test feedback during editing. Tests still run during `/done` validation (via the `test-coverage-validator` agent), so nothing is missed -- just delayed.

**How it connects.** Runs after `auto-format.sh`, so tests execute against formatted code. Uses `$CLAUDE_PROJECT_DIR` for root-relative test discovery.

**Dependencies:** `jq`, `uv`, `pytest`. Degrades gracefully if uv is not found.

</details>

### security-guidance Plugin

<details>
<summary>Why / What / Remove / Connects</summary>

**Why it exists.** The hooks catch dangerous commands and output. This plugin catches dangerous *code patterns* while Claude is writing them -- before they ever execute.

**What it does.** A Claude Code built-in plugin (`security-guidance@claude-code-plugins`) that emits real-time warnings when Claude writes code containing:
- Command injection patterns (`os.system()`, `subprocess(shell=True)`)
- Code injection (`eval()`, `exec()`, `__import__()` with user input)
- Unsafe deserialization (`pickle.loads()`, `yaml.load()` without SafeLoader)
- XSS patterns

Enabled via `enabledPlugins` in `settings.json`.

**What it does not do.** It does not block code from being written. It only warns. The developer or Claude must act on the warning.

**What happens if you remove it.** No inline security warnings during code editing. The `security-auditor` agent and `/security-audit` command can still catch these patterns, but only when explicitly invoked.

**How it connects.** Works alongside hooks (which cover commands and output) to cover the third attack surface: the code itself.

</details>

---

## Devcontainer Security Layers

These layers only apply when running inside the devcontainer. They are optional but recommended for autonomous usage.

### Network Firewall (init-firewall.sh)

<details>
<summary>Why / What / Remove / Connects</summary>

**Why it exists.** A containerized Claude Code session could download and execute arbitrary code from the internet. The firewall restricts network access to known-good services only.

**What it does.** Runs via `postStartCommand` (with sudo). Sets the default iptables OUTPUT policy to DROP, then whitelists:

- DNS (port 53, TCP/UDP)
- SSH (port 22)
- Localhost (loopback)
- GitHub IPs (fetched dynamically from GitHub's API, aggregated into CIDR ranges via `ipset`)
- Specific domains: PyPI (`pypi.org`, `files.pythonhosted.org`), Astral (`astral.sh`), Claude/Anthropic (`claude.ai`, `api.anthropic.com`, `sentry.io`, `statsig.com`), VS Code marketplace

GitHub CIDR ranges are aggregated using the `aggregate` tool, then stored in `ipset` with `hash:net` for efficient filtering instead of per-IP iptables rules. IPv6 is completely blocked. Self-tests at the end by verifying `example.com` is unreachable and `api.github.com` is reachable.

**What happens if you remove it.** The container has unrestricted network access. Claude Code could download arbitrary packages from any host, which is a supply-chain attack vector.

**How it connects.** Complements the `devcontainer-policy-blocker.sh` (which blocks `pip install` commands) by also blocking the network path. Even if someone bypasses the command-level block, the firewall prevents reaching unauthorized hosts.

**Dependencies:** `iptables-legacy`, `ipset`, `curl`. Degrades gracefully -- logs warning and exits 0 if iptables is unavailable.

</details>

### Policy Blocker (devcontainer-policy-blocker.sh)

<details>
<summary>Why / What / Remove / Connects</summary>

**Why it exists.** The three permission tiers (Assisted, Autonomous, Full Trust) need enforcement beyond settings.json patterns. This hook reads `$PERMISSION_TIER` and blocks commands that the current tier does not allow.

**What it does.** Triggers on every `Bash` tool invocation inside the devcontainer. Checks the command against blocked categories:

| Category | Tiers 0/1/2 | Tier 3 |
|----------|-------------|--------|
| Tool installation (pip, npm -g, apt, uv tool) | BLOCKED | Allowed |
| Package publishing (npm publish, uv publish, twine) | BLOCKED | BLOCKED |
| Supply-chain piping (curl url \| bash) | BLOCKED | BLOCKED |
| Docker escapes (--privileged, --cap-add=ALL) | BLOCKED | BLOCKED |
| GitHub mutations (gh pr merge, gh workflow run) | BLOCKED | Allowed |
| Infrastructure (terraform) | BLOCKED | Allowed |

**Critical behavior:** This hook is **fail-closed**. If `jq` is missing or `$PERMISSION_TIER` is unset, it blocks ALL bash commands (exit 2). This is intentional -- in a security-critical devcontainer, failing open would defeat the purpose.

**What happens if you remove it.** Tiers 1 and 2 lose their command-level enforcement. The settings.json permission patterns still apply, but the tier-specific blocking (e.g., blocking `pip install` in tier 2) disappears.

**How it connects.** Works with the tier files in `.devcontainer/permissions/` and the `$PERMISSION_TIER` env var set in `devcontainer.json`. See [How Tiers Work](#how-tiers-work-under-the-hood) below.

**Dependencies:** `jq` (REQUIRED -- no graceful degradation; fails closed).

</details>

### Non-root User

<details>
<summary>Why / What / Remove / Connects</summary>

**Why it exists.** Principle of least privilege. A root user inside the container could modify system files, install packages at the OS level, and potentially escape the container in some Docker configurations.

**What it does.** The Dockerfile creates a `vscode` user (uid 1000) and runs all commands as that user. Sudo is restricted to a single script: `/usr/local/bin/init-firewall.sh`. The user cannot run `sudo iptables` directly.

**What happens if you remove it.** Claude Code runs as root inside the container. Combined with removed firewall/policy hooks, this means unrestricted system access within the container.

**How it connects.** The firewall script uses sudo (allowed for firewall commands). The rest of the stack runs unprivileged.

</details>

---

## Agents

### How Agents Work

Agents are Claude Code sub-processes defined in `.claude/agents/`. Each agent file is a Markdown document with YAML frontmatter that specifies:

- **model**: Which Claude model to use. `haiku` is cheap and fast (good for lint/format). `sonnet` is more capable (good for review/analysis). Model choice directly affects token costs.
- **tools**: Which tools the agent can use. Read-only agents (`Read, Glob, Grep`) cannot modify files. Write-capable agents add `Edit` or `Bash`.
- **permissionMode**: Controls user prompting:
  - `dontAsk` -- runs silently, no prompts (used for read-only tasks)
  - `plan` -- generates recommendations without executing (used for auditors)
  - `acceptEdits` -- can create and modify files during execution (used for validators that auto-fix)

Agents are invoked by the workflow (typically via `/done`) using `subagent_type: "general-purpose"`. You do not invoke them directly -- the skill orchestrates them.

For the full agent reference table, see [Development Process > Agent Reference](DEVELOPMENT_PROCESS.md#agent-reference).

### Core Workflow Agents

These run automatically as part of `/done` for Standard and Project scope tasks.

<details>
<summary>code-quality-validator (model: haiku)</summary>

**Why.** Catches lint, format, and type errors before they reach CI. Uses Haiku for speed since the task is mechanical.

**What.** Runs `ruff check`, `ruff format --check`, and `pyright`. Can auto-fix issues via `Edit` tool (`permissionMode: acceptEdits`).

**Remove.** Lint/format/type issues reach CI instead of being caught locally. `/done` still works but skips this validation step.

</details>

<details>
<summary>test-coverage-validator (model: sonnet)</summary>

**Why.** Verifies tests pass and checks coverage. Uses Sonnet because it needs to reason about test adequacy, not just run commands.

**What.** Runs `pytest` with coverage flags. Analyzes results and reports findings. Read-only (`permissionMode: dontAsk` -- no Edit tool).

**Remove.** Tests are not validated before PR creation. CI still runs them, but you lose the pre-commit coverage check.

</details>

<details>
<summary>pr-writer (model: sonnet)</summary>

**Why.** Consistent, informative PR descriptions. Humans tend to write "fixed the thing" -- this agent reads the diff and produces a structured summary with test plan.

**What.** Reads `git diff`, `git log`, and changed files. Generates a PR description following the template in `.github/PULL_REQUEST_TEMPLATE.md`. Read-only (`permissionMode: dontAsk`).

**Remove.** You write PR descriptions manually. The PR template still applies but is not auto-filled.

</details>

<details>
<summary>code-reviewer (model: sonnet)</summary>

**Why.** Independent code review before the PR is created. Catches logic errors, security issues, and design problems that linters miss.

**What.** Reads the diff and applies the review rules (architecture, code-quality, performance, test). Reports findings with severity levels. Read-only (`permissionMode: dontAsk`, `memory: project` for CLAUDE.md context).

**Remove.** No pre-PR code review. The GitHub Actions `claude-code-review.yml` workflow still runs an AI review on the PR itself, so review is delayed but not eliminated.

</details>

<details>
<summary>docs-updater (model: sonnet)</summary>

**Why.** Keeps changelog and decision log in sync with code changes. Developers forget to update docs -- this agent does it automatically.

**What.** Reads the diff and recent commits. Updates `docs/CHANGELOG.md` and `docs/DECISIONS.md` if changes warrant it (`permissionMode: acceptEdits`).

**Remove.** Docs must be updated manually. The changelog and decision log drift out of sync with code.

</details>

### Project-Scope Agents

These run only for P-scoped (multi-phase) tasks.

<details>
<summary>acceptance-criteria-validator and implementation-tracker</summary>

**acceptance-criteria-validator.** Verifies that the implementation meets the acceptance criteria defined in `docs/IMPLEMENTATION_PLAN.md`. Runs at step P.3.2.

**implementation-tracker.** Keeps `IMPLEMENTATION_PLAN.md` in sync with actual progress. Can mark phases complete and update status (`permissionMode: acceptEdits`).

**Remove either.** Multi-phase projects lose automated progress tracking. You manage the plan manually.

</details>

### Optional Specialists

These are invoked manually, not by `/done`. They have no workflow dependencies.

<details>
<summary>Full list</summary>

| Agent | Purpose | Mode |
|-------|---------|------|
| security-auditor | OWASP-based vulnerability scan | plan (read-only) |
| refactoring-specialist | SOLID/code smell analysis | plan (read-only) |
| review-responder | Triage and fix automated PR review comments | acceptEdits |
| output-evaluator | LLM-as-Judge quality scoring | dontAsk |
| agent-auditor | Audit agent definitions against best practices | plan (read-only) |

**Remove any.** No workflow impact. These are convenience tools you invoke when needed.

</details>

---

## Skills and Commands

### Workflow Skills

The four workflow skills chain together to form the development lifecycle. Each reads and writes specific files.

| Skill | Reads | Writes | Depends on |
|-------|-------|--------|------------|
| `/sync` | git state | nothing | (standalone) |
| `/design` | DECISIONS.md, IMPLEMENTATION_PLAN.md | IMPLEMENTATION_PLAN.md (P-scope only) | (standalone) |
| `/done` | git diff, tests, IMPLEMENTATION_PLAN.md | commits, PR, CHANGELOG.md, DECISIONS.md | agents, hooks |
| `/landed` | git reflog, gh pr, gh run, deploy.json | branch deletion, plan status check | (standalone) |

<details>
<summary>What breaks if you remove one</summary>

**Remove /sync.** No pre-flight check. You might start work on a stale branch or with uncommitted files. Low risk -- it is a convenience.

**Remove /design.** No structured planning step. You can still plan manually and write to IMPLEMENTATION_PLAN.md yourself. The `/done` skill does not require `/design` to have run first.

**Remove /done.** This is the orchestrator. Without it, you must manually run lint, tests, code review, commit, push, create PR, and update docs. The agents and hooks still work individually, but nothing chains them together.

**Remove /landed.** No post-merge verification. You must manually check CI, delete branches, and identify the next phase for P-scope work.

</details>

### Utility Skill

**`/edit-permissions`** -- Interactive tool for managing `settings.json` permission rules. Provides pattern syntax reference and safety guardrails. Safe to remove -- you can edit `settings.json` manually.

### Commands

| Command | Purpose | Remove impact |
|---------|---------|---------------|
| `/cove` | Chain-of-Verification for high-stakes accuracy | No workflow impact. Use when you need verified facts. |
| `/cove-isolated` | CoVe with isolated verification agent | Same as `/cove` but prevents confirmation bias. |
| `/security-audit` | 6-phase Python security scan with A-F grading | No workflow impact. Use for periodic security review. |

---

## Rules

Rules are Markdown files in `.claude/rules/` that Claude loads as context in every conversation. They influence Claude's decisions but are not enforced programmatically -- they are instructions, not constraints.

| Rule | What it guides |
|------|---------------|
| architecture-review | Component boundaries, dependency direction, data flow, security boundaries |
| code-quality-review | DRY violations, error handling, type annotations, complexity |
| performance-review | N+1 queries, memory leaks, caching, algorithmic complexity |
| test-review | Coverage gaps, test quality, edge cases, assertion quality |

<details>
<summary>Adding, modifying, or removing rules</summary>

**Add a rule.** Create a new `.md` file in `.claude/rules/`. It is automatically loaded -- no registration needed.

**Modify a rule.** Edit the file directly. Changes take effect in the next conversation.

**Remove a rule.** Delete the file. Claude loses that review dimension. For example, removing `performance-review.md` means Claude stops checking for N+1 queries and memory leaks during code review.

Rules do not affect hooks, agents, or CI. They only affect Claude's reasoning during interactive sessions and when the `code-reviewer` agent runs (which has `memory: project` and reads CLAUDE.md context).

</details>

---

## Configuration Files

### settings.json

Location: `.claude/settings.json`

This is the central configuration file. It controls three things:

1. **Permissions** (allow/deny/ask lists with glob patterns)
2. **Hooks** (shell scripts triggered by tool events)
3. **Plugins** (built-in Claude Code extensions)

<details>
<summary>Permission evaluation order</summary>

For each command Claude wants to run:
1. Check **deny** list first -- if any pattern matches, block immediately (no prompt)
2. Check **ask** list -- if any pattern matches, prompt the user for approval
3. Check **allow** list -- if any pattern matches, execute without prompting
4. If nothing matches, prompt the user (default behavior)

Patterns use glob syntax: `Bash(git status)` matches the exact command, `Bash(git *)` matches any git subcommand.

</details>

<details>
<summary>Hook registration format</summary>

Hooks are registered in `settings.json` under the `hooks` key. Each hook specifies a trigger event (`PreToolUse` or `PostToolUse`), a matcher (which tools it applies to), and one or more command scripts. Multiple hooks on the same event/matcher run in array order. The `$CLAUDE_PROJECT_DIR` variable resolves to the project root at runtime.

</details>

### settings.local.json

Location: `.claude/settings.local.json` (gitignored)

Machine-specific overrides. If this file exists, it **replaces** (not merges with) `settings.json` for the keys it defines. This is how devcontainer tiers work: the `onCreateCommand` copies a tier file to `settings.local.json`, overriding the default permissions.

An example file is provided at `.claude/settings.local.json.example`.

### CLAUDE.md

Location: project root

The main agent directives file. Deliberately compact (~55 lines). Contains:
- Development process reference (which skills to use)
- Security rules (what to avoid)
- Development commands (how to run tests, lint, format)
- Code style conventions

**What belongs in CLAUDE.md vs elsewhere:**
- CLAUDE.md: short, always-loaded directives
- Rules (`.claude/rules/`): detailed review checklists (loaded as context but not as prominent)
- Agents (`.claude/agents/`): task-specific sub-process definitions
- Skills (`.claude/skills/`): workflow step definitions with their own prompts

Keep CLAUDE.md small. Everything Claude reads costs tokens on every message.

---

## Devcontainer Deep Dive

### How Tiers Work Under the Hood

```text
devcontainer.json
  containerEnv:
    PERMISSION_TIER: "${localEnv:PERMISSION_TIER:2}"   # default: 2
                        |
                        v
  onCreateCommand:
    case $PERMISSION_TIER in
      1) cp permissions/tier1-assisted.json -> .claude/settings.local.json
      2) cp permissions/tier2-autonomous.json -> .claude/settings.local.json
      3) cp permissions/tier3-full-trust.json -> .claude/settings.local.json
    esac
                        |
                        v
  Claude Code starts, loads:
    1. .claude/settings.json        (base config)
    2. .claude/settings.local.json  (tier override -- replaces matching keys)
                        |
                        v
  devcontainer-policy-blocker.sh reads $PERMISSION_TIER at runtime
  for additional command-level enforcement
```

Key details:
- `$PERMISSION_TIER` is set via `containerEnv` (not `build.args` -- there is no matching `ARG` in the Dockerfile)
- Tier files are **fully self-contained** (permissions + hooks + enabledPlugins). This is required because `settings.local.json` replaces keys, not merges.
- The `onCreateCommand` uses a `case` statement, not simple interpolation, because tier filenames include descriptive suffixes (`tier1-assisted`, not just `tier1`)
- If `$PERMISSION_TIER` is unset, the policy blocker defaults to tier 0 (strictest -- blocks everything)

For the full tier comparison table, see [Devcontainer Permissions](DEVCONTAINER_PERMISSIONS.md).

### Firewall Mechanics

The firewall uses `ipset` + `iptables` instead of DNS-based rules because:
1. DNS resolution can be spoofed
2. Services like GitHub use many IP addresses that change frequently
3. `ipset` handles CIDR ranges efficiently (one rule vs hundreds of per-IP rules)

Whitelisted domains and why each is needed:

| Domain | Why |
|--------|-----|
| GitHub IPs (dynamic) | Git operations, GitHub API, Actions |
| pypi.org, files.pythonhosted.org | Python package installation |
| astral.sh | uv package manager updates |
| claude.ai, api.anthropic.com | Claude Code API calls |
| sentry.io | Error reporting (Claude Code telemetry) |
| statsig.com | Feature flags (Claude Code) |
| VS Code marketplace | Extension updates |

The script self-tests by checking that `example.com` is unreachable and `api.github.com` is reachable. If DNS resolution fails during setup, the affected domain is skipped with a warning (the firewall still activates for everything else).

---

## CI/CD Workflows

All workflows are in `.github/workflows/`. They use `{{base_branch}}` placeholder (replaced by `setup_project.py`).

<details>
<summary>tests.yml -- Lint + Test + Typecheck</summary>

**Why.** Catches quality issues before merge. This is the primary quality gate.

**What.** Triggers on push to base branch or PR. Runs four jobs:
1. **Lint** (ruff format --check + ruff check) -- runs first
2. **test-core** (pytest libs/core/ tests/) -- runs after lint
3. **test-server** (pytest apps/server/) -- runs after lint
4. **typecheck** (pyright) -- runs after lint

**Remove.** No automated quality checks. Code review and local validation are the only safety nets.

</details>

<details>
<summary>claude-code-review.yml -- AI Code Review</summary>

**Why.** Automated code review on PRs using Claude. Catches issues that linters cannot: logic errors, security concerns, design problems.

**What.** Triggers on PR open/sync/ready. Uses `anthropics/claude-code-action@v1` with Sonnet. Reviews for correctness, security, performance, readability, and testing. Has read-only tools (Read, Glob, Grep -- no Bash). Posts findings as PR comments. 10-minute timeout.

**Remove.** No AI review on PRs. The local `code-reviewer` agent (run by `/done`) still provides pre-PR review.

</details>

<details>
<summary>template-integration.yml -- Template Validation</summary>

**Why.** Ensures `setup_project.py` works across all configuration variants. This is template-specific -- downstream projects can remove it.

**What.** Tests five configurations: mono-default, mono-renamed, mono-extra-pkgs, single-package, mono-postgres. Runs `scripts/test_template_integration.sh` for each.

**Remove.** Safe to remove in downstream projects. Only needed if you are modifying the template itself.

</details>

<details>
<summary>publish.yml -- PyPI Publishing</summary>

**Why.** Automated package publishing using OIDC (no stored API tokens).

**What.** Triggers on GitHub release or manual dispatch. Determines package from release tag (e.g., `core-v0.1.0` maps to `libs/core`). Builds with `uv build` and publishes via `pypa/gh-action-pypi-publish`. Requires Trusted Publisher configuration on PyPI.

**Remove.** Manual publishing only. You would run `uv build` and `twine upload` yourself.

</details>

<details>
<summary>template-sync.yml -- Upstream Template Sync</summary>

**Why.** Keeps downstream projects updated with template improvements (new hooks, agents, CI fixes).

**What.** Runs on schedule (weekly). Syncs template-managed paths while preserving project-specific content. Creates a PR with the updates for review.

**Remove.** No automatic updates from the template. You would manually cherry-pick improvements.

</details>

---

## Customization Guide

### Safe to Remove

These components have no dependencies. Removing them does not break any workflow.

- **Optional agents**: security-auditor, refactoring-specialist, review-responder, output-evaluator, agent-auditor
- **Commands**: /cove, /cove-isolated, /security-audit
- **Productivity hooks**: auto-format.sh, test-on-change.sh (CI still catches issues)
- **CI workflows**: template-integration.yml (in downstream projects), template-sync.yml, publish.yml
- **Rules**: any individual rule file (Claude loses that review dimension but everything else works)

### Safe to Modify

- **Hook patterns**: Add or remove blocked patterns in any hook script. The format is documented in the script comments.
- **Permission lists**: Edit `settings.json` allow/deny/ask patterns. Use `/edit-permissions` for guided editing.
- **Agent models**: Change `model:` in agent frontmatter. Use `haiku` for speed/cost, `sonnet` for capability.
- **Firewall whitelist**: Add domains to `init-firewall.sh`. Follow the existing pattern of DNS resolution + ipset addition.
- **CI workflows**: Add jobs, change triggers, modify test commands.
- **CLAUDE.md**: Add project-specific directives. Keep it concise.

### Risky to Remove

These components protect against real attack vectors or are load-bearing for the workflow.

| Component | Risk if removed |
|-----------|-----------------|
| dangerous-actions-blocker.sh | Destructive commands can execute unchecked |
| unicode-injection-scanner.sh | Vulnerable to trojan source attacks (CVE-2025-53109/53110) |
| output-secrets-scanner.sh | Secrets can leak into conversation logs without warning |
| security-guidance plugin | No real-time security warnings during code editing |
| devcontainer-policy-blocker.sh | Permission tiers lose command-level enforcement |
| init-firewall.sh | Container has unrestricted network access |
| /done skill | No workflow orchestration; must manually run lint, test, review, PR, docs |
| settings.json | Falls back to prompting for every command (functional but painful) |
| tests.yml | No automated quality gate before merge |
