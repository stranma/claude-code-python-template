# Devcontainer Permissions

## Tier System

The devcontainer uses graduated permission tiers stored in `.devcontainer/permissions/`. The chosen tier is copied to `.claude/settings.local.json` at container creation.

| Tier | Name | Who | Bash behavior |
|------|------|-----|---------------|
| 1 | Assisted | New users, compliance teams | Per-command approval |
| 2 | Autonomous (default) | Most developers | `Bash(*)` with curated deny list |
| 3 | Full Trust | Solo devs, strong CI/branch protection | `Bash(*)` with minimal deny list |

Set the tier via `PERMISSION_TIER` environment variable before building the devcontainer (default: `2`).

## Safety Layers (Always Active)

Regardless of tier, these layers provide defense-in-depth:

- **Firewall (iptables)**: All egress blocked except ~10 whitelisted domains
- **Non-root user**: Cannot install system packages or modify system files
- **dangerous-actions-blocker.sh**: Blocks rm -rf, sudo, force push, DROP DATABASE, secrets in args
- **output-secrets-scanner.sh**: Warns on leaked credentials in command output
- **unicode-injection-scanner.sh**: Blocks zero-width chars, RTL overrides in file content
- **devcontainer-policy-blocker.sh**: Catches denied patterns in chained commands
- **Base deny rules (settings.json)**: gh secret/auth/ssh-key/gpg-key, git clean/config, uv self

## Denied Commands and Approved Alternatives

| Denied Command | Approved Alternative | Rationale |
|----------------|---------------------|-----------|
| `pip install X` / `pip3 install X` | `uv add X` (project dep) or add to Dockerfile (tool) | Bypasses uv venv management, pollutes environment |
| `pipx install X` / `python -m pip install X` | Same as above | Alternate pip invocations |
| `npm install -g X` / `npm i -g X` | Add to Dockerfile `RUN npm install -g X` | Installs arbitrary executables |
| `cargo install X` | Add to Dockerfile `RUN cargo install X` | Installs arbitrary executables |
| `go install X` | Add to Dockerfile `RUN go install X` | Installs arbitrary executables |
| `gem install X` | Add to Dockerfile `RUN gem install X` | Installs arbitrary executables |
| `uv tool install X` | Add to Dockerfile | CLI tools belong in container image |
| `apt install X` / `apt-get install X` | Add to Dockerfile `RUN apt-get install -y X` | System packages belong in container image |
| `snap install X` / `brew install X` | Add to Dockerfile | System packages belong in container image |
| `npm publish` / `uv publish` / `twine upload` | Ask the user to publish manually | Irreversible; publishes to public registries |
| `gh pr merge` | Ask the user to merge (or use branch protection auto-merge) | Merges code without human final review |
| `gh workflow run` | Ask the user to trigger the workflow | Unexpected CI runs, costs, or deployments |
| `gh issue create/close/edit` | Ask the user to perform the action | Modifies shared issue tracker |
| `terraform *` | Ask the user to run terraform | Could modify cloud infrastructure |
| `docker run --privileged` | Use `docker run` without `--privileged` | Container escape vector |
| `curl ... \| bash` / `wget ... \| sh` | Do not pipe remote scripts. Add to Dockerfile instead. | Supply-chain attack vector |
| `cd path && command` | Use absolute paths: `command /absolute/path` | Chained commands bypass glob-based permission checks |
| `git remote add/set-url/remove/rename/set-head` | Ask the user to manage remotes | Prevents code exfiltration to unauthorized remotes |

## Tier Comparison

| Capability | Tier 1 | Tier 2 | Tier 3 |
|-----------|--------|--------|--------|
| Edit/Write/Read | auto | auto | auto |
| WebFetch | auto | auto | auto |
| Bash (general) | per-command | auto | auto |
| Python execution | ask | auto | auto |
| Git destructive (reset/rm) | auto | auto | auto |
| GitHub PR (non-merge) | ask | auto | auto |
| GitHub PR merge | deny | deny | auto |
| GitHub issue mutations | deny | deny | auto |
| GitHub workflow triggers | deny | deny | auto |
| Package publishing | deny | deny | deny |
| Tool installation | deny | deny | auto |
| Docker (non-escape) | ask | auto | auto |
| Docker escape flags | deny | deny | deny |
| Terraform | deny | deny | auto |

**Note**: With `Bash(*)` (Tier 2/3), there are no "ask" prompts for bash. Commands either execute (allow) or are hard-blocked (deny).

## Tier 3 Prerequisites

Do not use Tier 3 without these external guardrails:

- Branch protection requiring 1+ approving reviews before merge
- Required CI status checks on protected branches
- GitHub token scoped with fine-grained PAT (minimal permissions, no admin)
- If terraform is used: plan-only permissions in the container

## Changing Tiers

Set `PERMISSION_TIER` before building the devcontainer:

```bash
# In your shell before opening in devcontainer
export PERMISSION_TIER=1  # or 2, 3

# Or in VS Code settings (devcontainer.json override)
# "containerEnv": { "PERMISSION_TIER": "3" }
```

The tier is applied during `onCreateCommand` by copying the corresponding file to `.claude/settings.local.json`.
