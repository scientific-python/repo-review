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
pipx run <plugin-name>[cli] .
```

This uses [pipx][] (pip for executables) to download the plugin and all of its
dependencies (including repo-review itself) into a temporary virtual
environment (cached for a week), then runs it. For example:

```bash
pipx run sp-repo-review[cli] .
```

You can also use pipx install:

```bash
pipx install repo-review[cli]
pipx inject repo-review <plugin(s)>
repo-review .
```

Any other way you like installing things works too, including `pip install` and `uv pip install`.
Remember the `[cli]` extra if you are using the command line
interface.

A conda-forge package is also available. You can use `conda`, `mamba`, `micromamba`, or `pixi` to
install from the conda-forge channel.

Plugins are also encouraged to support pre-commit and GitHub Actions.

## Running checks

You can run checks with (`pipx run`) `repo-review <path>` or `python -m
repo_review <path>`. See [](./cli.md) for command-line options.

## Configuring

You can explicitly list checks to select or skip in your `pyproject.toml`:

```toml
[tool.repo-review]
select = ["A", "B", "C100"]
ignore = ["A100"]
```

You can list the letter prefix or the exact check name. The ignore list can also
be a table, with reasons for values. These will be shown explicitly in the report if
a reason is given.

```toml
[tool.repo-review.ignore]
A = "Skipping this whole family"
B101 = "Skipping this specific check"
C101 = ""  # Hidden from report, like a normal ignore
```

If `--select` or `--ignore` are given on the command line, they will override
the `pyproject.toml` config. You can use `--extend-select` and `--extend-ignore`
on the command line to extend the `pyproject.toml` config. These CLI options
are comma separated.

## Pre-commit

You can also use this from pre-commit:

```yaml
- repo: https://github.com/scientific-python/repo-review
  rev: <version>
  hooks:
    - id: repo-review
      additional_dependencies: ["repo-review[cli]", "sp-repo-review==<version>"]
```

(Insert the current version above, and ideally pin the plugin version, as long
as you have a way to auto-update it.)

Though check your favorite plugin, which might directly support running from
pre-commit, and then pre-commit's pinning system will pin on your plugin,
rather than the framework (repo-review).

:::{warning}

This currently has a couple of weird quirks. Pre-commit will not report the
correct version for repo-review (it's always 0.1), and it will lose the `cli`
requirements if you add additional dependencies (which you always do, it's a
plugin framework, so it needs plugins). To counter this, plugins can avoid
lower bounds and you can manually add `repo-review[cli]`, as seen above, or
plugins can provide their own hooks (like sp-repo-review also does).

In the future, a mirror will be set up so that we can avoid these issues.

:::

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

[pipx]: https://pipx.pypa.io
