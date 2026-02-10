# Suggested Commands

## Installation & Setup
- **Install Dependencies**: `uv sync` or `uv pip install -e .`
- **Build Docker**: `docker build -t crystaldba/postgres-mcp .`

## Development
- **Run (Dev)**: `just dev` or `uv run mcp dev -e . crystaldba/postgres_mcp/server.py`
- **Run (Prod)**: `uv run postgres-mcp`

## Testing & Quality Assurance
- **Run All Tests**: `uv run pytest`
- **Run Single Test**: `uv run pytest tests/path/to/test.py`
- **Lint Code**: `uv run ruff check .`
- **Format Code**: `uv run ruff format .`
- **Type Check**: `uv run pyright`

## System Utilities (Linux)
- **Git**: `git status`, `git pull`, `git push mine <branch>`
- **File Ops**: `ls`, `cd`, `grep`, `find`
