"""Tests for agent catalog conversion, validation, and setup integration."""

import json
import shutil
import textwrap
from pathlib import Path

import pytest

import sys

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from convert_agents import (
    assign_model,
    assign_permission_mode,
    build_description,
    convert_agent,
    generate_manifest,
    is_writing_agent,
    map_tools,
    parse_frontmatter,
    slugify,
    strip_emoji_from_header,
    transform_body,
)
from validate_agents import parse_frontmatter_simple, validate_agent

# Also import setup functions
sys.path.insert(0, str(Path(__file__).parent.parent))
from setup_project import cleanup_agent_catalog, install_agent_catalog, list_agent_categories


# --- parse_frontmatter tests ---


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        content = textwrap.dedent("""\
            ---
            name: Test Agent
            description: A test agent
            color: blue
            emoji: 🔧
            ---

            Body content here.
        """)
        result = parse_frontmatter(content)
        assert result is not None
        fm, body = result
        assert fm["name"] == "Test Agent"
        assert fm["description"] == "A test agent"
        assert fm["color"] == "blue"
        assert "Body content here." in body

    def test_no_frontmatter(self):
        content = "# Just a heading\n\nNo frontmatter here."
        assert parse_frontmatter(content) is None

    def test_incomplete_frontmatter(self):
        content = "---\nname: Test\nNo closing delimiter"
        assert parse_frontmatter(content) is None

    def test_quoted_values(self):
        content = '---\nname: "Quoted Name"\ncolor: \'single\'\n---\nBody'
        result = parse_frontmatter(content)
        assert result is not None
        fm, _ = result
        assert fm["name"] == "Quoted Name"
        assert fm["color"] == "single"


# --- slugify tests ---


class TestSlugify:
    def test_basic(self):
        assert slugify("Frontend Developer") == "frontend-developer"

    def test_special_chars(self):
        assert slugify("AI/ML Engineer") == "aiml-engineer"

    def test_consecutive_spaces(self):
        assert slugify("Hello   World") == "hello-world"

    def test_leading_trailing(self):
        assert slugify("  Test Agent  ") == "test-agent"

    def test_already_kebab(self):
        assert slugify("already-kebab") == "already-kebab"

    def test_underscores(self):
        assert slugify("some_agent_name") == "some-agent-name"


# --- strip_emoji_from_header tests ---


class TestStripEmoji:
    def test_emoji_in_h2(self):
        result = strip_emoji_from_header("## 🧠 Your Identity & Memory")
        assert "🧠" not in result
        assert "Identity & Memory" in result

    def test_no_emoji(self):
        result = strip_emoji_from_header("## Core Mission")
        assert result == "## Core Mission"

    def test_removes_your_prefix(self):
        result = strip_emoji_from_header("## Your Core Mission")
        assert result == "## Core Mission"


# --- assign_model tests ---


class TestAssignModel:
    def test_default_sonnet(self):
        assert assign_model("engineering", "frontend-developer") == "sonnet"

    def test_opus_for_orchestrator(self):
        assert assign_model("specialized", "agents-orchestrator") == "opus"

    def test_opus_for_software_architect(self):
        assert assign_model("engineering", "software-architect") == "opus"


# --- is_writing_agent / assign_permission_mode / map_tools tests ---


class TestPermissions:
    def test_engineering_is_writing(self):
        assert is_writing_agent("engineering", "frontend-developer") is True

    def test_testing_is_not_writing(self):
        assert is_writing_agent("testing", "reality-checker") is False

    def test_writer_pattern_matches(self):
        assert is_writing_agent("marketing", "content-creator") is True

    def test_permission_mode_writing(self):
        assert assign_permission_mode("engineering", "backend-architect") == "acceptEdits"

    def test_permission_mode_readonly(self):
        assert assign_permission_mode("testing", "reality-checker") == "dontAsk"

    def test_tools_with_edit(self):
        tools = map_tools("engineering", "frontend-developer")
        assert "Edit" in tools

    def test_tools_without_edit(self):
        tools = map_tools("testing", "reality-checker")
        assert "Edit" not in tools
        assert "Read" in tools


# --- build_description tests ---


class TestBuildDescription:
    def test_has_example_block(self):
        desc = build_description("Frontend Developer", "Expert in frontend", "engineering")
        assert "<example>" in desc
        assert "</example>" in desc
        assert "engineering tasks" in desc

    def test_has_task_tool_reference(self):
        desc = build_description("Test Agent", "Tests things", "testing")
        assert "Task tool" in desc


# --- transform_body tests ---


