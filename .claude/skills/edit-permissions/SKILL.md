---
name: edit-permissions
description: Manage Claude Code permission rules in .claude/settings.json. Use when adding, removing, or reviewing Bash/Read/Edit/WebFetch permission patterns.
argument-hint: "[add|remove|list|migrate] [pattern]"
allowed-tools: Read, Edit, Grep, Glob
---

# Edit Permissions

Manage Claude Code permission rules in `.claude/settings.json`. This skill helps you safely add, remove, list, and migrate permission patterns.

## Quick Reference -- Permission Rule Syntax

| Tool | Pattern Format | Example |
|------|---------------|---------|
| Bash | `Bash(command *)` | `Bash(npm run *)` |
| Read | `Read(path)` | `Read(/project/src/**)` |
| Edit | `Edit(path)` | `Edit(/project/src/**)` |
| WebFetch | `WebFetch(domain:...)` | `WebFetch(domain:docs.python.org)` |

## Shell Operator Protection

`Bash(cmd *)` does **NOT** match chained commands:

| Pattern | Matches | Does NOT Match |
|---------|---------|----------------|
| `Bash(ls *)` | `ls /foo` | `cd /foo && ls` |
| `Bash(pytest *)` | `pytest tests/` | `cd tests && pytest` |
| `Bash(grep *)` | `grep pattern /file` | `cat file \| grep pattern` |

Chained operators (`&&`, `\|`, `;`, `\|\|`) cause the **entire command** to be evaluated as one unit. Individual patterns will not match partial segments.

**Solution:** Use absolute paths instead of `cd && command` chains. Ensure CLAUDE.md instructs this.

## Pattern Syntax

- **Wildcards:** `*` matches any arguments. `Bash(ls *)` matches `ls`, `ls -la`, `ls /foo/bar`.
- **Word boundaries:** `Bash(ls *)` matches `ls` but NOT `lsof`. The space before `*` acts as a word boundary.
- **Exact match:** `Bash(ls)` matches only `ls` with no arguments.
- **Deprecated syntax:** `Bash(cmd:*)` is equivalent to `Bash(cmd *)` but is **deprecated**. Always use the space form.

## Evaluation Order

Permission rules are evaluated in this order:

1. **deny** -- checked first. If any deny rule matches, the action is blocked.
2. **ask** -- checked second. If any ask rule matches, the user is prompted.
3. **allow** -- checked last. If any allow rule matches, the action proceeds silently.

First match within each category wins.

## Settings File Locations

| Scope | Path | Purpose |
|-------|------|---------|
| Project | `.claude/settings.json` | Shared with team via git |
| User | `~/.claude/settings.json` | Personal preferences |
| Managed | System-dependent managed settings path | Enterprise/admin policies |

Project settings are checked first, then user settings. Managed settings override both.

## Common Patterns

### Git operations
```json
"Bash(git add *)", "Bash(git commit *)", "Bash(git push *)",
"Bash(git fetch *)", "Bash(git pull *)", "Bash(git rebase *)"
```

### Testing
```json
"Bash(pytest *)", "Bash(uv run pytest *)", "Bash(python -m pytest *)"
```

### Package management (uv)
```json
"Bash(uv sync *)", "Bash(uv add *)", "Bash(uv pip *)", "Bash(uv venv *)"
```

### Package management (npm)
```json
"Bash(npm install *)", "Bash(npm run *)", "Bash(npm test *)"
```

### Read-only utilities
```json
"Bash(ls *)", "Bash(cat *)", "Bash(find *)", "Bash(grep *)",
"Bash(head *)", "Bash(tail *)", "Bash(wc *)", "Bash(tree *)"
```

### GitHub CLI
```json
"Bash(gh pr create *)", "Bash(gh pr view *)", "Bash(gh pr list *)",
"Bash(gh pr checks *)", "Bash(gh api *)"
```

## Safety Rules

1. **Never add** `Bash` or `Bash(*)` to the allow list -- this permits arbitrary command execution.
2. **Prefer narrow patterns** over broad ones. `Bash(npm run build)` is safer than `Bash(npm *)`.
3. **Use `deny`** for destructive commands (e.g., `Bash(rm -rf *)`, `Bash(gh secret *)`).
4. **Use `ask`** for commands that are sometimes needed but carry risk (e.g., `Bash(docker *)`, `Bash(gh pr merge *)`).
5. **Keep allow list minimal** -- only add patterns for commands Claude needs to run frequently without prompting.

## Workflow

When the user asks to add, remove, or modify permission patterns:

1. **Read** `.claude/settings.json` first to see current rules.
2. **Show** the user the proposed change before editing (display the before/after diff).
3. **Edit** the file using the Edit tool.
4. **Validate** the JSON is still valid after editing (check for trailing commas, missing brackets).
5. **Warn** about any deprecated `:*` patterns found and offer to migrate them to ` *`.

### Adding a pattern

When adding a new Bash pattern:
- Determine whether it belongs in `allow`, `ask`, or `deny`
- Check if a broader or narrower pattern already covers it
- Place it in the appropriate section, grouped with similar commands

### Removing a pattern

When removing a pattern:
- Confirm with the user which specific pattern to remove
- Warn if removing from `deny` (this loosens security)

### Listing patterns

When listing, display patterns grouped by category (allow/ask/deny) with a brief explanation of each.

### Migrating deprecated syntax

When migrating:
- Find all `:*` patterns across allow, ask, and deny arrays
- Replace `:*)` with ` *)` in each entry
- Show the count of patterns migrated
