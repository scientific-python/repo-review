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

### Build Python Package

```bash
uv build
```

### Webapp (TypeScript/React)

The webapp lives in `src/repo-review-app/` and uses React + Pyodide. It requires `bun`:

```bash
# Type-check
bun run type

# Lint
bun run lint

# Format
bun run format

# Build docs bundle (outputs to `docs/_static/scripts/`)
bun run build

# Build npm dist bundle (outputs to `dist/`, published to npm on release)
bun run build-lib
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
- `src/repo-review-app/repo-review-app.tsx` → main React app (class component)
- `src/repo-review-app/utils/pyodideWorker.ts` → self-contained web worker (all Python interop; stringified into a Blob URL, so nothing inside `workerMain` may reference module scope)
- `src/repo-review-app/utils/pyodideClient.ts` → main-thread RPC client for the Pyodide worker
- `src/repo-review-app/utils/github.ts` → GitHub API helpers

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

4. If webapp changed, validate:

   ```bash
   bun run type
   bun run build
   ```

5. If API/docs changed:

   ```bash
   uvx hatch run api-docs:build
   ```

---

## PR Requirements

- Tests pass: `uv run pytest`
- Lint passes: `prek -a`
- If webapp changed: `bun run type && bun run build`
- If API changed: regenerate docs

---

## Key Notes

- Python ≥3.10 (uses modern syntax)
- Pre-commit handles formatting, linting, typing
- Tests are fast (~5–10s)
- Webapp uses React (class components) + Pyodide; built with `bun`
- Webapp build output goes to `docs/_static/scripts/`
- npm dist output goes to `dist/` (gitignored; built and published to npm on release)
