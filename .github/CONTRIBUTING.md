See the [Scientific-Python Development Pages][] for a
detailed description of best practices for developing Scikit-HEP packages.

[scientific-python development pages]: https://learn.scientific-python.org/development

## Quick development

The fastest way to start with development is to use hatch. If you don't have
hatch, you can use `pipx run hatch` to run it without installing, or `pipx
install hatch`. If you don't have pipx (pip for applications), then you can
install with with `pip install pipx` (the only case were installing an
application with regular pip is reasonable). If you use macOS, then pipx and
hatch are both in brew, use `brew install pipx hatch`. Hatch 1.10+ is required.

Here are some common tasks you might want to run:

```console
$ hatch run lint:lint        # all linters (pre-commit)
$ hatch run pylint:lint      # pylint
$ hatch fmt                  # just format & basic lint
$ hatch tests                # run the tests
$ hatch build                # build SDist and wheel
$ hatch run docs:serve       # build and serve the docs
$ hatch run docs:html        # just build the docs
$ hatch run docs:man         # build manpage
$ hatch run docs:linkcheck   # check for broken links
$ hatch run api-docs:build   # rebuild the API docs
$ hatch run webapp:serve     # serve the webapp
$ hatch run example:repo-review <args> # Run an example
```

Hatch handles everything for you, including setting up an temporary virtual
environment.

Using `uv run` directly is also supported.

## Setting up a development environment manually

You can set up a development environment in `.venv` by running:

```bash
uv sync
```

Or just prefix every command by `uv run`.

# Post setup

You should prepare pre-commit, which will help you by checking that commits
pass required checks:

```bash
pip install pre-commit # or brew install pre-commit on macOS
pre-commit install # Will install a pre-commit hook into the git repo
```

You can also/alternatively run `pre-commit run` (changes only) or `pre-commit run --all-files` to check even without installing the hook.

## Testing

Use pytest to run the unit checks:

```bash
pytest
```

## Building docs

You can build the docs using:

```bash
hatch run docs:docs
```

You can see a preview with:

```bash
hatch run docs:serve
```

You can rebuild the API docs with:

```bash
$ hatch run api-docs:build
```

## Pre-commit

This project uses pre-commit for all style checking. While you can run it with
hatch, this is such an important tool that it deserves to be installed on its
own. Install pre-commit and run:

```bash
pre-commit run -a
```

to check all files.

## Running DevContainer

You can use DevContainer, such as in GitHub Codespaces or locally. Hatch and a
local install will be available.
