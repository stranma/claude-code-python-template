"""Tests for setup_project.py -- validates all 5 template bugs are fixed."""

import importlib.util
import textwrap
from pathlib import Path

import pytest

# Load setup_project module from repo root
_spec = importlib.util.spec_from_file_location("setup_project", Path(__file__).parent.parent / "setup_project.py")
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

rename_packages = _mod.rename_packages


def _create_mock_project(tmp_path: Path, project_name: str, namespace: str) -> Path:
    """Create a mock project structure mimicking post-placeholder-substitution state.

    :param tmp_path: pytest temporary directory
    :param project_name: project name (e.g. "vizier")
    :param namespace: python namespace (e.g. "vizier")
    :return: root path of the mock project
    """
    root = tmp_path / project_name
    root.mkdir()

    # libs/core
    core_pkg = root / "libs" / "core" / namespace / "core"
    core_pkg.mkdir(parents=True)
    (core_pkg / "__init__.py").write_text(f'"""{project_name} core library."""\n\n__version__ = "0.1.0"\n')
    core_toml = root / "libs" / "core" / "pyproject.toml"
    core_toml.write_text(
        textwrap.dedent(f"""\
        [project]
        name = "{project_name}-core"
        version = "0.1.0"
        description = "A Python project - Core library"
        requires-python = ">=3.11,<3.13"
        dependencies = []

        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [tool.hatch.build.targets.wheel]
        packages = ["{namespace}"]
    """)
    )
    # libs/core/tests
    core_tests = root / "libs" / "core" / "tests"
    core_tests.mkdir()
    (core_tests / "__init__.py").write_text("")

    # apps/server
    server_pkg = root / "apps" / "server" / namespace / "server"
    server_pkg.mkdir(parents=True)
    (server_pkg / "__init__.py").write_text(f'"""{project_name} server application."""\n\n__version__ = "0.1.0"\n')
    server_toml = root / "apps" / "server" / "pyproject.toml"
    server_toml.write_text(
        textwrap.dedent(f"""\
        [project]
        name = "{project_name}-server"
        version = "0.1.0"
        description = "A Python project - Server application"
        requires-python = ">=3.11,<3.13"
        dependencies = [
            "{project_name}-core",
        ]

        [tool.uv.sources]
        "{project_name}-core" = {{ workspace = true }}

        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [tool.hatch.build.targets.wheel]
        packages = ["{namespace}"]
    """)
    )
    # apps/server/tests
    server_tests = root / "apps" / "server" / "tests"
    server_tests.mkdir()
    (server_tests / "__init__.py").write_text("")

    return root


class TestRenamePackagesContentUpdates:
    """Bug 1: rename_packages() must update pyproject.toml and __init__.py contents after directory renames."""

    def test_renamed_lib_has_correct_pyproject_name(self, tmp_path: Path) -> None:
        root = _create_mock_project(tmp_path, "vizier", "vizier")
        rename_packages(root, "vizier", ["engine", "server"])

        toml = (root / "libs" / "engine" / "pyproject.toml").read_text()
        assert 'name = "vizier-engine"' in toml
        assert "vizier-core" not in toml

    def test_renamed_app_has_correct_pyproject_name(self, tmp_path: Path) -> None:
        root = _create_mock_project(tmp_path, "vizier", "vizier")
        rename_packages(root, "vizier", ["core", "daemon"])

        toml = (root / "apps" / "daemon" / "pyproject.toml").read_text()
        assert 'name = "vizier-daemon"' in toml
        assert "vizier-server" not in toml

    def test_renamed_lib_has_correct_init_docstring(self, tmp_path: Path) -> None:
        root = _create_mock_project(tmp_path, "vizier", "vizier")
        rename_packages(root, "vizier", ["engine", "server"])

        init = (root / "libs" / "engine" / "vizier" / "engine" / "__init__.py").read_text()
        assert "engine" in init
        assert "core" not in init

    def test_renamed_app_has_correct_init_docstring(self, tmp_path: Path) -> None:
        root = _create_mock_project(tmp_path, "vizier", "vizier")
        rename_packages(root, "vizier", ["core", "daemon"])

        init = (root / "apps" / "daemon" / "vizier" / "daemon" / "__init__.py").read_text()
        assert "daemon" in init
        assert "server" not in init


