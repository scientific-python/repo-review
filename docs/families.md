# Families

Families are a set of simple strings that group together similar checks. You can provide a nicer user experience, however, by adding a mapping of information for repo-review to improve the ordering and display of families.

You can construct a dict with the following optional keys:

```python
class Family(typing.TypedDict, total=False):
    name: str  # defaults to key
    order: int  # defaults to 0
```

Then you can provide a function that maps family strings to this extra information:

```python
def get_familes() -> dict[str, Family]:
    return {
        "general": Family(
            name="General",
            order=-3,
        ),
        "pyproject": Family(
            name="PyProject",
            order=-2,
        ),
    }
```

And finally, you register this function as an entry-point:

```toml
[project.entry-points."repo_review.families"]
families = "my_plugin_package.my_family_module:get_families"
```

The entry-point name doesn't matter.

```{admonition} Fixtures
Unlike almost all other parts of the API, the family function does not support
fixtures. This could be added if there is a need, but usually not needed - if a
check is not present from a family, the family will not be displayed.
```
