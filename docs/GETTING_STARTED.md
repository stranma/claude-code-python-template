# Getting Started Guide

A step-by-step guide for developers who are new to Claude Code, modern Python tooling, or both.

## Prerequisites You Need

Before using this template, you should be comfortable with:

### Terminal basics
- Opening a terminal (VS Code integrated terminal, Windows Terminal, macOS Terminal)
- Navigating directories (`cd`, `ls`/`dir`)
- Running commands and reading their output
- Understanding file paths

### Git basics
- What a repository is
- `git clone`, `git add`, `git commit`, `git push`
- What a branch is and how to create one (`git checkout -b`)
- What a pull request (PR) is -- you don't need to be an expert, but you should understand the concept

If git is new to you, work through [Git - the simple guide](https://rogerdudler.github.io/git-guide/) first. It takes about 15 minutes.

### GitHub account
- You need a [GitHub](https://github.com) account to use the template and its CI/CD workflows
- Install the [GitHub CLI](https://cli.github.com/) (`gh`) -- the template's `/done` command uses it to create PRs and check CI status

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

uv replaces pip, virtualenv, and poetry. It's fast and handles everything.

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

### 4. VS Code + Dev Containers (recommended)

The template includes a devcontainer that sandboxes Claude Code for safety.

1. Install [VS Code](https://code.visualstudio.com/)
2. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
3. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
4. Clone your project, open in VS Code, and click "Reopen in Container" when prompted

The devcontainer comes with Python, uv, ruff, git, and Claude Code pre-installed.

## Your First Project

### 1. Create from template

Go to [stranma/claude-code-python-template](https://github.com/stranma/claude-code-python-template) and click **"Use this template"** > **"Create a new repository"**. Clone it locally.

### 2. Run setup

```bash
python setup_project.py --name my-first-project --namespace my_first_project --type single
```

This renames all placeholder files to match your project name.

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

All three should pass with no errors.

### 5. Start Claude Code

```bash
claude
```

Try these to get a feel for the workflow:

```
> /sync
> "Add a function that calculates fibonacci numbers with tests"
> /done
```

Claude Code will write the code, write tests, and `/done` will validate, commit, and create a PR.

## Key Concepts

### What is CLAUDE.md?

A file in your project root that tells Claude Code how to behave. It contains project rules, development commands, and workflow references. Think of it as a briefing document for your AI assistant. The template provides one pre-configured for the `/sync` -> `/design` -> `/done` workflow.

### What are agents?

Agents are specialized Claude Code sub-processes that handle specific tasks (linting, testing, code review). They run automatically as part of the workflow. You don't invoke them directly -- `/done` orchestrates them.

### What are hooks?

Shell scripts that run before or after Claude Code actions. For example, the `dangerous-actions-blocker` hook prevents Claude from running `rm -rf` or leaking secrets. They run silently in the background.

### What is TDD?

Test-Driven Development: write the test first, then write the code to make it pass. The template enforces this order. It feels backwards at first, but it produces more reliable code because you're always building toward a defined expectation.

### What is a devcontainer?

A Docker container configured for development. VS Code opens your project inside the container, so all tools are pre-installed and Claude Code runs in a sandbox. If something goes wrong, your host machine is unaffected.

## Next Steps

- Read the [Development Process](DEVELOPMENT_PROCESS.md) to understand the full workflow
- Try the `/design` command to plan a small feature before implementing it
- Run `/security-audit` to see how the security scanning works
- Check [Devcontainer Permissions](DEVCONTAINER_PERMISSIONS.md) if you want to adjust Claude Code's autonomy level
