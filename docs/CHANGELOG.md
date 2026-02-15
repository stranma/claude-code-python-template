# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Template packages now include tests/ directories so pytest discovers package tests immediately after setup
- Phase Completion Checklist now includes Step -1 requiring feature branch creation before starting work
- Added settings.json to enable uv run execution in Claude Code server environment

### Changed

- All documentation and CI workflows now use `uv sync --all-packages --group dev` to correctly install all workspace members

- Default base branch from "main" to "master" -- new projects created from this template will use "master" as the default branch name
- Claude Code permissions moved from settings.local.json to settings.json -- projects created from this template will automatically inherit tool permissions at the project level, reducing approval prompts

### Fixed

- Setup script now correctly renames package names inside pyproject.toml and __init__.py files when customizing packages beyond the defaults
- Additional packages created by setup script now get correct project-prefixed names instead of inheriting the template source package name (e.g., vizier-engine instead of vizier-core when adding engine package)
- Root pyproject.toml no longer includes a [build-system] section that caused hatchling build failures in workspace mode
