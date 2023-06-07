# CLI

Repo-review has a CLI interface.

```{program-output} python -m repo_review --help

```

There are four output formats; `rich` produces great terminal output, `svg`
produces an SVG based on the rich output, `html` produces a custom HTML report,
and `json` produces a output that can be processed easily. To make it easier to
support tools like GitHub Actions, there is also a `--stderr FORMAT` output
option that produces the selected format on stderr as well, and disables
producing terminal escape codes on stdout, even if `FORCE_COLOR` is set.

JSON output looks like this:

```json
{
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
