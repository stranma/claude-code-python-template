# Plan: Devcontainer Permission Tiers

## Context

Now that the devcontainer is working with strong isolation (network firewall, non-root user, security hooks), we can safely expand Claude Code permissions beyond the conservative baseline in `settings.json`. The goal is to reduce permission prompts that are unnecessary inside an isolated container, while keeping guardrails for truly dangerous operations.

**Key insight**: The security hooks (`dangerous-actions-blocker.sh`, `unicode-injection-scanner.sh`, `output-secrets-scanner.sh`) run **regardless of permission settings**, providing a non-bypassable safety net. The firewall blocks all egress except ~10 whitelisted domains.

**Reading PR comments** (CodeRabbit, users, etc.) already works -- `gh pr view --comments` and `gh api` are in the base allow list. No changes needed.

## Approach: settings.local.json Tiers

Use `settings.local.json` (gitignored, user-specific) for devcontainer expansions. The shared `settings.json` stays unchanged as the universal baseline for bare-metal hosts.

Create three tier files in `.devcontainer/permissions/` and copy the chosen tier to `.claude/settings.local.json` during container setup.

## Safety Layers (Always Active)

These provide defense-in-depth regardless of which tier is selected:

| Layer | What it blocks | Can be bypassed by Bash(*)? |
|-------|---------------|---------------------------|
| Firewall (iptables) | All egress except ~10 whitelisted domains | No (kernel-level) |
| Non-root user | System modification, package install | No (OS-level) |
| `dangerous-actions-blocker.sh` | rm -rf, sudo, force push, DROP DB, secrets in args | No (hook runs before command) |
| `output-secrets-scanner.sh` | Warns on leaked credentials in output | No (hook runs after command) |
| `unicode-injection-scanner.sh` | Zero-width chars, RTL overrides in file content | No (hook runs before edit) |
| Base deny rules | gh secret/auth/ssh-key/gpg-key, git clean/config, uv self | No (deny > allow precedence) |

---

## Tier 1: "Assisted" (Minimal Expansion)

**Who**: Developers new to Claude Code, compliance-heavy teams, containers with mounted secrets.

**What changes**: Auto-allow file operations, WebFetch, and recoverable git commands. Python execution still requires approval.

```json
{
  "permissions": {
    "allow": [
      "Edit", "Write", "Read",
      "WebFetch",
      "Bash(git reset *)", "Bash(git restore *)",
      "Bash(git rm *)", "Bash(git mv *)", "Bash(git worktree *)"
    ]
  }
}
```

**Still asks for**: python execution, docker, gh write ops, terraform, any unlisted bash command

---

## Tier 2: "Autonomous" (Recommended Default)

**Who**: Most developers doing daily work in the devcontainer.

**Philosophy**: Allow ALL bash commands by default (`Bash(*)`), guarded by a curated deny list. The container isolation + hooks + firewall make this safe. The deny list targets operations that affect **shared external state** or enable **container escape**.

```json
{
  "permissions": {
    "allow": [
      "Edit", "Write", "Read",
      "WebFetch",
      "Bash(*)"
    ],
    "deny": [
      "Bash(gh pr merge *)",
      "Bash(gh workflow run *)", "Bash(gh workflow enable *)", "Bash(gh workflow disable *)",
      "Bash(gh issue create *)", "Bash(gh issue close *)", "Bash(gh issue edit *)",
      "Bash(npm publish *)", "Bash(npx npm publish *)",
      "Bash(uv publish *)", "Bash(twine upload *)",
      "Bash(docker run --privileged *)",
      "Bash(docker run --cap-add=ALL *)",
      "Bash(docker run --pid=host *)",
      "Bash(docker run --network=host *)",
      "Bash(terraform *)",
      "Bash(pip install *)", "Bash(pip3 install *)",
      "Bash(npm install -g *)", "Bash(npm i -g *)",
      "Bash(cargo install *)", "Bash(go install *)", "Bash(gem install *)",
      "Bash(uv tool install *)", "Bash(uv tool *)",
      "Bash(apt install *)", "Bash(apt-get install *)", "Bash(dpkg -i *)",
      "Bash(snap install *)", "Bash(brew install *)"
    ]
  }
}
```

