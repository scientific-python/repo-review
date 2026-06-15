# Changelog

## Version 1.2.0

Features for the webapp:

- Run Pyodide in a web worker by @henryiii in https://github.com/scientific-python/repo-review/pull/404

Fixes:

- Core correctness fixes and polish by @henryiii in https://github.com/scientific-python/repo-review/pull/395
- Correct `GHPath` iterdir/glob/is_dir traversal semantics by @henryiii in https://github.com/scientific-python/repo-review/pull/394

Fixes for the webapp:

- Webapp security, races, and lint enforcement by @henryiii in https://github.com/scientific-python/repo-review/pull/397

Internal:

- Update Pyodide to 314.0.0 (Python 3.14) by @henryiii in https://github.com/scientific-python/repo-review/pull/402
- Repo config fixes (mypy files, action injection, PEP 639, dependabot) by @henryiii in https://github.com/scientific-python/repo-review/pull/396

CI:

- Unblock docs build broken by erbsland-sphinx-ansi 1.2.2 by @henryiii in https://github.com/scientific-python/repo-review/pull/399

Docs:

- Move changelog into the repo by @henryiii in https://github.com/scientific-python/repo-review/pull/406

Dependencies:

- Bump the npm group with 7 updates by @dependabot in https://github.com/scientific-python/repo-review/pull/403
- Bump the npm group across 1 directory with 3 updates by @dependabot in https://github.com/scientific-python/repo-review/pull/400
- Bump the github-actions group with 2 updates by @dependabot in https://github.com/scientific-python/repo-review/pull/401
- Update pre-commit hooks by @pre-commit-ci in https://github.com/scientific-python/repo-review/pull/393

## Version 1.1.3

Fixes for the webapp:

- Support theming better in anywidget form by @henryiii in https://github.com/scientific-python/repo-review/pull/390

Docs and internal:

- Add anywidget to documentation by @henryiii in https://github.com/scientific-python/repo-review/pull/391
- Remove webapp GitHub release artifact by @henryiii in https://github.com/scientific-python/repo-review/pull/392

## Version 1.1.2

### What's Changed

Features for the webapp:

- bundle fonts and SVG icons into webapp/anywidget by @henryiii in https://github.com/scientific-python/repo-review/pull/389

CI:

- Fix publish webapp by @henryiii in https://github.com/scientific-python/repo-review/pull/386

## Version 1.1.1

Features for the webapp:

- Allow passing in an element by @henryiii in https://github.com/scientific-python/repo-review/pull/384
- Include AnyWidget by @henryiii in https://github.com/scientific-python/repo-review/pull/385

CI for the webapp:

- Use npm trusted publishing for npm publish job by @henryiii in https://github.com/scientific-python/repo-review/pull/383

## Version 1.1.0

Fixes:

- Fix family sorting by @henryiii in https://github.com/scientific-python/repo-review/pull/376

Features for the webapp:

- Publish webapp to npm by @henryiii in https://github.com/scientific-python/repo-review/pull/380
- Load pyodide in app by @henryiii in https://github.com/scientific-python/repo-review/pull/369

CI and internal:

- Bump setup-uv to maintained tag scheme by @henryiii in https://github.com/scientific-python/repo-review/pull/372
- Add some tests for the webapp by @henryiii in https://github.com/scientific-python/repo-review/pull/368
- Split deploy-pages workflow into build and deploy jobs by @henryiii in https://github.com/scientific-python/repo-review/pull/378
- Secure CI configuration and update dependencies by @henryiii in https://github.com/scientific-python/repo-review/pull/379
- Bump version to 1.1.0 by @henryiii in https://github.com/scientific-python/repo-review/pull/382

## Version 1.0.3

Features for the WebApp:

- Support directory path by @henryiii in https://github.com/scientific-python/repo-review/pull/359

Fixes for the WebApp:

- Better button placement and sizing by @henryiii in https://github.com/scientific-python/repo-review/pull/366
- Safe set state by @henryiii in https://github.com/scientific-python/repo-review/pull/360
- Warning on splat with key by @henryiii in https://github.com/scientific-python/repo-review/pull/361
- Reloading autocomplete by @henryiii in https://github.com/scientific-python/repo-review/pull/365
- Rework standalone webapp page by @henryiii in https://github.com/scientific-python/repo-review/pull/363

Internal:

- Better serve by @henryiii in https://github.com/scientific-python/repo-review/pull/362

CI:

- Lint webapp in CI by @henryiii in https://github.com/scientific-python/repo-review/pull/364

## Version 1.0.2

Fixes for the WebApp:

- Fix webapp copy HTML crash due to destroyed borrowed PyProxy by @Copilot in https://github.com/scientific-python/repo-review/pull/358

## Version 1.0.1

