# repo-review

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][docs-badge]][docs-link]

[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

<!-- SPHINX-START -->

This is a framework for building checks designed to check to see if a
repository follows guidelines. By itself, it does nothing - it requires at
least one plugin to be installed.

With one or more plugins, it will produce a list of results - green checkmarks
mean this rule is followed, red x’s mean the rule is not. A yellow warning sign
means that the check was skipped because a previous required check failed. Four
output formats are supported: `rich`, `svg`, `html`, and `json`.

## Plugins

These are some known plugins. Feel free to request your plugin be added to this
list.

- [sp-repo-review][]: Checks based on the [Scientific-Python Development Guide][] at [scientific-python/cookie][].
- [validate-pyproject][]: Adds a check to validate pyproject sections, also supports plugins (like [validate-pyproject-schema-store][]).

`repo-review` itself also acts as a plugin for [validate-pyproject][], allowing
you to validate the `[tool.repo-review]` section of your `pyproject.toml`.

A live WebAssembly demo using [sp-repo-review][] and [validate-pyproject][] is
[available here][repo-review-demo].

## Running repo-review

Repo-review supports running multiple ways:

- [From the command line][cli] on a local folder (or multiple folders).
- From the command line on a remote repository on GitHub (`gh:org/repo@branch`)
- [From WebAssembly][webapp] in [Pyodide][] (example in `docs/index.html`)
- [From pre-commit][intro-pre-commit] (see caveats there)
- [From GitHub Actions][intro-github-actions]
- [From Python][programmatic-usage]

When installing, make sure you also install at least one plugin, as
`repo-review` has no integrated checks. If you are using the command line
interface, make sure you include the `cli` extra (`repo-review[cli]`). Some
plugins, like `sp-repo-review`, support running directly, such as:

```bash
pipx run sp-repo-review[cli] <args>
```

If the root of a package is not the repository root, pass `--package-dir a/b/c`.

## Configuration

Repo-review [supports configuration][intro-configuring] via `pyproject.toml`:

```toml
[tool.repo-review]
select = ["A", "B", "C100"]
ignore = ["A100"]
```

The ignore list can also be a table, with reasons for values.

If `--select` or `--ignore` are given on the command line, they will override
the `pyproject.toml` config. You can use `--extend-select` and `--extend-ignore`
on the command line to extend the `pyproject.toml` config. These CLI options
are comma separated.

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
plugins are more about requiring things to be present, like making sure all your
repos have some [pre-commit][] check.

## Development of repo-review and plugins

This project is intended to be fun and easy to develop and design checks for -
it requires and uses Python 3.10+, and uses a lot of the new features in 3.9 and
3.10. It's maybe not entirely conventional, but it enables very simple plugin
development. It works locally, remotely, and in WebAssembly (using
[Pyodide][]). [See the docs][writing-a-plugin].

There are a few key designs that are very useful and make this possible. First,
all paths are handled as Traversables. This allows a simple Traversable
implementation based on `open_url` to provide a web interface for use in the
webapp. It also would allow `zipfile.Path` to work just as well, too - no need
to extract.

[Checks][] can request [fixtures][] (like [pytest][]) as arguments. Check files
can add new fixtures as needed. Fixtures are specified with entry points,
and take any other fixture as arguments as well - the `root` and `package`
fixtures represents the root of the repository and of the package you are
checking, respectively, and are the basis for the other fixtures, which are
topologically sorted and cached. `pyproject` is provided as well. Checks are
specified via an entrypoint that returns a dict of checks; this can also can
accept fixtures, allowing dynamic check listings.

Check files do not depend on the main library, and can be extended (similar to
Flake8). You register new check files via entry-points - so extending this is
with custom checks or custom fixtures is easy and trivial. There's no need to
subclass or do anything with the base library - no dependency on repo-review required.

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

Checks are organized by [Families][]. A plugin can customize the display name,
change the sort order, and add an optional (dynamic) description. Like the other
collection functions, the family entry-point also supports fixtures.

## Links

This project inspired [Try-PyHF](https://kratsg.github.io/try-pyhf/), an
interface for a High Energy Physics package in Scikit-HEP.

This project inspired [abSENSE](https://princetonuniversity.github.io/abSENSE/), a
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
[sp-repo-review]: https://pypi.org/project/sp-repo-review
[validate-pyproject]: https://validate-pyproject.readthedocs.io
[validate-pyproject-schema-store]: https://github.com/henryiii/validate-pyproject-schema-store
[conda-badge]: https://img.shields.io/conda/vn/conda-forge/repo-review
[conda-link]: https://github.com/conda-forge/repo-review-feedstock

[intro-pre-commit]: https://repo-review.readthedocs.io/en/latest/intro.html#pre-commit
[intro-github-actions]: https://repo-review.readthedocs.io/en/latest/intro.html#github-actions
[cli]: https://repo-review.readthedocs.io/en/latest/cli.html
[programmatic-usage]: https://repo-review.readthedocs.io/en/latest/programmatic.html
[webapp]: https://repo-review.readthedocs.io/en/latest/webapp.html
[intro-configuring]: https://repo-review.readthedocs.io/en/latest/intro.html#configuring
[writing-a-plugin]: https://repo-review.readthedocs.io/en/latest/plugins.html
[fixtures]: https://repo-review.readthedocs.io/en/latest/fixtures.html
[checks]: https://repo-review.readthedocs.io/en/latest/checks.html
[families]: https://repo-review.readthedocs.io/en/latest/families.html
[changelog]: https://repo-review.readthedocs.io/en/latest/changelog.html
[api]: https://repo-review.readthedocs.io/en/latest/api/repo_review.html


<!-- prettier-ignore-end -->
