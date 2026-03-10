# Claude Code Python Template

[![CI](https://github.com/stranma/claude-code-python-template/actions/workflows/template-integration.yml/badge.svg)](https://github.com/stranma/claude-code-python-template/actions/workflows/template-integration.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![uv](https://img.shields.io/badge/uv-workspace-blueviolet)](https://docs.astral.sh/uv/)

**An opinionated Python project template that makes Claude Code produce consistent, tested, well-structured code.**

```
/sync                /design              /done                /landed
  |                    |                    |                    |
  fetch remote         scope detection     lint + format        verify merge CI
  branch state         plan generation     tests + coverage     deploy check
  dirty files          decision check      code review          branch cleanup
                                           PR + changelog       next phase
```

This is opinionated by design. It picks uv, ruff, pyright, pytest, and hatchling. It enforces TDD. It runs agents on every PR. It is designed for new Python projects -- not for retrofitting into existing repos. If that's what you want, you're in the right place.

## Who Is This For?

#### Solo developer who knows Python?

You move fast, but you still want tests, type checking, linted code, and proper PRs - why not, it is now almost for free! The template's agents handle the discipline so you can focus on the problem. The devcontainer setup means you can let Claude Code run more autonomously inside a sandbox -- no worrying about it running `rm -rf` on your host machine.

#### Leading a team adopting Claude Code?

Without a shared baseline, every developer has their own CLAUDE.md (or none). This template standardizes how your team uses Claude Code -- same workflow, same quality gates, same security hooks across all projects. The devcontainer with [permission tiers](docs/DEVCONTAINER_PERMISSIONS.md) lets you control how much autonomy Claude Code gets: from per-command approval (Tier 1) to full trust with minimal guardrails (Tier 3).

#### Data scientist or ML engineer?

You know Python and pandas, but software engineering practices (CI/CD, type annotations, code review) feel like overhead. This template adds those practices without you having to learn how to set them up. Claude Code handles the ceremony; you focus on the models.

#### New to Claude Code and still learning Python?

This template is a good way to learn professional practices by doing. It enforces TDD, type checking, linting, and proper git workflow -- things that are hard to pick up from tutorials alone. Claude Code walks you through it, and the agents catch mistakes before they stick. You'll need basic comfort with the terminal and git. If that's new to you, see [Getting Started Guide](docs/GETTING_STARTED.md) for the prerequisites.

## How It Works

Four commands. That's the whole workflow:

```
/sync    Preflight check. Fetches remote, reports branch state, dirty files.
/design  Turns brainstorming into a structured plan. Reads decision log,
         auto-classifies scope, outputs actionable steps.
/done    Ships your work. Auto-detects scope, validates (lint + test + review),
         commits, creates PR, updates docs. One command.
/landed  Post-merge. Verifies CI on master, checks deployments, cleans up
         branches, identifies next phase.
```

Real workflows:

```
Quick fix:     /sync -> fix the bug -> /done
New feature:   /sync -> brainstorm with Claude -> /design -> "implement this" -> /done -> /landed
Multi-phase:   /sync -> brainstorm -> /design -> "implement phase 1" -> /done -> /landed -> ... -> /landed
Exploration:   just talk to Claude -- no commands needed
```

You never classify tasks upfront. `/done` auto-detects scope from your branch, diff size, and whether an implementation plan exists -- then picks the right level of ceremony:

| Detected scope | What `/done` does |
|----------------|-------------------|
| **Quick** (on main, small diff) | Validate, commit, push, verify CI |
| **Standard** (feature branch) | Validate, commit, PR, CI, code review, update changelog |
| **Project** (has plan phases) | All of Standard + acceptance criteria + plan update + handoff note |

## Quick Start

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/getting-started/installation/), [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview). New to these tools? See [Getting Started Guide](docs/GETTING_STARTED.md).

**1. Create your project**

Click **"Use this template"** on GitHub to create your own repo, then clone it:

```bash
git clone https://github.com/YOUR_USERNAME/my-project.git
cd my-project
```

**2. Run setup**

```bash
# Simple project (recommended for first use):
python setup_project.py --name my-tool --namespace my_tool --type single

# Monorepo with multiple packages:
python setup_project.py --name my-project --namespace my_project --type mono --packages "core,api"
```

The setup script replaces `{{project_name}}` placeholders across all files, renames directories to match your namespace, and optionally initializes git. It only modifies files inside the project directory.

**3. Install and verify**

```bash
uv sync --all-packages --group dev
uv run pytest && uv run ruff check . && uv run pyright
```

That's it. Claude Code picks up the agents, hooks, and rules automatically.

## Devcontainer Setup (Recommended)

The template includes a full VS Code devcontainer configuration. This is the recommended way to work because it sandboxes Claude Code -- firewall, non-root user, and policy hooks limit what it can do, so you can give it more autonomy without risk to your host machine.

**What the devcontainer provides:**

- **Network firewall** -- all egress blocked except ~10 whitelisted domains (GitHub, PyPI, etc.)
- **Non-root user** -- Claude Code cannot install system packages or modify system files
- **Permission tiers** -- control how much autonomy Claude Code gets:

| Tier | Name | Who | Claude Code behavior |
|------|------|-----|----------------------|
| 1 | Assisted | New users, compliance teams | Per-command approval |
| 2 | Autonomous (default) | Most developers | Free to run commands, curated deny list |
| 3 | Full Trust | Solo devs with strong CI | Minimal restrictions |

- **Policy hooks** -- block dangerous patterns even in chained commands (`cd /tmp && rm -rf *`)
- **Pre-installed tools** -- Python, uv, ruff, git, Claude Code VS Code extension

Set the tier before building: `PERMISSION_TIER=1` (or 2, 3) in your environment. Default is 2.

See [Devcontainer Permissions](docs/DEVCONTAINER_PERMISSIONS.md) for the full denied commands list and approved alternatives.

## What's Included

### Core (always active)

- **CLAUDE.md** -- compact agent directives (~40 lines) with `/sync`, `/design`, `/done` workflow:

<details>
<summary>See the full CLAUDE.md</summary>

```markdown
## Development Process

Use /sync before starting work, /design to formalize a plan, and /done when
finished. /design estimates scope (Q/S/P) during planning; /done auto-detects
actual scope at completion based on workspace signals.

## Security

- Real-time scanning: security-guidance plugin warns about unsafe patterns
- Runtime hooks: 3 base security hooks (+ 1 devcontainer-only policy hook)
- Secrets handling: Never commit API keys, tokens, passwords, or private keys

## Development Commands

- Create virtual environment: uv venv
- Install all dependencies: uv sync --all-packages --group dev
- Use uv run from the repo root for all commands (pytest, ruff, pyright)

## Code Style

- Docstrings: reStructuredText format, PEP 257
- No special Unicode characters in code or output
- Use types everywhere possible
```

</details>

- **5 workflow agents** -- code quality, test coverage, PR writing, code review, docs updates
- **3 security hooks** -- block destructive commands, scan for leaked secrets, catch Unicode injection
- **CI/CD** -- GitHub Actions for lint + test + typecheck + publish + AI code review
- **Tool stack** -- [uv](https://docs.astral.sh/uv/) workspaces, [ruff](https://docs.astral.sh/ruff/), [pyright](https://github.com/microsoft/pyright), [pytest](https://pytest.org/), [hatchling](https://hatch.pypa.io/)

### Optional specialists

<details>
<summary>7 additional agents for larger projects</summary>

| Agent | Purpose |
|-------|---------|
| `acceptance-criteria-validator` | Verify acceptance criteria across phases |
| `implementation-tracker` | Keep plan and reality in sync |
| `review-responder` | Automated review triage |
| `agent-auditor` | Audit agent definitions for best practices |
| `security-auditor` | OWASP-based vulnerability detection (read-only) |
| `refactoring-specialist` | SOLID/code smell analysis (read-only) |
| `output-evaluator` | LLM-as-Judge quality scoring |

</details>

<details>
<summary>2 productivity hooks</summary>

- **auto-format** -- auto-formats Python files after edits
- **test-on-change** -- auto-runs associated tests after edits

</details>

<details>
<summary>Commands and skills</summary>

- `/sync` -- preflight workspace check before starting work
- `/design` -- crystallize brainstorming into a structured plan
- `/done` -- validate, ship, and document in one command
- `/landed` -- post-merge lifecycle: verify CI, check deploys, clean branches
- `/cove` -- Chain-of-Verification for high-stakes accuracy (4-step self-verification)
- `/cove-isolated` -- CoVe with isolated verification agent (prevents confirmation bias)
- `/security-audit` -- 6-phase security posture scan with A-F grading
- `/edit-permissions` -- manage Claude Code permission rules

</details>

<details>
<summary>4 review rules</summary>

Architecture, code quality, performance, and test quality -- applied automatically during code review.

</details>

## Project Structure

### Monorepo (default)

```
my-project/
├── CLAUDE.md                     # Agent directives (~40 lines)
├── apps/                         # Executable applications
│   └── api/
│       ├── pyproject.toml
│       └── my_project/api/
├── libs/                         # Reusable libraries
│   └── core/
│       ├── pyproject.toml
│       └── my_project/core/
├── tests/
├── docs/
│   ├── CHANGELOG.md
│   ├── DECISIONS.md
│   ├── DEVELOPMENT_PROCESS.md
│   └── IMPLEMENTATION_PLAN.md
├── .claude/                      # Claude Code config
│   ├── settings.json
│   ├── agents/                   # 12 agents
│   ├── skills/                   # /sync, /design, /done, /landed, /edit-permissions
│   ├── commands/                 # /cove, /cove-isolated, /security-audit
│   ├── hooks/                    # 5 hook scripts
│   └── rules/                    # 4 review rules
├── .devcontainer/                # VS Code devcontainer
│   ├── Dockerfile
│   ├── devcontainer.json
│   ├── init-firewall.sh
│   └── permissions/              # Tier 1/2/3 configs
├── .github/
│   ├── workflows/                # CI/CD
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
└── pyproject.toml                # Root workspace config
```

### Single Package

```
my-tool/
├── CLAUDE.md
├── src/my_tool/
├── tests/
├── docs/
├── .claude/
├── .devcontainer/
├── .github/
└── pyproject.toml
```

## Setup Script Options

| Flag | Default | Description |
|------|---------|-------------|
| `--name` | (required) | Project name (e.g., `my-project`) |
| `--namespace` | from name | Python namespace (e.g., `my_project`) |
| `--description` | "A Python project" | Short description |
| `--author` | "" | Author name |
| `--email` | "" | Author email |
| `--python-version` | "3.11" | Python version requirement |
| `--base-branch` | "master" | Git base branch |
| `--type` | "mono" | `mono` or `single` |
| `--packages` | "core,server" | Comma-separated package names (mono only) |
| `--git-init` | false | Init git + initial commit |

Package naming: by default, the first package is a library (in `libs/`), the rest are applications (in `apps/`). Use prefixes to control placement: `--packages "lib:models,lib:utils,app:api,app:worker"`.

## Token Costs

The agents use Claude sub-agents to validate code, run reviews, and write PR descriptions. This adds token usage beyond a bare Claude Code session. Here's what drives costs:

**Runs on every `/done`** (most frequent):
- `code-quality-validator` (Haiku) -- lint, format, type check
- `test-coverage-validator` (Sonnet) -- run tests, check coverage

**Runs once per PR** (Standard and Project scope only):
- `pr-writer` (Sonnet) -- generate PR description
- `code-reviewer` (Sonnet) -- independent code review
- `docs-updater` (Sonnet) -- update changelog and decision log

**Runs only when you invoke them** (optional specialists):
- `security-auditor`, `refactoring-specialist`, `output-evaluator`, etc.

The cost depends on your diff size and model pricing. For most PRs, the sub-agent overhead is small relative to the main session cost. We believe this trade-off is worth it -- developer time spent on manual review, PR writing, and re-running forgotten tests is far more expensive than tokens.

## Credits

Monorepo structure inspired by [carderne/postmodern-mono](https://github.com/carderne/postmodern-mono), which demonstrates excellent uv workspace patterns. Key differences:

- Direct `uv run` commands instead of Poe the Poet
- Standard pyright instead of basedpyright
- Claude Code methodology layer (CLAUDE.md, agents, skills, hooks)
- Setup script for template initialization

Chain-of-Verification commands and template sync workflow inspired by [serpro69/claude-starter-kit](https://github.com/serpro69/claude-starter-kit), a language-agnostic Claude Code starter template with MCP server integrations. Python SOLID checklist items in the refactoring-specialist agent also draw from their structured code review approach.

## License

MIT
