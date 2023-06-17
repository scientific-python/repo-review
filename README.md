# repo-review

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][docs-badge]][docs-link]

[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

<!-- SPHINX-START -->

This is a framework for building checks designed to check to see if a
repository follows guidelines. By itself, it does nothing - it requires at
least one plugin to be installed.

With one or more plugins, it will produce a list of results - green checkmarks
mean this rule is followed, red x’s mean the rule is not. A yellow warning sign
means that the check was skipped because a previous required check failed. Four
output formats are supported; `rich`, `svg`, `html`, and `json`.

`sp-repo-review` provides checks based on the
[Scientific-Python Development Guide][] at [scientific-python/cookie][]. A live
WebAssembly demo using `sp-repo-review` is
[here][repo-review-demo].

## Running repo-review

Repo-review supports running multiple ways:

- From the command line on a local folder
- From the command line on a remote repository on GitHub (`gh:org/repo@branch`)
- From WebAssembly in [Pyodide][] (example in `docs/index.html`)

If the root of a package is not the repository root, pass `--package-dir a/b/c`.

## Configuration

Repo-review supports configuration via `pyproject.toml`:

```toml
[tool.repo-review]
select = ["A", "B", "C100"]
ignore = ["A100"]
```

If `--select` or `--ignore` are given on the command line, they will override
the `pyproject.toml` config.

## Comparison to other frameworks

Repo-review was inspired by frameworks like [Flake8][] and [Ruff][]. It is
primarily different in two ways: It was designed to look at configuration files
rather than Python files; which means it also only needs a subset of the
repository (since most files are not configuration files). And it was designed
to be runnable on external repositories, rather than pre-configured and run
from inside the repository (which it can be). These differences also power the
WebAssembly/remote version, which only needs to make a few API calls to look at
the files that interest the plugin in question.

So if you want to lint Python code, use Flake8 or Ruff. But if you want to
check Flake8 or Ruff's configuration, use repo-review! Generally, repo-review
plugins are more about requiring things to be present, like making use all your
repos have some [pre-commit][] check.

## Development of repo-review and plugins

This project is intended to be fun and easy to develop and design checks for -
it requires and uses Python 3.10, and uses a lot of the new features in 3.9 and
3.10. It's maybe not entirely conventional, but it enables very simple plugin
development. It works locally, remotely, and in WebAssembly (using
[Pyodide][]).

There are a few key designs that are very useful and make this possible. First,
all paths are handled as Traversables. This allows a simple Traversable
implementation based on `open_url` to provide a web interface for use in the
webapp. It also would allow `zipfile.Path` to work just as well, too - no need
to extract.

Checks can request fixtures (like [pytest][]) as arguments. Check files can add new
fixtures as needed. Fixtures are are specified with entry points, and take any
other fixture as arguments as well - the `root` and `package` fixtures
represents the root of the repository and of the package you are checking,
respectively, and are the basis for all other fixtures. `pyproject` is provided
as well. Checks are specified via an entrypoint that returns a dict of checks;
this also can accept fixtures, allowing dynamic check listings.

Check files do not depend on the main library, and can be extended (similar to
Flake8). You register new check files via entry-points - so extending this is
with custom checks or custom fixtures is easy and trivial. There's no need to
subclass or do anything with the base library - no dependency required.

Checks are as simple as possible so they are easy to write. A check is a class
with the name (1-2 letters + number) and a docstring (the check message). It
should define a set of `requires` with any checks it depends on (by name), and
have a check classmethod. The docstring of this method is the failure message,
and supports substitution. Arguments to this method are fixtures, and `root` or
`package` are built-in providing a Traversable. Any other fixtures are available
by name. A new fixture can use any other fixtures, and can produce anything;
fixtures are topologically sorted, pre-computed and cached.

The runner will topologically sort the checks, and checks that do not run will
get a `None` result and the check method will not run. The front-end (Rich
powered CLI or Pyodide webapp) will render the markdown-formatted check
docstring only if the result is `False`.

## Links

This project inspired [Try-PyHF](https://kratsg.github.io/try-pyhf/), an
interface for a High Energy Physics package in Scikit-HEP.

This project inspired [abSENSE](https://princetonuniversity.github.io/abSENSE/), an
web interface to abSENSE.

This was developed for [Scikit-HEP][] before moving to Scientific-Python.

<!-- prettier-ignore-start -->

[actions-badge]: https://github.com/scientific-python/repo-review/workflows/CI/badge.svg
[actions-link]: https://github.com/scientific-python/repo-review/actions
[docs-badge]: https://readthedocs.org/projects/repo-review/badge/?version=latest
[docs-link]: https://repo-review.readthedocs.io/en/latest/?badge=latest
[flake8]: https://flake8.pycqa.org
[pre-commit]: https://pre-commit.com
[pyodide]: https://pyodide.org
[pypi-link]: https://pypi.org/project/repo-review/
[pypi-platforms]: https://img.shields.io/pypi/pyversions/repo-review
[pypi-version]: https://badge.fury.io/py/repo-review.svg
[pytest]: https://pytest.org
[repo-review-demo]: https://scientific-python.github.io/repo-review
[ruff]: https://beta.ruff.rs
[scientific-python development guide]: https://learn.scientific-python.org/development
[scientific-python/cookie]: https://github.com/scientific-python/cookie
[scikit-hep]: https://scikit-hep.org

<!-- prettier-ignore-end -->
