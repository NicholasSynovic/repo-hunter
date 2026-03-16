# Agent Guidelines for JOSS Dataset Repository

Instructions for agentic coding systems working in this Python project.

## Build, Lint, and Test Commands

### Development Setup

```bash
make create-dev  # Initial setup (installs pre-commit hooks and dependencies via uv)
make build       # Full build (versions, builds distribution, installs package)
```

### Linting and Formatting

```bash
pre-commit run --all-files  # Run all pre-commit checks

# Run on specific files
pre-commit run ruff-check --files joss/utils.py joss/main.py
pre-commit run ruff-format --files joss/utils.py joss/main.py
pre-commit run isort --files joss/utils.py joss/main.py
pre-commit run bandit --files joss/utils.py joss/main.py
```

### Testing

No test suite exists yet. When tests are added:

```bash
pytest                                    # Run all tests
pytest tests/test_parsers.py              # Single test file
pytest tests/test_parsers.py::test_parse_joss_issue  # Single test function
pytest --cov=joss --cov-report=term-missing  # With coverage
```

## Code Style Guidelines

### Language & Version

- **Python**: 3.13 (as per `pyproject.toml`), compatible with 3.10+

### Imports

- **Order**: isort (Black profile), configured in `.isort.cfg`
- **Line length**: 79 for import wrapping
- **Style**: Explicit absolute imports; no star imports
- Separate groups with blank lines (stdlib → third-party → local)

### Formatting

- **Formatter**: Ruff (`ruff format` via pre-commit)
- **Line length**: follow Ruff defaults
- **Quotes**: Double quotes (`"string"`)
- **Indentation**: 4 spaces
- **Trailing commas**: Keep if formatter adds them

### Type Hints

- **Mandatory**: All function parameters and returns must have type hints
- **Style**: Modern syntax (`list[T]` not `List[T]`, `int | str` not `Union[int, str]`)
- **Returns**: Always specify, use `-> None` for void functions
- **Any**: `typing.Any` allowed only when necessary, use `# noqa: ANN401`

### Naming Conventions

- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Privates**: Prefix with `_` (e.g., `_internal_helper()`)
- **Logger**: Use `LOGGER = logging.getLogger(__name__)` or `JOSSLogger`

### Documentation

- **Module docstrings**: Required at top of file
- **Public functions/methods**: Required docstrings
- **Format**: Google-style with Args, Returns, Raises sections
- Start multi-line docstrings on second line

### Error Handling

- **Exceptions**: Raise with explicit error messages
- **Type validation**: Check types explicitly before operations
- **Message style**: Store in `msg` variable before raising
- **Logging**: Use structured logging (`logger.info("... %s", value)`)

### Data and IO

- **Paths**: Use `pathlib.Path`
- **Encoding**: UTF-8 for file IO (`read_text`/`write_text`)
- **JSON**: Use `json.dumps(..., sort_keys=True)` for stable output

## Linting Rules (Ruff + Bandit)

Enabled: security (S), type annotations (ANN), naming (N), docstrings (D), and
other defaults via Ruff pre-commit hooks.

Ignored rules:
- `D203`: Blank line before docstring (conflicts with D211)
- `D212`: Summary after description newline
- `COM812`: Trailing comma conflicts with Black
- `S404`: Use of subprocess (when intentional)

Bandit runs via pre-commit on `*.py` files.

## File Requirements

- **Encoding**: UTF-8 with LF line endings
- **Final newline**: All files must end with newline
- **Copyright**: Include copyright notice at top of file

## Project Structure

```text
joss/
  ├── __init__.py          # APPLICATION_NAME constant
  ├── main.py              # Entry point with CLI subcommands
  ├── cli.py               # CLI argument parser
  ├── db.py                # Database models and utilities
  ├── logger.py            # Logging configuration
  ├── utils.py             # Shared utilities
  ├── parsers.py           # Text parsing utilities
  ├── interfaces.py        # Pydantic models for API data
  ├── ecosystems/          # JOSS ecosystem data modules
  │   ├── api/             # API client code
  │   └── papers/          # Paper data handling
  └── joss/                # Core ingestion/transform logic
      ├── runner.py        # Main ingestion runner
      ├── extract.py       # Data extraction
      ├── transform.py     # Data transformations
      └── load.py          # Data loading
```

## CLI Usage

```bash
joss joss --out-file joss.db  # Ingest GitHub issues (writes SQLite DB)
```

## Key Tools

- **Build**: Hatchling | **Dependency manager**: uv
- **Linter/Formatter**: Ruff v0.15.1 | **Pre-commit**: v6.0.0
- **Security**: Bandit v1.9.3 | **Import sorting**: isort 7.0.0
- **Data validation**: pydantic v2.12.5+

## Dependencies

- **requests**: HTTP client | **pydantic**: Data validation | **progress**: Terminal spinners
- **matplotlib**: Visualization | **seaborn**: Statistical visualization
- **ghapi**: GitHub API wrapper | **sqlalchemy**: Database access | **pandas**: Dataframes
