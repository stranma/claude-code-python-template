# CLAUDE.md

## Security

- **Real-time scanning**: The `security-guidance` plugin runs automatically during code editing, warning about command injection, eval/exec, pickle deserialization, XSS, and os.system() usage
- **Runtime hooks**: 3 security hooks run automatically via `.claude/hooks/`:
  - `dangerous-actions-blocker.sh` (PreToolUse/Bash): blocks `rm -rf`, `sudo`, `DROP DATABASE`, `git push --force`, secrets in args
  - `output-secrets-scanner.sh` (PostToolUse/Bash): warns if command output contains API keys, tokens, private keys, or DB URLs
  - `unicode-injection-scanner.sh` (PreToolUse/Edit|Write): blocks zero-width chars, RTL overrides, ANSI escapes, null bytes
- **Secrets handling**: Never commit API keys, tokens, passwords, or private keys -- use environment variables or `.env` files (which are gitignored)
- **Unsafe operations**: Avoid `eval`, `exec`, `pickle.loads`, `subprocess(shell=True)`, and `yaml.load` without SafeLoader in production code. If required, document the justification in a code comment
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

## Code Style

- **Docstrings**: reStructuredText format, PEP 257
- **No special Unicode characters** in code or output -- use plain ASCII (`[x]`, `[OK]`, `PASS`, `FAIL`)
- Use types everywhere possible
- Do not add comments that state the obvious

## Version Management

All packages maintain synchronized MAJOR.MINOR versions. Patch versions can differ. Check with `python scripts/check_versions.py`.

## Development Process

Before starting any task, classify it as **Q** (Quick), **S** (Standard), or **P** (Project) and follow the corresponding path in `docs/DEVELOPMENT_PROCESS.md`. This classification is mandatory -- do not skip it.
