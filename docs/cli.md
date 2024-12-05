# CLI

Repo-review has a CLI interface.

```{program-output} python -m repo_review --help

```

## Remote inputs

You can input a local directory, or you can input a GitHub repository
via `gh:org/repo@branch`. This will use the Web API and won't download
the whole repository. If the root of a package is not in the repository root,
pass `--package-dir <path>`.

## Output formats

There are four output formats; `rich` produces great terminal output, `svg`
produces an SVG based on the rich output, `html` produces a custom HTML report,
and `json` produces an output that can be processed easily. To make it easier to
support tools like GitHub Actions, there is also a `--stderr FORMAT` output
option that produces the selected format on stderr as well, and disables
producing terminal escape codes on stdout, even if `FORCE_COLOR` is set. This
was designed to allow you to redirect stdout to a file, and still get a report
in the logs.

JSON output looks like this:

```json
{
  "status": "passed",
  "families": {
    "pyproject": {},
    "general": {}
  },
  "checks": {
    "PY001": {
      "family": "general",
      "description": "Has a pyproject.toml",
      "result": true,
      "err_msg": "",
      "url": ""
    },
    "PY002": {
      "family": "general",
      "description": "Has a README.(md|rst) file",
      "result": true,
      "err_msg": "",
      "url": ""
    }
  }
}
```

HTML format is designed to look good in a markdown editor, like GitHub's
actions output or when pasted into a GitHub issue or comment.

## Limiting output

By default, all checks are printed out. You can remove the passing checks with
`--show=errskip`, or the skipped and passing checks with `--show=err`. Headings
for families with custom descriptions will still be shown.

```{versionadded} 0.10

```

## Multiple repos

You can input multiple repos. If you have more than one repo as input, the output formats change slightly:

- Rich/SVG add a banner on the top of each with the folder name of the repo.
- HTML puts each repo in a `<details>` block, with the repo folder name and error count.
- JSON adds an out dictionary keyed by the repo folder names.

To make processing a mixed collection of repositories, repo-review will look at the folder a `pyproject.toml` is in
if you pass it. That allows this idiom:

```console
$ repo-review */pyproject.toml
```

to run on all repos that have a pyproject.toml, and skip ones that don't.

If you'd like a way to get a collection of repos quickly, see [all-repos](https://github.com/asottile/all-repos).

```{versionadded} 0.10

```
