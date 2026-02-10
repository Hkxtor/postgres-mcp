# Coding Standards & Conventions

## Code Style
- **Formatter**: `ruff` with strict configuration.
    - Line length: 150
    - Quote style: Double quotes
- **Linter**: `ruff`
- **Typing**: Strict `pyright` compliance is required (`typeCheckingMode = "standard"` in `pyproject.toml`, effectively strict).
- **Async**: Use `async`/`await` patterns with `psycopg`.

## Safety & Security
- **SQL Execution**: Never execute raw SQL directly. Use `SqlDriver` or `SafeSql` validation.
- **Read-Only Mode**: Must be validated for restricted environments.
- **Transaction Safety**: No `COMMIT` or `ROLLBACK` allowed in user queries (parsed and rejected via `pglast`).

## Git Workflow
- **Remotes**:
    - `origin`: Upstream (read-only).
    - `mine`: Personal fork (read-write).
- **Pushing**: Always push to `mine` remote: `git push mine <branch>`.
- **Commits**: Follow Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`).
- **Main Branch**: `main` is production.
