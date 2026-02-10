# CLAUDE.md - Postgres MCP Pro

## Commands
- **Install**: `uv sync` or `uv pip install -e .`
- **Run (Dev)**: `just dev` or `uv run mcp dev -e . crystaldba/postgres_mcp/server.py`
- **Run (Prod)**: `uv run postgres-mcp`
- **Test**: `uv run pytest`
- **Test Single**: `uv run pytest tests/path/to/test.py`
- **Lint**: `uv run ruff check .`
- **Format**: `uv run ruff format .`
- **Type Check**: `uv run pyright`
- **Docker Build**: `docker build -t crystaldba/postgres-mcp .`

## Architecture
- **Type**: Python MCP Server for PostgreSQL (v3.12+)
- **Entry Point**: `src/postgres_mcp/server.py`
- **Key Directories**:
  - `src/postgres_mcp/database_health/`: Health check logic (vacuum, connections, cache)
  - `src/postgres_mcp/index/`: Index tuning algorithms (DTA implementation)
  - `src/postgres_mcp/sql/`: Safe SQL execution and parsing
  - `src/postgres_mcp/explain/`: Query plan analysis
- **Core Dependencies**: `mcp`, `psycopg` (Async), `pglast`, `humanize`, `instructor`
- **Extensions**: Requires `pg_stat_statements` and `hypopg` on target DB

## Code Style
- **Formatting**: strict `ruff` config (line-length 150, double quotes)
- **Typing**: Strict `pyright` compliance required
- **Async**: Use `async`/`await` patterns with `psycopg`
- **Safety**:
  - Never execute raw SQL without `SqlDriver` or `SafeSql` validation
  - Validate read-only mode for restricted environments
  - No `commit`/`rollback` in user queries (parsed via `pglast`)

## Git Workflow
- **Remotes**:
  - `origin`: Upstream repository (HTTPS, read-only).
  - `mine`: Personal fork (SSH, read-write).
- **Push Rule**: Always push changes to `mine` remote (`git push mine <branch>`).
- **Commits**: Conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- **Branch**: `main` is production.
