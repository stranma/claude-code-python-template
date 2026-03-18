"""Tests for .claude/commands/ -- validates no stale command files exist."""

from pathlib import Path

COMMANDS_DIR = Path(__file__).parent.parent / ".claude" / "commands"


class TestCommandsRemoved:
    """Verify commands directory was removed (all commands pruned)."""

    def test_commands_directory_does_not_exist(self) -> None:
        assert (
            not COMMANDS_DIR.exists()
        ), f"Commands directory should not exist after pruning, but found: {COMMANDS_DIR}"
