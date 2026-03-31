# Files

You can suggest files to pre-load in parallel when async loading is available.
Prefetching a small set of likely-used files (for example `pyproject.toml` and
CI/workflow configs) can significantly speed up checks that read repository
config, and keep the webapp responsive. Files not in this set will be loaded
normally. Does nothing on local repositories.

## Entry point

Declare an entry point in your project under the group `repo_review.prefetch_files`.
The entry-point must point to a callable that returns a `set[str]` of relative
paths or glob patterns. Repo-review will collect those values and, when running
against a `GHPath` (remote GitHub repository), will attempt to prefetch the
matching files concurrently.

Example `pyproject.toml` entry points:

```toml
[project.entry-points."repo_review.prefetch_files"]
prefetch_files = "my_package.prefetch:prefetch_files"
```

The entry-point name is ignored; the callable's return value is used.

## What to return

Return a `set[str]` containing file paths relative to the repository root.
You may use simple glob patterns (e.g. `.github/workflows/*.yml`) to match
multiple files. Repo-review uses `GHPath.glob()` to expand patterns when
running against remote repositories.

You don't need to return `"pyproject.toml"`, as that's already part of
repo-review (to read the configuration).

Example implementation:

```python
from importlib.resources.abc import Traversable

def prefetch_files() -> set[str]:
		"""Return files that would benefit from prefetching.

		Keep this list small and focused on files your checks actually read.
		"""
		return {
				".github/workflows/*.yml",
				".pre-commit-config.yaml",
		}
```

## How repo-review uses this

At startup repo-review collects all registered `repo_review.prefetch_files`
entry points and unions their returned sets. When running the CLI against a
`GHPath` (a GitHub-backed Traversable) repo-review will attempt to prefetch
the matching files in parallel using the async `GHPath.prefetch()` helper.
If async support (e.g. `httpx`) is not available repo-review falls back to the
regular synchronous loading path.