class TestTransformBody:
    def test_strips_h1(self):
        body = "# Agent Personality\n\n## Core Mission\n- Do things"
        result = transform_body(body, "Test", "Tests stuff")
        assert "# Agent Personality" not in result
        assert "Core Mission" in result

    def test_drops_identity_section(self):
        body = (
            "## 🧠 Your Identity & Memory\n- Role: Tester\n\n"
            "## 🎯 Your Core Mission\n- Test things"
        )
        result = transform_body(body, "Test", "Tests stuff")
        assert "Identity" not in result
        assert "Core Mission" in result

    def test_drops_communication_style(self):
        body = (
            "## Core Mission\n- Do stuff\n\n"
            "## 💭 Your Communication Style\n- Friendly tone"
        )
        result = transform_body(body, "Test", "Tests stuff")
        assert "Communication Style" not in result

    def test_keeps_critical_rules(self):
        body = "## 🚨 Critical Rules You Must Follow\n- Never skip tests"
        result = transform_body(body, "Test", "Tests stuff")
        assert "Critical Rules" in result
        assert "Never skip tests" in result

    def test_skips_duplicate_intro(self):
        body = (
            "# Test Agent Personality\n\n"
            "You are **TestAgent**, a specialist.\n\n"
            "## Core Mission\n- Do stuff"
        )
        result = transform_body(body, "Test", "Tests stuff")
        assert "You are **TestAgent**" not in result
        assert "Core Mission" in result

    def test_opening_line(self):
        body = "## Core Mission\n- Do stuff"
        result = transform_body(body, "Tester", "Expert in testing")
        assert result.startswith("You are a Tester specialist.")


# --- convert_agent tests ---


class TestConvertAgent:
    def test_full_conversion(self, tmp_path):
        source = tmp_path / "test-agent.md"
        source.write_text(textwrap.dedent("""\
            ---
            name: Test Agent
            description: A test agent for testing
            color: green
            ---

            # Test Agent Personality

            You are **TestAgent**, a testing specialist.

            ## Your Identity & Memory
            - Role: Tester

            ## Your Core Mission
            - Run comprehensive tests
            - Validate all outputs

            ## Critical Rules
            - Never skip validation
        """), encoding="utf-8")

        result = convert_agent(source, "testing")
        assert result is not None
        filename, content = result

        assert filename == "testing-test-agent.md"
        assert "name: testing-test-agent" in content
        assert "model: sonnet" in content
        assert "permissionMode: dontAsk" in content
        assert "color: green" in content
        assert "Core Mission" in content
        assert "Never skip validation" in content
        # Dropped sections
        assert "Identity & Memory" not in content

    def test_skips_non_agent(self, tmp_path):
        source = tmp_path / "not-an-agent.md"
        source.write_text("# Just a document\n\nNo frontmatter here.")
        assert convert_agent(source, "testing") is None

    def test_preserves_category_prefix(self, tmp_path):
        source = tmp_path / "engineering-backend-architect.md"
        source.write_text("---\nname: Backend Architect\ndescription: Builds backends\ncolor: blue\n---\n\nBody")
        result = convert_agent(source, "engineering")
        assert result is not None
        filename, _ = result
        assert filename == "engineering-backend-architect.md"


# --- validate_agent tests ---


class TestValidateAgent:
    def test_valid_agent(self, tmp_path):
        agent = tmp_path / "test.md"
        agent.write_text(textwrap.dedent("""\
            ---
            name: test-agent
            description: A test
            model: sonnet
            tools: Read, Grep
            permissionMode: dontAsk
            color: blue
            ---

            Body content here.
        """))
        errors = validate_agent(agent)
        assert errors == []

    def test_missing_fields(self, tmp_path):
        agent = tmp_path / "bad.md"
        agent.write_text("---\nname: test\n---\n\nBody")
        errors = validate_agent(agent)
        assert len(errors) > 0
        missing = [e for e in errors if "Missing" in e]
        assert len(missing) >= 4  # description, model, tools, permissionMode, color

    def test_invalid_model(self, tmp_path):
        agent = tmp_path / "bad-model.md"
        agent.write_text(
            "---\nname: t\ndescription: t\nmodel: gpt4\ntools: Read\n"
            "permissionMode: dontAsk\ncolor: blue\n---\n\nBody"
        )
        errors = validate_agent(agent)
        assert any("Invalid model" in e for e in errors)

    def test_invalid_permission_mode(self, tmp_path):
        agent = tmp_path / "bad-perm.md"
        agent.write_text(
            "---\nname: t\ndescription: t\nmodel: sonnet\ntools: Read\n"
            "permissionMode: admin\ncolor: blue\n---\n\nBody"
        )
        errors = validate_agent(agent)
        assert any("Invalid permissionMode" in e for e in errors)

    def test_no_frontmatter(self, tmp_path):
        agent = tmp_path / "no-fm.md"
        agent.write_text("# Just a doc\n\nNo frontmatter.")
        errors = validate_agent(agent)
        assert any("frontmatter" in e.lower() for e in errors)


# --- Integration test against real catalog ---


