# WebApp

## Example app

You can run repo-review in Pyodide as a webapp. An example webapp written in
JSX using React and MaterialUI is provided in the repository; the live demo is
available in the docs at the **Live Demo** page or at <https://scientific-python.github.io/repo-review>.

The webapp supports selecting org/repo, branch, and package directory via URL,
for example,
<a href="https://scientific-python.github.io/repo-review/?repo=scikit-hep/hist&ref=main&packageDir=src">https://scientific-python.github.io/repo-review/?repo=scikit-hep/hist&ref=main&packageDir=src</a>.

This webapp can be embedded into an existing webpage by setting
`header={false}` and you can set your own `deps` when calling `mountApp()`.

You can see the source at `/src/repo-review-app`, and you can see the file to
set up the `bun` bundle at `/package.json`. Releases of repo-review have a
zip attached with the webapp.

If you copy the webapp into your page, use this header (with the link to where
you extract the webapp):

```html
<!-- Fonts to support Material Design -->
<link
  rel="stylesheet"
  href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
/>
<!-- Icons to support Material Design -->
<link
  rel="stylesheet"
  href="https://fonts.googleapis.com/icon?family=Material+Icons"
/>
<link rel="modulepreload" href="/assets/js/repo-review-app.min.js" />
```

Then to use it:

```html
<div id="root">Loading (requires javascript and WebAssembly)...</div>
```

And then after that, call the script with whatever dependencies you want:

```html
<script type="module">
  import { mountApp } from "{% link assets/js/repo-review-app.min.js %}";

  mountApp({
    header: false,
    deps: ["repo-review~=1.0.0", "sp-repo-review==2026.04.04"],
  });
</script>
```

### Bundler notes

When bundling the app for the web, Pyodide is loaded inside a dedicated web
worker from the official CDN. The UI thread only talks to that worker via a
promise-based message API, so React never touches Pyodide objects directly.
Running `bun run build` writes the bundled ESM entrypoint to
`docs/_static/scripts/repo-review-app.min.js` and emits the worker module
alongside it.

## Custom app

If you prefer to write a custom integration, import the ESM bundle and mount
the app. Pyodide will initialize lazily inside the worker when the app starts.
For example:

```html
<script type="module">
  import { mountApp } from "./_static/scripts/repo-review-app.min.js";
  mountApp({ header: false, deps: ["repo-review"] });
</script>
```

The worker uses `micropip` to install any requested Python packages and keeps
the expensive Python state off the main thread.