Fixes for the WebApp:

- Make webapp input row responsive on mobile by @Copilot in https://github.com/scientific-python/repo-review/pull/355
- Keep Show dropdown and Run button always on the same line by @Copilot in https://github.com/scientific-python/repo-review/pull/356

## Version 1.0.0

Features:

- Use static versioning by @henryiii in https://github.com/scientific-python/repo-review/pull/320
- Support branch missing (HEAD) by @henryiii in https://github.com/scientific-python/repo-review/pull/335
- Remove click by @henryiii in https://github.com/scientific-python/repo-review/pull/310
- Support lazy imports (Python 3.15+) by @henryiii in https://github.com/scientific-python/repo-review/pull/311
- Add logging and timers by @henryiii in https://github.com/scientific-python/repo-review/pull/344
- Support async prefetching by @henryiii in https://github.com/scientific-python/repo-review/pull/345

Features for the WebApp:

- Make the WebApp a proper JS app by @henryiii in https://github.com/scientific-python/repo-review/pull/324
- Rename WebApp by @henryiii in https://github.com/scientific-python/repo-review/pull/353
- Use TypeScript by @henryiii in https://github.com/scientific-python/repo-review/pull/333
- Show known checks in webapp before a repo is submitted by @Copilot in https://github.com/scientific-python/repo-review/pull/323
- Show loading bar for Pyodide by @henryiii in https://github.com/scientific-python/repo-review/pull/329
- Add show options by @henryiii in https://github.com/scientific-python/repo-review/pull/339
- Copy button by @henryiii in https://github.com/scientific-python/repo-review/pull/340
- Use async files in webapp by @henryiii in https://github.com/scientific-python/repo-review/pull/346

Fixes for the WebApp:

- Some issues with the webapp by @henryiii in https://github.com/scientific-python/repo-review/pull/314
- Python variable references in webapp.js by @henryiii in https://github.com/scientific-python/repo-review/pull/326
- A few issues fixed by @henryiii in https://github.com/scientific-python/repo-review/pull/330
- Even more small things found in review by @henryiii in https://github.com/scientific-python/repo-review/pull/328
- More small things found in review by @henryiii in https://github.com/scientific-python/repo-review/pull/327
- Add more typescript types by @henryiii in https://github.com/scientific-python/repo-review/pull/347
- The web app was too dynamic in the results header by @henryiii in https://github.com/scientific-python/repo-review/pull/350

Fixes:

- Reduce the (sometimes remote) reads (faster) by @henryiii in https://github.com/scientific-python/repo-review/pull/343
- `collect_all` in wrong spot by @henryiii in https://github.com/scientific-python/repo-review/pull/341

Internal:

- Break up the webapp into multiple files by @henryiii in https://github.com/scientific-python/repo-review/pull/331
- Move more pyodide interactions to a file by @henryiii in https://github.com/scientific-python/repo-review/pull/332
- Autobuild dep missing by @henryiii in https://github.com/scientific-python/repo-review/pull/309
- Enable `ALL` for ruff by @henryiii in https://github.com/scientific-python/repo-review/pull/294
- Faster & remove rich tracebacks by @henryiii in https://github.com/scientific-python/repo-review/pull/317
- Fixed upstream in hatch by @henryiii in https://github.com/scientific-python/repo-review/pull/297
- More ruff codes by @henryiii in https://github.com/scientific-python/repo-review/pull/293
- pytest `log_level` is better than `log_cli_level` by @henryiii in https://github.com/scientific-python/repo-review/pull/291
- Require pytest 9+ by @henryiii in https://github.com/scientific-python/repo-review/pull/300
- Add `.github/copilot-instructions.md` (`AGENTS.md` now) for agent onboarding by @Copilot in https://github.com/scientific-python/repo-review/pull/298 and https://github.com/scientific-python/repo-review/pull/299
- Prepare for 1.0.0rc1 by @henryiii in https://github.com/scientific-python/repo-review/pull/336
- Avoid warning that breaks test in 3.15 pygments by @henryiii in https://github.com/scientific-python/repo-review/pull/342
- Format all ts files by @henryiii in https://github.com/scientific-python/repo-review/pull/348
- Rerun flake8-lazy by @henryiii in https://github.com/scientific-python/repo-review/pull/349

CI:

- Fix archive checksum changing after release by @henryiii in https://github.com/scientific-python/repo-review/pull/319
- Test on Python 3.15 by @henryiii in https://github.com/scientific-python/repo-review/pull/318
- Add zizmor by @henryiii in https://github.com/scientific-python/repo-review/pull/338
- Upload webapp build to release by @henryiii in https://github.com/scientific-python/repo-review/pull/337
- Fix release GH by @henryiii in https://github.com/scientific-python/repo-review/pull/351
- Try to fix release again by @henryiii in https://github.com/scientific-python/repo-review/pull/352

