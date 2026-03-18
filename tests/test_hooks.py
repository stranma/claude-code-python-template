"""Tests for .claude/hooks/ -- validates hook scripts exist, are executable, and have correct structure."""

import stat
import subprocess
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).parent.parent / ".claude" / "hooks"

ALL_HOOKS = [
    "dangerous-actions-blocker.sh",
    "auto-format.sh",
]


class TestHookExistence:
    """Verify all expected hook scripts exist."""

    def test_hooks_directory_exists(self) -> None:
        assert HOOKS_DIR.exists(), f"{HOOKS_DIR} does not exist"
        assert HOOKS_DIR.is_dir(), f"{HOOKS_DIR} is not a directory"

    @pytest.mark.parametrize("hook_name", ALL_HOOKS)
    def test_hook_file_exists(self, hook_name: str) -> None:
        hook_path = HOOKS_DIR / hook_name
        assert hook_path.exists(), f"Hook script missing: {hook_name}"

    def test_no_unexpected_hooks(self) -> None:
        actual_hooks = {f.name for f in HOOKS_DIR.iterdir() if f.is_file() and f.suffix == ".sh"}
        expected_hooks = set(ALL_HOOKS)
        unexpected = actual_hooks - expected_hooks
        assert not unexpected, f"Unexpected hook scripts found: {unexpected}"


