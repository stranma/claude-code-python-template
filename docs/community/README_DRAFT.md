# Claude Code Python Template

[![CI](https://github.com/stranma/claude-code-python-template/actions/workflows/tests.yml/badge.svg)](https://github.com/stranma/claude-code-python-template/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![uv](https://img.shields.io/badge/uv-workspace-blueviolet)](https://docs.astral.sh/uv/)

**An opinionated Python project template that makes Claude Code produce consistent, tested, production-quality code.**

Without structure, Claude Code results vary -- tests get skipped, context gets lost between sessions, small fixes turn into rewrites. This template gives you a complete starting point: TDD workflow, quality gates, security hooks, and a 3-command workflow that scales from typo fixes to multi-phase projects.

This is opinionated by design. It picks uv, ruff, pyright, pytest, and hatchling. It enforces TDD. It runs agents on every PR. If that's what you want, you're in the right place. If not, no hard feelings.

## Who Is This For?

**Getting started with Claude Code?** The template gives you a working CLAUDE.md, agents, hooks, and a modern Python toolchain -- all configured and ready. Instead of spending days figuring out what works, start with a setup that enforces good habits from day one.

**Building solo?** You move fast, but you still want tests, type checking, linted code, and proper PRs. The template's agents handle the discipline so you can focus on the problem.

**Leading a team adopting Claude Code?** Without a shared baseline, every developer has their own CLAUDE.md (or none). This template standardizes how your team uses Claude Code -- same workflow, same quality gates, same security hooks across all projects.

## How It Works

Three commands. That's the whole workflow:

```
/sync   Preflight check. Fetches remote, reports branch state, dirty files.
/design Turns brainstorming into a structured plan. Reads decision log,
        auto-classifies scope, outputs actionable steps.
/done   Ships your work. Auto-detects scope, validates (lint + test + review),
        commits, creates PR, updates docs. One command.
```

Real workflows:

```
Quick fix:     /sync -> fix the bug -> /done
New feature:   /sync -> brainstorm with Claude -> /design -> "implement this" -> /done
Multi-phase:   /sync -> brainstorm -> /design -> "implement phase 1" -> /done -> ... -> /done
Exploration:   just talk to Claude -- no commands needed
```

You never classify tasks upfront. `/done` auto-detects scope from your branch, diff size, and whether an implementation plan exists -- then picks the right level of ceremony:

| Detected scope | What `/done` does |
|----------------|-------------------|
| **Quick** (on main, small diff) | Validate, commit, push, verify CI |
| **Standard** (feature branch) | Validate, commit, PR, CI, code review, update changelog |
| **Project** (has plan phases) | All of Standard + acceptance criteria + plan update + handoff note |

## Quick Start

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/getting-started/installation/), [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)

**1. Create your project**

```bash
# From GitHub: click "Use this template", then clone your new repo
# Or directly:
git clone https://github.com/stranma/claude-code-python-template my-project
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

## What's Included

### Core (always active)

- **CLAUDE.md** -- compact agent directives (~40 lines) with `/sync`, `/design`, `/done` workflow
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
- `/catchup` -- restore context after session break or `/clear`
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
│   ├── skills/                   # /sync, /design, /done, /edit-permissions
│   ├── commands/                 # /catchup, /security-audit
│   ├── hooks/                    # 5 hook scripts
│   └── rules/                    # 4 review rules
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

## A Note on Token Costs

The agents in this template use Claude's sub-agents (mostly Sonnet, some Haiku) to validate code quality, run reviews, and write PR descriptions. This costs tokens beyond what you'd spend on a bare Claude Code session.

This is intentional. A few extra cents per PR is trivially cheap compared to the cost of your time debugging a bug that a code review agent would have caught, or manually writing PR descriptions, or re-running tests you forgot to run. The agents exist because developer time is the expensive resource, not tokens.

If cost is a concern, the workflow agents (code-quality-validator, test-coverage-validator) are the ones that run most frequently. The others (pr-writer, code-reviewer, docs-updater) run once per PR. The optional specialist agents only run when you explicitly invoke them.

## Credits

Monorepo structure inspired by [carderne/postmodern-mono](https://github.com/carderne/postmodern-mono), which demonstrates excellent uv workspace patterns. Key differences:

- Direct `uv run` commands instead of Poe the Poet
- Standard pyright instead of basedpyright
- Claude Code methodology layer (CLAUDE.md, agents, skills, hooks)
- Setup script for template initialization

## License

MIT
