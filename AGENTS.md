# AGENTS.md

`rh` (Repo Hunter): Python CLI that builds local SQLite datasets from open-source ecosystems — JOSS reviews, Ecosyste.ms Papers/Awesome, GitHub repo search. Pipelines live in `rh/ecosystems/{awesome,papers}/` and `rh/joss/` (each an extract→transform→load runner), GitHub search in `rh/gh/api.py`; `rh/main.py` wires the subcommands. Working entry point is `rh = "rh.main:main"` (distribution name in pyproject is still `joss`).

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

- **Broken commands.** `rh joss` crashes at import (`rh/joss/extract.py` needs `ghapi`/`fastcore`/`progress`, none declared in pyproject). The `joss` console script also fails: `joss.main` defines no `main()` despite the `joss.main:main` entry point. Top-level `joss/` is an in-progress requests-based rewrite of the JOSS pipeline; empty root dirs `awesome/`, `gh/`, `papers/` are untracked placeholders.
- **`rh gh` persists nothing yet** — it executes the GitHub GraphQL search and logs the match count. Do not write tests or docs assuming database output.
- **`GITHUB_TOKEN`** (classic PAT) is required for `rh gh` (`CLI.get_token` raises `RuntimeError` without it). `rh papers` and `rh awesome` need no token.
- **Lint only via pre-commit.** `uv run ruff`, `uv run bandit`, and `uv run isort` all fail — those tools are not installed in the project venv; pre-commit runs them in their own hook environments.
- **pre-commit runs a system prettier hook** (`language: system`) over Markdown/JSON/YAML with 4-space indent, LF endings, and print width 80 — commits fail if prettier is not on PATH.
- **"JOSS" names are legacy, not bugs.** `JOSSRunner`, `JOSSLogger`, and `joss_logger=` kwargs appear throughout `rh/` (e.g. `rh/ecosystems/awesome/runner.py`) because the package was formerly named `joss`. Do not rename opportunistically.
- **Python version mismatch.** `pyproject.toml` declares `requires-python = "~=3.13"`, but the venv and pre-commit's `default_language_version` use Python 3.14.
- **Version is derived from git tags at build time.** `make build` runs `uv version $(git describe --tags --abbrev=0)`, so the version in `pyproject.toml` is transient; releases are tag-driven.
- **No CI and no typechecker.** Verification is pre-commit + pytest locally; do not invent `mypy`/typecheck steps or CI badges.
- **Tests are offline.** `rh/tests/` uses fakes only — no network, no `GITHUB_TOKEN`. Keep new tests that way.
- **Style.** Public functions carry numpy-style docstrings (Parameters/Returns/Raises); ruff line length 88. README's "Project structure" section is stale — `analysis/` and `scripts/` no longer exist.
