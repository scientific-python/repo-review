# AI Instructions

## Overview

**repo-review**: Python 3.10+ framework for validating repository configuration (not source code).
Supports CLI, plugins, GitHub API, pre-commit, CI, and web (via Pyodide).

- Core: run checks over repo structure/config
- Extensible via entry points (`checks`, `fixtures`, `families`)

---

## Core Commands

### Setup

If `uv` and `prek` commands are not available, they can be installed from PyPI:

```bash
pip install uv prek
```

### Test & Lint

```bash
uv run pytest        # run tests
prek -a              # run all lint/format hooks
```

### Build

```bash
uv build
```

### Run Tool

```bash
uv run repo-review .
uv run repo-review --list-all
```

### Docs (only if needed)

```bash
uvx hatch run docs:html
uvx hatch run api-docs:build
```

---

## Key Architecture

### Important Files

- `src/repo_review/processor.py` → orchestrates checks
- `src/repo_review/checks.py` → discovers checks (entry points)
- `src/repo_review/fixtures.py` → dependency injection system
- `src/repo_review/__main__.py` → CLI interface
- `src/repo-review-app/` → A JavaScript webapp using Pyodide

### Plugin System

Entry points:

- `repo_review.checks`
- `repo_review.fixtures`
- `repo_review.families`

Checks are classes with:

- `requires`
- `check()` method
- docstring = message

---

## Development Workflow

1. Run baseline if needed:

   ```bash
   uv run pytest
   prek -a
   ```

2. Make changes

3. Validate:

   ```bash
   prek -a
   uv run pytest
   ```

4. If API/docs changed:

   ```bash
   uvx hatch run api-docs:build
   ```

---

## PR Requirements

- Tests pass: `uv run pytest`
- Lint passes: `prek -a`
- If API changed: regenerate docs

---

## Key Notes

- Python ≥3.10 (uses modern syntax)
- Pre-commit handles formatting, linting, typing
- Tests are fast (~5–10s)
