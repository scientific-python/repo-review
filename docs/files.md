# Files

You can suggest files to pre-load in parallel when async loading is available.
Prefetching a small set of likely-used files (for example `pyproject.toml` and
CI/workflow configs) can significantly speed up checks that read repository
config, and keep the webapp responsive. Files not in this set will be loaded
normally. Does nothing on local repositories. Prefetching is only performed on
Python 3.11+ when async support (e.g. `httpx`) is available; on Python 3.10
prefetching is skipped and entry-points will be ignored.

Only prefetch files that will be read; this will needlessly read the file if
the file is only checked for existence.

## Entry point

Declare an entry point in your project under the group `repo_review.prefetch_files`.
The entry-point must point to a callable that returns a `set[str]` of relative
paths or glob patterns. Repo-review will collect those values and, when running
against a `GHPath` (remote GitHub repository), will attempt to prefetch the
matching files concurrently.

Example `pyproject.toml` entry points:

```toml
[project.entry-points."repo_review.prefetch_files"]
root = "my_package.prefetch:prefetch_root"
package = "my_package.prefetch:prefetch_package"
```

The entry-point name controls where patterns are resolved:

- **`root`** (or empty): patterns are resolved relative to the repository root.
- **`package`**: patterns are resolved relative to the package directory
  (i.e. the path passed via `--package-dir`, or the root if not set).

Any other entry point name will produce a warning.

## What to return

Return a `set[str]` containing file paths relative to the base directory
determined by the entry-point name (`root` or `package`).
You may use simple glob patterns (e.g. `.github/workflows/*.yml`) to match
multiple files. Repo-review uses `PurePosixPath.match()` to expand patterns
when running against remote repositories, so matches must go to the end of the
name, can start anywhere, and `**` is not supported.

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
entry points and unions their returned sets as a dict using entry point key
names (anything other than a known key causes a warning and is not stored).
When running the CLI against a `GHPath` (a GitHub-backed Traversable)
repo-review will attempt to prefetch the matching files in parallel using the
async `GHPath.prefetch()` helper. If async support (e.g. `httpx`) is not
available repo-review falls back to the regular synchronous loading path.