class TestHookPermissions:
    """Verify all hook scripts are executable."""

    @pytest.mark.parametrize("hook_name", ALL_HOOKS)
    def test_hook_is_executable(self, hook_name: str) -> None:
        hook_path = HOOKS_DIR / hook_name
        repo_root = Path(__file__).parent.parent
        # Try git's tracked mode first (works on Windows where NTFS has no execute bit)
        result = subprocess.run(
            ["git", "ls-files", "-s", str(hook_path.relative_to(repo_root))],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        if result.stdout:
            assert result.stdout.startswith("100755"), (
                f"{hook_name} is not tracked as executable by git (expected mode 100755)"
            )
        else:
            # Not in a git repo (e.g. integration test copy) -- fall back to filesystem
            mode = hook_path.stat().st_mode
            assert mode & stat.S_IXUSR, f"{hook_name} is not executable (missing user execute bit)"

    @pytest.mark.parametrize("hook_name", ALL_HOOKS)
    def test_hook_is_readable(self, hook_name: str) -> None:
        hook_path = HOOKS_DIR / hook_name
        mode = hook_path.stat().st_mode
        assert mode & stat.S_IRUSR, f"{hook_name} is not readable"


class TestHookStructure:
    """Verify hook scripts have correct structure."""

    @pytest.mark.parametrize("hook_name", ALL_HOOKS)
    def test_hook_has_shebang(self, hook_name: str) -> None:
        hook_path = HOOKS_DIR / hook_name
        first_line = hook_path.read_text(encoding="utf-8").splitlines()[0]
        assert first_line == "#!/bin/bash", f"{hook_name} missing #!/bin/bash shebang, got: {first_line!r}"

    @pytest.mark.parametrize("hook_name", ALL_HOOKS)
    def test_hook_has_description_comment(self, hook_name: str) -> None:
        hook_path = HOOKS_DIR / hook_name
        content = hook_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        comment_lines = [line for line in lines[1:10] if line.startswith("#")]
        assert len(comment_lines) >= 1, f"{hook_name} missing description comment after shebang"

    @pytest.mark.parametrize("hook_name", ALL_HOOKS)
    def test_hook_uses_jq(self, hook_name: str) -> None:
        hook_path = HOOKS_DIR / hook_name
        content = hook_path.read_text(encoding="utf-8")
        assert "jq" in content, f"{hook_name} does not use jq for JSON parsing"

    @pytest.mark.parametrize("hook_name", ALL_HOOKS)
    def test_hook_handles_missing_jq(self, hook_name: str) -> None:
        hook_path = HOOKS_DIR / hook_name
        content = hook_path.read_text(encoding="utf-8")
        assert "command -v jq" in content, f"{hook_name} does not check for jq availability"

    @pytest.mark.parametrize("hook_name", ALL_HOOKS)
    def test_hook_ends_with_exit_0(self, hook_name: str) -> None:
        hook_path = HOOKS_DIR / hook_name
        content = hook_path.read_text(encoding="utf-8").rstrip()
        assert content.endswith("exit 0"), f"{hook_name} does not end with 'exit 0'"

    @pytest.mark.parametrize("hook_name", ALL_HOOKS)
    def test_hook_is_not_empty(self, hook_name: str) -> None:
        hook_path = HOOKS_DIR / hook_name
        content = hook_path.read_text(encoding="utf-8")
        assert len(content) > 100, f"{hook_name} appears to be too short ({len(content)} bytes)"


class TestExfiltrationGuardBehavior:
    """Verify dangerous-actions-blocker blocks exfiltration patterns."""

    def test_exits_2_for_blocks(self) -> None:
        content = (HOOKS_DIR / "dangerous-actions-blocker.sh").read_text(encoding="utf-8")
        assert "exit 2" in content, "dangerous-actions-blocker must exit 2 to block actions"

    def test_checks_bash_only(self) -> None:
        content = (HOOKS_DIR / "dangerous-actions-blocker.sh").read_text(encoding="utf-8")
        assert '"Bash"' in content, "dangerous-actions-blocker should only check Bash tool"

    def test_blocks_gh_gist_create(self) -> None:
        content = (HOOKS_DIR / "dangerous-actions-blocker.sh").read_text(encoding="utf-8")
        assert "gh gist create" in content, "dangerous-actions-blocker missing gh gist create pattern"

    def test_blocks_gh_issue_create_with_body(self) -> None:
        content = (HOOKS_DIR / "dangerous-actions-blocker.sh").read_text(encoding="utf-8")
        assert "gh issue create" in content, "dangerous-actions-blocker missing gh issue create pattern"
        assert "--body" in content, "dangerous-actions-blocker missing --body check"

    def test_blocks_publishing_commands(self) -> None:
        content = (HOOKS_DIR / "dangerous-actions-blocker.sh").read_text(encoding="utf-8")
        for pattern in ["twine upload", "npm publish", "uv publish"]:
            assert pattern in content, f"dangerous-actions-blocker missing publishing pattern: {pattern}"

    def test_checks_secrets(self) -> None:
        content = (HOOKS_DIR / "dangerous-actions-blocker.sh").read_text(encoding="utf-8")
        for pattern in ["ANTHROPIC_API_KEY", "AWS_SECRET_ACCESS_KEY", "AKIA", "sk-", "ghp_"]:
            assert pattern in content, f"dangerous-actions-blocker missing secret pattern: {pattern}"

    def test_does_not_block_local_destruction(self) -> None:
        content = (HOOKS_DIR / "dangerous-actions-blocker.sh").read_text(encoding="utf-8")
        # Extract only the block-list arrays (non-comment lines containing patterns)
        non_comment_lines = [line for line in content.splitlines() if not line.strip().startswith("#")]
        code_content = "\n".join(non_comment_lines)
        for pattern in ["rm -rf /", "'sudo'", "DROP DATABASE", "git push --force"]:
            assert pattern not in code_content, (
                f"dangerous-actions-blocker should NOT block local destruction pattern: {pattern}"
            )

    def test_has_security_model_comment(self) -> None:
        content = (HOOKS_DIR / "dangerous-actions-blocker.sh").read_text(encoding="utf-8")
        assert "Exfiltration guard" in content, "dangerous-actions-blocker missing security model comment"
        assert "disposable" in content, "dangerous-actions-blocker missing disposable devcontainer note"


class TestAutoFormatBehavior:
    """Verify auto-format hook has correct patterns."""

    def test_targets_python_files(self) -> None:
        content = (HOOKS_DIR / "auto-format.sh").read_text(encoding="utf-8")
        assert "*.py" in content or ".py" in content, "auto-format should target Python files"

    def test_uses_ruff(self) -> None:
        content = (HOOKS_DIR / "auto-format.sh").read_text(encoding="utf-8")
        assert "ruff format" in content, "auto-format should use ruff format"
        assert "ruff check --fix" in content, "auto-format should use ruff check --fix"

    def test_checks_edit_and_write(self) -> None:
        content = (HOOKS_DIR / "auto-format.sh").read_text(encoding="utf-8")
        assert '"Edit"' in content, "auto-format should check Edit tool"
        assert '"Write"' in content, "auto-format should check Write tool"