Docs:

- Bump webapp for 2025.11.10 by @henryiii in https://github.com/scientific-python/repo-review/pull/292
- Fix webapp link by @henryiii in https://github.com/scientific-python/repo-review/pull/316
- Minor cleanup by @henryiii in https://github.com/scientific-python/repo-review/pull/334
- Try duplicating link by @henryiii in https://github.com/scientific-python/repo-review/pull/315
- Update Pyodide and dependency versions in index.html by @henryiii in https://github.com/scientific-python/repo-review/pull/325
- Use 3.14 (color) for docs by @henryiii in https://github.com/scientific-python/repo-review/pull/277

New Contributors

- @Copilot made their first contribution in https://github.com/scientific-python/repo-review/pull/298

## v1.0.0rc3

Fixing CI upload, and rename the webapp to repo-review-app.

## v1.0.0rc2

Update to use async in web app and fix for web app binaries on releases.

## v1.0.0rc1

First RC.

## Version 0.12.3

This is a quick release to handle changes in rich-click 1.9 that break `--help` on Windows if not using unicode by default on your terminal.

Fixes:

- Support rich-click 1.9+ on Windows by @henryiii in https://github.com/scientific-python/repo-review/pull/286

WebApp:

- Bump webapp to 0.12.2 by @henryiii in https://github.com/scientific-python/repo-review/pull/276
- Bump to Pyodide 0.28 by @agriyakhetarpal in https://github.com/scientific-python/repo-review/pull/282

## Version 0.12.2

This release provides a much nicer error message if a invalid repository is given, and adds the Python 3.14 (Python π) trove classifier.

Fixes:

- Better error message if bad URL by @henryiii in https://github.com/scientific-python/repo-review/pull/272

WebApp:

- Support both branches and tags in the reference selector by @agriyakhetarpal in https://github.com/scientific-python/repo-review/pull/262
- Also support `HEAD` in the branch selector by @agriyakhetarpal in https://github.com/scientific-python/repo-review/pull/264
- Always show commonly-used branch names at the top by @agriyakhetarpal in https://github.com/scientific-python/repo-review/pull/263

Internal:

- Bump the action to 3.13 by @henryiii in https://github.com/scientific-python/repo-review/pull/274
- Bump to Pyodide version 0.27.3 and update dependencies by @agriyakhetarpal in https://github.com/scientific-python/repo-review/pull/261
- Bump to sp-repo-review 2025.05.02 in tests and webapp by @henryiii in https://github.com/scientific-python/repo-review/pull/268
- Run on Ubuntu/windows on 3.14 by @henryiii in https://github.com/scientific-python/repo-review/pull/273
- Test on Python π beta 1 by @henryiii in https://github.com/scientific-python/repo-review/pull/271

New Contributors:

- @agriyakhetarpal made their first contribution in https://github.com/scientific-python/repo-review/pull/261

## Version 0.12.1

This is a quick release improving the webapp for the new skip reasons.

Features:

- Add `Result.md_as_html()` method by @henryiii in https://github.com/scientific-python/repo-review/pull/259

Fixes:

- webapp support 0.12's skip reasons by @henryiii in https://github.com/scientific-python/repo-review/pull/259

## Version 0.12.0

This release adds support for supplying reasons for ignored checks by using a table in pyproject.toml. It also adds new `--extend-ignore`/ `--extend-select` options to the CLI, to avoid overriding the existing `pyproject.toml` ignores.

Features:

- Support reasons for ignores by @henryiii in https://github.com/scientific-python/repo-review/pull/258
- Extend pyproject lists by @henryiii in https://github.com/scientific-python/repo-review/pull/255

CI and internal:

- chore: support running coverage by @henryiii in https://github.com/scientific-python/repo-review/pull/256
- ci: tighten up permissions a bit by @henryiii in https://github.com/scientific-python/repo-review/pull/257

## Version 0.11.3

This release integrates the code blocks into the current theme instead of always being on a light background.

Fixes:

- Use `ansi_light` for syntax highlighting by @kurtmckee in https://github.com/scientific-python/repo-review/pull/251
- Fix spelling and grammar typos by @kurtmckee in https://github.com/scientific-python/repo-review/pull/247
- For developers, there is now better integration with `uv run` by @henryiii in https://github.com/scientific-python/repo-review/pull/252

New contributors:

- @kurtmckee made their first contribution in https://github.com/scientific-python/repo-review/pull/247

## Version 0.11.2

This release fixes a long standing issue if a check modifies the cached fixtures. Checks weren't supposed to do this, but `validate-pyproject` did this. Now a spare deep copy of the fixtures are kept, and restored with a warning if a check modifies them. There's also a new CLI flag to show all the installed plugin's versions.