### Deny list rationale

| Denied pattern | Why | Risk without denial |
|----------------|-----|---------------------|
| **GitHub shared state** | | |
| `gh pr merge` | Merges code to shared branches | Code merged without human final review |
| `gh workflow run/enable/disable` | Triggers/modifies CI pipelines | Unexpected CI runs, costs, or deployments |
| `gh issue create/close/edit` | Creates/modifies shared issue tracker | Spam or incorrect issue modifications |
| **Package publishing** | | |
| `npm publish`, `uv publish`, `twine upload` | Publishes packages to registries | PyPI and npm are firewall-whitelisted, so publishing IS possible |
| **Container escape** | | |
| `docker run --privileged/cap-add/pid/network` | Container escape vectors | Breaks all container isolation |
| **Infrastructure** | | |
| `terraform` | Infrastructure-as-code | Could modify cloud infrastructure |
| **Tool installation** | | |
| `pip install`, `pip3 install` | Direct pip bypasses uv venv management | Pollutes environment; use `uv add` for deps |
| `npm install -g`, `npm i -g` | Global npm package install | Installs arbitrary executables |
| `cargo install`, `go install`, `gem install` | Language-specific tool installers | Installs arbitrary executables |
| `uv tool install`, `uv tool` | uv tool management | Installs CLI tools outside project |
| `apt install`, `apt-get install`, `dpkg -i` | System package managers | Would fail anyway (no sudo), but explicit deny is defense-in-depth |
| `snap install`, `brew install` | Alternative package managers | Same rationale |

**Note on project dependencies**: `uv add` and `uv sync` (in base allow list) remain allowed -- these manage tracked project dependencies in `pyproject.toml`. The deny targets ad-hoc tool/system installation only.

### What this auto-allows (that was previously ask/unlisted)

- Python execution (`python`, `uv run python`)
- Docker (non-escape commands like `docker ps`, `docker logs`, `docker build`)
- All git operations (reset, restore, rm, mv, worktree, init, clone)
- All gh PR operations except merge (comment, review, ready, reopen)
- gh issue comment (read-only observation is fine)
- uv package management (remove, cache, init)
- Any other bash command not in deny list

### What's still blocked (base settings.json deny + tier deny + hooks)

- `gh secret/auth/ssh-key/gpg-key` (base deny)
- `git clean`, `git config` (base deny)
- `uv self` (base deny)
- `rm -rf /`, `sudo`, force push, DROP DATABASE, etc. (hook)
- Package publishing (tier deny)
- Tool installation: pip, npm -g, cargo, go, gem, uv tool, apt, snap, brew (tier deny)
- Docker escape flags (tier deny)
- Terraform (tier deny)
- PR merge and workflow triggers (tier deny)

---

## Tier 3: "Full Trust" (Near-Bypass with Guardrails)

**Who**: Solo devs, rapid prototyping, headless/batch sessions, teams with strong CI/branch protection.

**Philosophy**: Same as Tier 2 (`Bash(*)`) but with a minimal deny list -- only block container escape vectors and package publishing. GitHub mutations and terraform are allowed.

```json
{
  "permissions": {
    "allow": [
      "Edit", "Write", "Read",
      "WebFetch",
      "Bash(*)"
    ],
    "deny": [
      "Bash(npm publish *)", "Bash(npx npm publish *)",
      "Bash(uv publish *)", "Bash(twine upload *)",
      "Bash(docker run --privileged *)",
      "Bash(docker run --cap-add=ALL *)",
      "Bash(docker run --pid=host *)",
      "Bash(docker run --network=host *)"
    ]
  }
}
```

**Compared to Tier 2**: Allows `gh pr merge`, `gh workflow run`, `gh issue create/close/edit`, and `terraform`. Relies on CI checks, branch protection, and workflow permissions as external guardrails.

