# Workflow Skills Plan

Replace rigid QSP upfront classification with three entry-point skills that meet the user where they are.

**Status**: Implemented (2026-03-09). Note: `/plan` renamed to `/design` because `/plan` is a built-in Claude Code command.

---

## Problem

QSP requires classifying every task before starting work. Real usage doesn't work that way:

- Users brainstorm in plan mode, then want to implement -- classification happens mid-flow
- Users debug interactively, code evolves, then they want to ship -- classification is retroactive
- Read-only tasks (exploration, analysis) don't need classification
- For P-scoped work, users say "implement phase 2" and expect Claude to handle everything

## Solution: Entry-Point Skills

Three skills replace the rigid classify-then-follow model:

| Skill | Purpose | When to use |
|-------|---------|-------------|
| `/sync` | Pre-flight workspace sync | Before starting any work |
| `/plan` | Crystallize brainstorm into structured plan | At start or end of brainstorming |
| `/done` | Validate + ship/land/deliver + document | When work is finished |

QSP classification moves from a gate to an auto-detected property of `/done`.

## Workflow Maps

```
Interactive workflows (user calls /done):
  Quick fix:  /sync -> fix -> /done
  Debugging:  /sync -> debug with Claude -> /done

Delegated workflows (Claude handles /done automatically):
  Feature:    /sync -> brainstorm -> /plan -> "implement this" -> [build + /done]
  Project:    /sync -> brainstorm -> /plan -> "implement phase N" -> [build + /done]

Read-only:    no skills needed -- explore, analyze, review freely
```

## /done Auto-Detection

`/done` detects scope and uses the right verb:

- **Q -> ships**: validates, pushes to main, verifies CI
- **S -> lands**: validates, commits, creates PR, reviews, documents
- **P -> delivers**: lands + checks acceptance criteria + updates plan + handoff note

Detection heuristics:

| Signal | Q (ship) | S (land) | P (deliver) |
|--------|----------|----------|-------------|
| Branch | main/master | feature branch | feature branch |
| Files changed | <=3 | >3 | any |
| IMPLEMENTATION_PLAN.md | no phases | no phases | has phases |
| Diff size | <100 lines | >=100 lines | any |

Decision logic:
1. If IMPLEMENTATION_PLAN.md has active phases -> P (deliver)
2. If on feature branch -> S (land)
3. If on main AND small scope -> Q (ship)
4. If on main AND large scope -> warn user, suggest creating branch

## Skill Details

### /sync

Pre-flight workspace sync. Lightweight, fast.

- `git fetch origin && git status`
- Report: branch name, ahead/behind, dirty files, tracking info
- Warn if behind remote (suggest pull/rebase)
- Warn if on main/master with dirty state
- Quick context: last 3 commits (one-line each)

Does NOT classify the task. Does NOT read DECISIONS.md. Just "is my workspace ready?"

### /plan

Crystallize brainstorming into a structured plan. Works at BOTH start and end:

- **At start**: Guides brainstorming by reading codebase, checking DECISIONS.md
- **At end**: Structures the discussion into an actionable plan with scope classification

Auto-trigger: Claude should suggest `/plan` when brainstorming seems ready to formalize.

Steps:
1. Read `docs/DECISIONS.md` -- check for conflicts
2. Read `docs/IMPLEMENTATION_PLAN.md` -- check for overlapping work
3. Auto-classify scope (Q/S/P)
4. Output structured plan (varies by scope):
   - Q: state the fix and file, recommend proceeding directly
   - S: files to modify, approach, test strategy, risks, branch name
   - P: phase breakdown with acceptance criteria, write to IMPLEMENTATION_PLAN.md
5. List decision candidates for DECISIONS.md

### /done

Universal "I'm finished" command. Four phases:

**Phase 1: Detect scope** -- branch, diff size, plan file (see heuristics above)

**Phase 2: Validate** -- absorbs old `/ship` Tier 1/2/3 checklist:
- Pre-commit hygiene (TODO/FIXME, debug prints, secrets)
- Run code-quality-validator and test-coverage-validator agents in parallel
- Report as Blocker/High Priority/Recommended
- Skip Python tooling for non-code changes (if applicable)
- If blockers found: stop and report

**Phase 3: Ship/Land/Deliver**
- Q: git add + commit + push to main + gh run watch
- S: git add + commit + push + create PR + CI + automated review + code review
- P: same as S + acceptance criteria + update plan + handoff note + (final phase: version bump)

**Phase 4: Document**
- Q: CHANGELOG.md only if user-facing
- S/P: always CHANGELOG.md and DECISIONS.md

## What Changes

| Current | New |
|---------|-----|
| "Classify as Q/S/P before ANY task" in CLAUDE.md | Skill references + read-only exemption |
| Pre-flight section in DEVELOPMENT_PROCESS.md | `/sync` skill |
| Q/S/P rigid paths | Unified stage reference (skills orchestrate) |
| PCC shorthand ("PCC now") | `/done` |
| `/ship` command (read-only checklist) | Absorbed into `/done` Phase 2 |
| "Do not cherry-pick" rule | Skills check prerequisites automatically |

## What Stays

- The stages themselves (explore, plan, setup, build, validate, ship, document)
- All agents in `.claude/agents/`
- Failure protocol
- DECISIONS.md, CHANGELOG.md, IMPLEMENTATION_PLAN.md workflows
- Context Recovery Rule
- Hooks, rules, security

## Files to Change

| Action | File |
|--------|------|
| CREATE | `.claude/skills/sync/SKILL.md` |
| CREATE | `.claude/skills/plan/SKILL.md` |
| CREATE | `.claude/skills/done/SKILL.md` |
| DELETE | `.claude/commands/ship.md` |
| MODIFY | `CLAUDE.md` |
| MODIFY | `docs/DEVELOPMENT_PROCESS.md` |
| MODIFY | `tests/test_commands.py` |
| CREATE | `tests/test_skills.py` |
| MODIFY | `docs/DECISIONS.md` |
| MODIFY | `docs/CHANGELOG.md` |