Features:

- Add a `--versions` option to view all plugin versions by @henryiii in https://github.com/scientific-python/repo-review/pull/242

Fixes:

- Warn and correct if a check modifies a cached fixture by @henryiii in https://github.com/scientific-python/repo-review/pull/243

## Version 0.11.1

This release fixes an issue with (Windows) systems not set to unicode; it's no longer required to set `PYTHONUTF8` to 1 to run on these systems. We also now support a key-value structure in the Schema for ignores, which in the future may allow us to print out reasons for suppression (older versions still read this correctly). We also updated the docs, including links back to the source. We are ready and testing on Python 3.13, and 3.12 is now the default for things like the GitHub Action.

Fixes:

- Ensure utf-8 encoding if something else is default and unset by @henryiii in https://github.com/scientific-python/repo-review/pull/236
- Support object structure in schema by @henryiii in https://github.com/scientific-python/repo-review/pull/231

Documentation:

- Fix a few typos by @henryiii in https://github.com/scientific-python/repo-review/pull/215
- Link back to source by @henryiii in https://github.com/scientific-python/repo-review/pull/230
- Update webapp info for 0.11 by @henryiii in https://github.com/scientific-python/repo-review/pull/214
- Faster readthedocs by @henryiii in https://github.com/scientific-python/repo-review/pull/220
- Fix docs ci job by @henryiii in https://github.com/scientific-python/repo-review/pull/239

Internal and tests:

- Bump repo-review deps by @henryiii in https://github.com/scientific-python/repo-review/pull/233
- Some cleanup by @henryiii in https://github.com/scientific-python/repo-review/pull/237
- Use 3.12 by default for action by @henryiii in https://github.com/scientific-python/repo-review/pull/240
- Use maintained fork of prettier by @henryiii in https://github.com/scientific-python/repo-review/pull/238
- Use the new github actions reporter for pylint by @henryiii in https://github.com/scientific-python/repo-review/pull/222
- Changelog generation by @henryiii in https://github.com/scientific-python/repo-review/pull/219

## Version 0.11.0

Repo-review now supports pyodide directly, so you no longer need to inject a new `open_url` function, making the webapp slightly simpler.

Features:

- Integrate pyodide helper by @henryiii in https://github.com/scientific-python/repo-review/pull/206
- Better package listing in webapp by @henryiii in https://github.com/scientific-python/repo-review/pull/210

Internal and tests:

- Fix rich-click's self-inflicted warnings by @henryiii in https://github.com/scientific-python/repo-review/pull/211
- Use hatch instead of nox by @henryiii in https://github.com/scientific-python/repo-review/pull/212
- New issue template by @henryiii in https://github.com/scientific-python/repo-review/pull/213

## Version 0.10.6

This version adds one more small helper for unit tests.

Tests and testing:

- Extra testing helper by @henryiii in https://github.com/scientific-python/repo-review/pull/203
- Add an extra test file by @henryiii in https://github.com/scientific-python/repo-review/pull/204

## Version 0.10.5

Features:

- Add unit testing function by @henryiii in https://github.com/scientific-python/repo-review/pull/201

Fixes:

- Exception traceback is too big by @henryiii in https://github.com/scientific-python/repo-review/pull/191
- tests: Do not assume the folder is named repo-review by @henryiii in https://github.com/scientific-python/repo-review/pull/192

Docs:

- Link to conda-forge package by @henryiii in https://github.com/scientific-python/repo-review/pull/193
- Mention conda by @henryiii in https://github.com/scientific-python/repo-review/pull/194
- Mention Poetry way of doing entry-points by @henryiii in https://github.com/scientific-python/repo-review/pull/196

Internal:

- Use uv in CI by @henryiii in https://github.com/scientific-python/repo-review/pull/189

## Version 0.10.4

This is a small release mostly fixing the code display on the terminal with some themes. The demo now uses `validate-pyproject-schema-store` for `validate-pyproject`.

Fixes:

- Use default (light) theme for code by @henryiii in https://github.com/scientific-python/repo-review/pull/176
- Use validate-pyproject-schema-store by @henryiii in https://github.com/scientific-python/repo-review/pull/179

## Version 0.10.3

This is a small release to fix wrapping in the HTML output, making it nicer when used in GitHub issues and GHA output.

Fixes:

- Better wrapping in name column by @henryiii in https://github.com/scientific-python/repo-review/pull/174
- Better error if requires is not a set by @henryiii in https://github.com/scientific-python/repo-review/pull/173

Docs:

- Make TOML valid by @henryiii in https://github.com/scientific-python/repo-review/pull/162
- Fix pipx link by @henryiii in https://github.com/scientific-python/repo-review/pull/168

