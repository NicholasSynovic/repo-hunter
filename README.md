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

- **JOSS review tracker**: collect all Journal of Open Source Software review issues.
- **Ecosyste.ms Papers**: collect project and mention data from the Ecosyste.ms Papers API.
- **Ecosyste.ms Awesome**: collect list and project data from the Ecosyste.ms Awesome API.
- **GitHub repository search**: query GitHub for repositories matching configurable thresholds.

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

### `rh joss`

Collects Journal of Open Source Software review issues.

Options:

- `-o, --out-file` (required): SQLite database path to write results to.
- `--resolve-urls` (optional): resolve JOSS paper URLs to final redirected URLs.

```bash
rh joss --out-file data/joss.db --resolve-urls
```

### `rh papers`

Collects project and mention data from the Ecosyste.ms Papers API.

Options:

- `-o, --out-file` (required): SQLite database path to write results to.
- `--email` (required): contact email passed as the API `mailto` parameter.

```bash
rh papers --out-file data/papers.db --email you@example.com
```

### `rh awesome`

Collects list and project data from the Ecosyste.ms Awesome API.

Options:

- `-o, --out-file` (required): SQLite database path to write results to.
- `--email` (required): contact email passed as the API `mailto` parameter.

```bash
rh awesome --out-file data/awesome.db --email you@example.com
```

### `rh gh`

Searches for GitHub repositories matching configurable numeric thresholds.

Options (all optional, default `-1`, which disables the filter):

- `--star-count`: minimum stars.
- `--fork-count`: minimum forks.
- `--watcher-count`: minimum watchers.
- `--issue-count`: minimum issues.
- `--age-months`: maximum repository age in months.
- `--pr-count`: minimum pull requests.

```bash
rh gh --star-count 500 --fork-count 100
```

> [!NOTE]
> `rh gh` currently executes the search query and reports the number of
> matching repositories; saving results to a database is not implemented yet.

> [!IMPORTANT]
> `rh joss` and `rh gh` query GitHub, so they require a classic GitHub
> Personal Access Token in the environment:

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

Run the tests:

```bash
uv run pytest
```

## Project structure

- `rh/` — the Python package and `rh` CLI entry point.
- `analysis/` — matplotlib/seaborn scripts for plotting JOSS issue data.
- `scripts/` — helpers for collecting GitHub repository URLs and cloning them.

## License

This project is licensed under the [GNU AGPL v3.0](LICENSE).