@pytest.mark.skipif(
    not (Path(__file__).parent.parent / ".claude" / "agent-catalog" / "manifest.json").exists(),
    reason="Agent catalog not built yet",
)
class TestCatalogIntegration:
    """Integration tests that run against the actual converted catalog."""

    CATALOG_DIR = Path(__file__).parent.parent / ".claude" / "agent-catalog"

    def test_manifest_exists(self):
        assert (self.CATALOG_DIR / "manifest.json").exists()

    def test_manifest_has_categories(self):
        manifest = json.loads((self.CATALOG_DIR / "manifest.json").read_text())
        assert "categories" in manifest
        assert "total" in manifest
        assert manifest["total"] > 0

    def test_all_agents_valid(self):
        """Validate every agent in the catalog has correct frontmatter."""
        errors = []
        for md_file in sorted(self.CATALOG_DIR.rglob("*.md")):
            file_errors = validate_agent(md_file)
            if file_errors:
                rel = md_file.relative_to(self.CATALOG_DIR)
                errors.append(f"{rel}: {file_errors}")
        assert errors == [], f"Validation errors:\n" + "\n".join(errors)

    def test_agent_count_matches_manifest(self):
        manifest = json.loads((self.CATALOG_DIR / "manifest.json").read_text())
        actual_count = sum(1 for _ in self.CATALOG_DIR.rglob("*.md"))
        assert actual_count == manifest["total"]


# --- install_agent_catalog tests ---


class TestInstallAgentCatalog:
    def _create_catalog(self, root: Path):
        """Create a minimal test catalog structure."""
        catalog = root / ".claude" / "agent-catalog"
        agents_dir = root / ".claude" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        # Create engineering category with 2 agents
        eng_dir = catalog / "engineering"
        eng_dir.mkdir(parents=True)
        (eng_dir / "engineering-frontend.md").write_text(
            "---\nname: engineering-frontend\ndescription: t\nmodel: sonnet\n"
            "tools: Read\npermissionMode: acceptEdits\ncolor: cyan\n---\nBody"
        )
        (eng_dir / "engineering-backend.md").write_text(
            "---\nname: engineering-backend\ndescription: t\nmodel: sonnet\n"
            "tools: Read\npermissionMode: acceptEdits\ncolor: blue\n---\nBody"
        )

        # Create testing category with 1 agent
        test_dir = catalog / "testing"
        test_dir.mkdir(parents=True)
        (test_dir / "testing-qa.md").write_text(
            "---\nname: testing-qa\ndescription: t\nmodel: sonnet\n"
            "tools: Read\npermissionMode: dontAsk\ncolor: red\n---\nBody"
        )

        # Create manifest
        manifest = {
            "categories": {
                "engineering": {"label": "Engineering (2 agents)", "description": "Dev", "count": 2, "agents": []},
                "testing": {"label": "Testing (1 agent)", "description": "QA", "count": 1, "agents": []},
            },
            "total": 3,
        }
        (catalog / "manifest.json").write_text(json.dumps(manifest))

        return root

    def test_install_single_category(self, tmp_path):
        root = self._create_catalog(tmp_path)
        actions = install_agent_catalog(root, ["engineering"])
        agents_dir = root / ".claude" / "agents"
        assert (agents_dir / "engineering-frontend.md").exists()
        assert (agents_dir / "engineering-backend.md").exists()
        assert not (agents_dir / "testing-qa.md").exists()
        assert any("2 agents" in a for a in actions)

    def test_install_multiple_categories(self, tmp_path):
        root = self._create_catalog(tmp_path)
        actions = install_agent_catalog(root, ["engineering", "testing"])
        agents_dir = root / ".claude" / "agents"
        assert (agents_dir / "engineering-frontend.md").exists()
        assert (agents_dir / "testing-qa.md").exists()
        assert any("3 agents installed" in a for a in actions)

    def test_missing_category_warning(self, tmp_path):
        root = self._create_catalog(tmp_path)
        actions = install_agent_catalog(root, ["nonexistent"])
        assert any("Warning" in a for a in actions)

    def test_no_catalog_directory(self, tmp_path):
        actions = install_agent_catalog(tmp_path, ["engineering"])
        assert any("not found" in a for a in actions)


class TestCleanupAgentCatalog:
    def test_cleanup_removes_directory(self, tmp_path):
        catalog = tmp_path / ".claude" / "agent-catalog"
        catalog.mkdir(parents=True)
        (catalog / "test.md").write_text("test")

        actions = cleanup_agent_catalog(tmp_path)
        assert not catalog.exists()
        assert len(actions) == 1

    def test_cleanup_no_directory(self, tmp_path):
        actions = cleanup_agent_catalog(tmp_path)
        assert actions == []


class TestListAgentCategories:
    def test_lists_categories(self, tmp_path):
        catalog = tmp_path / ".claude" / "agent-catalog"
        catalog.mkdir(parents=True)
        manifest = {
            "categories": {
                "engineering": {"description": "Dev agents", "count": 5},
                "testing": {"description": "QA agents", "count": 3},
            }
        }
        (catalog / "manifest.json").write_text(json.dumps(manifest))

        result = list_agent_categories(tmp_path)
        assert len(result) == 2
        assert result[0][0] == "engineering"
        assert result[0][2] == 5

    def test_no_manifest(self, tmp_path):
        result = list_agent_categories(tmp_path)
        assert result == []
