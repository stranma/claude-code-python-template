#!/usr/bin/env python3
"""Post-clone setup script for the Claude Code Python Template.

Replaces placeholders in all template files with user-provided values.
Supports both interactive mode (for humans) and CLI mode (for Claude agents).

Usage:
    Interactive:  python setup_project.py
    CLI:          python setup_project.py --name my-project --namespace my_project
    Monorepo:     python setup_project.py --name my-project --namespace my_project --type mono --packages "api,core,client"
    Single:       python setup_project.py --name my-project --namespace my_project --type single
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent

PLACEHOLDERS = {
    "{{project_name}}": "",
    "{{namespace}}": "",
    "{{description}}": "",
    "{{author_name}}": "",
    "{{author_email}}": "",
    "{{python_version}}": "",
    "{{base_branch}}": "",
    "{{year}}": "",
}

# Files to process for placeholder substitution
TEXT_EXTENSIONS = {
    ".py",
    ".toml",
    ".yml",
    ".yaml",
    ".md",
    ".json",
    ".cfg",
    ".ini",
    ".txt",
    ".dockerfile",
    ".dockerignore",
    ".gitignore",
    "",
}

# Files/dirs to skip
SKIP_PATHS = {".git", "__pycache__", ".venv", "venv", "node_modules", "uv.lock"}


def is_text_file(path: Path) -> bool:
    """Check if a file should be processed for placeholder substitution."""
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {
        "Dockerfile",
        "Makefile",
        "LICENSE",
        ".gitignore",
        ".dockerignore",
    }


def replace_in_file(filepath: Path, replacements: dict[str, str]) -> bool:
    """Replace placeholders in a single file. Returns True if changes were made."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return False

    original = content
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False


def rename_namespace_dirs(root: Path, namespace: str) -> list[str]:
    """Rename {{namespace}} directories to the actual namespace value."""
    renamed = []
    # Walk bottom-up so child renames happen before parent
    for dirpath, dirnames, _filenames in os.walk(root, topdown=False):
        for dirname in dirnames:
            if dirname == "{{namespace}}":
                old_path = Path(dirpath) / dirname
                new_path = Path(dirpath) / namespace
                if old_path.exists():
                    shutil.move(str(old_path), str(new_path))
                    renamed.append(f"  {old_path} -> {new_path}")
    return renamed


def flatten_to_single_package(root: Path, namespace: str) -> list[str]:
    """Convert monorepo layout to single-package layout.

    Moves libs/core/ content to src/{{namespace}}/ and removes apps/libs structure.
    """
    actions = []
    src_dir = root / "src" / namespace
    src_dir.mkdir(parents=True, exist_ok=True)

    # Move core library code to src/
    core_pkg = root / "libs" / "core" / namespace / "core"
    if core_pkg.exists():
        for item in core_pkg.iterdir():
            dest = src_dir / item.name
            shutil.move(str(item), str(dest))
            actions.append(f"  Moved {item} -> {dest}")

    # Copy core init to src namespace init
    core_init = root / "libs" / "core" / namespace
    if core_init.exists():
        init_file = core_init / "__init__.py"
        if init_file.exists():
            shutil.copy2(str(init_file), str(src_dir / "__init__.py"))

    # Remove monorepo dirs
    for d in ["apps", "libs"]:
        target = root / d
        if target.exists():
            shutil.rmtree(str(target))
            actions.append(f"  Removed {d}/")

    # Update root pyproject.toml - remove workspace config
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        # Remove workspace section
        content = re.sub(
            r"\[tool\.uv\.workspace\]\nmembers = \[.*?\]\n*",
            "",
            content,
            flags=re.DOTALL,
        )
        # Update hatch build to point to src/
        if "[tool.hatch.build.targets.wheel]" not in content:
            content += '\n[tool.hatch.build.targets.wheel]\npackages = ["src/' + namespace + '"]\n'
        pyproject.write_text(content, encoding="utf-8")
        actions.append("  Updated pyproject.toml (removed workspace, added src build)")

    # Update CI workflow - remove per-package test jobs
    tests_yml = root / ".github" / "workflows" / "tests.yml"
    if tests_yml.exists():
        content = tests_yml.read_text(encoding="utf-8")
        # Simplify to single test job
        content = re.sub(
            r"  test-core:.*?(?=  typecheck:)",
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    needs: lint\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: astral-sh/setup-uv@v5\n"
            "        with:\n"
            '          version: ">=0.5.0"\n'
            "      - uses: actions/setup-python@v5\n"
            "        with:\n"
            '          python-version: "3.11"\n'
            "      - name: Install dependencies\n"
            "        run: uv sync --group dev\n"
            "      - name: Run tests\n"
            "        run: uv run pytest -v --tb=short\n\n",
            content,
            flags=re.DOTALL,
        )
        # Remove server test job
        content = re.sub(r"  test-server:.*?(?=  typecheck:)", "", content, flags=re.DOTALL)
        tests_yml.write_text(content, encoding="utf-8")
        actions.append("  Simplified tests.yml for single-package layout")

    # Remove Dockerfile (monorepo-specific)
    dockerfile = root / "apps" / "server" / "Dockerfile"
    if dockerfile.exists():
        dockerfile.unlink()

    actions.append("  Single-package layout complete: src/" + namespace + "/")
    return actions