## Version 0.10.2

This is quick patch release fixing a regression in GitHub path handling in 0.10.1.

Fixes:

- GitHub path bug (regression in 0.10.1) by @henryiii in https://github.com/scientific-python/repo-review/pull/160

## Version 0.10.1

This release primary improves the error message when a branch is missing in the CLI.

Fixes:

- Nicer error message when branch missing by @henryiii in https://github.com/scientific-python/repo-review/pull/152

Docs:

- Improve install suggestions by @henryiii in https://github.com/scientific-python/repo-review/pull/149

Other:

- Move to ruff-format by @henryiii in https://github.com/scientific-python/repo-review/pull/155
- Use sp-repo-review 2023.11.17 for webapp by @henryiii in https://github.com/scientific-python/repo-review/pull/159

## Version 0.10.0

This release adds support for running on multiple repositories at once. You can list as many as you need, and the output formats will be modified to better support multiple repos. You can also now filter out passing or passing + skipped checks, which is especially useful in long multi-repo reports. You can also pass the path to `pyproject.toml` instead of just the repo if it's at top-level.

Due to issues with Rich adding spaces and wrapping (which breaks JSON) even when not interactive, JSON and HTML output is no longer pretty-printed.

Features:

- `--show` `err` only or `errskip` only by @henryiii in https://github.com/scientific-python/repo-review/pull/132
- Allow passing the path to pyroject.toml by @henryiii in https://github.com/scientific-python/repo-review/pull/133
- Allow running on multiple directories at once by @henryiii in https://github.com/scientific-python/repo-review/pull/134

Fixes:

- Drop Rich color printout for html & JSON by @henryiii in https://github.com/scientific-python/repo-review/pull/135
- Support `*` for select by @henryiii in https://github.com/scientific-python/repo-review/pull/138

Docs:

- Add mention of recent features by @henryiii in https://github.com/scientific-python/repo-review/pull/137
- Add mention of pre-commit issues by @henryiii in https://github.com/scientific-python/repo-review/pull/139

## Version 0.9.3

This release adds support for `[tool.repo-review]` to validate-pyproject.

Features:

- Add schema and validate-pyproject support by @henryiii in https://github.com/scientific-python/repo-review/pull/130

Internal:

- Use 2x faster black mirror by @henryiii in https://github.com/scientific-python/repo-review/pull/124

Docs:

- Add some info about making tests for plugins by @henryiii in https://github.com/scientific-python/repo-review/pull/120
- Add more links and some updates by @henryiii in https://github.com/scientific-python/repo-review/pull/122
- Fix links in README by @henryiii in https://github.com/scientific-python/repo-review/pull/126
- Ddd validate-pyproject by @henryiii in https://github.com/scientific-python/repo-review/pull/129

## Version 0.9.2

A few fixes, one for a regression and one for the WebApp.

Fixes:

- Span wasn't set properly in the WebApp by @henryiii in https://github.com/scientific-python/repo-review/pull/119
- Pass correct self object by @henryiii in https://github.com/scientific-python/repo-review/pull/118

## Version 0.9.1

Quick WebApp fix for Pyodide having pyyaml 6.0.0.

Fixes:

- Pyodide has pyyaml 6.0.0 by @henryiii in https://github.com/scientific-python/repo-review/pull/117

## Version 0.9

This release adds a new `description` slot that is shown below the family name if present. You can request fixtures in the family collection function now, which allows the descriptions to be dynamic, based on the repo being evaluated. A minor breaking change is also present - the text return from checks is no longer run through `.format`, removing the need for escaping. A new checks-only fixture `name` is provided in case you did need the current check name.

Features:

- Drop formatting of dynamic messages, add "name" fixture by @henryiii in https://github.com/scientific-python/repo-review/pull/115
- Family descriptions and dynamic families by @henryiii in https://github.com/scientific-python/repo-review/pull/114

Fixes:

- Remove newlines in help line by @henryiii in https://github.com/scientific-python/repo-review/pull/113

Docs and other:

- Link to source in docs by @henryiii in https://github.com/scientific-python/repo-review/pull/106
- Use sphinx-autobuild by @henryiii in https://github.com/scientific-python/repo-review/pull/109
- Drop pytest Python 3.12 workaround by @henryiii in https://github.com/scientific-python/repo-review/pull/110

## Version 0.8.1

This release fixes a couple of issues with the webapp; it now supports pressing "enter" to move, and error messages (which hopefully you never see!) will get formatted nicely.

Fixes:

- Support enter in form by @henryiii in https://github.com/scientific-python/repo-review/pull/104
- Format error messages properly by @henryiii in https://github.com/scientific-python/repo-review/pull/105

## Version 0.8.0

