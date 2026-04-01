# Agent Guidelines for JOSS Dataset Repository

Instructions for coding agents working in this Python project.

## Rule Sources Checked

- Cursor rules in `.cursor/rules/`: not present.
- Cursor rules in `.cursorrules`: not present.
- Copilot rules in `.github/copilot-instructions.md`: not present.
- This file is the canonical agent guidance for this repository.

## Environment and Tooling

- Language: Python (`requires-python = "~=3.13"` in `pyproject.toml`).
- Dependency/package manager: `uv`.
- Build backend: `hatchling`.
- Lint/format: Ruff + isort via pre-commit hooks.
- Security scanning: Bandit via pre-commit.
- Line endings/encoding: LF + UTF-8 (`.editorconfig`).

## Build, Lint, and Test Commands

Use these commands first when validating changes:

```bash
# One-time local setup
make create-dev

# Build and install package from source
make build

# Run all checks on all files
pre-commit run --all-files
```

### Targeted Lint/Format Commands

Use targeted checks while iterating on changed files:

```bash
pre-commit run ruff-check --files joss/main.py joss/utils.py
pre-commit run ruff-format --files joss/main.py joss/utils.py
pre-commit run isort --files joss/main.py joss/utils.py
pre-commit run bandit --files joss/main.py joss/utils.py
```

Notes:

- Ruff line length is `88` (`ruff.toml`).
- isort line length is `79` for import wrapping (`.isort.cfg`).
- Ruff target version is `py310` for lint/format compatibility.

### Testing Commands (Especially Single-Test Runs)

There is currently no committed `tests/` directory. If/when tests are added,
use `pytest` node selection patterns like this:

```bash
# Run all tests
pytest

# Run one test file
pytest tests/test_parsers.py

# Run one test function
pytest tests/test_parsers.py::test_parse_joss_issue

# Run one test class
pytest tests/test_parsers.py::TestParserBehavior

# Run tests matching a keyword expression
pytest -k "parse_joss and not slow"

# Stop on first failure
pytest -x
```

Run the most specific test node covering your change first.

## CLI Run Commands

```bash
# Main ingestion flow
joss joss --out-file joss.db

# Papers ingestion flow
joss papers --out-file papers.db --email you@example.com
```

Environment requirements:

- `GITHUB_TOKEN` is required for GitHub ingestion.
- Missing token raises `RuntimeError` in `joss/cli.py`.

## Code Style Guidelines

### Imports

- Use absolute imports within the package (`from joss.db import DB`).
- Group imports as: standard library, third-party, local package.
- Keep imports sorted according to `.isort.cfg`.
- Do not use wildcard imports.

### Formatting

- Format with Ruff (`ruff-format` pre-commit hook).
- Use double quotes.
- Use 4-space indentation for Python.
- Respect Ruff line length (`88`).
- Keep trailing commas where formatter/linter expects them.
- Ensure final newline in all files.

### Type Hints

- Type all function/method arguments.
- Type all return values (`-> None` when appropriate).
- Prefer built-in generics (`list[str]`, `dict[str, int]`).
- Prefer `|` unions (`str | None`).
- Use `Any` only when required; keep waivers narrow.

### Naming Conventions

- Functions/variables/helpers: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Private/internal names: leading underscore.
- Keep CLI argument names explicit and descriptive.

### Docstrings and Documentation

- Keep module docstrings at top of file.
- Public functions/classes should include docstrings.
- Use Google-style sections (`Args`, `Returns`, `Raises`) when needed.
- Keep docstrings behavior-focused and concise.

### Error Handling and Logging

- Raise explicit, actionable exceptions.
- Prefer building a `msg` variable before raising complex errors.
- Validate external inputs early (CLI args, env vars, parsed payloads).
- Use structured logging placeholders (`logger.info("x=%s", x)`).
- Avoid silently swallowing exceptions.

### Data and I/O

- Use `pathlib.Path` for filesystem paths.
- Use explicit UTF-8 encoding for text file I/O.
- Use stable JSON serialization (`sort_keys=True`) when reproducible output matters.
- Keep timestamp handling explicit and UTC-based.

## Lint Rule Baseline

Ruff enables broad rule families (security, annotations, naming, docstrings,
pyflakes/pycodestyle, pylint-like checks, and modernization checks).

Repository Ruff ignore list:

- `D203`
- `D212`
- `COM812`
- `S404`

Bandit runs on Python files through pre-commit.

## File and Encoding Rules

- Follow `.editorconfig`: UTF-8, LF, final newline, trimmed trailing spaces.
- Python files use 4 spaces.
- Markdown indentation uses 2 spaces where indentation matters.

## Project Layout (High-Level)

```text
joss/
  cli.py, main.py, db.py, parsers.py, utils.py, logger.py, interfaces.py
  ecosystems/
    api/
    papers/
  joss/
    extract.py, transform.py, load.py, runner.py
analysis/
scripts/
```

## Agent Workflow Expectations

- Make minimal, targeted edits aligned with existing patterns.
- Avoid unrelated refactors in feature/fix tasks.
- Prefer updating existing modules over adding new abstractions.
- Run targeted checks first, then broader validation as needed.
- In PR/commit notes, record why the change exists and what was validated.

## Practical Agent Checklist

Use this flow for code changes:

1. Read affected module(s) and nearby conventions.
2. Implement the smallest viable change.
3. Run targeted pre-commit hooks on changed files.
4. Run relevant single-test node(s) if tests exist.
5. Run broader checks (`pre-commit run --all-files`) when practical.
6. Summarize what changed, why, and what was validated.
