# AGENTS.md

`rh` (Repo Hunter): Python CLI that builds local SQLite datasets from open-source ecosystems — JOSS reviews, Ecosyste.ms Papers/Awesome, GitHub repo search. Legacy pipelines live in `rh/ecosystems/{awesome,papers}/` and `rh/joss/` (each an extract→transform→load runner), GitHub search in `rh/gh/api.py`; `rh/main.py` wires the subcommands. A parallel requests-based rewrite lives in top-level `joss/` (plain `Extract`/`Transform` classes wired in `joss/main.py`): extract and transform work, load is not wired yet. Working entry point is `rh = "rh.main:main"` (distribution name in pyproject is still `joss`).

## Commands

```bash
make create-dev                                # pre-commit install/autoupdate + uv sync (no build)
uv run pytest                                  # tests live in rh/tests/, not tests/
uv run pytest rh/tests/test_cli.py::test_name  # single test
pre-commit run --all-files                     # ruff check/format + bandit + prettier
make build                                     # version from latest git tag, wipes dist/, builds + installs sdist locally
uv run rh --help                               # run the legacy CLI
uv run python -m joss.main --help              # run the in-progress joss rewrite
```

## Gotchas

- **Broken commands.** `rh joss` crashes at import (`rh/joss/extract.py` needs `ghapi`/`fastcore`/`progress`, none declared in pyproject). The `joss` console script fails: `joss.main` defines no `main()` despite the `joss.main:main` entry point — run the rewrite as `uv run python -m joss.main` instead. `joss/load.py` is also broken: it imports the deleted `joss.logger` and the undeclared `progress` package. `joss/cli.py` references an undefined `required` variable and is unused — `joss/main.py` builds its own parser. Empty root dirs `awesome/`, `gh/`, `papers/` are untracked placeholders.
- **`rh gh` persists nothing yet** — it executes the GitHub GraphQL search and logs the match count. Do not write tests or docs assuming database output.
- **`GITHUB_TOKEN`** (classic PAT) is required for `rh gh` (`CLI.get_token` raises `RuntimeError` without it) and for the `joss.main` pipeline (`-g` flag or env var). `rh papers` and `rh awesome` need no token.
- **Lint only via pre-commit.** `uv run ruff`, `uv run bandit`, and `uv run isort` all fail — those tools are not installed in the project venv; pre-commit runs them in their own hook environments.
- **pre-commit runs a system prettier hook** (`language: system`) over Markdown/JSON/YAML with 4-space indent, LF endings, and print width 80 — commits fail if prettier is not on PATH.
- **"JOSS" names are legacy, not bugs.** `JOSSRunner`, `JOSSLogger`, and `joss_logger=` kwargs appear throughout `rh/` (e.g. `rh/ecosystems/awesome/runner.py`) because the package was formerly named `joss`. Do not rename opportunistically; the `joss/` rewrite uses plain `Extract`/`Transform` names instead.
- **Python version mismatch.** `pyproject.toml` declares `requires-python = "~=3.13"`, but the venv and pre-commit's `default_language_version` use Python 3.14.
- **Version is derived from git tags at build time.** `make build` runs `uv version $(git describe --tags --abbrev=0)`, so the version in `pyproject.toml` is transient; releases are tag-driven.
- **No CI and no typechecker.** Verification is pre-commit + pytest locally; do not invent `mypy`/typecheck steps or CI badges.
- **Tests are offline.** `rh/tests/` uses fakes only — no network, no `GITHUB_TOKEN`. Keep new tests that way.
- **Style.** `rh/` public functions carry numpy-style docstrings (Parameters/Returns/Raises); the `joss/` rewrite deliberately uses `#` comments and no docstrings — match the file you are editing. ruff line length 88. README's "Project structure" section is stale — `analysis/` and `scripts/` no longer exist.
