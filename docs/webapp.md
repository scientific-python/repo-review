# WebApp

## Example app

You can run repo-review in Pyodide as a webapp if you wish. An example webapp
written in JSX using React and MaterialUI is provided at `docs/webapp.js` and
`docs/index.html`; the `index.html` uses `sp-repo-review` and can be seen at
<https://scientific-python.github.io/repo-review>. The webapp supports
selecting org/repo and branch via URL, too, such as
<https://scientific-python.github.io/repo-review/?repo=scikit-hep/hist&branch=main>.
On the results screen, you can click on the check numbers to jump to the URLs
provided by the checks.

This webapp can be embedded into an existing webpage if you set
`header={false}`. You can set your own deps with `deps = {["...", "..."]}`.

## Custom app

You can also use the `html` output and write your own webapp. You need to provide Pyodide:

```html
<script
  src="https://cdn.jsdelivr.net/pyodide/v0.23.2/full/pyodide.js"
  crossorigin
></script>
```

Then, you need to load your plugin & repo-review.

```js
async function prepare_pyodide() {
  const pyodide = await loadPyodide();

  await pyodide.loadPackage("micropip");
  await pyodide.runPythonAsync(`
        import micropip
        await micropip.install(["my_plugin", "repo-review"])
    `);
  return pyodide;
}
```

You can get the families and the checks:

```js
result_html_py = pyodide.runPython(`
  from pyodide.http import open_url
  from repo_review.processor import process
  from repo_review.ghpath import GHPath
  from repo_review.html import to_html

  GHPath.open_url = staticmethod(open_url)

  package = GHPath(repo="${state.repo}", branch="${state.branch}")
  to_html(*process(package))
`);
result_html = result_html_py.toString();
```

This can throw an error with `KeyError: 'tree'` if the repo or branch is invalid.
