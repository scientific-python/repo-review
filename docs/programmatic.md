# Programmatic usage

You can use repo-review from other Python code, as well, such as with
[`cog`][]. Also see [](./webapp.md).

## Processors

The core of repo-review is the {func}`repo_review.processor.process` function. Use it like this:

```python
root = Path(".")
processed = repo_review.processor.process(root, select=set(), ignore=set(), subdir=".")
```

The `root` parameter can be any
{class}`~importlib.resources.abc.Traversable`. The keyword arguments are
optional (defaults are shown). This returns a {class}`~typing.NamedTuple`,
{class}`~repo_review.processor.ProcessReturn`. `.families` is a dict mapping
family names to {class}`~repo_review.families.Family` and `.results` is a list
of {class}`~repo_review.processor.Result`s. If you want, you can turn the results
list into a simple list of dicts with {func}`~repo_review.processor.as_simple_dict`.

### Getting the family name

A common requirement is getting the "nice" family name given the short name.
There's a tiny helper for this, {func}`repo_review.families.get_family_name`:

```python
family_name = get_family_name(families, family)
```

```{versionadded} 0.8

```

## Listing all possible checks

You can also get a list of checks:

```python
collected = repo_review.processor.collect_all()
```

This returns a {class}`~repo_review.processor.CollectionReturn`. You can access the `.checks`,
`.families`, and `.fixtures`, all are dicts.

```{versionadded} 0.8

```

### Getting the check properties

A common requirement is getting the url from the
{class}`~repo_review.checks.Check`. While a
{class}`~repo_review.processor.Result` already has the URL fully rendered,
checks do not; they are directly returned by plugins. There's a tiny helper
for this, {func}`repo_review.checks.get_check_url`:

```python
url = get_check_url(name, check)
```

```{versionadded} 0.8

```

You can also use a helper to get `__doc__` with the correct substitution, as well:

```python
doc = get_check_description(name, check)
```

```{versionadded} 0.8

```

### Example: cog

Here's an example of using this to fill out a README with [`cog`][], formatting all possible checks in markdown:

```md
<!-- [[[cog
import itertools

from repo_review.processor import collect_all
from repo_review.checks import get_check_url, get_check_description
from repo_review.families import get_family_name

collected = collect_all()
print()
for family, grp in itertools.groupby(collected.checks.items(), key=lambda x: x[1].family):
    print(f'### {get_family_name(collected.families, family)}')
    for code, check in grp:
        url = get_check_url(code, check)
        link = f"[`{code}`]({url})" if url else f"`{code}`"
        print(f"- {link}: {get_check_description(code, check)}")
    print()
]]] -->
<!-- [[[end]]] -->
```

[`cog`]: https://nedbatchelder.com/code/cog
