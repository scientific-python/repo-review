import importlib.metadata

project = "repo-review"
copyright = "2022, Henry Schreiner"
author = "Henry Schreiner"
release = importlib.metadata.version("repo-review")

extensions = [
    "myst_parser",
    "sphinxcontrib.programoutput",
    "sphinxext.opengraph",
    "sphinx_copybutton",
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