**Risk**: `gh pr merge` can merge without human review. `terraform apply` can modify infrastructure. Package publishing is still blocked (the one truly irreversible action).

---

## Comparison Matrix

| Capability | Tier 1 | Tier 2 | Tier 3 |
|-----------|--------|--------|--------|
| Edit/Write/Read | auto | auto | auto |
| WebFetch | auto | auto | auto |
| Bash (general) | per-command | `Bash(*)` | `Bash(*)` |
| Python execution | ask | auto | auto |
| Git destructive (reset/rm) | auto | auto | auto |
| GitHub PR (non-merge) | ask | auto | auto |
| GitHub PR merge | ask | **deny** | auto |
| GitHub issue mutations | ask | **deny** | auto |
| GitHub workflow triggers | ask | **deny** | auto |
| Package publishing | ask | **deny** | **deny** |
| Tool installation (pip, npm -g, cargo, etc.) | ask | **deny** | auto |
| Docker (non-escape) | ask | auto | auto |
| Docker escape flags | ask | **deny** | **deny** |
| Terraform | ask | **deny** | auto |
| **Prompt frequency** | Moderate | **None** (deny = hard block) | **None** (deny = hard block) |

**Note**: With `Bash(*)`, there are no "ask" prompts for bash commands. Commands either execute (allow) or are blocked (deny). This means zero interruptions for bash -- the trade-off is that denied commands fail immediately rather than prompting for override.

---

## Steering Claude Away from Denied Patterns

### Problem
1. Deny rules use glob matching from the start of the command -- `cd path && pip install foo` bypasses `Bash(pip install *)`
2. Claude shouldn't waste turns attempting blocked commands when a correct alternative exists

### Solution: Two layers

**Layer A: CLAUDE.md guidance + alternatives doc** (prevents the attempt)

Add a brief "Devcontainer Rules" section to CLAUDE.md that references a detailed alternatives doc:

```markdown
## Devcontainer Rules

When running in a devcontainer, some operations are denied by policy. Before attempting
a command that might be blocked, check `docs/DEVCONTAINER_PERMISSIONS.md` for the
approved alternative. Key rules:

- **Dependencies**: Use `uv add <package>`, never `pip install`
- **System tools**: Add to `.devcontainer/Dockerfile`, do not install at runtime
- **No chained cd**: Use absolute paths. `cd /path && command` bypasses permission checks.
```

Create `docs/DEVCONTAINER_PERMISSIONS.md` with the full denied-to-alternative mapping:

| Denied Command | Approved Alternative |
|----------------|---------------------|
| `pip install X` / `pip3 install X` | `uv add X` (project dep) or add to Dockerfile (tool) |
| `npm install -g X` / `npm i -g X` | Add to Dockerfile `RUN npm install -g X` |
| `cargo install X` | Add to Dockerfile `RUN cargo install X` |
| `go install X` | Add to Dockerfile `RUN go install X` |
| `gem install X` | Add to Dockerfile `RUN gem install X` |
| `uv tool install X` | Add to Dockerfile |
| `apt install X` / `apt-get install X` | Add to Dockerfile `RUN apt-get install -y X` |
| `npm publish` / `uv publish` / `twine upload` | Ask the user to publish manually |
| `gh pr merge` | Ask the user to merge (or use branch protection auto-merge) |
| `gh workflow run` | Ask the user to trigger the workflow |
| `gh issue create/close/edit` | Ask the user to perform the action |
| `terraform *` | Ask the user to run terraform |
| `docker run --privileged` | Use `docker run` without `--privileged` |
| `cd path && command` | Use absolute paths: `command /absolute/path` |

The doc also explains WHY each is denied (container isolation, shared state, etc.) and the tier system so users understand the trade-offs.

**Layer B: Hook-based blocking** (catches what slips through, including chained commands)

Create a separate hook `devcontainer-tool-blocker.sh` that uses `grep -qiF` to search the **full command string**, catching patterns inside `&&`, `;`, and `|` chains.

New literal patterns to block:

