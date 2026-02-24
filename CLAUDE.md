# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Security

- **Real-time scanning**: The `security-guidance` plugin runs automatically during code editing, warning about command injection, eval/exec, pickle deserialization, XSS, and os.system() usage
- **Secrets handling**: Never commit API keys, tokens, passwords, or private keys -- use environment variables or `.env` files (which are gitignored)
- **Unsafe operations**: Avoid `eval`, `exec`, `pickle.loads`, `subprocess(shell=True)`, and `yaml.load` without SafeLoader in production code. If required, document the justification in a code comment
- **Code review**: The code-reviewer agent (step S.6.4) checks for logic-level security issues (authorization bypass, TOCTOU, data exposure) that static pattern matching cannot catch

---

## Repository Structure

This is a **monorepo** using uv workspaces:

```
{{project_name}}/
├── apps/                    # Executable applications (entry points)
│   └── server/              # Example server application
├── libs/                    # Reusable libraries (imported, not executed)
│   └── core/                # Core library
├── tests/                   # Root-level tests
├── scripts/                 # Development & maintenance scripts
├── docs/                    # Documentation
│   ├── CHANGELOG.md         # Running changelog (Keep a Changelog format)
│   ├── DECISIONS.md          # Decision log (feature requests + user decisions)
│   └── IMPLEMENTATION_PLAN.md  # Phase tracking
└── pyproject.toml           # Root workspace config (uv, ruff, pyright, pytest)
```

### Packages

| Package | Path | Purpose |
|---------|------|---------|
| **core** | `libs/core/` | Core library |
| **server** | `apps/server/` | Server application |

---

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

---

## Code Style

Configuration lives in root `pyproject.toml`:

- **Formatter/Linter**: ruff (line-length: 120)
- **Type checker**: pyright (standard mode)
- **Docstrings**: reStructuredText format, PEP 257
- **No special Unicode characters** in code or output -- use plain ASCII (`[x]`, `[OK]`, `PASS`, `FAIL`)
- Use types everywhere possible
- Do not add comments that state the obvious

---

## Testing

- **Framework**: pytest
- **Test locations**: `tests/` (root), `libs/*/tests/`, `apps/*/tests/`
- **Markers**: `slow`, `integration`, `production`
- **Coverage**: `uv run pytest --cov --cov-report=term-missing`

---

## Version Management

All packages should maintain synchronized MAJOR.MINOR versions. Patch versions can differ.

```bash
# Check versions across packages
python scripts/check_versions.py
```

| Client | Server | Compatible? |
|--------|--------|-------------|
| 1.2.3  | 1.2.7  | YES |
| 1.2.3  | 1.3.0  | NO |

---

## Context Recovery Rule -- CRITICAL

**After auto-compact or session continuation, ALWAYS read the relevant documentation files before continuing work:**

1. Read `docs/IMPLEMENTATION_PLAN.md` for current progress
2. Read `docs/CHANGELOG.md` for recent changes
3. Read `docs/DECISIONS.md` for prior feature requests and user decisions
4. Read any package-specific documentation relevant to the task

This ensures continuity and prevents duplicated or missed work.

---

## Development Process

Task complexity determines process depth. Classify each task, then follow the matching path. Within an activated path, execute all steps -- do not cherry-pick.

### Classification

| Path | When to use | Examples |
|------|-------------|---------|
| **Q** (Quick) | Trivial, obvious, single-location change | Typo fix, config tweak, one-liner bug fix |
| **S** (Standard) | Fits in one session, clear scope | New feature, multi-file refactor, bug requiring investigation |
| **P** (Project) | Needs phased execution across sessions | Multi-phase feature, architectural change, large migration |

### Q. Quick Path

1. **Fix it** -- make the change
2. **Validate** -- run `uv run ruff check . && uv run ruff format --check . && uv run pytest`
3. **Commit**

If the fix fails twice or reveals unexpected complexity, promote to **S**.

### S. Standard Path

**S.1 Explore** -- Read relevant code and tests. Identify patterns/utilities to reuse. Understand scope.

**S.2 Plan** -- Read `docs/DECISIONS.md`. Design approach. Identify files to modify. Log the feature request and any user decisions.

