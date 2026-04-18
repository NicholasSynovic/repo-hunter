# AGENTS.md
Guidance for coding agents operating in this repository.

## 1) Scope and precedence
- Applies repository-wide unless a deeper AGENTS.md exists.
- User instructions override this file.
- Future Cursor/Copilot rule files are higher-priority repo constraints.

## 2) Project snapshot
- Repository: `repo-hunter`
- Python package: `joss`
- CLI entrypoint command: `rh`
- Python requirement: `~=3.13`
- Build backend: `hatchling`
- Development/build toolchain: `uv`, `pre-commit`, `make`
- Architecture pattern: ETL (`extract -> transform -> load`)

Key paths:
- `joss/main.py` (top-level CLI dispatch)
- `joss/cli.py` (argument parsing and shared options)
- `joss/db.py` (SQLite schema bootstrap)
- `joss/joss/` (JOSS pipeline)
- `joss/ecosystems/papers/` (Papers pipeline)
- `joss/ecosystems/awesome/` (Awesome pipeline)
- `analysis/`, `scripts/` (support scripts)

## 3) Environment setup
Preferred setup:
`make create-dev`

`make create-dev` runs:
- `pre-commit install`
- `pre-commit autoupdate`
- `uv sync`
- `uv build`

Minimal setup:
- `uv sync`
- `pre-commit install`

Required runtime variable for GitHub-backed ingestion:
- `GITHUB_TOKEN`
- Example: `export GITHUB_TOKEN="ghp_your_token_here"`

## 4) Build commands
Preferred build command:
- `make build`

Direct build alternative:
- `uv build`

Build notes:
- `make build` sets version from latest git tag.
- Artifacts are written to `dist/`.
- `make build` installs `dist/*.tar.gz` locally via `uv pip install`.

## 5) Lint, format, and security commands
Primary full check:
- `pre-commit run --all-files`

Targeted file check:
- `pre-commit run --files <file1> <file2>`

Direct tool commands:
- `uv run ruff check .`
- `uv run ruff format .`
- `uv run isort .`
- `uv run bandit -r joss analysis scripts`

## 6) Test commands (including single test)
Current repo state:
- No committed `tests/` directory.
- No committed pytest config.

When tests exist, use these patterns:
- Full suite: `uv run pytest`
- Single file: `uv run pytest tests/path/test_module.py`
- Single test: `uv run pytest tests/path/test_module.py::test_name`
- Single parametrized case: `uv run pytest tests/path/test_module.py::test_name[param_case]`
- Name-filtered subset: `uv run pytest -k "keyword"`

Current runtime smoke checks:
- `rh --help`
- `rh joss --out-file /tmp/joss.db`
- `rh papers --out-file /tmp/papers.db --email you@example.com`
- `rh awesome --out-file /tmp/awesome.db --email you@example.com`

## 7) Code style guidelines
Formatting:
- Follow `.editorconfig`: LF, final newline, trim trailing whitespace.
- Python indentation: 4 spaces.
- Keep line length near 88 (`ruff.toml`).
- Use double quotes for Python strings.

Imports:
- Keep imports at module top unless lazy import is required.
- Sort/group imports with isort (`black` profile).
- Prefer explicit imports and remove unused imports.
- Do not use wildcard imports.

Types:
- Type-annotate function signatures.
- Prefer built-in generics (`list[str]`, `dict[str, Any]`).
- Prefer `X | None` syntax for optional values.
- Keep explicit return types on public APIs.

Naming:
- Functions/variables/modules: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Internal helpers: `_leading_underscore`
- Preserve ETL phase naming (`extract`, `transform`, `load`, `runner`).

Docstrings/comments:
- Use concise docstrings for public modules/classes/functions.
- Prefer clear code over verbose comments.
- Add comments only for non-obvious logic.

Error handling:
- Validate required args/env vars early.
- Raise specific exceptions with actionable messages.
- Avoid bare `except:` and broad swallowing.
- Log context before fallback/skip behavior.
- Fail fast on invalid configuration or input.

Logging:
- Prefer logger usage over `print` in `joss/` package code.
- Include context (IDs, URLs, counts, page numbers).
- Use levels consistently: `debug`, `info`, `warning`, `error`.

Data and DB consistency:
- Preserve schema intent in `joss/db.py` unless migration is intentional.
- Keep transform outputs aligned with loaders and table expectations.
- Preserve deterministic identifiers/mappings where established.

## 8) Agent working agreement
- Keep diffs focused and minimal.
- Preserve behavior unless the task explicitly requires change.
- Run relevant checks before finalizing; prefer `pre-commit` as final gate.
- If adding tests, cover happy path and failure path.
- Avoid adding new tooling without clear repository-wide benefit.

## 9) Cursor and Copilot rule files
Checked in this repository at authoring time:
- `.cursor/rules/`: not present
- `.cursorrules`: not present
- `.github/copilot-instructions.md`: not present

If these files are added later, update this AGENTS.md and follow them as
higher-priority repository instructions.
