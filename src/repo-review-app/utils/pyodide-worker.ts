/// <reference lib="webworker" />

import type { PyodideInterface } from "pyodide";
import type {
  KnownChecksData,
  ReviewRunData,
  WorkerRequest,
  WorkerResponse,
} from "./pyodide-common";

const PYODIDE_CDN_URL =
  "https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.mjs";

const workerScope = self as DedicatedWorkerGlobalScope;

let pyodidePromise: Promise<PyodideInterface> | null = null;
let prepareQueue: Promise<void> = Promise.resolve();
let micropipReady = false;
const installedDeps = new Set<string>();
let runCounter = 0;

function postMessage(message: WorkerResponse): void {
  workerScope.postMessage(message);
}

function asString(value: unknown): string {
  return typeof value === "string" ? value : String(value);
}

async function getPyodide(
  report?: (progress: number, message?: string) => void,
) {
  if (!pyodidePromise) {
    pyodidePromise = (async () => {
      report?.(5, "Initializing Pyodide runtime");
      const pyodideModule = (await import(PYODIDE_CDN_URL)) as {
        loadPyodide: () => Promise<PyodideInterface>;
      };
      const pyodide = await pyodideModule.loadPyodide();
      report?.(50, "Core Pyodide loaded");
      return pyodide;
    })();
  }

  return pyodidePromise;
}

async function preparePyodide(
  deps: string[],
  report?: (progress: number, message?: string) => void,
): Promise<void> {
  const requestedDeps = [...deps];
  const task = prepareQueue.then(async () => {
    const pyodide = await getPyodide(report);

    if (!micropipReady) {
      report?.(65, "Loading micropip");
      await pyodide.loadPackage("micropip");
      micropipReady = true;
    }

    const missingDeps = requestedDeps.filter((dep) => !installedDeps.has(dep));

    if (missingDeps.length > 0) {
      report?.(80, "Installing Python packages");
      pyodide.globals.set("deps_for_install", missingDeps);
      try {
        await pyodide.runPythonAsync(`
          import micropip
          await micropip.install(list(deps_for_install))
        `);
      } finally {
        pyodide.globals.delete("deps_for_install");
      }
      for (const dep of missingDeps) {
        installedDeps.add(dep);
      }
    }

    report?.(100, "Ready");
  });

  prepareQueue = task.catch(() => undefined);
  return task;
}

async function loadKnownChecks(): Promise<KnownChecksData> {
  const pyodide = await getPyodide();
  const data = pyodide.runPython(`
    import json
    from repo_review.processor import collect_all
    from repo_review.checks import get_check_url

    collected = collect_all()
    families_out = {k: {"name": v.get("name", k)} for k, v in collected.families.items()}
    results_out = []
    for name, check in collected.checks.items():
        desc = (check.__doc__ or "").strip()
        results_out.append({
            "name": name,
            "family": check.family,
            "description": desc,
            "url": get_check_url(name, check),
        })
    json.dumps({"families": families_out, "results": results_out})
  `);

  return JSON.parse(asString(data)) as KnownChecksData;
}

async function runReview(
  repo: string,
  ref: string,
  subdir: string,
): Promise<ReviewRunData> {
  const pyodide = await getPyodide();
  const token = `run-${Date.now()}-${++runCounter}`;
  const repoLiteral = JSON.stringify(repo);
  const refLiteral = JSON.stringify(ref);
  const subdirLiteral = JSON.stringify(subdir);
  const tokenLiteral = JSON.stringify(token);

  const output = await pyodide.runPythonAsync(`
      import json
      from repo_review.files import collect_prefetch_files, process_prefetch_files
      from repo_review.ghpath import GHPath
      from repo_review.processor import collect_all, process, md_as_html

      repo_name = ${repoLiteral}
      repo_ref = ${refLiteral}
      repo_subdir = ${subdirLiteral}
      run_token = ${tokenLiteral}

      package = await GHPath.async_from_repo(repo_name, repo_ref)
      prefetch_files = collect_prefetch_files()
      await process_prefetch_files(package, prefetch_files, subdir=repo_subdir)
      collected = collect_all(package, subdir=repo_subdir)
      families, checks = process(package, collected=collected, subdir=repo_subdir)

      for family_data in families.values():
          if family_data.get("description"):
              family_data["description"] = md_as_html(family_data["description"])

      def _stringify(value):
          return "" if value is None else str(value)

      families_out = {}
      results_out = {}

      for family_key, family_data in families.items():
          families_out[family_key] = {
              "name": _stringify(family_data.get("name", family_key)),
              "description": (
                  _stringify(family_data.get("description"))
                  if family_data.get("description")
                  else None
              ),
          }
          results_out[family_key] = []

      for result in checks:
          results_out.setdefault(result.family, []).append({
              "name": _stringify(result.name),
              "description": _stringify(result.description),
              "state": result.result,
              "err_msg": _stringify(result.err_msg),
              "url": _stringify(result.url),
              "skip_reason": _stringify(result.skip_reason),
          })

      _repo_review_last_token = run_token
      _repo_review_last_families = families
      _repo_review_last_checks = checks

      json.dumps({
          "token": run_token,
          "families": families_out,
          "results": results_out,
      })
    `);

  return JSON.parse(asString(output)) as ReviewRunData;
}

async function generateHtml(token: string, show: string): Promise<string> {
  const pyodide = await getPyodide();
  const tokenLiteral = JSON.stringify(token);
  const showLiteral = JSON.stringify(show || "all");

  const output = await pyodide.runPythonAsync(`
      from repo_review.html import to_html

      html_run_token = ${tokenLiteral}
      show_for_html = ${showLiteral}

      if globals().get("_repo_review_last_token") != html_run_token:
          raise RuntimeError(
              "Stored results do not match current repo/ref - please run the checks first"
          )

      match show_for_html:
          case "all":
              filtered = _repo_review_last_checks
          case "err":
              filtered = [c for c in _repo_review_last_checks if c.result is False]
          case "errskip":
              filtered = [c for c in _repo_review_last_checks if c.result is not True]
          case _:
              filtered = _repo_review_last_checks

      to_html(_repo_review_last_families, filtered)
    `);

  return asString(output);
}

async function handleRequest(request: WorkerRequest): Promise<void> {
  const reportProgress = (progress: number, message?: string) => {
    postMessage({ id: request.id, type: "progress", progress, message });
  };

  try {
    switch (request.type) {
      case "prepare":
        await preparePyodide(request.deps, reportProgress);
        postMessage({ id: request.id, type: "success" });
        return;
      case "loadKnownChecks":
        postMessage({
          id: request.id,
          type: "success",
          payload: await loadKnownChecks(),
        });
        return;
      case "runReview":
        postMessage({
          id: request.id,
          type: "success",
          payload: await runReview(request.repo, request.ref, request.subdir),
        });
        return;
      case "generateHtml":
        postMessage({
          id: request.id,
          type: "success",
          payload: await generateHtml(request.token, request.show),
        });
        return;
    }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    postMessage({ id: request.id, type: "error", error: message });
  }
}

workerScope.addEventListener(
  "message",
  (event: MessageEvent<WorkerRequest>) => {
    void handleRequest(event.data);
  },
);

export {};
