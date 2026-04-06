import type {
  KnownChecksData,
  ReviewRunData,
  WorkerRequest,
  WorkerResponse,
} from "./pyodide-common";

type ProgressHandler = (progress: number, message?: string) => void;

const PYODIDE_CDN_URL =
  "https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.js";

const LOAD_KNOWN_CHECKS_CODE = `
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
`;

const RUN_REVIEW_CODE = `
  import json
  from repo_review.files import collect_prefetch_files, process_prefetch_files
  from repo_review.ghpath import GHPath
  from repo_review.processor import collect_all, process, md_as_html

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
`;

const GENERATE_HTML_CODE = `
  from repo_review.html import to_html

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
`;

function createPyodideWorkerUrl(): string {
  const workerSource = `
const PYODIDE_CDN_URL = ${JSON.stringify(PYODIDE_CDN_URL)};
const LOAD_KNOWN_CHECKS_CODE = ${JSON.stringify(LOAD_KNOWN_CHECKS_CODE)};
const RUN_REVIEW_CODE = ${JSON.stringify(RUN_REVIEW_CODE)};
const GENERATE_HTML_CODE = ${JSON.stringify(GENERATE_HTML_CODE)};

let pyodidePromise = null;
let prepareQueue = Promise.resolve();
let micropipReady = false;
const installedDeps = new Set();
let runCounter = 0;

function postMessageToMain(message) {
  self.postMessage(message);
}

function asString(value) {
  return typeof value === "string" ? value : String(value);
}

async function getPyodide(report) {
  if (!pyodidePromise) {
    pyodidePromise = (async () => {
      report?.(5, "Initializing Pyodide runtime");
      self.importScripts(PYODIDE_CDN_URL);
      const pyodide = await self.loadPyodide();
      report?.(50, "Core Pyodide loaded");
      return pyodide;
    })();
  }

  return pyodidePromise;
}

async function preparePyodide(deps, report) {
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
        await pyodide.runPythonAsync(
          "import micropip\\nawait micropip.install(list(deps_for_install))",
        );
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

async function loadKnownChecks() {
  const pyodide = await getPyodide();
  const data = pyodide.runPython(LOAD_KNOWN_CHECKS_CODE);
  return JSON.parse(asString(data));
}

async function runReview(repo, ref, subdir) {
  const pyodide = await getPyodide();
  const token = "run-" + Date.now() + "-" + ++runCounter;

  pyodide.globals.set("repo_name", repo);
  pyodide.globals.set("repo_ref", ref);
  pyodide.globals.set("repo_subdir", subdir);
  pyodide.globals.set("run_token", token);

  try {
    const output = await pyodide.runPythonAsync(RUN_REVIEW_CODE);
    return JSON.parse(asString(output));
  } finally {
    pyodide.globals.delete("repo_name");
    pyodide.globals.delete("repo_ref");
    pyodide.globals.delete("repo_subdir");
    pyodide.globals.delete("run_token");
  }
}

async function generateHtml(token, show) {
  const pyodide = await getPyodide();
  pyodide.globals.set("html_run_token", token);
  pyodide.globals.set("show_for_html", show || "all");

  try {
    const output = await pyodide.runPythonAsync(GENERATE_HTML_CODE);
    return asString(output);
  } finally {
    pyodide.globals.delete("html_run_token");
    pyodide.globals.delete("show_for_html");
  }
}

async function handleRequest(request) {
  const reportProgress = (progress, message) => {
    postMessageToMain({
      id: request.id,
      type: "progress",
      progress,
      message,
    });
  };

  try {
    switch (request.type) {
      case "prepare":
        await preparePyodide(request.deps, reportProgress);
        postMessageToMain({ id: request.id, type: "success" });
        return;
      case "loadKnownChecks":
        postMessageToMain({
          id: request.id,
          type: "success",
          payload: await loadKnownChecks(),
        });
        return;
      case "runReview":
        postMessageToMain({
          id: request.id,
          type: "success",
          payload: await runReview(request.repo, request.ref, request.subdir),
        });
        return;
      case "generateHtml":
        postMessageToMain({
          id: request.id,
          type: "success",
          payload: await generateHtml(request.token, request.show),
        });
        return;
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    postMessageToMain({ id: request.id, type: "error", error: message });
  }
}

self.addEventListener("message", (event) => {
  void handleRequest(event.data);
});
`;

  return URL.createObjectURL(
    new Blob([workerSource], { type: "text/javascript" }),
  );
}

