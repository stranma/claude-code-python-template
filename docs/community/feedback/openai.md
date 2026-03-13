You are mid experienced developer and midly familiar with Claude Code. 

Please read this readme and tell me honest opinion if this repo would be helpful and if you would try it based on this readme. What else you wound need to decide? How to improve the readme? How to improve the repo?

# Claude Code Python Template

[![CI](https://github.com/stranma/claude-code-python-template/actions/workflows/tests.yml/badge.svg)](https://github.com/stranma/claude-code-python-template/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![uv](https://img.shields.io/badge/uv-workspace-blueviolet)](https://docs.astral.sh/uv/)

**An opinionated Python project template that makes Claude Code produce consistent, tested, production-quality code.**

Without structure, Claude Code results vary -- tests get skipped, context gets lost between sessions, small fixes turn into rewrites. This template gives you a complete starting point: TDD workflow, quality gates, security hooks, and a 3-command workflow that scales from typo fixes to multi-phase projects.

This is opinionated by design. It picks uv, ruff, pyright, pytest, and hatchling. It enforces TDD. It runs agents on every PR. If that's what you want, you're in the right place. If not, no hard feelings.

## Who Is This For?

**Solo developer who knows Python?** You move fast, but you still want tests, type checking, linted code, and proper PRs - why not, it is now almost for free! The template's agents handle the discipline so you can focus on the problem. The devcontainer setup means you can let Claude Code run more autonomously inside a sandbox -- no worrying about it running rm -rf on your host machine.

**Leading a team adopting Claude Code?** Without a shared baseline, every developer has their own CLAUDE.md (or none). This template standardizes how your team uses Claude Code -- same workflow, same quality gates, same security hooks across all projects. The devcontainer with [permission tiers](docs/DEVCONTAINER_PERMISSIONS.md) lets you control how much autonomy Claude Code gets: from per-command approval (Tier 1) to full trust with minimal guardrails (Tier 3).

**Data scientist or ML engineer?** You know Python and pandas, but software engineering practices (CI/CD, type annotations, code review) feel like overhead. This template adds those practices without you having to learn how to set them up. Claude Code handles the ceremony; you focus on the models.

**New to Claude Code and still learning Python?** This template is a good way to learn professional practices by doing. It enforces TDD, type checking, linting, and proper git workflow -- things that are hard to pick up from tutorials alone. Claude Code walks you through it, and the agents catch mistakes before they stick. You'll need basic comfort with the terminal and git. If that's new to you, see [Getting Started Guide](docs/GETTING_STARTED.md) for the prerequisites.

## How It Works

Three commands. That's the whole workflow:


/sync   Preflight check. Fetches remote, reports branch state, dirty files.
/design Turns brainstorming into a structured plan. Reads decision log,
        auto-classifies scope, outputs actionable steps.
/done   Ships your work. Auto-detects scope, validates (lint + test + review),
        commits, creates PR, updates docs. One command.


Real workflows:


Quick fix:     /sync -> fix the bug -> /done
New feature:   /sync -> brainstorm with Claude -> /design -> "implement this" -> /done
Multi-phase:   /sync -> brainstorm -> /design -> "implement phase 1" -> /done -> ... -> /done
Exploration:   just talk to Claude -- no commands needed


You never classify tasks upfront. /done auto-detects scope from your branch, diff size, and whether an implementation plan exists -- then picks the right level of ceremony:

| Detected scope | What /done does |
|----------------|-------------------|
| **Quick** (on main, small diff) | Validate, commit, push, verify CI |
| **Standard** (feature branch) | Validate, commit, PR, CI, code review, update changelog |
| **Project** (has plan phases) | All of Standard + acceptance criteria + plan update + handoff note |

## Quick Start

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/getting-started/installation/), [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview). New to these tools? See [Getting Started Guide](docs/GETTING_STARTED.md).

**1. Create your project**


bash
# From GitHub: click "Use this template", then clone your new repo
# Or directly:
git clone https://github.com/stranma/claude-code-python-template my-project
cd my-project


**2. Run setup**


bash
# Simple project (recommended for first use):
python setup_project.py --name my-tool --namespace my_tool --type single

# Monorepo with multiple packages:
python setup_project.py --name my-project --namespace my_project --type mono --packages "core,api"


The setup script replaces {{project_name}} placeholders across all files, renames directories to match your namespace, and optionally initializes git. It only modifies files inside the project directory.

**3. Install and verify**


bash
uv sync --all-packages --group dev
uv run pytest && uv run ruff check . && uv run pyright


That's it. Claude Code picks up the agents, hooks, and rules automatically.

## Devcontainer Setup (Recommended)

The template includes a full VS Code devcontainer configuration. This is the recommended way to work because it sandboxes Claude Code -- firewall, non-root user, and policy hooks limit what it can do, so you can give it more autonomy without risk to your host machine.

**What the devcontainer provides:**

- **Network firewall** -- all egress blocked except ~10 whitelisted domains (GitHub, PyPI, etc.)
- **Non-root user** -- Claude Code cannot install system packages or modify system files
- **Permission tiers** -- control how much autonomy Claude Code gets:

| Tier | Name | Who | Claude Code behavior |
|------|------|-----|----------------------|
| 1 | Assisted | New users, compliance teams | Per-command approval |
| 2 | Autonomous (default) | Most developers | Free to run commands, curated deny list |
| 3 | Full Trust | Solo devs with strong CI | Minimal restrictions |

- **Policy hooks** -- block dangerous patterns even in chained commands (cd /tmp && rm -rf *)
- **Pre-installed tools** -- Python, uv, ruff, git, Claude Code VS Code extension

Set the tier before building: PERMISSION_TIER=1 (or 2, 3) in your environment. Default is 2.

See [Devcontainer Permissions](docs/DEVCONTAINER_PERMISSIONS.md) for the full denied commands list and approved alternatives.

## What's Included

### Core (always active)

- **CLAUDE.md** -- compact agent directives (~40 lines) with /sync, /design, /done workflow
- **5 workflow agents** -- code quality, test coverage, PR writing, code review, docs updates
- **3 security hooks** -- block destructive commands, scan for leaked secrets, catch Unicode injection
- **CI/CD** -- GitHub Actions for lint + test + typecheck + publish
- **Tool stack** -- [uv](https://docs.astral.sh/uv/) workspaces, [ruff](https://docs.astral.sh/ruff/), [pyright](https://github.com/microsoft/pyright), [pytest](https://pytest.org/), [hatchling](https://hatch.pypa.io/)

### Optional specialists

<details>
<summary>7 additional agents for larger projects</summary>

| Agent | Purpose |
|-------|---------|
| acceptance-criteria-validator | Verify acceptance criteria across phases |
| implementation-tracker | Keep plan and reality in sync |
| review-responder | Automated review triage |
| agent-auditor | Audit agent definitions for best practices |
| security-auditor | OWASP-based vulnerability detection (read-only) |
| refactoring-specialist | SOLID/code smell analysis (read-only) |
| output-evaluator | LLM-as-Judge quality scoring |

</details>

<details>
<summary>2 productivity hooks</summary>

- **auto-format** -- auto-formats Python files after edits
- **test-on-change** -- auto-runs associated tests after edits

</details>

<details>
<summary>Commands and skills</summary>

- /sync -- preflight workspace check before starting work
- /design -- crystallize brainstorming into a structured plan
- /done -- validate, ship, and document in one command
- /landed -- post-merge lifecycle: verify CI, check deploys, clean branches
- /cove -- Chain-of-Verification for high-stakes accuracy
- /cove-isolated -- CoVe with isolated verification agent
- /security-audit -- 6-phase security posture scan with A-F grading
- /edit-permissions -- manage Claude Code permission rules

</details>

<details>
<summary>4 review rules</summary>

Architecture, code quality, performance, and test quality -- applied automatically during code review.

</details>

## Project Structure

### Monorepo (default)


my-project/
├── CLAUDE.md                     # Agent directives (~40 lines)
├── apps/                         # Executable applications
│   └── api/
│       ├── pyproject.toml
│       └── my_project/api/
├── libs/                         # Reusable libraries
│   └── core/
│       ├── pyproject.toml
│       └── my_project/core/
├── tests/
├── docs/
│   ├── CHANGELOG.md
│   ├── DECISIONS.md
│   ├── DEVELOPMENT_PROCESS.md
│   └── IMPLEMENTATION_PLAN.md
├── .claude/                      # Claude Code config
│   ├── settings.json
│   ├── agents/                   # 12 agents
│   ├── skills/                   # /sync, /design, /done, /landed, /edit-permissions
│   ├── commands/                 # /cove, /cove-isolated, /security-audit
│   ├── hooks/                    # 5 hook scripts
│   └── rules/                    # 4 review rules
├── .devcontainer/                # VS Code devcontainer
│   ├── Dockerfile
│   ├── devcontainer.json
│   ├── init-firewall.sh
│   └── permissions/              # Tier 1/2/3 configs
├── .github/
│   ├── workflows/                # CI/CD
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
└── pyproject.toml                # Root workspace config


### Single Package


my-tool/
├── CLAUDE.md
├── src/my_tool/
├── tests/
├── docs/
├── .claude/
├── .devcontainer/
├── .github/
└── pyproject.toml


## Setup Script Options

| Flag | Default | Description |
|------|---------|-------------|
| --name | (required) | Project name (e.g., my-project) |
| --namespace | from name | Python namespace (e.g., my_project) |
| --description | "A Python project" | Short description |
| --author | "" | Author name |
| --email | "" | Author email |
| --python-version | "3.11" | Python version requirement |
| --base-branch | "master" | Git base branch |
| --type | "mono" | mono or single |
| --packages | "core,server" | Comma-separated package names (mono only) |
| --git-init | false | Init git + initial commit |

Package naming: by default, the first package is a library (in libs/), the rest are applications (in apps/). Use prefixes to control placement: --packages "lib:models,lib:utils,app:api,app:worker".

## A Note on Token Costs

The agents in this template use Claude's sub-agents (mostly Sonnet, some Haiku) to validate code quality, run reviews, and write PR descriptions. This costs tokens beyond what you'd spend on a bare Claude Code session.

This is intentional. A few extra cents per PR is trivially cheap compared to the cost of your time debugging a bug that a code review agent would have caught, or manually writing PR descriptions, or re-running tests you forgot to run. The agents exist because developer time is the expensive resource, not tokens.

If cost is a concern, the workflow agents (code-quality-validator, test-coverage-validator) are the ones that run most frequently. The others (pr-writer, code-reviewer, docs-updater) run once per PR. The optional specialist agents only run when you explicitly invoke them.

## Credits

Monorepo structure inspired by [carderne/postmodern-mono](https://github.com/carderne/postmodern-mono), which demonstrates excellent uv workspace patterns. Key differences:

- Direct uv run commands instead of Poe the Poet
- Standard pyright instead of basedpyright
- Claude Code methodology layer (CLAUDE.md, agents, skills, hooks)
- Setup script for template initialization

## License

MIT

Thought for a couple of seconds

Assumptions: I am judging only from the README text you pasted, not from the actual repo contents, code quality, hook implementations, or maintenance history.

Answer

My honest opinion: this looks potentially useful, but not yet obviously compelling enough that I would adopt it just from this README alone. I would likely bookmark it and inspect the repo, but I would not immediately use it for a real project without checking several concrete things first.

Why:

The README communicates a clear opinionated workflow.

It targets a real pain point: Claude Code drift, inconsistent process, skipped tests, weak session continuity.

It has a strong positioning angle: “template for disciplined AI-assisted Python development.”

But it also raises several concerns:

It promises a lot.
“Production-quality,” “agents on every PR,” “security hooks,” “3-command workflow,” “permission tiers,” “sandboxed autonomy” — that is a broad surface area. Broad templates often become brittle, noisy, or high-maintenance.

The core value proposition is still partly abstract.
I can see what it includes, but I cannot yet tell whether it actually improves day-to-day work versus adding ceremony.

The workflow feels optimized for people who want strong process, not necessarily for people who want speed.
That is fine, but the README slightly oversells “almost for free.” This stack is not free in cognitive overhead. It may save discipline, but it adds framework.

The biggest missing proof is operational proof.
I need examples of what Claude Code actually does better with this template than without it.

So: helpful? Possibly yes. Would I try it? Yes, but only in a throwaway repo first. Would I trust it in production based on this README alone? No.

Rationale
What is strong in this README
1. Clear target problem

The README identifies real failure modes of AI coding workflows:

skipped tests

inconsistent outputs

lost context

over-rewrites

lack of team standardization

That is credible and relevant.

2. Opinionated choices are a strength

Choosing uv, ruff, pyright, pytest, hatchling is sensible. For a Python template, that is a strong baseline. It reduces decision fatigue.

3. The command-based workflow is memorable

/sync, /design, /done is a good abstraction. It is easy to remember and easy to explain.

4. Devcontainer + restricted permissions is a genuinely valuable angle

This is probably the most differentiated part. “Let Claude operate more freely, but inside a sandbox” is a practical idea.

5. Audience segmentation is good

The README speaks separately to solo devs, team leads, DS/ML engineers, and beginners. That improves reach.

What weakens it
1. Too many claims, not enough evidence

The README says this template makes Claude Code produce:

consistent code

tested code

production-quality code

safer code

better PRs

proper docs

scalable workflow

That is a large promise stack. I need evidence like:

before/after examples

sample generated PR

example implementation plan

example /done output

what the agents actually check

failure cases

Without that, this reads slightly like “process theater with AI branding.”

2. It is not clear what is essential vs optional

The README lists:

agents

hooks

commands

rules

CI/CD

devcontainer

security audits

productivity hooks

permission tiers

But I cannot quickly tell:

what absolutely runs in normal use

what runs only if enabled

what is expensive

what is intrusive

what is safe to remove

A mid-level developer evaluating adoption wants a clearer mental model:
what is the minimum viable template, and what is advanced add-on machinery?

3. The “TDD enforced” claim may turn people away

This is a polarizing choice. Many developers like tests but do not want rigid TDD enforcement. If the template truly blocks non-TDD flows, that is a major adoption constraint.

You should be brutally explicit:

Does it require red-green-refactor every time?

Does /done fail if tests were added after implementation?

Is this a recommendation or a hard workflow constraint?

Right now it sounds stricter than many teams would tolerate.

4. “Runs agents on every PR” can be either great or annoying

This could mean:

useful automation, or

token burn, latency, noise, and low-signal comments

The README defends token costs, but not review quality. Cost is rarely the only concern. Signal-to-noise ratio matters more.

5. The repo may be over-engineered relative to its audience

For beginners and many solo devs, this may be too much machinery:

monorepo support

multiple agents

security hooks

permission tiers

review rules

implementation plan docs

changelog updates

handoff notes

That can help discipline, but it can also overwhelm the very people who most need simplicity.

Would I try it?
My actual decision

Yes, I would try it in a sandbox project for 30–60 minutes.
I would not adopt it directly into an active codebase.

Why I would try it

Because it has enough potentially high-value ideas:

constrained AI workflow

sandboxing Claude

explicit ship command

standard team baseline

less setup for quality gates

Why I would hesitate

Because templates like this often fail in one of four ways:

Too rigid — slows normal work.

Too magical — hard to debug or customize.

Too noisy — too many automated checks/comments.

Too fragile — breaks when real project structure deviates from template assumptions.

What else I would need to decide

This is the main missing section. To decide, I would need:

1. One realistic demo

Not a list of features. A concrete walkthrough:

create repo

run setup

ask Claude to implement a feature

use /design

use /done

show resulting commit / PR / CI / docs update

This would do more than half the persuasion work.

2. Example outputs of the commands

Show exactly what /sync, /design, /done produce.

Questions I want answered:

Is /design just a prompt wrapper, or does it create durable artifacts?

Does /done ask follow-up questions?

What does “auto-detect scope” really look like?

What if it misclassifies?

3. Maintenance story

Who maintains this? How often? How stable is Claude Code compatibility?

AI-tooling templates rot faster than normal templates because upstream behavior changes. I need to know:

how often this repo is updated

supported Claude Code versions

changelog/release policy

compatibility guarantees, if any

4. Escape hatches

Can I disable pieces cleanly?

I would want to know:

can I use only CLAUDE.md + commands without devcontainer?

can I disable PR agents?

can I switch off TDD enforcement?

can I use basedpyright, mypy, or no pyright?

can I keep single-package only?

5. Proof the security model is real

The devcontainer section sounds promising, but security claims need specifics:

what exactly is blocked

what is only best-effort

what happens on macOS/Linux/Windows

can Claude still exfiltrate through allowed domains

what threat model is covered

Right now it is directionally good, but still marketing-heavy.

6. Repo examples or adopters

I would want:

one minimal sample app

one real repo using it

maybe one “team mode” example

That would reduce perceived risk a lot.

How to improve the README
1. Add a “Should you use this?” decision section near the top

Example structure:

Use this if:

you use Claude Code regularly

you want standardized Python quality gates

you are comfortable with opinionated tooling

you want containerized/sandboxed AI workflow

Do not use this if:

you want minimal process

you do not want TDD pressure

you dislike devcontainers

you want framework-agnostic freedom

you already have strong CI + project conventions

This would build trust immediately.

2. Add “What this actually changes in your daily workflow”

A plain-language section:

before template

after template

what you do differently each day

Right now the README explains features more than behavior.

3. Add one end-to-end demo

This is the highest-impact improvement.

Include:

prompt given to Claude

generated plan

tests created

/done output

PR result

Even screenshots or terminal transcripts would help.

4. Separate “core” from “extended” more aggressively

Make it obvious:

Minimal mode

CLAUDE.md

uv + ruff + pyright + pytest

/sync, /design, /done

Advanced mode

agents

hooks

devcontainer

review rules

security audit

That makes adoption feel incremental instead of all-or-nothing.

5. Be more precise about enforcement

For example:

“enforces TDD” → explain whether hard or soft

“runs agents on every PR” → specify which agents, default behavior, and expected cost

“production-quality” → define what that means operationally

Avoid fuzzy claims.

6. Add a “Failure modes / limitations” section

This would massively increase credibility.

Examples:

may be overkill for tiny scripts

agent quality depends on Claude model behavior

may require tuning for existing repos

devcontainer setup may be heavy on some machines

hooks can occasionally block legitimate commands

PR review agents are advisory, not authoritative

That kind of honesty would make me trust the project more.

7. Explain migration path for existing repos

Many people do not start greenfield. Add:

how to apply template to existing repo

what files to copy

what to keep/remove

how to phase adoption

8. Reorder for speed

Suggested order:

What problem this solves

Should you use it?

2-minute demo

Quick start

What is included

Devcontainer/security

Deep details

Current README is decent, but still a bit feature-first.

How to improve the repo

Based on the README alone, these are the highest-value repo improvements.

1. Add an examples/ directory

Include:

minimal single-package example

monorepo example

example PR generated through workflow

example docs evolution across phases

2. Add automated smoke tests for template generation

Templates often fail in placeholder substitution and project generation.

You want CI that verifies:

single-package setup works

monorepo setup works

generated project installs

tests/lint/typecheck pass after generation

Without this, template repos rot quietly.

3. Add a compatibility matrix

Document:

Python versions

Claude Code versions or assumptions

VS Code/devcontainer assumptions

host OS notes

4. Make modules independently adoptable

Let people adopt:

just CLAUDE.md

just commands

just devcontainer

just hooks

That will broaden adoption and reduce fear.

5. Add a “disable/override” guide

This is important for real teams.

Examples:

switch TDD policy off

remove auto docs updates

disable review agents

change base branch to main

replace pyright with mypy/basedpyright

remove hatchling if not publishing

6. Provide observability into agent behavior

A common failure in AI automation repos is hidden logic.

You want:

logs

dry-run mode

verbose mode

clear explanation of why /done chose a given scope

“Auto-detect scope” needs transparency.

7. Add benchmark-style evidence

Even lightweight:

median time to first PR

number of issues caught by hooks

common PR review findings

token cost per typical workflow

Not fake precision—just honest metrics.

8. Add repo health signals

I would look for:

releases or tags

changelog

issue templates

examples of active maintenance

test coverage for setup logic and hooks

9. Reduce magic in setup script

The setup script should be extremely predictable, idempotent, and test-covered. If it is doing global find/replace across many files, that is a source of subtle breakage.

10. Add comparison section

Compare against:

plain Claude Code + manual workflow

cookiecutter/copier Python templates

generic Python project templates

team-internal CLAUDE.md only

That helps people understand the delta.

Alternatives with tradeoffs
Option 1 — Try this template as-is in a throwaway repo

Best when: you want to evaluate the full opinionated experience.
Upside: fastest way to assess real value.
Downside: you may confuse template complexity with Claude Code complexity.

Option 2 — Borrow only the core ideas

Take:

CLAUDE.md

/sync, /design, /done

uv + ruff + pyright + pytest

Skip:

heavy agents

devcontainer

advanced hooks initially

Best when: you want lower adoption risk.
Upside: much easier to trial.
Downside: you miss the differentiated security and automation story.

Option 3 — Use it only as a design reference for your own internal template

Best when: you already know your team preferences.
Upside: keeps the good ideas, avoids lock-in to someone else’s opinions.
Downside: more up-front effort.

Option 4 — Do nothing and keep a lightweight Claude workflow

Use:

your own CLAUDE.md

normal CI

pre-commit

standard PR template

Best when: your current process is already disciplined.
Upside: minimal overhead.
Downside: less standardization and fewer AI-specific safeguards.

My weighting:

0.40 Option 2: borrow the core ideas only

0.30 Option 1: trial the full template in a sandbox

0.20 Option 3: use it as inspiration for an internal template

0.10 Option 4: ignore it entirely

Uncertainty note: these weights would change significantly after seeing the actual agent definitions, hooks, and one real demo.

Confidence + what I’d need to be more certain

Confidence: 0.74

Why not higher:

I only saw the README

the biggest unknowns are implementation quality and maintenance discipline

this category is highly sensitive to polish and edge cases

To be more certain, I would inspect:

CLAUDE.md

the definitions of /sync, /design, /done

one or two hook scripts

CI workflows

setup script tests

evidence of active maintenance

one generated example repo

That would be enough to move to either:

“yes, I’d try this seriously,” or

“no, this is mostly process packaging.”

Opportunity Radar
1. Turn the README into a conversion funnel

Impact: high
Effort: medium
Risk: low
Confidence: high

Right now it is informative, but not maximally persuasive. A short demo, limitations section, and “who should not use this” section would sharply improve trust.

2. Add a “lite mode”

Impact: high
Effort: medium
Risk: low
Confidence: high

A lot of potential users will want 20% of the system for 80% of the value. Make that path explicit.

3. Productize the proof, not just the features

Impact: very high
Effort: medium
Risk: medium
Confidence: medium-high

The repo’s success likely depends less on adding more agents and more on proving that the current ones materially improve outcomes. Real examples beat more capability claims.

If you want, paste the actual repo tree or key files (CLAUDE.md, the 3 commands, hooks, CI), and I’ll give you a much harsher and more concrete assessment.