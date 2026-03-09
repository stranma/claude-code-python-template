#!/bin/bash
# PreToolUse hook: Blocks devcontainer-denied commands via grep on full command string.
# Catches patterns inside chained commands (&&, ;, |) that glob-based deny rules miss.
# Uses $PERMISSION_TIER env var: 1/2 = all categories blocked, 3 = omit GH/infra/tool-install blocks.
# Fail-closed: if PERMISSION_TIER is unset, all categories are blocked (strictest).
# Exit 2 = block the action, Exit 0 = allow.
# Requires jq for JSON parsing; fails closed if missing (blocks all bash).

if ! command -v jq &>/dev/null; then
    printf '%s\n' '{"decision":"block","reason":"devcontainer-policy-blocker requires jq for policy enforcement. Install jq in the Dockerfile."}'
    exit 2
fi

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

if [ "$TOOL_NAME" != "Bash" ]; then
    exit 0
fi

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
    exit 0
fi

TIER="${PERMISSION_TIER:-0}"

block() {
    jq -n --arg reason "$1" '{"decision":"block","reason":$reason}'
    exit 2
}

# --- Tool installation (tiers 0/1/2 only, allowed in tier 3) ---
if [ "$TIER" != "3" ]; then
    BLOCKED_TOOL_INSTALL=(
        'pip install'
        'pip3 install'
        'pipx install'
        'python -m pip install'
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

    for pattern in "${BLOCKED_TOOL_INSTALL[@]}"; do
        if echo "$COMMAND" | grep -qiF "$pattern"; then
            block "Blocked by devcontainer-policy-blocker: '$pattern' is not allowed in tier $TIER. Use 'uv add <package>' for project dependencies or add to .devcontainer/Dockerfile for tools."
        fi
    done
fi

# --- Package publishing (all tiers) ---
BLOCKED_PUBLISH=(
    'npm publish'
    'npx npm publish'
    'uv publish'
    'twine upload'
)

for pattern in "${BLOCKED_PUBLISH[@]}"; do
    if echo "$COMMAND" | grep -qiF "$pattern"; then
        block "Blocked by devcontainer-policy-blocker: '$pattern' is not allowed. Ask the user to publish manually."
    fi
done

# --- Supply-chain vectors (all tiers) ---
BLOCKED_SUPPLY_CHAIN=(
    '| bash'
    '|bash'
    '| sh'
    '|sh'
    '| zsh'
    '|zsh'
)

for pattern in "${BLOCKED_SUPPLY_CHAIN[@]}"; do
    if echo "$COMMAND" | grep -qiF "$pattern"; then
        block "Blocked by devcontainer-policy-blocker: piping to a shell ('$pattern') is not allowed. Add tools to .devcontainer/Dockerfile instead."
    fi
done

# --- Docker escape vectors (all tiers) ---
BLOCKED_DOCKER_ESCAPE=(
    'docker run --privileged'
    'docker run --cap-add=ALL'
    'docker run --pid=host'
    'docker run --network=host'
)

for pattern in "${BLOCKED_DOCKER_ESCAPE[@]}"; do
    if echo "$COMMAND" | grep -qiF "$pattern"; then
        block "Blocked by devcontainer-policy-blocker: '$pattern' is not allowed. Use 'docker run' without escape flags."
    fi
done

# --- GitHub shared state mutations (tiers 0/1/2 only, allowed in tier 3) ---
if [ "$TIER" != "3" ]; then
    BLOCKED_GH_MUTATIONS=(
        'gh pr merge'
        'gh workflow run'
        'gh workflow enable'
        'gh workflow disable'
        'gh issue create'
        'gh issue close'
        'gh issue edit'
    )

    for pattern in "${BLOCKED_GH_MUTATIONS[@]}"; do
        if echo "$COMMAND" | grep -qiF "$pattern"; then
            block "Blocked by devcontainer-policy-blocker: '$pattern' is not allowed in tier $TIER. Ask the user to perform this action."
        fi
    done
fi

# --- Infrastructure (tiers 0/1/2 only, allowed in tier 3) ---
if [ "$TIER" != "3" ]; then
    if echo "$COMMAND" | grep -qiF 'terraform '; then
        block "Blocked by devcontainer-policy-blocker: 'terraform' is not allowed in tier $TIER. Ask the user to run terraform."
    fi
fi

exit 0
