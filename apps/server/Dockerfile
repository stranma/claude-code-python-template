FROM python:3.11-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workspace

# Copy workspace config and lock file
COPY pyproject.toml uv.lock /workspace/

# Copy package configs
COPY libs/core/pyproject.toml /workspace/libs/core/pyproject.toml
COPY apps/server/pyproject.toml /workspace/apps/server/pyproject.toml

# Install dependencies (without workspace packages)
RUN uv sync --frozen --no-install-workspace --package {{project_name}}-server

# Copy source code
COPY libs/ /workspace/libs/
COPY apps/server/ /workspace/apps/server/

# Install workspace packages
RUN uv sync --frozen --package {{project_name}}-server

# Run the server
CMD ["uv", "run", "python", "-m", "{{namespace}}.server"]
