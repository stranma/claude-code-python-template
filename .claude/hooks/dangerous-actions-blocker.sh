#!/bin/bash
# Exfiltration guard for autonomous mode.
# Primary defense: iptables firewall (network whitelist).
# This hook catches exfiltration via TRUSTED channels (GitHub API, package registries)
# and secrets leaked as command arguments.
# Local destruction (rm -rf, sudo, etc.) is not blocked -- devcontainer is disposable.

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

# --- Exfiltration via trusted channels (exit 2 = hard block) ---

EXFIL_LITERAL_PATTERNS=(
    'gh gist create'
    'twine upload'
    'npm publish'
    'pip upload'
    'uv publish'
)

for pattern in "${EXFIL_LITERAL_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qiF "$pattern"; then
        jq -n --arg reason "Blocked by dangerous-actions-blocker hook: exfiltration via trusted channel '$pattern'" \
            '{"decision":"block","reason":$reason}'
        exit 2
    fi
done

# gh issue create with --body or --body-file (data exfil via issue body)
if echo "$COMMAND" | grep -qiF "gh issue create" && echo "$COMMAND" | grep -qiE '\-\-body(-file)?'; then
    jq -n '{"decision":"block","reason":"Blocked by dangerous-actions-blocker hook: exfiltration via gh issue create --body/--body-file"}'
    exit 2
fi

# --- Secrets as literal command arguments ---

SECRET_REGEX_PATTERNS=(
    'AKIA[0-9A-Z]{16}'
    'sk-[a-zA-Z0-9_-]{20,}'
    'ghp_[a-zA-Z0-9]{36}'
    'gho_[a-zA-Z0-9]{36}'
    'github_pat_[a-zA-Z0-9_]{22,}'
    'Bearer [a-zA-Z0-9_./-]+'
    'token=[a-zA-Z0-9_./-]+'
)

SECRET_LITERAL_PATTERNS=(
    'ANTHROPIC_API_KEY='
    'OPENAI_API_KEY='
    'AWS_SECRET_ACCESS_KEY='
    'GITHUB_TOKEN='
    'GH_TOKEN='
    'DATABASE_URL='
)

for pattern in "${SECRET_LITERAL_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qF "$pattern"; then
        jq -n '{"decision":"block","reason":"Blocked by dangerous-actions-blocker hook: command appears to contain secrets or credentials. Use environment variables instead."}'
        exit 2
    fi
done

for pattern in "${SECRET_REGEX_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qE "$pattern"; then
        jq -n '{"decision":"block","reason":"Blocked by dangerous-actions-blocker hook: command appears to contain secrets or credentials. Use environment variables instead."}'
        exit 2
    fi
done

exit 0
