/**
 * Pyodide web worker for repo-review.
 *
 * `workerMain` is completely self-contained: the client stringifies it with
 * `Function.prototype.toString()` and loads it into a `Worker` via a Blob URL
 * (see pyodideClient.ts). This keeps the whole app a single bundled file —
 * which the docs page, the npm package, and the anywidget build all rely on —
 * and works with any bundler (esbuild, `bun serve`, ...) without any
 * worker-specific build configuration.
 *
 * Rules for code inside `workerMain`:
 *   - It must not reference anything outside the function at runtime: no
 *     imported values, no module-level constants. Type-only imports and
 *     annotations are fine because they are erased during compilation.
 *   - Nothing that the bundler would downlevel with injected helper functions
 *     (the build targets ES2022, so async/await is safe as-is).
 *   - No dynamic `import()` directly in this file: bundlers rewrite it into
 *     runtime helpers that don't exist inside the stringified function (Bun's
 *     dev server turns it into an `hmr` helper call, for example). Instead,
 *     the client builds the Blob source as
 *     `(workerMain.toString())((u) => import(u))` — the `import()` there is
 *     plain text inside a string, invisible to bundlers — and `workerMain`
 *     receives it as the `dynImport` parameter. (Pyodide 0.28+/314 dropped
 *     classic worker support, so `importScripts()` is not an option.)
 */
import type { PyodideInterface } from "pyodide";

// ---- Message protocol (shared with pyodideClient.ts) ----

export type WorkerRequestPayload =
  | { type: "init"; deps: string[]; baseUrl: string }
  | { type: "runChecks"; repo: string; ref: string; packageDir: string }
  | { type: "knownChecks" }
  | { type: "generateHtml"; show: string };

export type WorkerRequest = WorkerRequestPayload & { id: number };

export type WorkerResponse =
  | { kind: "progress"; percent: number; message: string }
  | { kind: "response"; id: number; ok: true; result: unknown }
  | { kind: "response"; id: number; ok: false; error: string };

// ---- Data shapes returned by the worker (plain JSON, no PyProxies) ----

export interface FamilyData {
  name: string;
  description?: string | null;
}

export interface ResultData {
  family: string;
  name: string;
  description: string;
  result: boolean | null;
  err_msg: string;
  url: string;
  skip_reason: string;
}

export interface RunChecksData {
  families: Record<string, FamilyData>;
  results: ResultData[];
}

export interface KnownChecksData {
  families?: Record<string, { name: string }>;
  results?: {
    name: string;
    family: string;
    description: string;
    url: string;
  }[];
}

