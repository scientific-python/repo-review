from __future__ import annotations

import importlib
import importlib.metadata
import inspect
import os
from pathlib import Path
from typing import Any

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

html_theme_options: dict[str, Any] = {
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/scientific-python/repo-review",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
    "source_repository": "https://github.com/scientific-python/repo-review/",
    "source_branch": "main",
    "source_directory": "docs/",
}

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
