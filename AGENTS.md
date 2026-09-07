# AGENTS.md

A single Python package `rh/` (distribution name `rh`) that builds local SQLite datasets through two structurally identical ETL pipelines: `joss` (Journal of Open Source Software review issues from the GitHub GraphQL API) and `awesome` (Ecosyste.ms Awesome lists plus each list's projects). Layout: `rh/main.py` (defines a real `main()` dispatching the `joss`/`awesome` subcommands), `rh/db.py` (shared SQLAlchemy wrapper, `DB(db_path)` + `create_tables(dataset=...)`), `rh/etl/__init__.py` (shared `ExtractInterface`/`TransformInterface`/`LoadInterface` over pydantic `BaseModel`), and `rh/etl/{joss,awesome}/` (pydantic models + dataset constants in each `__init__.py`; plain `Extract`/`Transform`/`Load` classes in `etl/{extract,transform,load}.py`). The two subpackages are deliberate mirrors — apply structural or method-contract changes to both.

## Commands

```bash
pre-commit run --all-files                     # ruff check/format + bandit + prettier — the only quality gate
uv run rh --help                               # works offline; use for smoke checks (also per-subcommand --help)
uv run rh joss -o /tmp/joss.db                 # real run: network ETL, needs GITHUB_TOKEN, -o must not exist
uv run rh awesome -o /tmp/awesome.db --email you@example.com
                                               # real run: network ETL, no token needed, -o must not exist
make create-dev                                # pre-commit install/autoupdate + uv sync
make build                                     # version from latest git tag, wipes dist/, builds + installs sdist locally
```

The `rh` console script is the working entry point (`rh = "rh.main:main"`); the old `joss` and `awesome` scripts were removed. `python -m rh.main` works too.

## Gotchas

- **No tests exist.** `uv run pytest` collects 0 items and still exits 0 — it proves nothing. Verify with pre-commit plus `uv run rh --help` smoke runs.
- **`pre-commit run --all-files` only checks git-tracked files.** New files are silently skipped until `git add`ed — pass them explicitly with `pre-commit run --files <paths>`.
- **DB refuses existing outputs.** `DB(db_path)` calls `sys.exit(1)` when the `-o` path already exists, and load writes via pandas `to_sql` with `if_exists="delete_rows"` — reruns need a fresh path.
- **Real runs hit the network.** `rh joss` pages through every JOSS review issue via GraphQL (needs a classic-PAT `GITHUB_TOKEN`: `-g` flag or env var; argparse makes `-g` required when the env var is unset). `rh awesome` needs no token (its `--email` is just the API `mailto`), but its transform fetches projects for every list, so it makes thousands of GETs after extraction.
- **README is stale.** Its `rh papers` and `rh gh` examples describe features that don't exist, and it still lists `analysis/`/`scripts/` under "Project structure". Its `rh joss`/`rh awesome` examples now match the merged CLI.
- **Lint only via pre-commit.** `uv run ruff` and `uv run bandit` fail — those tools are not installed in the project venv; pre-commit runs them in their own hook environments.
- **pre-commit runs a system prettier hook** (`language: system`) over Markdown/JSON/YAML with 4-space indent, LF endings, and print width 80 — commits fail if prettier is not on PATH.
- **Python version mismatch.** `pyproject.toml` declares `requires-python = "~=3.13"`, but the venv and pre-commit's `default_language_version` use Python 3.14; uv also prints a tilde-specifier ambiguity warning on every run.
- **Version is derived from git tags at build time.** `make build` runs `uv version $(git describe --tags --abbrev=0)`, so the version in `pyproject.toml` is transient; releases are tag-driven.
- **No CI and no typechecker.** Verification is pre-commit + smoke runs locally; do not invent `mypy`/typecheck steps or CI badges.
- **Style.** All of `rh/` deliberately uses `#` comments and no docstrings — match the file you are editing. ruff line length 88.
