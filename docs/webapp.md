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

The webapp loads Pyodide automatically from the jsDelivr CDN
(`https://cdn.jsdelivr.net/pyodide/`) at runtime; no extra `<script>` tag is
required. The version loaded matches the `pyodide` npm package version used at
build time. Running `bun run build` writes a bundled ESM file to
`docs/_static/scripts/repo-review-app.min.js`, which the Live Demo imports as a
module.

## Custom app

To embed the app, simply import the ESM bundle and call `mountApp()`:

```html
<script type="module">
  import { mountApp } from "./_static/scripts/repo-review-app.min.js";
  mountApp({ header: false, deps: ["repo-review"] });
</script>
```

The webapp loads Pyodide and uses `micropip` to install any requested Python packages.
