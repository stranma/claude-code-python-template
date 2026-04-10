# Getting Started Guide

A step-by-step guide for developers who are new to Claude Code, modern Python tooling, or both.

## Prerequisites You Need

Before using this template, you should be comfortable with:

### Terminal basics
- Opening a terminal (VS Code integrated terminal, Windows Terminal, macOS Terminal)
- Navigating directories (`cd`, `ls`/`dir`)
- Running commands and reading their output

### Git basics
- `git clone`, `git add`, `git commit`, `git push`
- What a branch is and how to create one (`git checkout -b`)
- What a pull request (PR) is

If git is new to you, work through [Git - the simple guide](https://rogerdudler.github.io/git-guide/) first.

### Python basics
- You can write and run a Python script
- You understand imports, functions, and classes at a basic level
- You don't need to know testing, type annotations, or packaging -- the template teaches these through practice

## Tools to Install

### 1. Python 3.11+

Check your version:
```bash
python --version
```

If you need to install or upgrade: [python.org/downloads](https://www.python.org/downloads/)

### 2. uv (package manager)

```bash
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify: `uv --version`

### 3. Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

You'll need an Anthropic API key or a Claude subscription. See [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code/overview).

### 4. Devcontainer (optional)

For a secure sandbox where Claude Code runs in isolation:

```bash
python setup_project.py --name my-project --devcontainer trailofbits --egress-firewall
```

This clones [trailofbits/claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer) and adds an egress firewall. You'll need:

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. VS Code [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

## Your First Project

### 1. Create from template

Go to [stranma/claude-code-python-template](https://github.com/stranma/claude-code-python-template) and click **"Use this template"**. Clone it locally.

### 2. Run setup

```bash
python setup_project.py --name my-first-project --namespace my_first_project --type single
```

### 3. Install dependencies

```bash
uv sync --all-packages --group dev
```

### 4. Verify everything works

```bash
uv run pytest
uv run ruff check .
uv run pyright
```

### 5. Start Claude Code

```bash
claude
```

Try:
```
> /sync
> "Add a function that calculates fibonacci numbers with tests"
> /done
```

## Key Concepts

### What is CLAUDE.md?

A file in your project root that tells Claude Code how to behave -- project rules, development commands, workflow references. The template provides one pre-configured.

### What are agents?

Specialized Claude Code sub-processes for specific tasks (linting, testing, code review). They run automatically as part of `/done`.

### What are hooks?

Shell scripts that run before or after Claude Code actions. For example, `auto-format` runs ruff after edits.

### What is a devcontainer?

A Docker container configured for development. VS Code opens your project inside it, so all tools are pre-installed and Claude Code runs in a sandbox.

## Next Steps

- Install [pyclaude-forge](https://github.com/stranma/pyclaude-forge) for the full Claude Code workflow (`/sync`, `/design`, `/done`, `/landed`)
- Try the `/design` command to plan a feature before implementing it
- Read the [CHANGELOG](CHANGELOG.md) for the latest updates
