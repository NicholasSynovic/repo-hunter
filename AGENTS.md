# AGENTS.md

Guidance for coding agents working in this repository.

## Project Overview

- Repository name: `repo-hunter`
- Python package name: `joss`
- CLI command name: `rh`
- Python requirement: `~=3.13`
- Workflow style: CLI + ETL pipeline (`extract -> transform -> load`)
- Dependency/build tool: `uv`
- Main quality gate: `pre-commit`

Key config files:
- `pyproject.toml`
- `Makefile`
- `ruff.toml`
- `.pre-commit-config.yaml`
- `.editorconfig`
- `.isort.cfg`

## Repository Layout

- `joss/`: installable package and CLI implementation
  - `joss/main.py`: CLI entrypoint
  - `joss/cli.py`: argparse helpers and subcommands
  - `joss/db.py`: SQLite schema/bootstrap
  - `joss/joss/`: JOSS ingestion flow
  - `joss/ecosystems/`: `papers` and `awesome` flows
- `analysis/`: analysis scripts
- `scripts/`: utility scripts

## Setup and Environment

Preferred setup:
- `make create-dev`

`make create-dev` runs:
- `pre-commit install`
- `pre-commit autoupdate`
- `uv sync`
- `uv build`

Minimal setup:
- `uv sync`
- `pre-commit install`

Runtime variable:
- `GITHUB_TOKEN` is required for GitHub-backed ingestion.

Example:
- `export GITHUB_TOKEN="ghp_your_token"`

## Build Commands

Use one of:
- `make build` (preferred)
- `uv build` (direct)

Build notes:
- `make build` updates version from latest git tag.
- Artifacts are written to `dist/`.
- `make build` installs `dist/*.tar.gz` locally via `uv pip install`.

## Lint / Format / Security Commands

Primary command:
- `pre-commit run --all-files`

Targeted commands:
- `uv run ruff check .`
- `uv run ruff format .`
- `uv run isort .`
- `uv run bandit -r joss analysis scripts`

When only a few files changed:
- `pre-commit run --files <file1> <file2>`

## Test Commands

Current status:
- No `tests/` directory is committed right now.
- No canonical pytest config/suite is present.

When tests are added, use these exact patterns:
- Full suite: `uv run pytest`
- Single file: `uv run pytest tests/path/test_module.py`
- Single test: `uv run pytest tests/path/test_module.py::test_name`
- Single parametrized case: `uv run pytest tests/path/test_module.py::test_name[param]`

Practical runtime verification commands today:
- `rh --help`
- `rh joss --out-file /tmp/joss.db`
- `rh papers --out-file /tmp/papers.db --email you@example.com`
- `rh awesome --out-file /tmp/awesome.db --email you@example.com`

## Code Style Guidelines

### Typing and Python

- Use Python 3.13-compatible language features.
- Prefer built-in generics (`list[str]`, `dict[str, Any]`) and `X | None`.
- Add type hints to all function signatures.
- Prefer explicit return annotations on public functions/methods.
- Use existing Pydantic models for normalized ETL records.

### Formatting and Whitespace

- Python indentation: 4 spaces.
- Max line length: 88 (Ruff).
- Strings: double quotes.
- Remove trailing whitespace.
- Ensure final newline at EOF.

### Imports

- Keep imports at module top unless a deferred import is required.
- Keep imports sorted/grouped consistently with isort (black profile).
- Prefer explicit imports.
- Avoid wildcard imports.
- Remove unused imports.

### Naming

- Variables/functions/modules: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Internal helpers: leading underscore (`_helper`)
- Keep ETL stage naming explicit (`extract`, `transform`, `load`, `runner`).

### Docstrings and Comments

- Use concise docstrings for public APIs and non-obvious logic.
- Include `Args`/`Returns`/`Raises` where helpful.
- Keep comments minimal; prefer clear code.

### Error Handling

- Fail fast on missing config, args, and required inputs.
- Raise specific exceptions with actionable messages.
- Avoid bare `except:`.
- Catch concrete exception classes.
- Log context before fallback or skip behavior.
- Do not silently swallow parse/network/API failures.

### Logging

- Use logger instances in package code (avoid `print` in `joss/`).
- Include context (IDs, URLs, counts, page numbers) in log lines.
- Use levels consistently: `debug`, `info`, `warning`, `error`.

### Data and DB Consistency

- Preserve table names/schema intent in `joss/db.py`.
- Keep transformed output fields aligned with models/schema.
- Preserve deterministic IDs/mappings where present.

### CLI and UX

- Extend shared parser helpers in `joss/cli.py`.
- Keep help text short and task-focused.
- Validate required args/env vars early.

## Agent Working Agreement

- Make focused, minimal diffs.
- Preserve existing behavior unless the task explicitly changes it.
- Run relevant quality checks before finishing.
- Prefer `pre-commit` for final validation.
- If adding tests, include happy-path and failure-path coverage.
- Do not add new tooling without a clear repo-level benefit.

## Cursor / Copilot Rules

Checked in this repository:
- `.cursor/rules/`: not present
- `.cursorrules`: not present
- `.github/copilot-instructions.md`: not present

If these files are added later, treat them as higher-priority instructions and
update this AGENTS.md summary.
