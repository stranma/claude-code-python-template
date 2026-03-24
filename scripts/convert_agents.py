#!/usr/bin/env python3
"""Convert agency-agents Markdown files to claude-code-python-template agent format.

Reads agent definitions from the agency-agents repo (Markdown with personality-rich
YAML frontmatter) and converts them to the template's structured agent format
(with model, tools, permissionMode fields and action-oriented body).

Usage:
    python scripts/convert_agents.py --source /path/to/agency-agents --output .claude/agent-catalog/
    python scripts/convert_agents.py --source /path/to/agency-agents --output .claude/agent-catalog/ --category engineering
    python scripts/convert_agents.py --source /path/to/agency-agents --output .claude/agent-catalog/ --dry-run
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Categories to scan in the source repo (directories containing agent .md files)
AGENT_CATEGORIES = [
    "academic",
    "design",
    "engineering",
    "game-development",
    "marketing",
    "paid-media",
    "product",
    "project-management",
    "sales",
    "spatial-computing",
    "specialized",
    "strategy",
    "support",
    "testing",
]

# Categories whose agents primarily write/create files (get Edit tool + acceptEdits)
WRITING_CATEGORIES = {
    "engineering",
    "game-development",
    "design",
}

# Specific agent name patterns that should get write permissions even in non-writing categories
WRITING_AGENT_PATTERNS = [
    "creator",
    "writer",
    "builder",
    "generator",
    "developer",
    "engineer",
    "scripter",
    "architect",
    "prototyper",
    "designer",
]

# Agents that should use opus model (complex orchestration)
OPUS_AGENTS = {
    "agents-orchestrator",
    "software-architect",
    "autonomous-optimization-architect",
}

# Agents that should use haiku model (simple/focused tasks)
HAIKU_CATEGORIES = set()  # None by default; most agents benefit from sonnet

# Sections to keep from the source agent body (after stripping emoji)
KEEP_SECTIONS = {
    "core mission",
    "critical rules",
    "critical rules you must follow",
    "workflow process",
    "workflow",
    "technical deliverables",
    "your core mission",
    "your workflow process",
    "your technical deliverables",
    "mandatory process",
    "your mandatory process",
    "advanced capabilities",
    "your advanced capabilities",
    "specialized skills",
    "your specialized skills",
    "decision framework",
    "your decision framework",
    "output format",
    "your output format",
}

# Sections to drop (personality/memory content not useful for stateless subagents)
DROP_SECTIONS = {
    "identity & memory",
    "your identity & memory",
    "communication style",
    "your communication style",
    "learning & memory",
    "your learning & memory",
    "learning and memory",
    "success metrics",
    "your success metrics",
}


def parse_frontmatter(content: str) -> tuple[dict, str] | None:
    """Extract YAML frontmatter and body from a Markdown file.

    :param content: full file content
    :return: (frontmatter_dict, body) or None if no valid frontmatter
    """
    if not content.startswith("---"):
        return None

    end = content.find("---", 3)
    if end == -1:
        return None

    frontmatter_text = content[3:end].strip()
    body = content[end + 3:].strip()

    # Simple YAML parsing (no external dependency needed for flat key-value)
    fm = {}
    current_key = None
    current_list: list[dict] | None = None

    for line in frontmatter_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Handle list items under a key (e.g., services)
        if stripped.startswith("- ") and current_key and current_list is not None:
            # Sub-item of a list
            item_match = re.match(r"-\s+(\w+):\s*(.*)", stripped)
            if item_match:
                if not current_list or not isinstance(current_list[-1], dict):
                    current_list.append({})
                current_list[-1][item_match.group(1)] = item_match.group(2).strip()
            else:
                current_list.append(stripped[2:].strip())
            continue

        # Handle top-level key: value
        kv_match = re.match(r"^(\w[\w-]*):\s*(.*)", stripped)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2).strip()

            if not value:
                # This might be a list/object key
                current_key = key
                current_list = []
                fm[key] = current_list
            else:
                # Remove surrounding quotes
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                fm[key] = value
                current_key = key
                current_list = None

    return fm, body


def slugify(name: str) -> str:
    """Convert a human-readable name to kebab-case slug.

    :param name: e.g. "Frontend Developer"
    :return: e.g. "frontend-developer"
    """
    slug = name.lower().strip()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def build_description(name: str, original_desc: str, category: str) -> str:
    """Generate a template-style description with example blocks.

    :param name: agent display name
    :param original_desc: original one-line description
    :param category: agent category
    :return: multi-line description with examples
    """
    # Clean up the original description
    desc = original_desc.strip().rstrip(".")

    task_phrase = f"Use this agent for {category} tasks -- {desc.lower()}"

    examples = (
        f"{task_phrase}.\\n\\n"
        f"**Examples:**\\n\\n"
        f"<example>\\n"
        f"Context: Need help with {category} work.\\n\\n"
        f'user: "Help me with {name.lower()} tasks"\\n\\n'
        f'assistant: "I\'ll use the {slugify(name)} agent to help with this."\\n\\n'
        f"<uses Task tool to launch {slugify(name)} agent>\\n"
        f"</example>"
    )
    return examples


def assign_model(category: str, agent_slug: str) -> str:
    """Assign a model based on category and agent complexity.

    :param category: agent category
    :param agent_slug: kebab-case agent name (without category prefix)
    :return: model name (haiku, sonnet, opus)
    """
    if agent_slug in OPUS_AGENTS:
        return "opus"
    if category in HAIKU_CATEGORIES:
        return "haiku"
    return "sonnet"


def is_writing_agent(category: str, agent_slug: str) -> bool:
    """Determine if an agent primarily writes/creates files.

    :param category: agent category
    :param agent_slug: kebab-case agent name
    :return: True if agent should have write permissions
    """
    if category in WRITING_CATEGORIES:
        return True
    for pattern in WRITING_AGENT_PATTERNS:
        if pattern in agent_slug:
            return True
    return False


def assign_permission_mode(category: str, agent_slug: str) -> str:
    """Assign permission mode based on whether the agent writes files.

    :param category: agent category
    :param agent_slug: kebab-case agent name
    :return: permission mode string
    """
    if is_writing_agent(category, agent_slug):
        return "acceptEdits"
    return "dontAsk"


def map_tools(category: str, agent_slug: str) -> str:
    """Map tools based on agent category and capabilities.

    :param category: agent category
    :param agent_slug: kebab-case agent name
    :return: comma-separated tool list
    """
    base_tools = "Read, Glob, Grep, Bash"
    if is_writing_agent(category, agent_slug):
        return f"{base_tools}, Edit"
    return base_tools


def strip_emoji_from_header(header: str) -> str:
    """Remove emoji characters from a Markdown header line.

    :param header: header line (e.g. "## 🧠 Your Identity & Memory")
    :return: cleaned header (e.g. "## Identity & Memory")
    """
    # Remove emoji and variation selectors
    cleaned = re.sub(
        r"[\U0001F000-\U0001FFFF\u2600-\u27FF\uFE00-\uFE0F\u200D\u20E3"
        r"\U0001FA00-\U0001FAFF\U0001F900-\U0001F9FF]+\s*",
        "",
        header,
    )
    # Remove "Your " prefix for cleaner headers
    cleaned = re.sub(r"^(#+\s+)Your\s+", r"\1", cleaned)
    return cleaned.strip()


def normalize_section_name(header_text: str) -> str:
    """Extract and normalize section name from a header for matching.

    :param header_text: header text after ## markers
    :return: lowercase normalized name
    """
    # Remove ## markers and emoji
    text = re.sub(r"^#+\s*", "", header_text)
    text = re.sub(
        r"[\U0001F000-\U0001FFFF\u2600-\u27FF\uFE00-\uFE0F\u200D\u20E3"
        r"\U0001FA00-\U0001FAFF\U0001F900-\U0001F9FF]+\s*",
        "",
        text,
    )
    return text.strip().lower()


def transform_body(body: str, agent_name: str, original_desc: str) -> str:
    """Transform the agency-agent body to template format.

    Strips emoji from headers, removes personality sections, keeps actionable content,
    and adds a concise opening line.

    :param body: original body text (after frontmatter)
    :param agent_name: display name of the agent
    :param original_desc: original description for context
    :return: transformed body text
    """
    lines = body.split("\n")
    result_lines: list[str] = []
    skip_section = False
    found_first_h2 = False

    # Opening line
    result_lines.append(
        f"You are a {agent_name} specialist. {original_desc.strip().rstrip('.')}."
    )
    result_lines.append("")

    for line in lines:
        # Skip the H1 agent personality title
        if line.startswith("# ") and not found_first_h2:
            continue

        # Skip the "You are **AgentName**" intro paragraph (we already have our opening line)
        if not found_first_h2 and line.startswith("You are **"):
            continue

        # Handle H2 section headers
        if line.startswith("## "):
            found_first_h2 = True
            section_name = normalize_section_name(line)

            if section_name in DROP_SECTIONS:
                skip_section = True
                continue

            # Check if this is a section to keep
            keep = False
            for keep_name in KEEP_SECTIONS:
                if keep_name in section_name:
                    keep = True
                    break

            if not keep and section_name not in DROP_SECTIONS:
                # Unknown section - keep it (conservative approach)
                keep = True

            if keep:
                skip_section = False
                cleaned_header = strip_emoji_from_header(line)
                result_lines.append(cleaned_header)
                continue
            else:
                skip_section = True
                continue

        # Handle H3+ headers within sections
        if line.startswith("### ") or line.startswith("#### "):
            if not skip_section:
                cleaned = strip_emoji_from_header(line)
                result_lines.append(cleaned)
            continue

        # Skip lines in dropped sections
        if skip_section:
            continue

        # Keep all other content lines (including empty lines for formatting)
        result_lines.append(line)

    # Clean up excessive blank lines
    cleaned = "\n".join(result_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def convert_agent(source_path: Path, category: str) -> tuple[str, str] | None:
    """Convert a single agency-agent file to template format.

    :param source_path: path to the source .md file
    :param category: category name (e.g. "engineering")
    :return: (filename, content) tuple or None if not a valid agent
    """
    content = source_path.read_text(encoding="utf-8")
    result = parse_frontmatter(content)
    if result is None:
        return None

    fm, body = result

    # Must have at least a name to be considered an agent
    if "name" not in fm:
        return None

    name = fm["name"]
    original_desc = fm.get("description", name)
    color = fm.get("color", "blue")
    agent_slug = slugify(name)

    # Build the filename: category-prefix + slug
    # Check if the source filename already has the category prefix
    source_stem = source_path.stem
    if source_stem.startswith(f"{category}-"):
        filename = f"{source_stem}.md"
        full_slug = source_stem
    else:
        filename = f"{category}-{agent_slug}.md"
        full_slug = f"{category}-{agent_slug}"

    # Assign template-specific fields
    model = assign_model(category, agent_slug)
    tools = map_tools(category, agent_slug)
    perm_mode = assign_permission_mode(category, agent_slug)
    description = build_description(name, original_desc, category)

    # Transform body
    transformed_body = transform_body(body, name, original_desc)

    # Build output
    output = f"""---
