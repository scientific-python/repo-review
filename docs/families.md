# Families

Families are a set of simple strings that group together similar checks. You can
provide a nicer user experience, however, by adding a mapping of information for
repo-review to improve the ordering and display of families.

You can construct a dict with the following optional keys:

```python
class Family(typing.TypedDict, total=False):
    name: str  # defaults to key
    order: int  # defaults to 0
    description: str  # defaults to empty
```

The `name` will be shown instead if given. The families will be sorted by
`order` then key. And a `description` will be shown after the name if provided;
it is expected to be in Markdown format.

```{versionadded} 0.9
Descriptions are now supported.
```

Then you can provide a function that maps family strings to this extra information:

```python
def get_families() -> dict[str, Family]:
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

```{versionchanged} 0.9
You can request fixtures for this function, like all the other collection functions.
This allows dynamic descriptions based on repo contents.
```

And finally, you register this function as an entry-point:

```toml
[project.entry-points."repo_review.families"]
families = "my_plugin_package.my_family_module:get_families"
```

The entry-point name doesn't matter.
