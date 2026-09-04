# AGENTS.md — repo-hunter

This file compiles high-signal guidance for future OpenCode sessions working in this repository. Every line below is something an agent would likely miss or get wrong without prior context.

## CLI entrypoint and subcommands

- The CLI entrypoint is `rh`. Top-level help: `rh --help`.
- Four dataset subcommands: `rh joss`, `rh papers`, `rh awesome`, `rh gh`.
- Every subcommand requires `--out-file` (SQLite db path).
- `rh papers` and `rh awesome` additionally require `--email` (sent as API `mailto` parameter).
- `rh gh` accepts optional numeric filters: `--star-count`, `--fork-count`, `--watcher-count`, `--issue-count`, `--age-months`, `--pr-count`. Use value `-1` to disable a filter; the CLI normalizes sentinel `-1` values to `None` internally.

## Development setup

- Run `make create-dev` to install pre-commit, sync dependencies, and build the package.
- Or manually: `pre-commit install && pre-commit autoupdate && uv sync && uv build`.
- Python `~=3.13` is required.
- `GITHUB_TOKEN` must be set as a classic GitHub PAT with upstream GitHub access before running any command that queries GitHub data.

## Build

- `make build` — builds and installs the package locally (also updates version from latest git tag).
- `uv build` + `uv pip install dist/*.tar.gz` is the direct equivalent.
- Build artifacts go into `dist/`.

## Quality checks (lint / format / security)

- Run all: `pre-commit run --all-files`.
- Targeted: `uv run ruff check .`, `uv run ruff format .`, `uv run isort .`, `uv run bandit -r rh analysis scripts`.
- Pre-commit hooks (configured in `.pre-commit-config.yaml`) run on every commit and include: ruff-check, ruff-format, bandit, check-yaml, check-toml, trailing-whitespace, end-of-file-fixer, etc.

## Testing

- Tests live in `tests/` and use pytest.
- Run all: `uv run pytest`.
- Run a specific file: `uv run pytest tests/test_cli.py` or `uv run pytest tests/test_gh_api.py`.
- Test patterns from `tests/test_cli.py` cover: subcommand requirement, gh filter normalization, filter parsing rejection, and subcommand parsing.

## ETL pipeline (JOSS)

- JOSS data flow: `rh/joss/runner.py` orchestrates extract → transform → load.
- `download_data()` extracts raw GitHub issues via `GhApi`.
- `transform_data()` normalizes issues into `_joss_github_issues` and `_joss_paper_project_issue_mapping` tables.
- `load_data()` writes normalized data into the SQLite DB (via SQLAlchemy).
- `resolve_urls` flag (`--resolve-urls` on `rh joss`) controls whether JOSS paper URLs are resolved via HTTP redirect.

## Database schema (SQLite, SQLAlchemy)

- Tables created automatically: `_runs`, `_joss_snapshots`, `_ecosystems_projects`, `_ecosystems_mentions`.
- `_runs` tracks execution metadata (id, subparser, timestamps, status, resolve_urls, counts, error_message).
- `_joss_snapshots` stores fetched GitHub issue records.
- `_ecosystems_projects` and `_ecosystems_mentions` store Papers/Awesome API data.

## Key code conventions

- `-1` is the disabled-filter sentinel, defined as `CLI.DISABLED_FILTER` in `rh/cli.py:16`. It is normalized to `None` for GH filter args by `_normalize_gh_filter_args()`.
- All logger instances go through `rh.logger.JOSSLogger`. Logging is configured via `setup_file_logging(prefix)` which creates a `<prefix>_<timestamp>.log` file.
- `rh/utils.py` provides `get_timestamp()`, `iso_to_unix()`, `extract_timestamp_from_filename()`, and JSON I/O helpers.
- `rh/ecosystems/api/__init__.py` defines `HTTP_GET_TIMEOUT`, `HTTP_HEAD_TIMEOUT`, `HTTP_POST_TIMEOUT = 60`.
- Import structure: `rh/__init__.py` exports `APPLICATION_NAME = "rh"`. CLI entrypoint is mapped in `pyproject.toml` as `rh = "rh.main:main"`.

## Directory ownership

- `rh/main.py` — CLI dispatch and orchestration.
- `rh/cli.py` — argument parsing and normalization.
- `rh/joss/` — JOSS ETL pipeline (extract/transform/load runners).
- `rh/ecosystems/awesome/` — Ecosyste.ms Awesome extraction.
- `rh/ecosystems/papers/` — Ecosyste.ms Papers extraction (full ETL).
- `rh/gh/` — GitHub GraphQL API wrapper.
- `tests/` — pytest test suite.
- `scripts/` — helper bash scripts.
