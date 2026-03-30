# Live Demo

This demo is using two of the most popular plugins: `sp-repo-review` and
`validate-pyproject` (with `validate-pyproject-schema-store`).

<div id="root">Loading...</div>

<script
      src="https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.js"
      crossorigin
></script>

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

<script type="module">

  import { mountApp } from "./_static/scripts/webapp.min.js";

  mountApp({
    header: false,
    deps: [
      "repo-review~=0.12.3",
      "sp-repo-review==2026.03.02",
      "validate-pyproject[all]~=0.25.0",
      "validate-pyproject-schema-store==2026.03.29",
    ],
  });
</script>
