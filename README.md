# Claude Code Python Template

A production-ready Python project template designed for use with [Claude Code](https://claude.com/claude-code). Includes a battle-tested development methodology with TDD workflow, automated quality gates, and an 11-step Phase Completion Checklist enforced by 7 custom Claude Code agents.

## What's Included

- **Monorepo layout** with `apps/` + `libs/` separation using [uv](https://docs.astral.sh/uv/) workspaces (inspired by [carderne/postmodern-mono](https://github.com/carderne/postmodern-mono))
- **CLAUDE.md** with generalized development methodology (~400 lines):
  - Test-Driven Development process
  - 11-step Phase Completion Checklist (PCC)
  - Failure & Rollback Protocol
  - Context Recovery Rule
- **7 Claude Code agents** automating quality gates:
  - `code-quality-validator` (haiku) -- linting, formatting, type checks
  - `test-coverage-validator` (sonnet) -- TDD validation & coverage
  - `acceptance-criteria-validator` (sonnet) -- cumulative criteria verification
  - `implementation-tracker` (sonnet) -- plan vs reality sync
  - `docs-updater` (sonnet) -- auto-update docs & changelog
  - `pr-writer` (sonnet) -- structured PR descriptions
  - `review-responder` (sonnet) -- automated review triage (optional)
- **CI/CD workflows** for GitHub Actions (lint + test + typecheck + publish)
- **GitHub templates** for PRs, bug reports, and feature requests
- **Setup script** for one-command project initialization

## Quick Start

### 1. Create from Template

Click **"Use this template"** on GitHub, or clone directly:

```bash
git clone https://github.com/YOUR_USERNAME/claude-code-python-template my-project
cd my-project
```

### 2. Run Setup

**Interactive mode** (for humans):
```bash
python setup_project.py
```

**CLI mode** (for Claude agents or scripts):
```bash
python setup_project.py \
  --name my-project \
  --namespace my_project \
  --description "My awesome project" \
  --author "Your Name" \
  --email "you@example.com" \
  --base-branch main \
  --type mono \
  --packages "core,api,worker"
```

**Single-package mode** (no monorepo):
```bash
python setup_project.py \
  --name my-tool \
  --namespace my_tool \
  --type single
```

### 3. Install Dependencies

```bash
uv sync --group dev
```

### 4. Install Claude Code Plugins

The setup script attempts this automatically. If Claude Code wasn't installed at setup time:

```bash
claude plugin install security-guidance --scope project
```

### 5. Verify

```bash
uv run pytest
uv run ruff check .
uv run pyright
```

### 6. Remove Setup Script

```bash
rm setup_project.py
```

## Project Structure

### Monorepo (default)

```
my-project/
├── CLAUDE.md                     # Development methodology
├── apps/                         # Executable applications
│   └── api/                      # Example: API server
│       ├── pyproject.toml
│       └── my_project/api/
├── libs/                         # Reusable libraries
│   └── core/                     # Example: Core library
│       ├── pyproject.toml
│       └── my_project/core/
├── tests/                        # Root-level tests
├── scripts/                      # Dev scripts
├── docs/                         # Documentation
│   ├── CHANGELOG.md
│   └── IMPLEMENTATION_PLAN.md
├── .claude/                      # Claude Code config
│   ├── settings.local.json       # Tool permissions
│   └── agents/                   # 7 custom agents
├── .github/                      # CI/CD
│   ├── workflows/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
└── pyproject.toml                # Root workspace config
```

### Single Package

```
my-tool/
├── CLAUDE.md
├── src/my_tool/                  # Package source
├── tests/
├── docs/
├── .claude/
├── .github/
└── pyproject.toml
```

## Development Methodology

This template encodes a development process proven across real production projects:

### TDD Workflow

1. **Structure** -- Define classes/functions with type annotations
2. **Test** -- Write unit tests for the interface
3. **Implement** -- Write code to pass tests
4. **Iterate** -- Repeat for next increment
5. **Integrate** -- Run integration tests
6. **Validate** -- Run Phase Completion Checklist

### Phase Completion Checklist (PCC)

After each development phase, 11 mandatory steps run in order:

| Step | Name | Agent |
|------|------|-------|
| 0 | Sync with Remote | -- |
| 1 | Pre-Commit Hygiene | -- |
| 2 | Commit & Push | -- |
| 3a | Code Quality | `code-quality-validator` |
| 3b | Test Coverage | `test-coverage-validator` |
| 3c | Acceptance Criteria | `acceptance-criteria-validator` |
| 4 | Implementation Check | `implementation-tracker` |
| 5 | Documentation Update | `docs-updater` |
| 6 | Version Changelog | -- (if applicable) |
| 7 | Create PR | `pr-writer` |
| 8 | Verify CI | -- |
| 9 | Code Review | `review-responder` (optional) |
| 10 | Phase Handoff | -- |

## Setup Script Options

| Flag | Default | Description |
|------|---------|-------------|
| `--name` | (required) | Project name (e.g., `my-project`) |
| `--namespace` | from name | Python namespace (e.g., `my_project`) |
| `--description` | "A Python project" | Short description |
| `--author` | "" | Author name |
| `--email` | "" | Author email |
| `--python-version` | "3.11" | Python version requirement |
| `--base-branch` | "main" | Git base branch |
| `--type` | "mono" | `mono` or `single` |
| `--packages` | "core,server" | Comma-separated package names |
| `--git-init` | false | Init git + initial commit |
| `--keep-setup` | false | Don't suggest deleting setup script |

### Package naming

By default, the first package is created as a library (in `libs/`) and subsequent packages as applications (in `apps/`). Use prefixes to control placement:

```bash
--packages "lib:models,lib:utils,app:api,app:worker"
```

## Tool Stack

| Tool | Purpose |
|------|---------|
| [uv](https://docs.astral.sh/uv/) | Package management & workspaces |
| [ruff](https://docs.astral.sh/ruff/) | Linting & formatting (line-length: 120) |
| [pyright](https://github.com/microsoft/pyright) | Type checking (standard mode) |
| [pytest](https://pytest.org/) | Testing framework |
| [hatchling](https://hatch.pypa.io/) | Build backend |

## Credits

Monorepo structure inspired by [carderne/postmodern-mono](https://github.com/carderne/postmodern-mono), which demonstrates excellent uv workspace patterns. Key differences from that project:

- Direct `uv run` commands instead of Poe the Poet
- Standard pyright instead of basedpyright
- Claude Code methodology layer (CLAUDE.md, agents, PCC)
- Setup script for template initialization

## License

MIT
