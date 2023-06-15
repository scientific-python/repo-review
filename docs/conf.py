import importlib.metadata
import os

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
