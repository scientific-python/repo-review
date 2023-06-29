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

    def check(self) -> bool | str | None:
        """
        Error message if returns False.
        """
        ...
```

You need to implement `family`, which is a string indicating which family it is
grouped under, and `check()`, which can take [](./fixtures.md), and returns `True` if
the check passes, or `False` if the check fails. If you want a dynamic error
explanation instead of the `check()` docstring, you can return a non-empty
string from the check instead of `False`. Returning `None` makes a check
"skipped". Docstrings/error messages can access their own object with `{self}`
and check name with `{name}` (these are processed with `.format()`, so escape `{}`
as `{{}}`). The error message is in markdown format.

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
This function can take [](./fixtures.md), as well, allowing customization of checks
based on repo properties.

Here is the suggested function for the above example:

```python
def repo_review_checks() -> dict[str, General | PyProject]:
    general = {p.__name__: p() for p in General.__subclasses__()}
    pyproject = {p.__name__: p() for p in PyProject.__subclasses__()}
    return general | pyproject
```

You tell repo-review to use this function via an entry-point:

```toml
[project.entry-points."repo_review.checks"]
general_pyproject = "my_plugin_package.my_checks_module:repo_review_checks"
```

The entry-point name doesn't matter.

## Customizable checks

You can customize checks, as well, using this system. Here is an example,
using the (synthetic) case were we want to add a check based on the build-backend,
and we want to require that `tool.<build-backend>` is present, where this
depends on which build-backend we recognized. (Don't actually do this, you don't
have to have a tool section to use the backends shown below!)

```python
import dataclasses
from typing import ClassVar


@dataclasses.dataclass
class PP003(PyProject):
    "Has a tool section for the {self.name!r} build backend"

    requires: ClassVar[set[str]] = {"PY001"}
    url: ClassVar[str] = "https://peps.python.org/pep-0517"

    name: str

    def check(self, pyproject: dict[str, Any]) -> bool:
        """
        Must have a {self.name!r} section.
        """
        match pyproject:
            case {"tool": {self.name: object()}}:
                return True
            case _:
                return False


def repo_review_checks(pyproject: dict[str, Any]) -> dict[str, PyProject]:
    backends = {
        "setuptools.build_api": "setuptools",
        "scikit_build_core.build": "scikit-build",
    }
    match pyproject:
        case {"build-system": {"build-backend": str(x)}} if x in backends:
            return {"PP003": PP003(name=backends[x])}
        case _:
            return {}
```

### Handling empty generation

If repo-review is listing all checks, a
{class}`repo_review.ghpath.EmptyTraversable` is passed for `root` and
`package`. This will appear to be a directory with no contents. If you have
conditional checks, you should handle this case to support being listed as a
possible check. As a helper for this case, a
{func}`~repo_review.fixtures.list_all` fixture is provided that returns {obj}`True`
only if a list-all operation is being performed. The above can then be written:

```python
def repo_review_checks(
    list_all: bool, pyproject: dict[str, Any]
) -> dict[str, PyProject]:
    backends = {
        "setuptools.build_api": "setuptools",
        "scikit_build_core.build": "scikit-build",
    }

    if list_all:
        return {"PP003": PP003(name="<backend>")}

    match pyproject:
        case {"build-system": {"build-backend": str(x)}} if x in backends:
            return {"PP003": PP003(name=backends[x])}
        case _:
            return {}
```

```{versionadded} 0.8
The {func}`~repo_review.fixtures.list_all` fixture.
```
