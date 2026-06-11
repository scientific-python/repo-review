/**
 * AnyWidget entry point for repo-review.
 *
 * Usage in a MyST/Jupyter Book document:
 *
 * ```{anywidget} repo-review-anywidget.mjs
 * {
 *   "deps": ["repo-review", "sp-repo-review"],
 *   "pyodide_base_url": "https://cdn.jsdelivr.net/pyodide/v314.0.0/full"
 * }
 * ```
 *
 * Model attributes:
 *   - deps (string[]): Python packages to install via micropip.
 *   - pyodide_base_url (string, optional): Override the Pyodide CDN base URL.
 *   - url_sync (boolean, optional): Enable URL syncing. Disabled by default
 *     when embedded as a widget.
 */
import ReactDOM from "react-dom/client";
import createCache from "@emotion/cache";
import { CacheProvider } from "@emotion/react";
import { App } from "./repo-review-app";
import type { AppProps } from "./repo-review-app";
import { injectFonts } from "./utils/injectFonts";

interface AnyWidgetModel {
  get(key: string): unknown;
}

function render({ model, el }: { model: AnyWidgetModel; el: HTMLElement }) {
  injectFonts();
  const deps = (model.get("deps") as string[] | null) ?? [];
  const disableUrlSync = !model.get("url_sync");
  const pyodideBaseUrl =
    (model.get("pyodide_base_url") as string | null) || undefined;

  // Inject emotion/MUI styles into the shadow root so they apply inside the widget.
  const rootNode = el.getRootNode();
  const cache = createCache({
    key: "rr",
    container: rootNode instanceof ShadowRoot ? rootNode : undefined,
  });

  const props: AppProps = { deps, pyodideBaseUrl, disableUrlSync };

  const root = ReactDOM.createRoot(el);
  root.render(
    <CacheProvider value={cache}>
      <App {...props} />
    </CacheProvider>,
  );

  return () => root.unmount();
}

export default { render };
