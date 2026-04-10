# Claude Code Python Template

[![CI](https://github.com/stranma/claude-code-python-template/actions/workflows/template-integration.yml/badge.svg)](https://github.com/stranma/claude-code-python-template/actions/workflows/template-integration.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![uv](https://img.shields.io/badge/uv-workspace-blueviolet)](https://docs.astral.sh/uv/)

Opinionated Python project template. Picks uv, ruff, pyright, pytest, hatchling. Optionally composes with external tools for Claude Code workflow and secure devcontainer.

## Composition

This template is the scaffolding. Three external components plug into it:

```
                  claude-code-python-template
                     (project structure)
                             |
             setup_project.py orchestrates:
             /               |               \
            v                v                v
   pyclaude-forge    trailofbits/         egress firewall
   (pip install)     claude-code-         (gist fetch)
                     devcontainer
   Installs to       Cloned to            Fetched to
   .claude/          .devcontainer/       .devcontainer/
   - skills          - Dockerfile           init-firewall.sh
   - agents          - devcontainer.json
   - rules           - post_install.py
   - hooks           - install.sh (devc)
   - settings.json
```

| Component | What it does | Required? |
|-----------|--------------|-----------|
| **[pyclaude-forge](https://github.com/stranma/pyclaude-forge)** | Claude Code workflow: `/sync`, `/design`, `/done`, `/landed` skills, 6 agents, 4 review rules, hooks | No |
| **[trailofbits/claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer)** | Secure sandbox: isolated filesystem, OAuth token forwarding, `devc` CLI | No |
| **[Egress firewall](https://gist.github.com/stranma/f43d932bedc8335e24404c9784fcf190)** | iptables whitelist preventing code exfiltration to untrusted domains | No |

Each is independent. Use all three, any combination, or none.

## Quick Start

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# Clone template
git clone https://github.com/stranma/claude-code-python-template.git my-project
cd my-project

# Interactive setup (prompts for everything)
python setup_project.py

# Or CLI mode
python setup_project.py --name my-project --namespace my_project --type single
```

### With devcontainer + firewall

```bash
python setup_project.py --name my-project --namespace my_project \
    --devcontainer trailofbits --egress-firewall
```

### With Claude Code workflow

After setup, install [pyclaude-forge](https://github.com/stranma/pyclaude-forge):

```bash
pip install pyclaude-forge   # or: uv tool install pyclaude-forge
pyclaude-forge install       # installs skills, agents, rules, hooks to .claude/
```

## Project Types

### Monorepo (default)

```
my-project/
  apps/server/           # Applications
  libs/core/             # Libraries
  tests/
  pyproject.toml         # uv workspace root
```

### Single package

```
my-tool/
  src/my_tool/
  tests/
  pyproject.toml
```

## Setup Script Options

| Flag | Default | Description |
|------|---------|-------------|
| `--name` | (required) | Project name (e.g., `my-project`) |
| `--namespace` | from name | Python namespace (e.g., `my_project`) |
| `--type` | `mono` | `mono` or `single` |
| `--packages` | `core,server` | Package names, comma-separated (mono only) |
| `--services` | `none` | Docker Compose services: `none`, `postgres`, `postgres-redis`, `custom` |
| `--devcontainer` | `none` | `none` or `trailofbits` |
| `--egress-firewall` | false | Fetch egress firewall into `.devcontainer/` |
| `--python-version` | `3.11` | Python version |
| `--base-branch` | `master` | Git base branch |
| `--git-init` | false | Init git + initial commit |

Package prefixes control placement: `--packages "lib:models,lib:utils,app:api,app:worker"`.

## Development Commands

```bash
uv sync --all-packages --group dev    # Install dependencies
uv run pytest                          # Run tests
uv run ruff check .                    # Lint
uv run ruff format .                   # Format
uv run pyright                         # Type check
```

## CI/CD Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `tests.yml` | Push, PRs | Lint + test + typecheck (per-package) |
| `template-integration.yml` | Push, PRs | Validates `setup_project.py` across 5 configs |
| `publish.yml` | Release | Publish packages to PyPI |
| `template-sync.yml` | Weekly | Sync workflow/script updates from upstream |

## Credits

Monorepo structure inspired by [carderne/postmodern-mono](https://github.com/carderne/postmodern-mono). Template sync workflow inspired by [serpro69/claude-starter-kit](https://github.com/serpro69/claude-starter-kit).

## License

MIT