def rename_packages(root: Path, namespace: str, packages: list[str]) -> list[str]:
    """Rename example packages (core, server) to user-specified names."""
    actions = []

    # Map default packages to user packages
    default_libs = ["core"]
    default_apps = ["server"]
    user_libs = []
    user_apps = []

    # Simple heuristic: first package is a lib, rest are apps
    # Or user can specify with lib: and app: prefixes
    for pkg in packages:
        pkg = pkg.strip()
        if pkg.startswith("lib:"):
            user_libs.append(pkg[4:])
        elif pkg.startswith("app:"):
            user_apps.append(pkg[4:])
        else:
            # Default: first goes to libs, rest to apps
            if not user_libs:
                user_libs.append(pkg)
            else:
                user_apps.append(pkg)

    # Rename lib packages
    for old, new in zip(default_libs, user_libs, strict=False):
        old_path = root / "libs" / old
        new_path = root / "libs" / new
        if old_path.exists() and old != new:
            shutil.move(str(old_path), str(new_path))
            # Rename inner namespace dir
            old_inner = new_path / namespace / old
            new_inner = new_path / namespace / new
            if old_inner.exists():
                shutil.move(str(old_inner), str(new_inner))
            actions.append(f"  libs/{old} -> libs/{new}")

    # Rename app packages
    for old, new in zip(default_apps, user_apps, strict=False):
        old_path = root / "apps" / old
        new_path = root / "apps" / new
        if old_path.exists() and old != new:
            shutil.move(str(old_path), str(new_path))
            old_inner = new_path / namespace / old
            new_inner = new_path / namespace / new
            if old_inner.exists():
                shutil.move(str(old_inner), str(new_inner))
            actions.append(f"  apps/{old} -> apps/{new}")

    # Create additional packages if more than defaults
    for lib in user_libs[len(default_libs) :]:
        lib_path = root / "libs" / lib
        pkg_path = lib_path / namespace / lib
        pkg_path.mkdir(parents=True, exist_ok=True)
        (pkg_path / "__init__.py").write_text(f'"""{lib} library."""\n\n__version__ = "0.1.0"\n')
        # Create pyproject.toml from core template
        core_toml = root / "libs" / (user_libs[0] if user_libs else "core") / "pyproject.toml"
        if core_toml.exists():
            content = core_toml.read_text(encoding="utf-8")
            content = content.replace(user_libs[0], lib)
            (lib_path / "pyproject.toml").write_text(content, encoding="utf-8")
        actions.append(f"  Created libs/{lib}/")

    for app in user_apps[len(default_apps) :]:
        app_path = root / "apps" / app
        pkg_path = app_path / namespace / app
        pkg_path.mkdir(parents=True, exist_ok=True)
        (pkg_path / "__init__.py").write_text(f'"""{app} application."""\n\n__version__ = "0.1.0"\n')
        # Create pyproject.toml from server template
        first_app = user_apps[0] if user_apps else "server"
        server_toml = root / "apps" / first_app / "pyproject.toml"
        if server_toml.exists():
            content = server_toml.read_text(encoding="utf-8")
            content = content.replace(first_app, app)
            (app_path / "pyproject.toml").write_text(content, encoding="utf-8")
        actions.append(f"  Created apps/{app}/")

    return actions


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"{prompt}: ").strip()