type WorkerRequestPayload =
  | { type: "prepare"; deps: string[] }
  | { type: "loadKnownChecks" }
  | { type: "runReview"; repo: string; ref: string; subdir: string }
  | { type: "generateHtml"; token: string; show: string };

interface PendingRequest {
  resolve: (value: unknown) => void;
  reject: (reason?: unknown) => void;
  onProgress?: ProgressHandler;
}

export interface PyodideClient {
  prepare(deps: string[], onProgress?: ProgressHandler): Promise<void>;
  loadKnownChecks(): Promise<KnownChecksData>;
  runReview(repo: string, ref: string, subdir?: string): Promise<ReviewRunData>;
  generateHtml(token: string, show?: string): Promise<string>;
  dispose(): void;
}

class WorkerPyodideClient implements PyodideClient {
  private readonly worker: Worker;

  private readonly workerUrl: string;

  private readonly pending = new Map<number, PendingRequest>();

  private nextRequestId = 1;

  constructor() {
    this.workerUrl = createPyodideWorkerUrl();
    this.worker = new Worker(this.workerUrl);
    this.worker.addEventListener("message", this.handleMessage);
    this.worker.addEventListener("error", this.handleError);
  }

  private handleMessage = (event: MessageEvent<WorkerResponse>): void => {
    const response = event.data;
    const pending = this.pending.get(response.id);
    if (!pending) {
      return;
    }

    if (response.type === "progress") {
      pending.onProgress?.(response.progress, response.message);
      return;
    }

    this.pending.delete(response.id);

    if (response.type === "error") {
      pending.reject(new Error(response.error));
      return;
    }

    pending.resolve(response.payload);
  };

  private handleError = (event: ErrorEvent): void => {
    const location = event.filename
      ? ` (${event.filename}:${event.lineno}:${event.colno})`
      : "";
    const message = `${event.message || "Pyodide worker failed"}${location}`;
    for (const [, pending] of this.pending) {
      pending.reject(new Error(message));
    }
    this.pending.clear();
  };

  private request<T>(
    request: WorkerRequestPayload,
    onProgress?: ProgressHandler,
  ): Promise<T> {
    const id = this.nextRequestId++;

    return new Promise<T>((resolve, reject) => {
      this.pending.set(id, {
        resolve: (value: unknown) => resolve(value as T),
        reject,
        onProgress,
      });
      const message: WorkerRequest = { id, ...request };
      this.worker.postMessage(message);
    });
  }

  prepare(deps: string[], onProgress?: ProgressHandler): Promise<void> {
    return this.request<void>({ type: "prepare", deps }, onProgress);
  }

  loadKnownChecks(): Promise<KnownChecksData> {
    return this.request<KnownChecksData>({ type: "loadKnownChecks" });
  }

  runReview(
    repo: string,
    ref: string,
    subdir: string = "",
  ): Promise<ReviewRunData> {
    return this.request<ReviewRunData>({
      type: "runReview",
      repo,
      ref,
      subdir,
    });
  }

  generateHtml(token: string, show: string = "all"): Promise<string> {
    return this.request<string>({ type: "generateHtml", token, show });
  }

  dispose(): void {
    this.worker.removeEventListener("message", this.handleMessage);
    this.worker.removeEventListener("error", this.handleError);
    for (const [, pending] of this.pending) {
      pending.reject(new Error("Pyodide worker disposed"));
    }
    this.pending.clear();
    this.worker.terminate();
    URL.revokeObjectURL(this.workerUrl);
  }
}

export function createPyodideClient(): PyodideClient {
  return new WorkerPyodideClient();
}
