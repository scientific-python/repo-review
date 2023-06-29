# Programmatic usage

You can use repo-review from other Python code, as well, such as with [`cog`][].

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

You can also get a list of checks:

```python
collected = repo_review.processor.collect_all()
```

This returns a {class}`~repo_review.processor.CollectionReturn`. You can access the `.checks`,
`.families`, and `.fixtures`, all are dicts.

Here's an example of using this to fill out a README with [`cog`][]:

```md
<!-- [[[cog
import itertools

from repo_review.processor import collect_all

collected = collect_all()
print()
for family, grp in itertools.groupby(collected.checks.items(), key=lambda x: x[1].family):
    print(f'### {collected.families[family].get("name", family)}')
    for code, check in grp:
        url = getattr(check, "url", "").format(self=check, name=code)
        link = f"[`{code}`]({url})" if url else f"`{code}`"
        print(f"- {link}: {check.__doc__}")
    print()
]]] -->
<!-- [[[end]]] -->
```

[`cog`]: https://nedbatchelder.com/code/cog
