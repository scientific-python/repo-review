# WebApp

## Example app

You can run repo-review in Pyodide as a webapp. An example webapp written in
JSX using React and MaterialUI is provided in the repository; the live demo is
available in the docs at the **Live Demo** page.

The webapp supports selecting org/repo and branch via URL, for example, try
appending `?repo=scikit-hep/hist&ref=main`.

This webapp can be embedded into an existing webpage by setting
`header={false}` and you can set your own `deps` when calling `mountApp()`.

### Bundler notes

When bundling the app for the web, Pyodide is included via the `pyodide` npm
package and imported as a module (no global `<script>` tag required). The
project build writes a bundled ESM file to `docs/_static/webapp.min.js` which
the Live Demo page imports as a module.

## Custom app

If you prefer to write a custom integration, you can still use Pyodide directly
by importing `loadPyodide()` from the `pyodide` package in an ESM environment:

```js
import { loadPyodide } from "pyodide";

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

You can then call into `repo_review` as shown in the demo app. Note that an
invalid repository or branch can surface a `KeyError: 'tree'` exception.