This release adds a new fixture (`list_all`, a bool), several new helper functions (`get_check_url`, `get_check_description`, `get_family_name`), and makes `collect_all` part of the public API, with a structured return. This enables easier programmatic usage, especially when listing all (unevaluated) checks. This is use for a new new cog example in a new documentation page on programmatic usage.

Features:

- feat: better list-all support by @henryiii in https://github.com/scientific-python/repo-review/pull/101

## Version 0.7.0

This is the first stand-alone release after being split out from `sp-repo-review` and moved to scientific Python.

Features:

- feat: `--list-all` rename and improvements, `--version` addition by @henryiii in https://github.com/scientific-python/repo-review/pull/96
- feat: add `--list` to show all checks by @henryiii in https://github.com/scientific-python/repo-review/pull/83
- feat: add Composite Action by @henryiii in https://github.com/scientific-python/repo-review/pull/45
- feat: add pre-commit support by @henryiii in https://github.com/scientific-python/repo-review/pull/48
- feat: add select by @henryiii in https://github.com/scientific-python/repo-review/pull/75
- feat: allow name sub in URL by @henryiii in https://github.com/scientific-python/repo-review/pull/80
- feat: dynamic error messages by @henryiii in https://github.com/scientific-python/repo-review/pull/70
- feat: exit codes by @henryiii in https://github.com/scientific-python/repo-review/pull/76
- feat: selection for output by @henryiii in https://github.com/scientific-python/repo-review/pull/87
- feat: support for URLs by @henryiii in https://github.com/scientific-python/repo-review/pull/72
- feat: support root / package dir separation by @henryiii in https://github.com/scientific-python/repo-review/pull/71
- refactor: rename and split by @henryiii in https://github.com/scientific-python/repo-review/pull/68
- refactor: rename err_markdown to err_as_html by @henryiii in https://github.com/scientific-python/repo-review/pull/99
- refactor: stderr/stdout by @henryiii in https://github.com/scientific-python/repo-review/pull/95

Fixes:

- fix: URL visible in results by @henryiii in https://github.com/scientific-python/repo-review/pull/77
- fix: corrections while adding docs by @henryiii in https://github.com/scientific-python/repo-review/pull/78
- fix: stderr never has format codes by @henryiii in https://github.com/scientific-python/repo-review/pull/90
- fix: update webapp and tests for sp-repo-review by @henryiii in https://github.com/scientific-python/repo-review/pull/81
- fix: webapp details by @henryiii in https://github.com/scientific-python/repo-review/pull/85
- fix: webapp supports setting dependencies by @henryiii in https://github.com/scientific-python/repo-review/pull/82

Other things:

- chore: auto-versioning by @henryiii in https://github.com/scientific-python/repo-review/pull/89
- chore: bump sp-repo-review version by @henryiii in https://github.com/scientific-python/repo-review/pull/97
- ci: prepare dist by @henryiii in https://github.com/scientific-python/repo-review/pull/73
- docs: fill out some API docs by @henryiii in https://github.com/scientific-python/repo-review/pull/98
- docs: add changelog by @henryiii in https://github.com/scientific-python/repo-review/pull/100
- docs: add docs by @henryiii in https://github.com/scientific-python/repo-review/pull/74
- docs: add version number by @henryiii in https://github.com/scientific-python/repo-review/pull/92
- docs: add version number by @henryiii in https://github.com/scientific-python/repo-review/pull/93
- docs: add version number by @henryiii in https://github.com/scientific-python/repo-review/pull/94
- docs: filling out a bit more by @henryiii in https://github.com/scientific-python/repo-review/pull/79
- docs: link to live preview. by @henryiii in https://github.com/scientific-python/repo-review/pull/84
- docs: minor fixes by @henryiii in https://github.com/scientific-python/repo-review/pull/91
- docs: some getting started info by @henryiii in https://github.com/scientific-python/repo-review/pull/86

## Version 0.7.0 beta 10

Renaming a confusing method before release.

- refactor: rename `err_markdown` to `err_as_html` by @henryiii in https://github.com/scientific-python/repo-review/pull/99

## Version 0.7.0 beta 9

- chore: bump sp-repo-review version by @henryiii in https://github.com/scientific-python/repo-review/pull/97
- docs: Fill out some API docs by @henryiii in https://github.com/scientific-python/repo-review/pull/98

## Version 0.7.0 beta 8

Features:

- stderr/stdout refactor by @henryiii in https://github.com/scientific-python/repo-review/pull/95
- `--list-all` rename and improvements, --version addition by @henryiii in https://github.com/scientific-python/repo-review/pull/96

## Version 0.7.0 beta 7

This release improves the PyPI landing page a little, and touches up the docs with better versioning.

Documentation:

