# CLI

Repo-review has a CLI interface.

```{program-output} python -m repo_review --help

```

There are three output formats; `rich` produces great terminal output, `html`
produces an HTML report, and `json` produces a output that can be processed
easily.

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
