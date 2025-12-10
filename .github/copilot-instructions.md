# Copilot Instructions for repo-review

## Repository Overview

**repo-review** is a Python framework (Python 3.10+) for building checks to verify repositories follow guidelines. It's designed for checking configuration files rather than Python code, and can run locally, remotely (via GitHub API), in pre-commit, GitHub Actions, or WebAssembly (Pyodide).

- **Project Type**: Python package with CLI, plugin system, and web interface
- **Size**: ~32MB repository, ~1,635 lines of main source code
- **Languages/Frameworks**: Python 3.10-3.14, uses Hatch for builds, pytest for testing
- **Key Technologies**: Rich (terminal UI), Click (CLI), Markdown-it-py, PyYAML, Traversable API

## Build System & Commands

### Environment Setup

**Primary Tools**: Use `uv` to manage virtual environments and dependencies, and `prek` for pre-commit hooks.

**Installation**:

```bash
pip install uv prek  # or pipx install uv prek, or brew install uv prek
```

### Key Commands (Verified Working)

**Testing** (takes ~5-10 seconds):

```bash
uv run pytest                # Run tests on current Python
```

**Linting/Formatting** (takes ~60-90 seconds first time due to hook installation):

```bash
prek -a                      # Run all pre-commit hooks (comprehensive)
uvx hatch run pylint:lint    # Run pylint only (~7 seconds)
```

**Building** (takes ~10-15 seconds):

```bash
uv build                     # Build sdist and wheel to dist/
```

**Documentation** (takes ~30-45 seconds):

```bash
uvx hatch run docs:html          # Build HTML docs to docs/_build/html
uvx hatch run docs:serve         # Build and serve docs locally with auto-reload
uvx hatch run docs:linkcheck     # Check for broken links in docs
uvx hatch run docs:man           # Build manpage
uvx hatch run api-docs:build     # Rebuild API documentation
```

**Running the Tool**:

```bash
uv run repo-review --help
uv run repo-review .                # Check current directory
uv run repo-review --list-all       # List all available checks
```

**WebApp**:

```bash
uvx hatch run webapp:serve       # Serve webapp on http://localhost:8080
```

## Project Structure

### Source Code Layout

```
src/repo_review/          # Main package (1,635 lines total)
├── __init__.py           # Package initialization
├── __main__.py           # CLI entry point (rich-click based)
├── checks.py             # Check collection and processing
├── families.py           # Check families/grouping system
├── fixtures.py           # Fixture system (pytest-like)
├── processor.py          # Main processing logic
├── ghpath.py             # GitHub/remote path handling (Traversable)
├── html.py               # HTML output generation
├── schema.py             # JSON schema for validate-pyproject
├── testing.py            # Testing utilities for plugins
├── _compat/              # Compatibility shims for Python versions
└── resources/            # Bundled resource files

tests/                    # Test suite (pytest)
├── conftest.py           # Pytest configuration/fixtures
├── test_*.py             # Test files (41 tests total)
└── test_utilities/       # Example plugin for testing
    └── pyproject.py      # Test plugin implementation

docs/                     # Sphinx documentation
├── index.md, intro.md    # User-facing docs
├── plugins.md, checks.md # Plugin development docs
└── api/                  # Auto-generated API docs
```

### Configuration Files

- **pyproject.toml**: Main project config (build, dependencies, tools, hatch envs)
- **.pre-commit-config.yaml**: Pre-commit / prek hooks (ruff, mypy, prettier, etc.)
- **.readthedocs.yaml**: ReadTheDocs build configuration
- **action.yml**: GitHub Action composite action definition

### Key Source Files

**Entry Points**:

- `src/repo_review/__main__.py`: CLI with rich output, handles formats (rich/json/html/svg)
- `src/repo_review/processor.py`: Core logic for collecting and running checks
- `src/repo_review/checks.py`: Check discovery via entry points
- `src/repo_review/fixtures.py`: Fixture system (root, package, pyproject)

**Plugin System**:

Entry points in `pyproject.toml`:

- `repo_review.fixtures`: Add new fixtures
- `repo_review.checks`: Plugin entry point returning check dicts
- `repo_review.families`: Customize check grouping/display

## CI/CD Pipelines

### GitHub Actions (.github/workflows/)

**ci.yml** (main CI pipeline):

1. **pre-commit job**: Runs `pre-commit` hooks + pylint on ubuntu-latest, Python 3.x
2. **checks job**: Runs `hatch test -a` on ubuntu/macos/windows with Python 3.10-3.14
3. **dist job**: Builds distribution with `hynek/build-and-inspect-python-package@v2`
4. **docs job**:
   - Runs `hatch run docs:linkcheck` to check for broken links
   - Runs `hatch run docs:html -W` (warnings as errors)
   - Verifies API docs are up-to-date: `hatch run api-docs:build && git diff --exit-code`
