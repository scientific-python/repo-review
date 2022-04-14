from __future__ import annotations

import shutil
from pathlib import Path

import nox

DIR = Path(__file__).parent.resolve()

nox.options.sessions = ["lint", "pylint", "tests"]


@nox.session(reuse_venv=True)
def run(session: nox.Session) -> None:
    """
    Run the program
    """

    session.install("-e", ".[cli]")
    session.run("python", "-m", "scikit_hep_repo_review", *session.posargs)


@nox.session
def lint(session: nox.Session) -> None:
    """
    Run the linter.
    """
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session
def pylint(session: nox.Session) -> None:
    """
    Run PyLint.
    """
    # This needs to be installed into the package environment, and is slower
    # than a pre-commit check
    session.install(".", "pylint")
    session.run("pylint", "src", *session.posargs)


@nox.session
def tests(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    session.install(".[test]")
    session.run("pytest", *session.posargs)


@nox.session(reuse_venv=True)
def build(session: nox.Session) -> None:
    """
    Build an SDist and wheel.
    """

    build_p = DIR.joinpath("build")
    if build_p.exists():
        shutil.rmtree(build_p)

    session.install("build")
    session.run("python", "-m", "build")


@nox.session(reuse_venv=True)
def serve(session: nox.Session) -> None:
    """
    Build (maybe --serve) the website.
    """
    session.install("build")
    session.run("python", "-m", "build", "--wheel", "--outdir", "web")

    if "--serve" in session.posargs:
        session.cd("web")
        session.run("python", "-m", "http.server", "8080")