- minor fixes by @henryiii in https://github.com/scientific-python/repo-review/pull/91
- add version number by @henryiii in https://github.com/scientific-python/repo-review/pull/92
- add version number by @henryiii in https://github.com/scientific-python/repo-review/pull/93
- add version number by @henryiii in https://github.com/scientific-python/repo-review/pull/94

(GitHub was having an outage)

## Version 0.7.0 beta 6

Features:

- Add pre-commit support by @henryiii in https://github.com/scientific-python/repo-review/pull/48
- Add Composite Action by @henryiii in https://github.com/scientific-python/repo-review/pull/45
- Rework selection for output by @henryiii in https://github.com/scientific-python/repo-review/pull/87 and https://github.com/scientific-python/repo-review/pull/90

Other:

- Some getting started info in the docs by @henryiii in https://github.com/scientific-python/repo-review/pull/86
- Auto-versioning by @henryiii in https://github.com/scientific-python/repo-review/pull/89

## Version 0.7.0 beta 5

Features:

- Add `--list` to show all checks by @henryiii in https://github.com/scientific-python/repo-review/pull/83
- Webapp supports setting dependencies by @henryiii in https://github.com/scientific-python/repo-review/pull/82

Other:

- Update webapp and tests for `sp-repo-review` by @henryiii in https://github.com/scientific-python/repo-review/pull/81
- Link to live preview in docs by @henryiii in https://github.com/scientific-python/repo-review/pull/84
- Touch up some webapp details by @henryiii in https://github.com/scientific-python/repo-review/pull/85

## Version 0.7.0 beta 4

Features:

- Allow name sub in URL by @henryiii in https://github.com/scientific-python/repo-review/pull/80

## Version 0.7.0 beta 3

Features:

- Add select by @henryiii in https://github.com/scientific-python/repo-review/pull/75
- Exit codes by @henryiii in https://github.com/scientific-python/repo-review/pull/76

Fixes:

- URL visible in results by @henryiii in https://github.com/scientific-python/repo-review/pull/77
- Corrections found while adding docs by @henryiii in https://github.com/scientific-python/repo-review/pull/78

Docs:

- Add docs by @henryiii in https://github.com/scientific-python/repo-review/pull/74
- Filling out a bit more by @henryiii in https://github.com/scientific-python/repo-review/pull/79

## Version 0.7.2 beta 2

Adding a few more features before release of scientific-python version. Split root/package, add URL support, and support dynamic error messages.

Features:

- feat: dynamic error messages by @henryiii in https://github.com/scientific-python/repo-review/pull/70
- feat: support root / package dir separation by @henryiii in https://github.com/scientific-python/repo-review/pull/71
- feat: support for URLs by @henryiii in https://github.com/scientific-python/repo-review/pull/72

Other:

- ci: prepare dist by @henryiii in https://github.com/scientific-python/repo-review/pull/73

## Version 0.7.0b1

- refactor: rename and split by @henryiii in https://github.com/scientific-python/repo-review/pull/68

## Version 0.6.1

Fix a regression in 0.6.0 with error messages not showing up, and also improve the output formatting a bit by removing the extra paragraph tag.

### What's Changed

Fixes:

- Produce the correct error message by @henryiii in https://github.com/scikit-hep/repo-review/pull/66
- Strip paragraph tags when converting to markdown by @henryiii in https://github.com/scikit-hep/repo-review/pull/67

## Version 0.6.0

This version has a lot of internal rewrites, preparing it for splitting up into a general runner and a specific tool, as discussed at the Scientific-Python Developer Summit. This is likely the last release before the split.

### What's Changed

Features:

- feat: add families by @henryiii in https://github.com/scikit-hep/repo-review/pull/62
- feat: add html output option by @henryiii in https://github.com/scikit-hep/repo-review/pull/58
- feat: adding ignores by @henryiii in https://github.com/scikit-hep/repo-review/pull/49
- feat: json format output & a fix by @henryiii in https://github.com/scikit-hep/repo-review/pull/47
- feat: request from github by @henryiii in https://github.com/scikit-hep/repo-review/pull/56
- feat: simplify result for json by @pllim in https://github.com/scikit-hep/repo-review/pull/46
- feat: topological graph for fixtures, too by @henryiii in https://github.com/scikit-hep/repo-review/pull/60

Refactoring:

- refactor: 'checks' in json output to save space for later additions by @henryiii in https://github.com/scikit-hep/repo-review/pull/61
- refactor: checks as objects by @henryiii in https://github.com/scikit-hep/repo-review/pull/63
- refactor: entry points by @henryiii in https://github.com/scikit-hep/repo-review/pull/52
- refactor: move functions to files that make more sense by @henryiii in https://github.com/scikit-hep/repo-review/pull/65
- refactor: rating -> check unified language by @henryiii in https://github.com/scikit-hep/repo-review/pull/57
- refactor: rework families by @henryiii in https://github.com/scikit-hep/repo-review/pull/55