name: {full_slug}
description: {description}
model: {model}
tools: {tools}
permissionMode: {perm_mode}
color: {color}
---

{transformed_body}
"""
    return filename, output


def find_agent_files(source_dir: Path, category: str) -> list[Path]:
    """Find all agent .md files in a category directory (including subdirs).

    :param source_dir: root of agency-agents repo
    :param category: category directory name
    :return: list of .md file paths that are agents (have frontmatter)
    """
    cat_dir = source_dir / category
    if not cat_dir.exists():
        return []

    files = []
    for md_file in sorted(cat_dir.rglob("*.md")):
        # Skip README and non-agent files
        if md_file.name.lower() in {"readme.md", "contributing.md", "license.md"}:
            continue
        files.append(md_file)
    return files


def generate_manifest(catalog_dir: Path) -> dict:
    """Build manifest.json from the catalog directory contents.

    :param catalog_dir: path to .claude/agent-catalog/
    :return: manifest dict
    """
    manifest: dict = {"categories": {}, "total": 0}
    total = 0

    for cat_dir in sorted(catalog_dir.iterdir()):
        if not cat_dir.is_dir():
            continue

        agents = sorted(f.stem for f in cat_dir.glob("*.md"))
        count = len(agents)
        total += count

        # Build a readable label
        category = cat_dir.name
        label = f"{category.replace('-', ' ').title()} ({count} agents)"

        # Category descriptions
        descriptions = {
            "academic": "Research, historical analysis, anthropology, psychology, narratology",
            "design": "UI/UX design, brand guardianship, visual storytelling, inclusive design",
            "engineering": "Frontend, backend, DevOps, security, AI/ML, databases, cloud architecture",
            "game-development": "Game design, narrative, mechanics, Godot, Unity, Unreal, Roblox, Blender",
            "marketing": "Growth hacking, content creation, social media, SEO, influencer marketing",
            "paid-media": "PPC, search query analysis, tracking, creative strategy, programmatic ads",
            "product": "Sprint planning, trend research, feedback synthesis, behavioral psychology",
            "project-management": "Studio production, project coordination, operations, experiment tracking",
            "sales": "Outbound prospecting, discovery, deal strategy, pipeline management",
            "spatial-computing": "AR/VR/XR, spatial interfaces, 3D interaction, immersive experiences",
            "specialized": "Orchestration, governance, blockchain, compliance, memory systems",
            "strategy": "Strategic planning, market analysis, competitive positioning",
            "support": "Customer success, community management, onboarding, analytics",
            "testing": "QA, test automation, performance testing, accessibility validation",
        }

        manifest["categories"][category] = {
            "label": label,
            "description": descriptions.get(category, f"{category} agents"),
            "count": count,
            "agents": agents,
        }

    manifest["total"] = total
    return manifest


def main() -> None:
    """Run the agent conversion."""
    parser = argparse.ArgumentParser(description="Convert agency-agents to template format")
    parser.add_argument(
        "--source",
        required=True,
        help="Path to agency-agents repository root",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for converted agents (e.g., .claude/agent-catalog/)",
    )
    parser.add_argument(
        "--category",
        default="",
        help="Convert only this category (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without writing files",
    )
    args = parser.parse_args()

    source_dir = Path(args.source).resolve()
    output_dir = Path(args.output).resolve()

    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        sys.exit(1)

    categories = [args.category] if args.category else AGENT_CATEGORIES
    total_converted = 0
    total_skipped = 0

    for category in categories:
        agent_files = find_agent_files(source_dir, category)
        if not agent_files:
            print(f"  [{category}] No agent files found, skipping")
            continue

        cat_output_dir = output_dir / category
        converted = 0

        for agent_file in agent_files:
            result = convert_agent(agent_file, category)
            if result is None:
                total_skipped += 1
                if args.dry_run:
                    print(f"  [{category}] SKIP {agent_file.name} (no valid frontmatter)")
                continue

            filename, content = result
            converted += 1

            if args.dry_run:
                print(f"  [{category}] {agent_file.name} -> {filename}")
            else:
                cat_output_dir.mkdir(parents=True, exist_ok=True)
                (cat_output_dir / filename).write_text(content, encoding="utf-8")

        total_converted += converted
        print(f"  [{category}] Converted {converted} agents (from {len(agent_files)} files)")

    # Generate manifest
    if not args.dry_run and total_converted > 0:
        manifest = generate_manifest(output_dir)
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\nManifest written: {output_dir / 'manifest.json'}")

    print(f"\nTotal: {total_converted} agents converted, {total_skipped} files skipped")


if __name__ == "__main__":
    main()
