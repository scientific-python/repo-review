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
set up the `bun` bundle at `/package.json`. The bundle is published to npm as
`repo-review-webapp`.

## Using the CDN bundle

The simplest way to embed the webapp is via jsDelivr — no download or hosting
required:

```html
<script type="module">
  import { mountApp } from "https://cdn.jsdelivr.net/npm/repo-review-webapp/dist/repo-review-app.mjs";

  mountApp({
    header: false,
    deps: ["repo-review~=1.1.3", "sp-repo-review==2026.04.04"],
  });
</script>
```

Pin to a specific version for stability:

```html
<script type="module">
  import { mountApp } from "https://cdn.jsdelivr.net/npm/repo-review-webapp@1.1.3/dist/repo-review-app.mjs";
  mountApp({ header: false, deps: ["repo-review~=1.1.3"] });
</script>
```

## Self-hosting

If you copy the webapp into your page, use this header (with the link to where
you extract the webapp):

```html
<link rel="modulepreload" href="/assets/js/repo-review-app.min.js" />
```

The Roboto font and Material Design icons are bundled into the webapp — no
external `<link>` tags for Google Fonts are required. If Roboto is already
loaded by the host page, the bundled injection will detect it and skip.

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
    deps: ["repo-review~=1.1.3", "sp-repo-review==2026.04.04"],
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

## MyST AnyWidget

For [mystmd](https://mystmd.org) (e.g. Jupyter Book), we provide an integration
that you can embed using the `anywidget` directive, which requires no
JavaScript setup:

```markdown
:::{anywidget} https://cdn.jsdelivr.net/npm/repo-review-webapp@1.1.3/dist/repo-review-anywidget.mjs
{
"url_sync": true,
"deps": [
"repo-review~=1.1.3",
"sp-repo-review==2026.04.04"
]
}
:::
```

Set `url_sync: true` if you want the selected repo/branch is reflected in (and
restored from) the page URL. Add any extra Python packages you need to `deps`.

## Custom app

To embed the app, simply import the ESM bundle and call `mountApp()`:

```html
<script type="module">
  import { mountApp } from "./_static/scripts/repo-review-app.min.js";
  mountApp({ header: false, deps: ["repo-review"] });
</script>
```

The webapp loads Pyodide and uses `micropip` to install any requested Python packages.
