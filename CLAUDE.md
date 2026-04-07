# CLAUDE.md

## Development Commands

- Create virtual environment: `uv venv`
- Install all dependencies: `uv sync --all-packages --group dev`

Use `uv run` from the repo root for all commands:

```bash
uv run pytest                           # All tests
uv run pytest libs/core/ -v             # Core tests only
uv run pytest apps/server/ -v           # Server tests only
uv run ruff check .                     # Lint
uv run ruff format .                    # Format
uv run pyright                          # Type check
```

Do not use unnecessary cd like `cd /path/to/cwd && git log`.

## Code Style

- **Docstrings**: reStructuredText format, PEP 257
- **No special Unicode characters** in code or output -- use plain ASCII (`[x]`, `[OK]`, `PASS`, `FAIL`)
- Use types everywhere possible
- Do not add comments that state the obvious

## Version Management

All packages maintain synchronized MAJOR.MINOR versions. Patch versions can differ. Check with `python scripts/check_versions.py`.

## Optional Integrations

This template can be composed with:
- **[claude-code-harness](../claude-code-harness)** -- Claude Code workflow (skills, agents, rules, hooks)
- **[claude-code-devcontainer](../claude-code-devcontainer)** -- secure devcontainer with egress firewall
