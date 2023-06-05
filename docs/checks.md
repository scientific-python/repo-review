# Checks

Plugins provide checks; repo-review requires at least one plugin providing checks to operate; there are no built-in checks.

## Writing a check

A check is an object following a specific Protocol:

```python
class Check:
    """
    Short description.
    """

    family: str
    requires: Set[str] = frozenset()  # Optional
    url: str = ""  # Optional

    def check(self) -> bool | str:
        """
        Error message if returns False.
        """
        ...
```

You need to implement `family`, which is a string indicating which family it is
grouped under, and `check()`, which can take [](fixtures), and returns `True` if
the check passes, or `False` if the check fails. If you want a dynamic error
explanation instead of the `check()` docstring, you can return a non-empty
string from the check instead of `False`. Docstrings/error messages can access
their own object with `{self}` and name with `{name}`. The error message is in
markdown format.

If the check named in `requires` does not pass, the check is skipped.

A suggested convention for easily writing checks is as follows:

```python
class General:
    family = "general"


class PY001(General):
    "Has a pyproject.toml"

    @staticmethod
    def check(package: Traversable) -> bool:
        """
        All projects should have a `pyproject.toml` file to support a modern
        build system and support wheel installs properly.
        """
        return package.joinpath("pyproject.toml").is_file()


class PyProject:
    family = "pyproject"


class PP002(PyProject):
    "Has a proper build-system table"

    requires = {"PY001"}
    url = "https://peps.python.org/pep-0517"

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        """
        Must have `build-system.requires` *and* `build-system.backend`. Both
        should be present in all modern packages.
        """

        match pyproject:
            case {"build-system": {"requires": list(), "build-backend": str()}}:
                return True
            case _:
                return False
```

Key features:

- The base class allows setting the family once, and gives a quick shortcut for accessing all the checks via `.__subclasses__`.
- The name of the check class itself is the check code.
- The check method is a classmethod since it has no state.
- Likewise, all attributes are set on the class (`family`, `requires`, `url`) since there is no state.
- `requries` is used so that the pyproject checks are skipped if the pyproject file is missing.

## Registering checks

You register checks with a function that returns a dict of checks, with the code
of the check (letters + number) as the key, and check instances as the values.
This function can take [](fixtures), as well, allowing customization of checks
based on repo properties.

Here is the suggested function for the above example:

```python
def repo_review_checks() -> dict[str, General | PyProject]:
    return {p.__name__: p() for p in General.__subclasses__()} | {
        p.__name__: p() for p in PyProject.__subclasses__()
    }
```

You tell repo review to use this function via an entry-point:

```toml
[project.entry-points."repo_review.checks"]
general_pyproject = "my_plugin_package.my_checks_module:repo_review_checks"
```

The entry-point name doesn't matter.
