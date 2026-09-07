# AGENTS.md

`rh` (Repo Hunter): Python CLI that builds local SQLite datasets from open-source ecosystems — JOSS reviews, Ecosyste.ms Papers/Awesome, GitHub repo search. Two parallel codebases: legacy `rh/` (extract→transform→load runners in `rh/ecosystems/{awesome,papers}/` and `rh/joss/`, wired by `rh/main.py`, plus shared `rh/{cli,db,logger,parsers,interfaces,utils}.py`) and a requests-based rewrite in top-level `joss/` (`joss/main.py` wires `joss/etl/{extract,transform,load}.py` end-to-end, writing tables `joss_github_issues` and `joss_paper_project_issues`; pydantic models + ETL interfaces live in `joss/etl/__init__.py`). pyproject distribution name is `joss`, not `rh`.

## Commands

```bash
make create-dev                                # pre-commit install/autoupdate + uv sync
uv run pytest                                  # tests live in rh/tests/, not tests/
uv run pytest rh/tests/test_cli.py::test_name  # single test
pre-commit run --all-files                     # ruff check/format + bandit + prettier
uv run python -m joss.main -o /tmp/joss.db     # run the rewrite: real network ETL, needs GITHUB_TOKEN, -o path must not exist
make build                                     # version from latest git tag, wipes dist/, builds + installs sdist locally
```

**No console script works.** `uv run rh` (any subcommand, even `--help`), `uv run python -m rh.main`, and `uv run joss` all crash at import; the only runnable pipeline is `uv run python -m joss.main` (with `--help` it just prints usage). See first gotcha.

## Gotchas

- **Legacy `rh/` CLI cannot run at all.** `rh/main.py` imports every runner at module top, and runners import undeclared packages: `progress` (`rh/ecosystems/*/extract.py`, `transform.py`, `load.py`, `rh/joss/*`) plus `ghapi`/`fastcore` (`rh/joss/extract.py`). None are in pyproject, so all `rh` subcommands die with `ModuleNotFoundError: progress` before argparse runs. To exercise the legacy CLI you must add those deps; to test argument parsing, import `rh.cli.CLI` directly (as the tests do).
- **`joss/db.py` refuses existing outputs.** The DB constructor `sys.exit(1)`s when the `-o` path already exists, and load writes via pandas `to_sql` with `if_exists="delete_rows"` — reruns need a fresh path.
- **`joss/joss.sqlite3` (73 MB) is a gitignored local artifact** (`*.sqlite3` rule) from a rewrite test run, sitting inside the `joss/` package dir — `uv build` bundles it into the sdist (~76 MB tar.gz). Delete or move it before building releases.
- **`rh gh` persists nothing yet** — it executes the GitHub GraphQL search and logs the match count. Do not write tests or docs assuming database output.
- **`GITHUB_TOKEN`** (classic PAT) is required for `rh gh` (`CLI.get_token` in `rh/cli.py` raises `RuntimeError` without it) and for the `joss` rewrite (`-g` flag or env var; argparse makes `-g` required when the env var is unset). `rh papers` and `rh awesome` need no token.
- **Lint only via pre-commit.** `uv run ruff` and `uv run bandit` fail — those tools are not installed in the project venv; pre-commit runs them in their own hook environments.
- **pre-commit runs a system prettier hook** (`language: system`) over Markdown/JSON/YAML with 4-space indent, LF endings, and print width 80 — commits fail if prettier is not on PATH.
- **"JOSS" names are legacy, not bugs.** `JOSSRunner`, `JOSSLogger`, and `joss_logger=` kwargs appear throughout `rh/` (e.g. `rh/ecosystems/awesome/runner.py`) because the package was formerly named `joss`. Do not rename opportunistically; the `joss/` rewrite uses plain `Extract`/`Transform`/`Load` names instead.
- **Python version mismatch.** `pyproject.toml` declares `requires-python = "~=3.13"`, but the venv and pre-commit's `default_language_version` use Python 3.14; uv also prints a tilde-specifier ambiguity warning on every run.
- **Version is derived from git tags at build time.** `make build` runs `uv version $(git describe --tags --abbrev=0)`, so the version in `pyproject.toml` is transient; releases are tag-driven.
- **No CI and no typechecker.** Verification is pre-commit + pytest locally; do not invent `mypy`/typecheck steps or CI badges.
- **Tests are offline.** `rh/tests/` (`test_cli.py`, `test_gh_api.py`) uses fakes only — no network, no `GITHUB_TOKEN`. Keep new tests that way.
- **Style.** `rh/` public functions carry numpy-style docstrings (Parameters/Returns/Raises); the `joss/` rewrite deliberately uses `#` comments and no docstrings — match the file you are editing. ruff line length 88. Empty root dirs `awesome/`, `gh/`, `papers/` are untracked placeholders. README's "Project structure" section is stale (`analysis/` and `scripts/` no longer exist) and its `rh` usage examples don't run — see gotchas above.
