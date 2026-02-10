# Task Completion Protocol

When a task is completed, perform the following steps to ensure quality and adherence to project standards:

1.  **Format Code**: Run `uv run ruff format .` to ensure code style compliance.
2.  **Lint Code**: Run `uv run ruff check .` to catch potential issues.
3.  **Type Check**: Run `uv run pyright` to ensure strict type compliance.
4.  **Run Tests**: Run `uv run pytest` to ensure no regressions.
5.  **Git Status**: Check `git status` to verify changes.