export function workerMain(
  dynImport: (url: string) => Promise<unknown>,
): void {
  // `self` is typed as Window in this project's tsconfig; narrow it to the
  // worker-shaped subset we use.
  const ctx = self as unknown as {
    postMessage(message: unknown): void;
    onmessage: ((event: MessageEvent) => void) | null;
  };

  let pyodide: PyodideInterface | null = null;

  function post(message: WorkerResponse): void {
    ctx.postMessage(message);
  }

  function progress(percent: number, message: string): void {
    post({ kind: "progress", percent, message });
  }

  function requirePyodide(): PyodideInterface {
    if (!pyodide) {
      throw new Error("Pyodide is not initialized");
    }
    return pyodide;
  }

  async function init(deps: string[], baseUrl: string): Promise<void> {
    progress(5, "Initializing Pyodide runtime");
    const mod = (await dynImport(`${baseUrl}/pyodide.mjs`)) as {
      loadPyodide: (options?: {
        indexURL?: string;
      }) => Promise<PyodideInterface>;
    };
    const py = await mod.loadPyodide({ indexURL: `${baseUrl}/` });
    progress(50, "Core Pyodide loaded");
    progress(65, "Loading micropip");
    await py.loadPackage("micropip");
    progress(80, "Installing Python packages");
    // Pass deps via globals instead of string interpolation for safety
    py.globals.set("_rr_deps", deps);
    await py.runPythonAsync(`
      import micropip
      await micropip.install(list(_rr_deps))
    `);
    py.globals.delete("_rr_deps");
    pyodide = py;
    progress(100, "Ready");
  }

  async function runChecks(
    repo: string,
    ref: string,
    packageDir: string,
  ): Promise<RunChecksData> {
    const py = requirePyodide();
    py.globals.set("_rr_repo", repo);
    py.globals.set("_rr_ref", ref);
    py.globals.set("_rr_subdir", packageDir);
    try {
      const json = (await py.runPythonAsync(`
        import json

        from repo_review.files import collect_prefetch_files, process_prefetch_files
        from repo_review.ghpath import GHPath
        from repo_review.processor import collect_all, md_as_html, process

        _rr_package = await GHPath.async_from_repo(_rr_repo, _rr_ref)
        await process_prefetch_files(_rr_package, collect_prefetch_files(), subdir=_rr_subdir)
        _rr_collected = collect_all(_rr_package, subdir=_rr_subdir)
        _rr_families, _rr_checks = process(_rr_package, collected=_rr_collected, subdir=_rr_subdir)

        for _rr_family in _rr_families.values():
            if _rr_family.get("description"):
                _rr_family["description"] = md_as_html(_rr_family["description"])
        _rr_checks = [_rr_res.md_as_html() for _rr_res in _rr_checks]

        # Keep the run so generate_html can reuse it without rerunning checks
        _rr_last_run = (_rr_families, _rr_checks)

        json.dumps({
            "families": {
                _rr_key: {
                    "name": _rr_family.get("name", _rr_key),
                    "description": _rr_family.get("description"),
                }
                for _rr_key, _rr_family in _rr_families.items()
            },
            "results": [
                {
                    "family": _rr_res.family,
                    "name": _rr_res.name,
                    "description": _rr_res.description,
                    "result": _rr_res.result,
                    "err_msg": _rr_res.err_msg,
                    "url": _rr_res.url,
                    "skip_reason": _rr_res.skip_reason,
                }
                for _rr_res in _rr_checks
            ],
        })
      `)) as string;
      return JSON.parse(json) as RunChecksData;
    } finally {
      py.globals.delete("_rr_repo");
      py.globals.delete("_rr_ref");
      py.globals.delete("_rr_subdir");
    }
  }

  function knownChecks(): KnownChecksData {
    const py = requirePyodide();
    const json = py.runPython(`
      import json

      from repo_review.checks import get_check_url
      from repo_review.processor import collect_all

      _rr_collected = collect_all()
      json.dumps({
          "families": {
              _rr_key: {"name": _rr_family.get("name", _rr_key)}
              for _rr_key, _rr_family in _rr_collected.families.items()
          },
          "results": [
              {
                  "name": _rr_name,
                  "family": _rr_check.family,
                  "description": (_rr_check.__doc__ or "").strip(),
                  "url": get_check_url(_rr_name, _rr_check),
              }
              for _rr_name, _rr_check in _rr_collected.checks.items()
          ],
      })
    `) as string;
    return JSON.parse(json) as KnownChecksData;
  }

  function generateHtml(show: string): string {
    const py = requirePyodide();
    py.globals.set("_rr_show", show || "all");
    try {
      return py.runPython(`
        from repo_review.html import to_html

        try:
            _rr_html_families, _rr_html_checks = _rr_last_run
        except NameError:
            raise RuntimeError("No stored results; run the checks first") from None

        match _rr_show:
            case "err":
                _rr_filtered = [_rr_c for _rr_c in _rr_html_checks if _rr_c.result is False]
            case "errskip":
                _rr_filtered = [_rr_c for _rr_c in _rr_html_checks if _rr_c.result is not True]
            case _:
                _rr_filtered = _rr_html_checks

        to_html(_rr_html_families, _rr_filtered)
      `) as string;
    } finally {
      py.globals.delete("_rr_show");
    }
  }

  async function handle(request: WorkerRequest): Promise<unknown> {
    switch (request.type) {
      case "init":
        return init(request.deps, request.baseUrl);
      case "runChecks":
        return runChecks(request.repo, request.ref, request.packageDir);
      case "knownChecks":
        return knownChecks();
      case "generateHtml":
        return generateHtml(request.show);
    }
  }

  // Process requests strictly one at a time: the Python globals (and Pyodide
  // itself) are shared state, so interleaving at await points is unsafe.
  let queue: Promise<void> = Promise.resolve();
  ctx.onmessage = (event: MessageEvent) => {
    const request = event.data as WorkerRequest;
    queue = queue.then(async () => {
      try {
        const result = await handle(request);
        post({ kind: "response", id: request.id, ok: true, result });
      } catch (err) {
        const error = err instanceof Error ? err.message : String(err);
        post({ kind: "response", id: request.id, ok: false, error });
      }
    });
  };
}
