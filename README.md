<!-- prettier-ignore -->
<div align="center">

# Repo Hunter

A command-line toolkit for building local SQLite datasets from open-source repository ecosystems.

[![License](docs/license_badge.svg)](LICENSE)

[Overview](#overview) • [Getting started](#getting-started) • [Usage](#usage) • [Development](#development) • [Project structure](#project-structure) • [License](#license)

![Repo Hunter mascot](docs/hero.jpeg)

</div>

## Overview

Repo Hunter provides ETL-style commands for researchers and developers who need
datasets of open-source software projects:

- **Extract** upstream project and review metadata from public ecosystem APIs
- **Transform** records into normalized, table-oriented structures
- **Load** the results into a local SQLite database

## Features

- **JOSS review tracker**: collect all Journal of Open Source Software review
  issues from the GitHub GraphQL API.
- **Ecosyste.ms Awesome**: collect Awesome lists and every project they
  reference.
- **Identical pipelines**: both datasets run the same extract, transform, and
  load steps into a local SQLite database.

## Getting started

Prerequisites:

- Python `~=3.13`
- [`uv`](https://docs.astral.sh/uv/) for dependency and build management
- `pre-commit` (used by `make create-dev`)

Preferred setup:

```bash
make create-dev
```

This runs `pre-commit install`, `pre-commit autoupdate`, and `uv sync`.

Minimal setup:

```bash
uv sync
pre-commit install
```

## Usage

Show top-level help:

```bash
rh --help
```

> [!NOTE]
> The output file passed to `-o` must not already exist; the tool exits
> rather than overwrite a database.

### `rh joss`

Collects Journal of Open Source Software review issues.

Options:

- `-o, --out-file` (required): SQLite database path to write results to.
- `-g, --github-token`: classic GitHub Personal Access Token. Required unless
  the `GITHUB_TOKEN` environment variable is set.
- `--resolve-urls` (optional): resolve JOSS paper URLs to their final
  redirected URLs. Can take a while.

```bash
rh joss --out-file data/joss.db
```

### `rh awesome`

Collects Ecosyste.ms Awesome lists and their projects.

Options:

- `-o, --out-file` (required): SQLite database path to write results to.
- `--email` (required): contact email passed as the API `mailto` parameter.

```bash
rh awesome --out-file data/awesome.db --email you@example.com
```

> [!NOTE]
> The awesome transform fetches projects for every list, so a full run makes
> thousands of requests and can take a while.

> [!IMPORTANT]
> `rh joss` queries GitHub, so it requires a classic GitHub Personal Access
> Token via `-g` or the environment:

```bash
export GITHUB_TOKEN="ghp_your_classic_token_here"
```

## Development

Build the package. This updates the version from the latest git tag, writes
artifacts to `dist/`, and installs the built source dist locally:

```bash
make build
```

Run all configured quality checks (linting, formatting, security scanning):

```bash
pre-commit run --all-files
```

Run checks on only changed files:

```bash
pre-commit run --files <file1> <file2>
```

> [!NOTE]
> The prettier hook runs from your system PATH, so commits fail if
> `prettier` is not installed. Pre-commit also only checks git-tracked files;
> untracked files are silently skipped until `git add`ed.

## Project structure

- `rh/` — the Python package and `rh` CLI entry point.
- `rh/main.py` — CLI dispatch for the `joss` and `awesome` subcommands.
- `rh/db.py` — SQLite wrapper shared by both pipelines.
- `rh/etl/__init__.py` — the shared Extract/Transform/Load interfaces.
- `rh/etl/joss/` — the JOSS pipeline: pydantic models in `__init__.py`, plus
  `extract`, `transform`, and `load` steps.
- `rh/etl/awesome/` — the Awesome pipeline, a deliberate structural mirror of
  the JOSS pipeline.

## License

This project is licensed under the [GNU AGPL v3.0](LICENSE).
