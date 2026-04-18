# Repo Hunter

Repo Hunter is a command-line data collection toolkit for building local
SQLite datasets from open-source repository ecosystems.

The Python package in this repository is currently named `joss`, and the CLI
entrypoint command is `rh`.

## What It Does

Repo Hunter provides ETL-style commands that:

- extract upstream project/review metadata
- transform records into normalized table-oriented structures
- load data into local SQLite databases

Current supported sources:

- JOSS review tracker issues (`rh joss`)
- Ecosyste.ms Papers API (`rh papers`)
- Ecosyste.ms Awesome API (`rh awesome`)
- GitHub repository search filters (`rh gh`)

## Prerequisites

- Python `~=3.13`
- [`uv`](https://docs.astral.sh/uv/) for dependency and build management
- `pre-commit` (installed automatically by `make create-dev`)

## Development Setup

Preferred setup:

```bash
make create-dev
```

This runs:

- `pre-commit install`
- `pre-commit autoupdate`
- `uv sync`
- `uv build`

Minimal setup:

```bash
uv sync
pre-commit install
```

## Build

Recommended build command:

```bash
make build
```

Alternative direct build command:

```bash
uv build
```

Build notes:

- `make build` updates package version from the latest git tag.
- Build artifacts are written to `dist/`.
- `make build` installs the built source dist locally.

## Quality Checks

Run all configured checks:

```bash
pre-commit run --all-files
```

Useful targeted checks:

```bash
uv run ruff check .
uv run ruff format .
uv run isort .
uv run bandit -r joss analysis scripts
```

Run checks on only changed files:

```bash
pre-commit run --files <file1> <file2>
```

## Testing

There is currently no dedicated `tests/` directory in this repository.

When pytest tests are added, use these patterns:

```bash
uv run pytest
uv run pytest tests/path/test_module.py
uv run pytest tests/path/test_module.py::test_name
uv run pytest tests/path/test_module.py::test_name[param]
```

## Runtime Requirements

`GITHUB_TOKEN` is required and must be a classic GitHub Personal Access Token
(PAT) with access needed to query upstream GitHub data.

```bash
export GITHUB_TOKEN="ghp_your_classic_token_here"
```

## Running the CLI

Show top-level help:

```bash
rh --help
```

Example runs:

```bash
rh joss --out-file /tmp/joss.db
rh papers --out-file /tmp/papers.db --email you@example.com
rh awesome --out-file /tmp/awesome.db --email you@example.com
rh gh --star-count 200 --fork-count 50 --watcher-count 25 --issue-count 10 --age-months 24 --pr-count 5
```

## CLI Subcommands and Options

### `rh joss`

Collects Journal of Open Source Software review issues.

Options:

- `-o, --out-file` (required): SQLite database path to write results to.
- `--resolve-urls` (optional): resolve JOSS paper URLs to final redirected URLs.

Example:

```bash
rh joss --out-file data/joss.db --resolve-urls
```

### `rh papers`

Collects project and mention data from the Ecosyste.ms Papers API.

Options:

- `-o, --out-file` (required): SQLite database path to write results to.
- `--email` (required): contact email passed as the API `mailto` parameter.

Example:

```bash
rh papers --out-file data/papers.db --email you@example.com
```

### `rh awesome`

Collects list/project data from the Ecosyste.ms Awesome API.

Options:

- `-o, --out-file` (required): SQLite database path to write results to.
- `--email` (required): contact email passed as the API `mailto` parameter.

Example:

```bash
rh awesome --out-file data/awesome.db --email you@example.com
```

### `rh gh`

Searches for GitHub repositories that match configurable numeric thresholds.

Options:

- `--star-count` (optional, default: `-1`): minimum stars; `-1` disables filter.
- `--fork-count` (optional, default: `-1`): minimum forks; `-1` disables filter.
- `--watcher-count` (optional, default: `-1`): minimum watchers; `-1` disables filter.
- `--issue-count` (optional, default: `-1`): minimum issues; `-1` disables filter.
- `--age-months` (optional, default: `-1`): maximum repository age in months; `-1` disables filter.
- `--pr-count` (optional, default: `-1`): minimum pull requests; `-1` disables filter.

Validation:

- All `rh gh` numeric filters must be integers greater than or equal to `-1`.

Examples:

```bash
rh gh
rh gh --star-count 500 --fork-count 100
rh gh --age-months 12 --issue-count 20 --pr-count 10
```