```bash
BLOCKED_TOOL_INSTALL_PATTERNS=(
    'pip install'
    'pip3 install'
    'npm install -g'
    'npm i -g'
    'cargo install'
    'go install'
    'gem install'
    'uv tool install'
    'apt install'
    'apt-get install'
    'dpkg -i'
    'snap install'
    'brew install'
)
```

These return a helpful message: `"Blocked: tool installation not allowed in devcontainer. Use 'uv add' for project dependencies or add to Dockerfile for system tools."`

**Important**: This hook is only active in devcontainer context -- it's configured via `settings.local.json` (copied from tier files), not the shared `settings.json`. This way bare-metal usage is unaffected.

### Updated tier file structure

Tier files include hooks in addition to permissions:

```json
{
  "permissions": { "allow": [...], "deny": [...] },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": ["\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/devcontainer-tool-blocker.sh"]
      }
    ]
  }
}
```

**Note**: Need to verify if `settings.local.json` hooks merge with or replace `settings.json` hooks. If they replace, the tier files must include ALL hooks (including the base ones).

---

## Implementation Steps

### 1. Create devcontainer tool blocker hook
- `.claude/hooks/devcontainer-tool-blocker.sh` -- blocks tool installation patterns via grep (catches chained commands)

### 2. Create tier files (include both permissions and hook config)
- `.devcontainer/permissions/tier1-assisted.json`
- `.devcontainer/permissions/tier2-autonomous.json`
- `.devcontainer/permissions/tier3-full-trust.json`

### 3. Update devcontainer.json
Add `PERMISSION_TIER` build arg (default: `2`) and a copy step in `onCreateCommand`:
```
cp .devcontainer/permissions/tier${PERMISSION_TIER:-2}.json .claude/settings.local.json && uv sync ...
```

### 4. Add devcontainer guidance to CLAUDE.md
Brief section on preferred patterns (uv add > pip install, no cd chaining, no tool installation).

### 5. Create docs/DEVCONTAINER_PERMISSIONS.md
Full denied-command-to-approved-alternative mapping with rationale.

### 6. Update settings.local.json.example
Document the tier system with brief descriptions of each tier.

### 7. Update docs/DECISIONS.md
Record the decision: why tiers, why settings.local.json, risk analysis summary.

### 8. Do NOT modify settings.json
The base settings remain the universal baseline for all environments.

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `.claude/hooks/devcontainer-tool-blocker.sh` | Create (tool install blocking hook) |
| `.devcontainer/permissions/tier1-assisted.json` | Create |
| `.devcontainer/permissions/tier2-autonomous.json` | Create |
| `.devcontainer/permissions/tier3-full-trust.json` | Create |
| `.devcontainer/devcontainer.json` | Modify (add build arg + copy step) |
| `CLAUDE.md` | Modify (add devcontainer rules section with ref to alternatives doc) |
| `docs/DEVCONTAINER_PERMISSIONS.md` | Create (denied commands -> approved alternatives mapping) |
| `.claude/settings.local.json.example` | Modify (document tiers) |
| `docs/DECISIONS.md` | Modify (add decision record) |

---

## Verification

1. Build devcontainer with default tier (2) -- verify `settings.local.json` is created with Tier 2 content
2. Rebuild with `PERMISSION_TIER=1` -- verify Tier 1 content
3. Test that Edit/Write/Read no longer prompt in any tier
4. Test that `python -c "print('hello')"` prompts in Tier 1 but auto-runs in Tier 2
5. Test that `gh pr merge` is hard-denied in Tier 2 but auto-allowed in Tier 3
6. Test that `npm publish` is denied in both Tier 2 and 3
7. Test that `docker run --privileged` is denied in Tier 2 and 3
8. Test that `cd /tmp && pip install foo` is caught by the devcontainer-tool-blocker hook
9. Verify hooks still fire: run a command with secrets in args, confirm `dangerous-actions-blocker.sh` blocks it
10. Verify base `settings.json` deny rules still apply (e.g., `gh secret list` is still blocked)
