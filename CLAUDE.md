# CLAUDE.md

## Development Process

Use `/sync` before starting work, `/design` to formalize a plan, `/done` when finished, and `/landed` after the PR merges. `/design` estimates scope (Q/S/P) during planning; `/done` auto-detects actual scope at completion based on workspace signals. Before creating any plan, read `docs/DEVELOPMENT_PROCESS.md` first.

## Security

Two-layer defense against data exfiltration:

1. **Firewall** (primary): iptables whitelist in devcontainer blocks all non-approved network domains
2. **Exfiltration guard** (hook): `dangerous-actions-blocker.sh` (PreToolUse/Bash) blocks exfiltration via trusted channels -- `gh gist create`, `gh issue create --body`, package publishing (`twine`/`npm`/`uv publish`), and secrets as literal command arguments

Additional:
- **Real-time scanning**: The `security-guidance` plugin runs automatically during code editing, warning about command injection, eval/exec, deserialization, XSS, and unsafe system calls
- **Secrets handling**: Never commit API keys, tokens, passwords, or private keys -- use environment variables or `.env` files (which are gitignored)
- **Unsafe operations**: Avoid `eval`, `exec`, unsafe deserialization, `subprocess(shell=True)`, and `yaml.load` without SafeLoader in production code. If required, document the justification in a code comment
- **Code review**: The code-reviewer agent checks for logic-level security issues (authorization bypass, TOCTOU, data exposure) that static pattern matching cannot catch

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

## Devcontainer

- **Dependencies**: Use `uv add <package>`, never `pip install`
- **System tools**: Add to `.devcontainer/Dockerfile`, do not install at runtime

## Code Style

- **Docstrings**: reStructuredText format, PEP 257
- **No special Unicode characters** in code or output -- use plain ASCII (`[x]`, `[OK]`, `PASS`, `FAIL`)
- Use types everywhere possible
- Do not add comments that state the obvious

## Version Management

All packages maintain synchronized MAJOR.MINOR versions. Patch versions can differ. Check with `python scripts/check_versions.py`.