Other:

- chore: Add devcontainer by @crazy4pi314 in https://github.com/scikit-hep/repo-review/pull/44
- chore: add 3.12 to classifiers by @henryiii in https://github.com/scikit-hep/repo-review/pull/59
- chore: bump version by @henryiii in https://github.com/scikit-hep/repo-review/pull/64
- fix(dev): devcontainer post create by @henryiii in https://github.com/scikit-hep/repo-review/pull/54

### New Contributors

- @crazy4pi314 made their first contribution in https://github.com/scikit-hep/repo-review/pull/44
- @pllim made their first contribution in https://github.com/scikit-hep/repo-review/pull/46

## Version 0.5.1

Small release fixing a check that was reporting fail instead of skip if Ruff config was not present.

Now using trusted publisher PyPI deployment, too.

### What's Changed

- fix: ruff requirement missing by @henryiii in https://github.com/scikit-hep/repo-review/pull/38

## Version 0.5.0

Moved from various other style checkers to Ruff, following the Scikit-HEP developer guidelines and scikit-hep/cookie.

### What's Changed

- feat: move to checking for Ruff by @henryiii in https://github.com/scikit-hep/repo-review/pull/23

## Version 0.4.2

Small release moving to using Ruff internally (next release will move to using Ruff). Also fixed a potential issue with Python 3.11 requiring tomli.

### What's Changed

- chore(deps): update pre-commit hooks by @pre-commit-ci in https://github.com/scikit-hep/repo-review/pull/16
- ci: update to Python 3.11 final by @henryiii in https://github.com/scikit-hep/repo-review/pull/18
- chore: move to using Ruff by @henryiii in https://github.com/scikit-hep/repo-review/pull/22
- chore(deps): bump pypa/gh-action-pypi-publish from 1.5.1 to 1.6.4 by @dependabot in https://github.com/scikit-hep/repo-review/pull/21

### New Contributors

- @pre-commit-ci made their first contribution in https://github.com/scikit-hep/repo-review/pull/16

## Version 0.4.1

Small update that mostly adds Python 3.11 testing & a pyodide update for the docs. For development, pytest is now expected to be 7+, since we aren't testing with <7.

### What's Changed

- chore: update & include py311 by @henryiii in https://github.com/scikit-hep/repo-review/pull/15

## Version 0.4.0

This release changes to the new dependabot best practice of not limiting official versions, since it now handles v1->v2 instead of v1->v2.0.0. It also adds a check for test naming.

### What's Changed

- feat: Add 'name-tests-test' to pre-commit hooks by @matthewfeickert in https://github.com/scikit-hep/repo-review/pull/9
- feat: change check for dependabot GHA by @henryiii in https://github.com/scikit-hep/repo-review/pull/11

- fix(webapp): show changed URL when running by @henryiii in https://github.com/scikit-hep/repo-review/pull/6

- chore(deps): bump pre-commit/action from 2.0.3 to 3.0.0 by @dependabot in https://github.com/scikit-hep/repo-review/pull/7
- chore: switch to hatchling by @henryiii in https://github.com/scikit-hep/repo-review/pull/10
- chore(deps): bump actions/setup-python from 3 to 4 by @dependabot in https://github.com/scikit-hep/repo-review/pull/8
- chore(deps): bump pypa/gh-action-pypi-publish from 1.5.0 to 1.5.1 by @dependabot in https://github.com/scikit-hep/repo-review/pull/12
- chore: bump to version 0.4.0 by @henryiii in https://github.com/scikit-hep/repo-review/pull/14

### New Contributors

- @matthewfeickert made their first contribution in https://github.com/scikit-hep/repo-review/pull/9

## Version 0.3.0

First version under the scikit-hep org. Added two new checks (prettier, blacken-docs), which also are applied to this codebase (repo-review self-checks fully passing). Fixed several bugs - filter warnings was misreporting, and bugbear didn't work if you pinned bugbear.

### What's Changed

- feat: prettier/blacken-docs by @henryiii in https://github.com/scikit-hep/repo-review/pull/4
- fix: a couple of mistakes by @henryiii in https://github.com/scikit-hep/repo-review/pull/5

## Version 0.2.4

Updates to the web app, like the ability to pre-fill the fields with `?repo=...&branch=...`. The web app now prints `[skipped]` as well. The app now passes its own tests. Lots of documentation updates to the checks, and several fixes for the checks.

## Version 0.2.3

Minor updates to error messages, also correcting a skip issue with GHA.

## Version 0.2.2

Integrating webapp Python code for simpler usage.

## Version 0.2.1

Fix for skipping checks.
