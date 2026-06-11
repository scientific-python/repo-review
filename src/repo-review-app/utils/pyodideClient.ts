/**
 * Main-thread client for the Pyodide web worker.
 *
 * Runs the Python runtime off the main thread so the UI stays responsive
 * while packages install and checks run. Communication is a small
 * promise-based RPC over postMessage; only structured-cloneable plain data
 * crosses the boundary, so no PyProxy lifetime management leaks into React.
 *
 * The worker is created from a Blob URL built out of the stringified
 * `workerMain` function, so the app remains a single bundled file and works
 * under any bundler, including `bun serve`. See pyodideWorker.ts for details.
 */
import pyodidePackage from "pyodide/package.json";
import { workerMain } from "./pyodideWorker";
import type {
  KnownChecksData,
  RunChecksData,
  WorkerRequest,
  WorkerRequestPayload,
  WorkerResponse,
} from "./pyodideWorker";

export type {
  FamilyData,
  KnownChecksData,
  ResultData,
  RunChecksData,
} from "./pyodideWorker";

// Version resolved from the npm package at build time; runtime files loaded from CDN
const DEFAULT_PYODIDE_BASE_URL = `https://cdn.jsdelivr.net/pyodide/v${pyodidePackage.version}/full`;

export type ProgressCallback = (percent: number, message?: string) => void;

interface Pending {
  resolve: (value: unknown) => void;
  reject: (error: Error) => void;
}

export class PyodideClient {
  private worker: Worker;
  private objectUrl: string;
  private pending = new Map<number, Pending>();
  private nextId = 0;
  private onProgress?: ProgressCallback;

  constructor(onProgress?: ProgressCallback) {
    this.onProgress = onProgress;
    // The `(u) => import(u)` importer lives in this string (not in
    // pyodideWorker.ts) so no bundler ever sees it as code and rewrites it;
    // see the comment atop pyodideWorker.ts.
    const source = `(${workerMain.toString()})((u) => import(u));\n`;
    this.objectUrl = URL.createObjectURL(
      new Blob([source], { type: "text/javascript" }),
    );
    this.worker = new Worker(this.objectUrl, {
      type: "module",
      name: "repo-review-pyodide",
    });
    this.worker.onmessage = (event: MessageEvent<WorkerResponse>) => {
      this.handleMessage(event.data);
    };
    this.worker.onerror = (event: ErrorEvent) => {
      this.rejectAll(new Error(event.message || "Pyodide worker error"));
    };
  }

  /** Load Pyodide and install the Python dependencies. */
  init(deps: string[], pyodideBaseUrl?: string): Promise<void> {
    const baseUrl = pyodideBaseUrl ?? DEFAULT_PYODIDE_BASE_URL;
    return this.call({ type: "init", deps, baseUrl });
  }

  /**
   * Fetch a repo and run all checks on it. The worker also stores the run so
   * generateHtml() can reuse it without rerunning the checks.
   */
  runChecks(
    repo: string,
    ref: string,
    packageDir = "",
  ): Promise<RunChecksData> {
    return this.call({ type: "runChecks", repo, ref, packageDir });
  }

  /** List all installed checks (without running them). */
  knownChecks(): Promise<KnownChecksData> {
    return this.call({ type: "knownChecks" });
  }

  /** Render the most recent runChecks() result as standalone HTML. */
  generateHtml(show = "all"): Promise<string> {
    return this.call({ type: "generateHtml", show });
  }

  /** Stop the worker and release its resources. */
  terminate(): void {
    this.worker.terminate();
    URL.revokeObjectURL(this.objectUrl);
    this.rejectAll(new Error("Pyodide worker terminated"));
  }

  private call<T>(payload: WorkerRequestPayload): Promise<T> {
    const id = this.nextId++;
    return new Promise<T>((resolve, reject) => {
      this.pending.set(id, {
        resolve: resolve as (value: unknown) => void,
        reject,
      });
      const request: WorkerRequest = { ...payload, id };
      this.worker.postMessage(request);
    });
  }

  private handleMessage(message: WorkerResponse): void {
    if (message.kind === "progress") {
      this.onProgress?.(message.percent, message.message);
      return;
    }
    const pending = this.pending.get(message.id);
    if (!pending) {
      return;
    }
    this.pending.delete(message.id);
    if (message.ok) {
      pending.resolve(message.result);
    } else {
      pending.reject(new Error(message.error));
    }
  }

  private rejectAll(error: Error): void {
    for (const pending of this.pending.values()) {
      pending.reject(error);
    }
    this.pending.clear();
  }
}
