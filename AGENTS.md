# AGENTS.md

`rh` (Repo Hunter): Python CLI that builds local SQLite datasets from open-source ecosystems — JOSS reviews, Ecosyste.ms Papers/Awesome, GitHub repo search. Package lives in `rh/`; entry point is `rh = "rh.main:main"`.

## Commands

```bash
make create-dev                                # pre-commit install/autoupdate + uv sync (no build)
uv run pytest                                  # tests live in rh/tests/, not tests/
uv run pytest rh/tests/test_cli.py::test_name  # single test
pre-commit run --all-files                     # ruff check/format + bandit + prettier
make build                                     # version from latest git tag, wipes dist/, builds + installs sdist locally
uv run rh --help                               # run the CLI
```

## Gotchas

- **Lint only via pre-commit.** `uv run ruff`, `uv run bandit`, and `uv run isort` all fail — those tools are not installed in the project venv; pre-commit runs them in their own hook environments.
- **"JOSS" names are legacy, not bugs.** `JOSSRunner`, `JOSSLogger`, and `joss_logger=` kwargs appear in every dataset module (e.g. `rh/ecosystems/awesome/runner.py`) because the package was formerly named `joss`. Do not rename opportunistically.
- **Python version mismatch.** `pyproject.toml` declares `requires-python = "~=3.13"`, but the venv and pre-commit's `default_language_version` use Python 3.14.
- **pre-commit runs a system prettier hook** (`language: system`) over Markdown/JSON/YAML with 4-space indent and print width 80 — commits fail if prettier is not on PATH.
- **`GITHUB_TOKEN`** (classic PAT) is required for `rh joss` (ghapi reads it from the environment) and `rh gh` (`CLI.get_token` raises without it). `rh papers` and `rh awesome` do not need it.
- **`rh gh` persists nothing yet** — it executes the GitHub GraphQL search and logs the match count. Do not write tests or docs assuming database output.
- **Version is derived from git tags at build time.** `make build` runs `uv version $(git describe --tags --abbrev=0)`, so the version in `pyproject.toml` is transient; releases are tag-driven.
- **No CI and no typechecker.** Verification is pre-commit + pytest locally; do not invent `mypy`/typecheck steps or CI badges.
- **`analysis/` scripts use relative imports** — run them as `uv run python -m analysis.issues_per_year` (they read `data/derived/joss_submissions.json` and write PNGs to `data/plots/`).
