# AGENTS.md

Two parallel, structurally identical Python packages that build local SQLite datasets: top-level `joss/` (JOSS review issues from the GitHub GraphQL API) and top-level `awesome/` (Ecosyste.ms Awesome lists plus each list's projects). Each package: `main.py` (wires extract→transform→load via module functions under `if __name__ == "__main__":`), `db.py` (SQLAlchemy wrapper, `DB(db_path)` + `create_tables()`), `etl/` (pydantic models + `ExtractInterface`/`TransformInterface`/`LoadInterface` in `etl/__init__.py`; plain `Extract`/`Transform`/`Load` classes in `etl/{extract,transform,load}.py`). They are deliberate mirrors — apply structural or method-contract changes to both. The legacy `rh/` package was deleted (only an empty untracked dir remains). pyproject distribution name is `joss`.

## Commands

```bash
pre-commit run --all-files                     # ruff check/format + bandit + prettier — the only quality gate
uv run python -m joss.main -o /tmp/joss.db     # real run: network ETL, needs GITHUB_TOKEN, -o must not exist
uv run python -m awesome.main -o /tmp/awesome.db --email you@example.com
                                               # real run: network ETL, no token needed, -o must not exist
make create-dev                                # pre-commit install/autoupdate + uv sync
make build                                     # version from latest git tag, wipes dist/, builds + installs sdist locally
```

**No console script works.** All three declared in pyproject fail: `uv run rh` (`ModuleNotFoundError: No module named 'rh.main'` — code deleted), `uv run joss` and `uv run awesome` (`ImportError: cannot import name 'main'` — neither `main.py` defines a `main()`; the pipeline only runs under `python -m`, mirroring each other's flaw). `--help` works for both `-m` entry points.

## Gotchas

- **No tests exist.** `rh/tests/` was deleted; `uv run pytest` collects 0 items and still exits 0 — it proves nothing. Verify with pre-commit plus `python -m <pkg>.main --help` smoke runs.
- **DB constructors refuse existing outputs.** Both `DB(db_path)`s `sys.exit(1)` when the `-o` path already exists, and load writes via pandas `to_sql` with `if_exists="delete_rows"` — reruns need a fresh path.
- **Real runs hit the network.** joss pages through every JOSS review issue via GraphQL (needs a classic-PAT `GITHUB_TOKEN`: `-g` flag or env var; argparse makes `-g` required when the env var is unset). awesome needs no token (its `--email` is just the API `mailto`), but its transform fetches projects for every list, so it makes thousands of GETs after extraction.
- **`joss/joss.sqlite3` (73 MB) is a gitignored local artifact** (`*.sqlite3` rule) from a rewrite test run sitting inside the package dir; hatchling excludes it from builds. Do not commit it.
- **`make build` wheel ships only `joss/`** — hatchling auto-detects the package from the project name, so `awesome/` rides in the sdist but is absent from the wheel and won't be importable from installed environments.
- **README is stale.** It documents the deleted `rh` CLI (every usage example fails), still lists `rh/` in "Project structure", and claims `analysis/`/`scripts/` exist.
- **Lint only via pre-commit.** `uv run ruff` and `uv run bandit` fail — those tools are not installed in the project venv; pre-commit runs them in their own hook environments.
- **pre-commit runs a system prettier hook** (`language: system`) over Markdown/JSON/YAML with 4-space indent, LF endings, and print width 80 — commits fail if prettier is not on PATH.
- **Python version mismatch.** `pyproject.toml` declares `requires-python = "~=3.13"`, but the venv and pre-commit's `default_language_version` use Python 3.14; uv also prints a tilde-specifier ambiguity warning on every run.
- **Version is derived from git tags at build time.** `make build` runs `uv version $(git describe --tags --abbrev=0)`, so the version in `pyproject.toml` is transient; releases are tag-driven.
- **No CI and no typechecker.** Verification is pre-commit + smoke runs locally; do not invent `mypy`/typecheck steps or CI badges.
- **Style.** Both rewrites deliberately use `#` comments and no docstrings — match the file you are editing. ruff line length 88.