**S.3 Setup** -- Create feature branch (`fix/...`, `feat/...`, `refactor/...`). Run `git fetch origin` and sync with base branch.

**S.4 Build (TDD cycle)**
1. Create code structure (interfaces, types)
2. Write tests
3. Write implementation
4. Write docstrings for public APIs; record non-trivial decisions in `docs/IMPLEMENTATION_PLAN.md`
5. Iterate (back to step 2 if needed)

**S.5 Validate** -- run both in parallel via agents:

| Agent | File | What it does |
|-------|------|-------------|
| Code Quality | `.claude/agents/code-quality-validator.md` | Lint, format, type check (auto-fixes) |
| Test Coverage | `.claude/agents/test-coverage-validator.md` | Run tests, check coverage |

Pre-commit hygiene (before agents): no leftover `TODO`/`FIXME`/`HACK`, no debug prints, no hardcoded secrets.

All agents use `subagent_type: "general-purpose"`. Do NOT use `feature-dev:code-reviewer`.

**S.6 Ship**
1. Commit and push
2. Create PR (use `.claude/agents/pr-writer.md` agent to generate description)
3. Verify CI with `gh pr checks`
4. Code review: use `.claude/agents/code-reviewer.md` agent, or `.claude/agents/review-responder.md` if an automated reviewer (e.g., CodeRabbit) is configured. Fix Critical issues before merge.

**S.7 Document** -- Update `docs/CHANGELOG.md` with user-facing changes and `docs/DECISIONS.md` with decisions made. Use `.claude/agents/docs-updater.md` to verify.

**On failure:** fix the issue, amend or re-commit, re-run from the failed step. If multiple steps fail repeatedly, reassess scope.

### P. Project Path

**P.1 Analyze**
- Explore codebase architecture and boundaries
- Read `docs/IMPLEMENTATION_PLAN.md`, `docs/CHANGELOG.md`, and `docs/DECISIONS.md` for prior decisions
- **Consistency check**: scan `docs/DECISIONS.md` for conflicts or obsolete entries. Prune stale decisions. If conflicts found, present the contradiction to the user before proceeding.

**P.2 Plan**
- Design approach and write implementation plan in `docs/IMPLEMENTATION_PLAN.md`
- Define phases with acceptance criteria

**P.3 Execute** (repeat per phase)
1. Run Standard Path (S.1 through S.7) for the phase
2. Verify acceptance criteria (use `.claude/agents/acceptance-criteria-validator.md`)
3. Update `docs/IMPLEMENTATION_PLAN.md` (use `.claude/agents/implementation-tracker.md` or built-in `Plan` agent)
4. Write phase handoff note (2-5 sentences: what completed, deviations, risks, dependencies, intentional debt)

**P.4 Finalize** -- Merge. Version bump and changelog consolidation if applicable.

### Agent Reference

All custom agents are in `.claude/agents/` and use `subagent_type: "general-purpose"`.

| Step | Agent File | Purpose |
|------|-----------|---------|
| S.5 | `code-quality-validator.md` | Lint, format, type check |
| S.5 | `test-coverage-validator.md` | Tests and coverage |
| S.6.2 | `pr-writer.md` | Generate PR description |
| S.6.4 | `code-reviewer.md` | Independent code review |
| S.6.4 | `review-responder.md` | Handle automated reviewer comments |
| S.7 | `docs-updater.md` | Verify and update documentation |
| P.3.2 | `acceptance-criteria-validator.md` | Verify acceptance criteria |
| P.3.3 | `implementation-tracker.md` | Verify plan matches reality |

---

## Changelog Format

Use [Keep a Changelog](https://keepachangelog.com/) format. Sections: Added, Changed, Deprecated, Removed, Fixed, Migration.

Entries must describe **user impact**, not just name the change:
- **Good**: "Users can now filter results by date range using `--since` and `--until` flags"
- **Bad**: "Added date filter"

Update changelog for every MINOR or MAJOR version bump. Patch updates are optional.

---

## PCC Shorthand

When the user says **"PCC"** or **"PCC now"**, execute S.5 through S.7 in order (Validate, Ship, Document).
