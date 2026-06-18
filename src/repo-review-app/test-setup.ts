// Preload for the DOM-capable test lane (wired via bunfig.toml `[test] preload`).
//
// Registers a real DOM so react-dom/client's `createRoot` can mount components
// and actually run effects and refs. The SSR-string tests (renderToStaticMarkup)
// run no effects and never mount, so they can't catch ref/effect regressions
// like the MUI v9 Autocomplete breakage in #407 — this lane can.
import { GlobalRegistrator } from "@happy-dom/global-registrator";

// A concrete origin (not the default about:blank) is required for history
// pushState/replaceState to update window.location — the app mirrors the Show
// filter into the URL query, and tests assert on it.
GlobalRegistrator.register({ url: "http://localhost/" });

// Mounting <App> spawns a Pyodide web worker (PyodideClient) in componentDidMount.
// Tests never drive the Python runtime, so replace Worker with an inert stub:
// this keeps mounts from launching a real worker thread that would hit the
// network (Pyodide CDN) and pollute console output that the regression tests
// assert against. URL.createObjectURL/revokeObjectURL stay as their real impls.
class InertWorker {
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: ErrorEvent) => void) | null = null;
  postMessage(): void {}
  terminate(): void {}
  addEventListener(): void {}
  removeEventListener(): void {}
}
globalThis.Worker = InertWorker as unknown as typeof Worker;
