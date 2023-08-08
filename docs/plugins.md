# Writing a plugin

To write a plugin for repo-review, you should provide one or more [](./checks.md).
You can also add new [](./fixtures.md), and customize [](./families.md) with sorting and
nicer display names. When writing a plugin, you should also do a few things
when setting up the package. These suggestions assume you are using a
standardized backend, such as `hatchling`, `flit-core`, `pdm-backend`, or
`setuptools>=61`. If you are using some other build backend, please adjust
accordingly.

## Entry points

You need to specify entry points as listed in the fixtures/checks/families
pages in order for repo-review to use your plugin. In summary, they look like this:

```toml
[project.entry-points]
"repo_review.fixtures".fixture_name = "my_plugin_package.my_fixture_module:fixture_name"
"repo_review.checks".anything = "my_plugin_package.my_checks_module:repo_review_checks"
"repo_review.families".anything = "my_plugin_package.my_family_module:repo_review_families"
```

Only the fixture entry-point name matters (it's the name of the fixture);
checks and families produce multiple items, so they can be under any name.

## Testing

If you'd like to test your plugin, add `repo-review; python_version>="3.10"` to
your test dependencies (if your package is only a plugin for repo-review, you
don't need the Python limit there). Then add some valid and/or invalid examples
to your test suite (you can write them out during testing, as well, which is
what is shown below). Then a test looks like this:

```python
from pathlib import Path

import pytest

repo_review_processor = pytest.importorskip("repo_review.processor")


def test_has_tool_ruff(tmp_path: Path) -> None:
    # In this example, tool.ruff is required to be present by this plugin
    d = tmp_path / "some_package"
    d.mkdir()
    d.joinpath("pyproject.toml").write_text("[tool.ruff]")
    processed = repo_review_processor.process(d)
    assert all(r.result for r in processed.results), f"{processed.results}"
```

You have `processed.results` and `processed.families` from the return of
{func}`~repo_review.processor.process` to work with. You can also run
{func}`~repo_review.processor.collect_all` to get `.fixtures`, `.checks`, and
`.families`.

## An existing package

Since writing a plugin does not require depending on repo-review, you can also
integrate your plugins into existing packages. If that's the case, you only
need to add your entry-points (see the links above), and tests.

## A plugin-only package

If you are writing a package that is only a plugin for repo-review, there are
several things you can do if you'd like a user to be able to run the package
directly. `sp-repo-review` does these things to make it easy to run as a
complete package. This design is mostly useful if you are providing a complete
set of checks for an ecosystem.

### Avoiding CLI requirements on WebAssembly usage

Repo-review uses `repo-review[cli]` to keep CLI requirements from being
included in the base package, and plugins can follow this if they want to be
used directly:

```toml
[project.optional-dependencies]
cli = [
  "repo-review[cli]",
]
```

### Custom entry-point (optional)

If you want to provide your own CLI name, you can
add this to your `pyproject.toml`:

```toml
[project.scripts]
my_plugin_cli_name = "repo_review.__main__:main"
```

However, there is no benefit over just running `repo-review`, so this is not
really recommended.

### Pipx run support (recommended)

If you chose not to add a custom command-line entry point (above), you should
still support `pipx run <your-plugin>`, and you can do that by adding the
following to your `pyproject.toml`:

```toml
[project.entry-points."pipx.run"]
my_plugin_package_name = "repo_review.__main__:main"
```

### Pre-commit support

You can add a `.pre-commit-hooks.yaml` file with contents similar to this to
natively support pre-commit:

```yaml
id: repo-review
name: repo-review
description: Check for configuration best practices
entry: repo-review
language: python
types_or: [text]
minimum_pre_commit_version: 2.9.0
```

You can also narrow down the `files` / `types_or` if your plugin only supports
a subset of files (which most should).

### GitHub Actions support

You can add an `action.yml` file similar to this to natively support GitHub
Actions & dependabot:

```yaml
name: repo-review
description: "Runs repo-review"
inputs:
  package-dir:
    description: "Path to Python package, if different from repo root"
    required: false
    default: ""

runs:
  using: composite
  steps:
    - uses: actions/setup-python@v4
      id: python
      with:
        python-version: "3.11"
        update-environment: false

    - name: Run repo-review
      shell: bash
      run: >
        pipx run
        --python '${{ steps.python.outputs.python-path }}'
        --spec '${{ github.action_path }}[cli]'
        repo-review .
        --format html
        --stderr rich
        --select "${{ inputs.select }}"
        --ignore "${{ inputs.ignore }}"
        --package-dir "${{ inputs.package-dir }}"
        >> $GITHUB_STEP_SUMMARY
```
