#!/usr/bin/env python3
"""Validate converted agent files in the agent catalog.

Checks that all agent .md files have valid YAML frontmatter with required fields
and correct values.

Usage:
    python scripts/validate_agents.py .claude/agent-catalog/
    python scripts/validate_agents.py .claude/agents/
"""

import re
import sys
from pathlib import Path

REQUIRED_FIELDS = {"name", "description", "model", "tools", "permissionMode", "color"}
VALID_MODELS = {"haiku", "sonnet", "opus"}
VALID_PERMISSION_MODES = {"dontAsk", "acceptEdits", "bypassPermissions"}

# Emoji pattern for detecting emoji in section headers
EMOJI_PATTERN = re.compile(
    r"[\U0001F000-\U0001FFFF\u2600-\u27FF\uFE00-\uFE0F\u200D\u20E3"
    r"\U0001FA00-\U0001FAFF\U0001F900-\U0001F9FF]"
)


def parse_frontmatter_simple(content: str) -> dict | None:
    """Extract frontmatter fields from a Markdown file.

    :param content: full file content
    :return: dict of key-value pairs or None if no frontmatter
    """
    if not content.startswith("---"):
        return None

    end = content.find("---", 3)
    if end == -1:
        return None

    fm_text = content[3:end].strip()
    fm = {}
    for line in fm_text.split("\n"):
        match = re.match(r"^(\w[\w-]*):\s*(.*)", line.strip())
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            if value:
                fm[key] = value

    return fm


def get_body(content: str) -> str:
    """Extract body text after frontmatter.

    :param content: full file content
    :return: body text
    """
    if not content.startswith("---"):
        return content

    end = content.find("---", 3)
    if end == -1:
        return content

    return content[end + 3:].strip()


def validate_agent(filepath: Path) -> list[str]:
    """Validate a single agent file.

    :param filepath: path to the .md file
    :return: list of error messages (empty if valid)
    """
    errors = []

    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError) as e:
        return [f"Cannot read file: {e}"]

    # Check frontmatter exists
    fm = parse_frontmatter_simple(content)
    if fm is None:
        return ["No valid YAML frontmatter found"]

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"Missing required field: {field}")

    # Validate model value
    if "model" in fm and fm["model"] not in VALID_MODELS:
        errors.append(f"Invalid model '{fm['model']}' (expected: {', '.join(sorted(VALID_MODELS))})")

    # Validate permissionMode value
    if "permissionMode" in fm and fm["permissionMode"] not in VALID_PERMISSION_MODES:
        errors.append(
            f"Invalid permissionMode '{fm['permissionMode']}' "
            f"(expected: {', '.join(sorted(VALID_PERMISSION_MODES))})"
        )

    # Check body is non-empty
    body = get_body(content)
    if not body.strip():
        errors.append("Body is empty")

    # Check for emoji in section headers
    for line in body.split("\n"):
        if line.startswith("## ") or line.startswith("### "):
            if EMOJI_PATTERN.search(line):
                errors.append(f"Emoji in section header: {line.strip()[:60]}")

    return errors


def main() -> None:
    """Run validation on all agent files in the given directory."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_agents.py <agent-directory>")
        sys.exit(1)

    agent_dir = Path(sys.argv[1]).resolve()
    if not agent_dir.exists():
        print(f"Error: Directory not found: {agent_dir}")
        sys.exit(1)

    total = 0
    failed = 0
    all_errors: list[tuple[str, list[str]]] = []

    for md_file in sorted(agent_dir.rglob("*.md")):
        total += 1
        errors = validate_agent(md_file)
        if errors:
            failed += 1
            rel_path = md_file.relative_to(agent_dir)
            all_errors.append((str(rel_path), errors))

    # Report results
    if all_errors:
        print(f"FAIL: {failed}/{total} agents have validation errors\n")
        for filepath, errors in all_errors:
            print(f"  {filepath}:")
            for error in errors:
                print(f"    - {error}")
        print()
        sys.exit(1)
    else:
        print(f"PASS: All {total} agents validated successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
