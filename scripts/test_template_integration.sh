#!/usr/bin/env bash
# Template integration test: apply setup_project.py with a given configuration
# and verify the resulting project builds, lints, type-checks, and passes tests.
#
# Usage:
#   scripts/test_template_integration.sh \
#     --source-dir /path/to/template \
#     --work-dir /tmp/test-project \
#     --project-type mono \
#     --packages "core,server" \
#     --services none

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
SOURCE_DIR=""
WORK_DIR=""
PROJECT_TYPE="mono"
PACKAGES="core,server"
SERVICES="none"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --source-dir)  SOURCE_DIR="$2";  shift 2 ;;
        --work-dir)    WORK_DIR="$2";    shift 2 ;;
        --project-type) PROJECT_TYPE="$2"; shift 2 ;;
        --packages)    PACKAGES="$2";    shift 2 ;;
        --services)    SERVICES="$2";    shift 2 ;;
        --help|-h)
            echo "Usage: $0 --source-dir DIR --work-dir DIR [--project-type mono|single] [--packages LIST] [--services none|postgres|postgres-redis|custom]"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

if [[ -z "$SOURCE_DIR" || -z "$WORK_DIR" ]]; then
    echo "ERROR: --source-dir and --work-dir are required" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
step_pass() { echo "  [PASS] $1"; }
step_fail() { echo "  [FAIL] $1" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
echo "=== Template Integration Test ==="
echo "  type=$PROJECT_TYPE  packages=$PACKAGES  services=$SERVICES"
echo "  source: $SOURCE_DIR"
echo "  work:   $WORK_DIR"
echo ""

# ---------------------------------------------------------------------------
# Step 1: Copy template to work directory
# ---------------------------------------------------------------------------
echo "Step 1: Copy template to work directory"
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

# Use rsync if available, otherwise fall back to cp + cleanup
if command -v rsync > /dev/null 2>&1; then
    rsync -a \
        --exclude='.git' \
        --exclude='.venv' \
        --exclude='__pycache__' \
        --exclude='.coverage' \
        --exclude='.ruff_cache' \
        --exclude='.pytest_cache' \
        --exclude='node_modules' \
        "$SOURCE_DIR/" "$WORK_DIR/"
else
    cp -a "$SOURCE_DIR/." "$WORK_DIR/"
    rm -rf "$WORK_DIR/.git" "$WORK_DIR/.venv" "$WORK_DIR/node_modules"
    find "$WORK_DIR" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
    find "$WORK_DIR" -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
    find "$WORK_DIR" -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
fi
step_pass "Copied template"

# ---------------------------------------------------------------------------
# Step 2: Apply template
# ---------------------------------------------------------------------------
echo "Step 2: Apply template (setup_project.py)"
python "$WORK_DIR/setup_project.py" \
    --name test-project \
    --namespace test_project \
    --description "CI integration test" \
    --author "CI Bot" \
    --email "ci@test.com" \
    --python-version 3.11 \
    --base-branch main \
    --type "$PROJECT_TYPE" \
    --packages "$PACKAGES" \
    --services "$SERVICES" \
    --keep-setup \
|| step_fail "setup_project.py exited with non-zero status"
step_pass "Template applied"

# ---------------------------------------------------------------------------
# Step 3: Verify no remaining placeholders
# ---------------------------------------------------------------------------
echo "Step 3: Check for remaining template placeholders"
cd "$WORK_DIR"

# Search for actual template placeholders (not GitHub Actions ${{ }} expressions).
# The pattern matches {{word}} but NOT ${{word}} (GHA syntax).
# Excludes setup_project.py (defines them) and test files (reference them in fixtures).
PLACEHOLDER_PATTERN='\{\{(project_name|namespace|description|author_name|author_email|python_version|base_branch|year)\}\}'
PLACEHOLDER_HITS=$(grep -rE "$PLACEHOLDER_PATTERN" \
    --include='*.py' --include='*.toml' --include='*.yml' --include='*.yaml' \
    --include='*.md' --include='*.json' --include='*.cfg' --include='*.ini' \
    --include='*.txt' --include='*.sh' \
    --exclude='setup_project.py' \
    --exclude='test_setup_project.py' \
    --exclude='test_template_integration.sh' \
    . 2>/dev/null || true)

if [[ -n "$PLACEHOLDER_HITS" ]]; then
    echo "$PLACEHOLDER_HITS"
    step_fail "Found remaining template placeholders"
fi
step_pass "No remaining placeholders"

# ---------------------------------------------------------------------------
# Step 4: Verify directory structure
# ---------------------------------------------------------------------------
echo "Step 4: Verify directory structure"
if [[ "$PROJECT_TYPE" == "single" ]]; then
    [[ -d "src/test_project" ]] || step_fail "src/test_project/ missing"
    [[ ! -d "libs" ]]          || step_fail "libs/ should not exist in single-package mode"
    [[ ! -d "apps" ]]          || step_fail "apps/ should not exist in single-package mode"
    step_pass "Single-package layout correct"
else
    [[ -d "libs" ]] || step_fail "libs/ missing"
    [[ -d "apps" ]] || step_fail "apps/ missing"
    step_pass "Monorepo layout correct"
fi

# ---------------------------------------------------------------------------
# Step 5: Install dependencies
# ---------------------------------------------------------------------------
echo "Step 5: Install dependencies (uv sync)"
if [[ "$PROJECT_TYPE" == "single" ]]; then
    uv sync --group dev || step_fail "uv sync failed"
else
    uv sync --all-packages --group dev || step_fail "uv sync failed"
fi
step_pass "Dependencies installed"

# ---------------------------------------------------------------------------
# Step 6: Lint
# ---------------------------------------------------------------------------
echo "Step 6: Lint (ruff)"
uv run ruff check . || step_fail "ruff check failed"
uv run ruff format --check . || step_fail "ruff format check failed"
step_pass "Lint passed"

# ---------------------------------------------------------------------------
# Step 7: Type check
# ---------------------------------------------------------------------------
echo "Step 7: Type check (pyright)"
uv run pyright || step_fail "pyright failed"
step_pass "Type check passed"

# ---------------------------------------------------------------------------
# Step 8: Run tests (pytest)
# ---------------------------------------------------------------------------
echo "Step 8: Run tests (pytest)"
# Run package tests only (not root tests/ which contains template meta-tests
# already covered by the unit-tests CI job).
if [[ "$PROJECT_TYPE" == "single" ]]; then
    uv run pytest tests/ -v --tb=short --ignore=tests/test_setup_project.py \
        || step_fail "pytest failed"
else
    uv run pytest libs/ apps/ tests/ -v --tb=short --ignore=tests/test_setup_project.py \
        || step_fail "pytest failed"
fi
step_pass "Tests passed"

# ---------------------------------------------------------------------------
# Step 9: Verify services (if applicable)
# ---------------------------------------------------------------------------
if [[ "$SERVICES" != "none" ]]; then
    echo "Step 9: Verify docker-compose.yml"
    [[ -f ".devcontainer/docker-compose.yml" ]] \
        || step_fail ".devcontainer/docker-compose.yml missing"
    # Basic validation: check for 'services:' key
    grep -q 'services:' ".devcontainer/docker-compose.yml" \
        || step_fail "docker-compose.yml missing 'services:' key"
    step_pass "docker-compose.yml present and valid"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "=== All checks passed ==="