def interactive_setup() -> dict[str, str]:
    """Collect configuration interactively."""
    print("\n=== Claude Code Python Template Setup ===\n")

    config = {}
    config["project_name"] = get_input("Project name (e.g., my-project)")
    config["namespace"] = get_input(
        "Python namespace (e.g., my_project)",
        config["project_name"].replace("-", "_"),
    )
    config["description"] = get_input("Short description", "A Python project")
    config["author_name"] = get_input("Author name")
    config["author_email"] = get_input("Author email")
    config["python_version"] = get_input("Python version", "3.11")
    config["base_branch"] = get_input("Base branch name", "main")

    print("\nProject type:")
    print("  1. Monorepo (apps/ + libs/ with uv workspaces)")
    print("  2. Single package (src/ layout)")
    choice = get_input("Choose [1/2]", "1")
    config["type"] = "single" if choice == "2" else "mono"

    if config["type"] == "mono":
        packages = get_input(
            "Package names (comma-separated, prefix with lib: or app:)",
            "core,server",
        )
        config["packages"] = packages

    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup Claude Code Python Template")
    parser.add_argument("--name", help="Project name (e.g., my-project)")
    parser.add_argument("--namespace", help="Python namespace (e.g., my_project)")
    parser.add_argument("--description", default="A Python project", help="Short description")
    parser.add_argument("--author", default="", help="Author name")
    parser.add_argument("--email", default="", help="Author email")
    parser.add_argument("--python-version", default="3.11", help="Python version (default: 3.11)")
    parser.add_argument("--base-branch", default="main", help="Base branch (default: main)")
    parser.add_argument("--type", choices=["mono", "single"], default="mono", help="Project type")
    parser.add_argument("--packages", default="core,server", help="Package names (comma-separated)")
    parser.add_argument("--git-init", action="store_true", help="Initialize git and make initial commit")
    parser.add_argument("--keep-setup", action="store_true", help="Don't delete this setup script after running")

    args = parser.parse_args()

    # Interactive mode if no name provided
    if not args.name:
        config = interactive_setup()
    else:
        config = {
            "project_name": args.name,
            "namespace": args.namespace or args.name.replace("-", "_"),
            "description": args.description,
            "author_name": args.author,
            "author_email": args.email,
            "python_version": args.python_version,
            "base_branch": args.base_branch,
            "type": args.type,
            "packages": args.packages,
        }

    # Validate required fields
    if not config.get("project_name"):
        print("Error: Project name is required.")
        sys.exit(1)

    # Build replacements
    replacements = {
        "{{project_name}}": config["project_name"],
        "{{namespace}}": config.get("namespace", config["project_name"].replace("-", "_")),
        "{{description}}": config.get("description", "A Python project"),
        "{{author_name}}": config.get("author_name", ""),
        "{{author_email}}": config.get("author_email", ""),
        "{{python_version}}": config.get("python_version", "3.11"),
        "{{base_branch}}": config.get("base_branch", "main"),
        "{{year}}": str(datetime.now().year),
    }
    namespace = replacements["{{namespace}}"]

    print(f"\nSetting up project: {config['project_name']}")
    print(f"  Namespace: {namespace}")
    print(f"  Type: {config.get('type', 'mono')}")
    print(f"  Base branch: {config.get('base_branch', 'main')}")

    # Step 1: Rename {{namespace}} directories
    print("\nRenaming namespace directories...")
    renamed = rename_namespace_dirs(TEMPLATE_DIR, namespace)
    for r in renamed:
        print(r)

    # Step 2: Replace placeholders in all text files
    print("\nReplacing placeholders...")
    changed_count = 0
    for dirpath, dirnames, filenames in os.walk(TEMPLATE_DIR):
        # Skip hidden/build dirs
        dirnames[:] = [d for d in dirnames if d not in SKIP_PATHS]
        for filename in filenames:
            filepath = Path(dirpath) / filename
            if is_text_file(filepath) and replace_in_file(filepath, replacements):
                changed_count += 1
    print(f"  Updated {changed_count} files")

    # Step 3: Handle project type
    if config.get("type") == "single":
        print("\nConverting to single-package layout...")
        actions = flatten_to_single_package(TEMPLATE_DIR, namespace)
        for a in actions:
            print(a)
    elif config.get("packages") and config["packages"] != "core,server":
        print("\nRenaming packages...")
        packages = [p.strip() for p in config["packages"].split(",")]
        actions = rename_packages(TEMPLATE_DIR, namespace, packages)
        for a in actions:
            print(a)

    # Step 4: Update CLAUDE.md package table
    claude_md = TEMPLATE_DIR / "CLAUDE.md"
    if claude_md.exists() and config.get("type") == "mono":
        content = claude_md.read_text(encoding="utf-8")
        packages = [p.strip() for p in config.get("packages", "core,server").split(",")]
        table_lines = []
        for pkg in packages:
            pkg_clean = pkg.replace("lib:", "").replace("app:", "")
            if pkg.startswith("lib:") or pkg == packages[0]:
                table_lines.append(f"| **{pkg_clean}** | `libs/{pkg_clean}/` | {pkg_clean.title()} library |")
            else:
                table_lines.append(f"| **{pkg_clean}** | `apps/{pkg_clean}/` | {pkg_clean.title()} application |")
        table_str = "\n".join(table_lines)
        content = re.sub(
            r"\| \*\*core\*\*.*?\| \*\*server\*\*.*?\|",
            table_str,
            content,
            flags=re.DOTALL,
        )
        claude_md.write_text(content, encoding="utf-8")

    # Step 5: Git init if requested
    if getattr(args, "git_init", False):
        print("\nInitializing git repository...")
        os.system("git init")
        os.system("git add -A")
        os.system('git commit -m "Initial project setup from Claude Code Python Template"')
        print("  Git repository initialized with initial commit")

    # Step 6: Self-delete unless --keep-setup
    if not getattr(args, "keep_setup", False):
        print(f"\nRemoving setup script ({Path(__file__).name})...")
        print("  Run: rm setup_project.py")

    print("\n=== Setup complete! ===")
    print("\nNext steps:")
    print(f"  1. cd {TEMPLATE_DIR}")
    print("  2. uv sync --group dev")
    print("  3. uv run pytest")
    print("  4. Start coding!")


if __name__ == "__main__":
    main()
