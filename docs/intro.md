# Installing / Getting Started

Repo-review is a framework for running checks from plugins. You need to have a
plugin for repo-review to do anything. The examples below use `sp-repo-review`
as an example. You can also use the WebAssembly version from web pages, [like
the demo page](https://scientific-python.github.io/repo-review).

## Installing

`repo-review` (and presumably, most/all plugins) are available from pip. If you
want to run a single plugin that depends on repo-review, then the easiest way
to use it is:

```bash
pipx run sp-repo-review .
```

This uses [pipx][] (pip for executables) to download the plugin and all of it's
dependencies (including repo-review itself) into a temporary virtual
environment (cached for a week), then runs it.

Any other way you like installing things works too, including `pipx install`
and `pip install`.

Plugins are also encouraged to support pre-commit and GitHub Actions.

## Running checks

You can run checks with (`pipx run`) `repo-review <path>` or `python -m
repo_review <path>`. See [](./cli.md) for command-line options.

## Configuring

You can explicitly list checks to select or skip in your `pyproject.toml`:

```toml
[tool.repo-review]
select = [...]
ignore = [...]
```

## Pre-commit

You can also use this from pre-commit:

```yaml
- repo: https://github.com/scientific-python/repo-review
  rev: <version>
  hooks:
    - id: repo-review
      additional_dependencies: ["sp-repo-review==<version>"]
```

(Insert the current version above, and ideally pin the plugin version, as long
as you have a way to auto-update it.)

Though check your favorite plugin, which might directly support running from
pre-commit, and then pre-commit's pinning system will pin on your plugin,
rather than the framework (repo-review).

## GitHub Actions

```yaml
- uses: scientific-python/repo-review@<version>
  with:
    plugins: sp-repo-review
```

(Insert the current version above, optionally pin the plugin version, as long
as you have a way to auto-update it.)

Though check your favorite plugin, which might directly support running from
GitHub Actions, and then Dependabot's updating system will pin on your plugin,
rather than the framework (repo-review).

[pipx]: https://pypa.github.io/pipx
