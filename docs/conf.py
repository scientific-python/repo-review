import importlib
import importlib.metadata
import inspect
import os
from pathlib import Path

import repo_review

DIR = Path(__file__).parent.resolve()

project = "repo-review"
copyright = "2022, Henry Schreiner"
author = "Henry Schreiner"
version = importlib.metadata.version("repo-review").split("+")[0]
release = version

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinxcontrib.programoutput",
    "sphinx_github_changelog",
    "sphinxext.opengraph",
    "sphinx.ext.linkcode",
]

source_suffix = [".rst", ".md"]

exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

html_theme = "furo"

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

nitpick_ignore = [
    ("py:class", "_io.StringIO"),
    ("py:class", "_io.BytesIO"),
    ("py:class", "repo_review.fixtures.T"),
]

always_document_param_types = True

sphinx_github_changelog_token = os.environ.get("GITHUB_API_TOKEN")

commit = os.environ.get("READTHEDOCS_GIT_COMMIT_HASH", "main")
code_url = "https://github.com/scientific-python/repo-review/blob"

linkcheck_ignore = [r"https://pypi.org/project/repo-review/v0\.[23456]"]


def linkcode_resolve(domain: str, info: dict[str, str]) -> str | None:
    if domain != "py":
        return None

    mod = importlib.import_module(info["module"])
    if "." in info["fullname"]:
        objname, attrname = info["fullname"].split(".")
        obj = getattr(mod, objname)
        try:
            # object is a method of a class
            obj = getattr(obj, attrname)
        except AttributeError:
            # object is an attribute of a class
            return None
    else:
        obj = getattr(mod, info["fullname"])

    try:
        file = Path(inspect.getsourcefile(obj))
        lines = inspect.getsourcelines(obj)
    except TypeError:
        # e.g. object is a typing.Union
        return None
    try:
        mod = Path(inspect.getsourcefile(repo_review)).parent
        file = file.relative_to(mod)
    except ValueError:
        return None
    start, end = lines[1], lines[1] + len(lines[0]) - 1

    return f"{code_url}/{commit}/src/repo_review/{file}#L{start}-L{end}"