5. **action job**: Tests the GitHub Action itself with a plugin

**cd.yml** (release pipeline):

- Builds distribution and publishes to PyPI on releases

### Pre-commit Hooks

Hooks run via `hatch run lint:lint` or `pre-commit run --all-files`:

- **blacken-docs**: Format Python code in docs
- **ruff-check**, **ruff-format**: Linting and formatting
- **prettier**: Format YAML, markdown, HTML, CSS, JSON
- **check-yaml**, **check-merge-conflict**, **trailing-whitespace**, etc.
- **mypy**: Type checking on src/, web/, tests/
- **codespell**: Spell checking
- **validate-pyproject**: Validate pyproject.toml
- **check-dependabot**, **check-github-workflows**, **check-readthedocs**

## Important Build Notes & Gotchas

### Known Issues & Workarounds

1. **Documentation Warnings**:
   - Building docs shows ~55 warnings about missing reference targets
   - These are existing and expected (mostly importlib.resources type references)
   - Build succeeds despite warnings

2. **Python Version Requirements**:
   - Minimum: Python 3.10
   - Tested: Python 3.10, 3.11, 3.12, 3.13, 3.14
   - Uses modern Python features (match statements, typing, etc.)

### Command Order Best Practices

1. **Before making changes**: Always run `uv run pytest` and `prek -a` to understand baseline
2. **After code changes**: Run `prek -a` first (fast), then `uv run pytest` (slower)
3. **Before committing**: Run `prek -a` to ensure pre-commit hooks pass
4. **Documentation changes**: Run `uvx hatch run docs:html -W` and `uvx hatch run api-docs:build`
5. **If API changes**: Always regenerate API docs with `uvx hatch run api-docs:build`

### Development Workflow

1. **Install hatch**: `pip install uv prek` (or use pipx/brew)
2. **Run tests**: `uv run pytest` - ensures environment is working
3. **Make changes**: Edit files in src/repo_review/ or tests/
4. **Test changes**: `uv run pytest` (quick validation)
5. **Lint**: `prek -a` (comprehensive checks)
6. **Fix lint issues**: `prek -a` (auto-fix formatting)
7. **Build docs** (if needed): `uvx hatch run docs:html`
8. **Build package** (if needed): `uv build`

## Validation Checklist

Before completing a PR:

- [ ] `uv run pytest` passes (all 41 tests)
- [ ] `prek -a` passes (or only shows pre-existing warnings)
- [ ] `prek -a` passes (10.00/10 rating)
- [ ] If docs changed: `uvx hatch run docs:html -W` succeeds
- [ ] If code changed: `uvx hatch run docs:linkcheck` succeeds
- [ ] If API changed: Run `uvx hatch run api-docs:build` and commit changes
- [ ] Build succeeds: `uv build`

## Coding guidelines

The code is written in modern Python (3.10+) with an emphasis on clean, readable code using high level constructs.

## Additional Context

### Dependencies Management

- **Build**: hatchling, hatch-vcs (for version from git)
- **Runtime**: markdown-it-py, pyyaml, tomli (Python <3.11)
- **CLI optional**: click>=8, rich>=12.2, rich-click
- **Dev**: pytest>=7, sp-repo-review (for self-checking), validate-pyproject

### Testing Notes

- **pytest configuration**: See `[tool.pytest.ini_options]` in pyproject.toml
- **Test fixtures**: See tests/conftest.py for entry point mocking
- **Integration tests**: Use tests/test_utilities/ as example plugin
- **Coverage**: Use `hatch run cov:test` for coverage reports

### Documentation Structure

- **Sphinx-based**: Uses MyST parser for markdown
- **Theme**: Furo
- **Extensions**: autodoc-typehints, copybutton, programoutput, opengraph
- **Auto-generated**: API docs in docs/api/ via sphinx-apidoc
- **Manual docs**: docs/{intro,cli,plugins,checks,families,fixtures}.md

### Plugin Development

Plugins extend repo-review via entry points:

- Checks are classes with `requires` set, `check()` classmethod, docstring as message
- Fixtures use dependency injection (pytest-style)
- Entry points: `repo_review.checks`, `repo_review.fixtures`, `repo_review.families`
- Example plugin: tests/test_utilities/pyproject.py

### Performance Notes

- **Testing**: ~5-10 seconds for single Python version
- **Linting**: ~60-90 seconds first time (pre-commit hook installation), ~10-15 seconds after
- **Building**: ~10-15 seconds
- **Documentation**: ~30-45 seconds

## Trust These Instructions

These instructions have been validated by running all commands successfully. Only search for additional information if:

- You encounter an error not documented here
- You need to understand implementation details not covered
- The task requires knowledge beyond build/test/lint workflows

For routine code changes, follow the workflows documented above without additional exploration.
