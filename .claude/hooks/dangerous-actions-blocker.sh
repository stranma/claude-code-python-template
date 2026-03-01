#!/bin/bash
# PreToolUse hook: Blocks dangerous shell commands before execution.
# Exit 2 = block the action, Exit 0 = allow.
# Requires jq for JSON parsing; degrades gracefully if missing.

if ! command -v jq &>/dev/null; then
    echo "WARNING: jq not found, dangerous-actions-blocker hook disabled" >&2
    exit 0
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

# Patterns that should be blocked outright
BLOCKED_PATTERNS=(
    'rm -rf /'
    'rm -rf /*'
    'rm -rf ~'
    'rm -rf $HOME'
    'sudo rm -rf'
    'mkfs\.'
    'dd if=/dev/zero'
    ':(){:|:&};:'
    'chmod -R 777 /'
    'chmod -R 777 /*'
    '> /dev/sda'
    'git push --force'
    'git push -f '
    'git push origin +master'
    'git push origin +main'
    'DROP DATABASE'
    'DROP TABLE'
    'TRUNCATE TABLE'
    'DELETE FROM .* WHERE 1'
    'shutdown'
    'reboot'
    'init 0'
    'init 6'
    'halt'
    'poweroff'
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        echo '{"decision":"block","reason":"Blocked by dangerous-actions-blocker hook: command matches dangerous pattern '"'$pattern'"'"}'
        exit 2
    fi
done

# Block commands containing secrets/tokens passed as arguments
SECRET_PATTERNS=(
    'ANTHROPIC_API_KEY='
    'OPENAI_API_KEY='
    'AWS_SECRET_ACCESS_KEY='
    'GITHUB_TOKEN='
    'GH_TOKEN='
    'DATABASE_URL=.*://.*:.*@'
    'password='
    'passwd='
    'secret='
    'token='
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiE "$pattern"; then
        echo '{"decision":"block","reason":"Blocked by dangerous-actions-blocker hook: command appears to contain secrets or credentials. Use environment variables instead."}'
        exit 2
    fi
done

exit 0
