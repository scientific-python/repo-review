# Live Demo

This demo is using two of the most popular plugins: `sp-repo-review` and
`validate-pyproject` (with `validate-pyproject-schema-store`).

<div id="root">Loading...</div>

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

  import { mountApp } from "./_static/scripts/repo-review-app.min.js";

  mountApp({
    header: false,
    deps: [
      "repo-review~=1.2.1",
      "sp-repo-review==2026.08.14",
      "validate-pyproject[all]~=0.26.0",
      "validate-pyproject-schema-store==2026.10.06",
    ],
  });
</script>
