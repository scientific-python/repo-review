# Writing a plugin

To write a plugin for repo-review, you should provide one or more [](./checks.md).
You can also add new [](./fixtures.md), and customize [](./families.md) with sorting and
nicer display names. When writing a plugin, you should also do a few things
when setting up the package. These suggestions assume you are using a
standardized backend, such as `hatchling`, `flit-core`, `pdm-backend`, or
`setuptools>=61`. If you are using some other build backend, please adjust
accordingly.

## Avoiding CLI requirements on WebAssembly usage

Repo-review uses `repo-review[cli]` to keep CLI requirements from being
included in the base package, and plugins can follow this if they want to be
used directly:

```toml
[project.optional-dependencies]
cli = [
  "repo-review[cli]",
]
```

## Custom entry-point (optional)

If you want to provide your own CLI name, you can
add this to your `pyproject.toml`:

```toml
[project.scripts]
my_plugin_cli_name = "repo_review.__main__:main"
```

However, there is no benefit over just running `repo-review`, so this is not
really recommended.

## Pipx run support (recommended)

If you chose not to add a custom command-line entry point (above), you should
still support `pipx run <your-plugin>`, and you can do that by adding the
following to your `pyproject.toml`:

```toml
[project.entry-points."pipx.run"]
my_plugin_package_name = "repo_review.__main__:main"
```

## Pre-commit support

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

## GitHub Actions support

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
