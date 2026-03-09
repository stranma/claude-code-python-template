---
name: sync
description: Pre-flight workspace sync. Run before starting any work to check branch state, remote tracking, dirty files, and recent commits.
allowed-tools: Read, Bash, Grep
disable-model-invocation: true
---

# Sync

Pre-flight workspace sync. Run this before starting any work.

## Steps

1. **Fetch remote refs**
   - Run `git fetch origin`

2. **Check workspace state**
   - Run `git status` to see dirty files, staged changes, untracked files
   - Run `git branch -vv` to see current branch, tracking info, ahead/behind counts

3. **Warn on problems**
   - If behind remote: warn and suggest `git pull --rebase` or `git rebase origin/<branch>`
   - If on main/master with dirty working tree: warn that uncommitted changes exist on the base branch
   - If no upstream tracking branch: note that the branch is local-only

4. **Show recent context**
   - Run `git log --oneline -3` to show the last 3 commits

5. **Output structured report**

```
# Workspace Sync

Branch: <name> (tracking: <remote>/<branch>)
Status: <clean | N dirty files | N staged, M unstaged>
Remote: <up to date | N ahead, M behind>

## Warnings
- <any warnings from step 3, or "None">

## Recent Commits
- <hash> <message>
- <hash> <message>
- <hash> <message>
```

## What This Skill Does NOT Do

- Does NOT classify the task as Q/S/P
- Does NOT read DECISIONS.md or IMPLEMENTATION_PLAN.md
- Does NOT modify any files

This is purely a workspace readiness check.
