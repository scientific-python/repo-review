# Fixtures

Like pytest fixtures, fixtures in repo-review are requested by name. There are four built-in fixtures:

- `root`: {class}`~importlib.resources.abc.Traversable` - The repository path. All checks or fixtures that depend on the root of the repository should use this.
- `package`: `~importlib.resources.abc.Traversable` - The path to the package directory. This is the same as `root` unless `--package-dir` is passed.
- {func}`~repo_review.fixtures.pyproject`: `dict[str, Any]` - The `pyproject.toml` in the package if it exists, an empty dict otherwise.
- {func}`~repo_review.fixtures.list_all`: `bool` - returns True if repo-review is just trying to collect all checks to list them.

Repo-review doesn't necessarily assume any form or language for your repository,
but since it already looks for configuration in `pyproject.toml`, this fixture
is provided.

## Writing a fixture

You can provide new fixtures easily. A fixture can take any other fixture(s) as
arguments; repo-review topologically sorts fixtures before computing them. The
result of a fixture is cached and provided when requested. The return from a
fixture should be treated as immutable.

A fixture function looks like this:

```python
import yaml
from importlib.resources.abc import Traversable


def workflows(root: Traversable) -> dict[str, Any]:
    workflows_base_path = package.joinpath(".github/workflows")
    workflows_dict: dict[str, Any] = {}
    if workflows_base_path.is_dir():
        for workflow_path in workflows_base_path.iterdir():
            if workflow_path.name.endswith(".yml"):
                with workflow_path.open("rb") as f:
                    workflows_dict[Path(workflow_path.name).stem] = yaml.safe_load(f)

    return workflows_dict
```

Don't assume a specific `Traversable`, like `Path`; for remote repos or in
WebAssembly, this will be a custom `Traversable`.

To register the fixture with repo-review, you need to declare it as an entry-point:

```toml
[project.entry-points."repo_review.fixtures"]
workflows = "my_plugin_package.my_fixture_module:workflows"
```

The name of the entry-point is the fixture name. It is recommended that you name
the fixture function with the same name for simplicity, but it is not required.