class TestCrossReferenceUpdates:
    """Bug 1 (cross-refs): When a lib is renamed, app pyproject.toml dependencies must update."""

    def test_app_dependency_updated_when_lib_renamed(self, tmp_path: Path) -> None:
        root = _create_mock_project(tmp_path, "vizier", "vizier")
        rename_packages(root, "vizier", ["engine", "daemon"])

        toml = (root / "apps" / "daemon" / "pyproject.toml").read_text()
        assert "vizier-engine" in toml
        assert "vizier-core" not in toml

    def test_app_uv_sources_updated_when_lib_renamed(self, tmp_path: Path) -> None:
        root = _create_mock_project(tmp_path, "vizier", "vizier")
        rename_packages(root, "vizier", ["engine", "daemon"])

        toml = (root / "apps" / "daemon" / "pyproject.toml").read_text()
        assert '"vizier-engine"' in toml
        assert '"vizier-core"' not in toml


class TestAdditionalPackageNames:
    """Bug 2: Additional packages must use -name pattern replacement, not bare name."""

    def test_additional_lib_gets_correct_name(self, tmp_path: Path) -> None:
        root = _create_mock_project(tmp_path, "vizier", "vizier")
        rename_packages(root, "vizier", ["engine", "lib:utils", "daemon"])

        toml = (root / "libs" / "utils" / "pyproject.toml").read_text()
        assert 'name = "vizier-utils"' in toml
        assert "vizier-engine" not in toml

    def test_additional_app_gets_correct_name(self, tmp_path: Path) -> None:
        root = _create_mock_project(tmp_path, "vizier", "vizier")
        rename_packages(root, "vizier", ["engine", "daemon", "worker"])

        toml = (root / "apps" / "worker" / "pyproject.toml").read_text()
        assert 'name = "vizier-worker"' in toml
        assert "vizier-daemon" not in toml

    def test_additional_packages_have_tests_dir(self, tmp_path: Path) -> None:
        root = _create_mock_project(tmp_path, "vizier", "vizier")
        rename_packages(root, "vizier", ["engine", "lib:utils", "daemon", "worker"])

        assert (root / "libs" / "utils" / "tests" / "__init__.py").exists()
        assert (root / "apps" / "worker" / "tests" / "__init__.py").exists()


class TestDefaultPackageNames:
    """When package names match defaults ("core", "server"), no renames should occur."""

    def test_default_names_cause_no_changes(self, tmp_path: Path) -> None:
        root = _create_mock_project(tmp_path, "vizier", "vizier")
        actions = rename_packages(root, "vizier", ["core", "server"])

        assert len(actions) == 0
        assert (root / "libs" / "core" / "pyproject.toml").exists()
        assert (root / "apps" / "server" / "pyproject.toml").exists()


class TestRootBuildSystem:
    """Bug 3: Root pyproject.toml must NOT have a [build-system] section."""

    def test_root_pyproject_has_no_build_system(self) -> None:
        root_toml = Path(__file__).parent.parent / "pyproject.toml"
        content = root_toml.read_text()
        assert "[build-system]" not in content


class TestTemplateTestDirectories:
    """Bug 4: Template packages must include tests/ directories."""

    def test_server_has_tests_dir(self) -> None:
        tests_init = Path(__file__).parent.parent / "apps" / "server" / "tests" / "__init__.py"
        assert tests_init.exists()

    def test_core_has_tests_dir(self) -> None:
        tests_init = Path(__file__).parent.parent / "libs" / "core" / "tests" / "__init__.py"
        assert tests_init.exists()


class TestUvSyncCommand:
    """Bug 5: All uv sync commands must include --all-packages."""

    @pytest.fixture
    def all_text_files(self) -> list[Path]:
        """Collect all text files in the repo that might contain uv sync commands."""
        root = Path(__file__).parent.parent
        extensions = {".md", ".yml", ".yaml", ".py"}
        files = []
        skip = {".git", "__pycache__", ".venv", "venv", "node_modules", "uv.lock"}
        skip_files = {"PROPOSALS.md"}
        for path in root.rglob("*"):
            if any(s in path.parts for s in skip):
                continue
            if path.name in skip_files:
                continue
            if path.is_file() and path.suffix in extensions:
                files.append(path)
        return files

    def test_no_uv_sync_without_all_packages(self, all_text_files: list[Path]) -> None:
        violations = []
        for path in all_text_files:
            content = path.read_text(encoding="utf-8")
            for i, line in enumerate(content.splitlines(), 1):
                if "uv sync" in line and "--group dev" in line and "--all-packages" not in line:
                    violations.append(f"{path.relative_to(Path(__file__).parent.parent)}:{i}: {line.strip()}")
        assert not violations, "Found uv sync --group dev without --all-packages:\n" + "\n".join(violations)
