# Community Growth Plan: Make It Usable, Then Known

Synthesized from assessments by Claude, Gemini, and OpenAI (March 2025).

---

## Phase 1: Lower the Barrier (Coding)

All three sources agree: **usability before promotion**. Nobody shares a tool that's hard to start with.

### 1.1 Restructure README for instant comprehension
- Add a **"Why this template?"** pain-point section at the very top (currently jumps straight into features)
- Add a **60-second quickstart** block: 3 commands to a working project
- Lead with **single-package mode** as the default, monorepo as "advanced" (currently `--type single` is buried)
- Group agents as **"5 core + 7 optional specialists"** instead of "12 agents" which sounds overwhelming
- Add badges: CI status, Python version, license

### 1.2 Create a "Hello World" example repo
- Generate a real project from the template and actually build something small with it (e.g., a CLI tool or a tiny FastAPI app)
- Use the template's own workflow to build it (`/sync`, `/design`, `/done`) -- this proves the workflow works end-to-end
- Publish as `stranma/example-from-template`
- Include screenshots + `tree` output showing the end result
- Link from README: "See what a generated project looks like"
- This is the single most convincing proof point -- it shows the output, not just the scaffolding

### 1.3 Harden setup_project.py
- Graceful failure when `uv` isn't installed -- detect and print install instructions
- Add a `--minimal` flag that installs only core agents/hooks for people wanting to ease in

### 1.4 Add community health files
- `CONTRIBUTING.md` -- explain how to add agents, hooks, improve prompts
- `SECURITY.md` -- describe the trust model: what hooks/agents execute and why you shouldn't run on untrusted repos
- `CODE_OF_CONDUCT.md`

### 1.5 Fix inconsistencies
- Repo description says "7 custom agents" but README says 12 -- align
- Add a brief section describing the trust model for hooks

---

## Phase 2: Build Trust Signals (Coding + GitHub)

### 2.1 Release strategy
- Tag `v1.0.0` and create a GitHub Release with notes (currently 0 tags)
- Future changes get proper releases with migration notes

### 2.2 GitHub discoverability
- Set Topics: `claude-code`, `python-template`, `uv`, `tdd`, `monorepo`, `ruff`, `pyright`, `ai-agents`, `pre-commit`
- Tighten the one-line repo description for search

### 2.3 "Where did you find this?" discussion
- Enable GitHub Discussions, add a "How did you find us?" pinned thread (lightweight adoption telemetry)

### 2.4 Comparison table
- Add honest comparison vs. `iepathos/python-claude-code`, `discus0434/python-template-for-claude-code`, `scotthavird/claude-code-template`, `serpro69/claude-starter-kit`
- People respect honesty about trade-offs

---

## Phase 3: Create Content (Real-World)

### 3.1 Record a demo
- 60-second asciinema/Loom showing: template -> setup -> Claude Code catches a linting error -> forced to write tests
- Embed in README

### 3.2 Write the "methodology" article
- Publish on dev.to/Medium: "How to structure Python projects for AI coding assistants"
- Focus on the Q/S/P classification and *why* -- the methodology is the interesting content, the template is the reference implementation
- Educational first, link to repo as implementation -- not an ad

### 3.3 Short YouTube/Loom walkthrough
- 5 minutes max showing the full workflow

---

## Phase 4: Distribute (Real-World)

### 4.1 Targeted communities (do first)
- Submit PR to **awesome-claude-code** list under "Project Templates"
- Post to **Claude Developers Discord** as "here's what I built, feedback welcome"
- Post to **r/ClaudeAI**, **r/Python** -- text post explaining the problem, not just a link drop

### 4.2 Show HN
- Title: `Show HN: A Python template that forces Claude Code to use TDD`
- Must have the demo GIF and polished README ready first

### 4.3 Social media
- X/LinkedIn thread with before/after narrative
- Tag **@AnthropicAI** and **@astaborsky** (Astral/uv/ruff creators)

### 4.4 Newsletters (medium-term)
- Pitch to PyCoder's Weekly, TLDR AI, Python Weekly

---

## Phase 5: Sustain (Ongoing)

### 5.1 Find 3-5 early adopters
- More important than broadcasting widely -- one genuine testimonial beats 100 impressions
- Their issues/PRs make the repo look alive (10 closed issues > 0 issues)

### 5.2 Cross-reference from own projects
- Use the template in your public projects, link back
- Real usage is the best advertisement

### 5.3 Manage support expectations
- Set clear expectations in README/CONTRIBUTING about response times
- Public repos create support obligations

---

## Completed (PR #21)

- [x] README restructure (1.1) -- personas, workflow, devcontainer section, honest tone
- [x] Getting Started guide (partial 1.4) -- docs/GETTING_STARTED.md
- [x] Fix "battle-tested" / "production-quality" claims (1.5)

## Priority Order (remaining)

| Priority | Step | Type | Impact |
|----------|------|------|--------|
| 1 | Example project (1.2) | Code | "Show don't tell" |
| 2 | Community files -- CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md (1.4) | Code | Trust signals |
| 3 | v1.0.0 release + GitHub topics (2.1, 2.2) | GitHub | Discoverability |
| 4 | Demo recording (3.1) | Real-world | Conversion driver |
| 5 | awesome-claude-code + Discord + Reddit (4.1) | Real-world | First users |
| 6 | Blog post (3.2) | Real-world | Long-tail discovery |
| 7 | Show HN + social (4.2, 4.3) | Real-world | Broader reach |
