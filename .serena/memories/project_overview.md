# Project Overview: postgres-mcp

**Purpose**:
Postgres MCP Pro is a Model Context Protocol (MCP) server for PostgreSQL (v3.12+). It provides tools for database health checks, index tuning (using DTA algorithms), query plan analysis (EXPLAIN), and safe SQL execution. It supports both stdio and SSE transports.

**Architecture**:
- **Entry Point**: `src/postgres_mcp/server.py`
- **Core Dependencies**:
    - `mcp`: Model Context Protocol implementation.
    - `psycopg`: Async PostgreSQL driver.
    - `pglast`: SQL parsing for safety checks.
    - `humanize`: Human-readable formatting.
    - `instructor`: Structured output.
- **Extensions**: Relies on `pg_stat_statements` and `hypopg` on the target database for analysis.

**Key Directories**:
- `src/postgres_mcp/database_health/`: Logic for vacuum, connections, cache, sequence checks.
- `src/postgres_mcp/index/`: Index tuning algorithms.
- `src/postgres_mcp/sql/`: Safe SQL execution and parsing logic.
- `src/postgres_mcp/explain/`: Query plan analysis.

**Tech Stack**:
- Python >= 3.12
- `uv` for dependency management.
- `hatchling` for build backend.
- `docker` for containerized deployment.
