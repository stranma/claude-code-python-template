# CLAUDE.md

## Development Process

Use `/sync` before starting work, `/design` to formalize a plan, and `/done` when finished. `/design` estimates scope (Q/S/P) during planning; `/done` auto-detects actual scope at completion based on workspace signals. Before creating any plan, read `docs/DEVELOPMENT_PROCESS.md` first.

## Security

- **Real-time scanning**: The `security-guidance` plugin runs automatically during code editing, warning about command injection, eval/exec, pickle deserialization, XSS, and os.system() usage
- **Runtime hooks**: 3 base security hooks run automatically via `.claude/hooks/` (+ 1 devcontainer-only policy hook):
  - `dangerous-actions-blocker.sh` (PreToolUse/Bash): blocks `rm -rf`, `sudo`, `DROP DATABASE`, `git push --force`, secrets in args
  - `output-secrets-scanner.sh` (PostToolUse/Bash): warns if command output contains API keys, tokens, private keys, or DB URLs
  - `unicode-injection-scanner.sh` (PreToolUse/Edit|Write): blocks zero-width chars, RTL overrides, ANSI escapes, null bytes
  - `devcontainer-policy-blocker.sh` (PreToolUse/Bash, devcontainer only): blocks tool installation, publishing, supply-chain piping, and tier-dependent GH/infra commands
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

Do not use unnecessary cd like `cd /path/to/cwd && git log`.

## Devcontainer Rules

When running in a devcontainer, some operations are denied by policy. Before attempting a command that might be blocked, check `docs/DEVCONTAINER_PERMISSIONS.md` for the approved alternative. Key rules:

- **Dependencies**: Use `uv add <package>`, never `pip install`
- **System tools**: Add to `.devcontainer/Dockerfile`, do not install at runtime
- **No chained cd**: Use absolute paths. `cd /path && command` bypasses permission checks.

## Code Style

- **Docstrings**: reStructuredText format, PEP 257
- **No special Unicode characters** in code or output -- use plain ASCII (`[x]`, `[OK]`, `PASS`, `FAIL`)
- Use types everywhere possible
- Do not add comments that state the obvious

## Version Management

All packages maintain synchronized MAJOR.MINOR versions. Patch versions can differ. Check with `python scripts/check_versions.py`.
