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
- **[pyclaude-forge](https://github.com/stranma/pyclaude-forge)** -- Claude Code workflow (skills, agents, rules, hooks)
- **[trailofbits/claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer)** -- secure devcontainer with Claude Code
- **[Egress firewall](https://gist.github.com/stranma/f43d932bedc8335e24404c9784fcf190)** -- iptables whitelist preventing code exfiltration
