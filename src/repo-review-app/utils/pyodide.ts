import type {
  KnownChecksData,
  ReviewRunData,
  WorkerRequest,
  WorkerResponse,
} from "./pyodide-common";

type ProgressHandler = (progress: number, message?: string) => void;

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

  private readonly pending = new Map<number, PendingRequest>();

  private nextRequestId = 1;

  constructor() {
    this.worker = new Worker(this.getWorkerUrl(), { type: "module" });
    this.worker.addEventListener("message", this.handleMessage);
    this.worker.addEventListener("error", this.handleError);
  }

  private getWorkerUrl(): URL {
    const currentUrl = new URL(import.meta.url);
    const isSourceModule = currentUrl.pathname.includes(
      "/src/repo-review-app/",
    );

    return isSourceModule
      ? new URL("./pyodide-worker.ts", import.meta.url)
      : new URL("./utils/pyodide-worker.min.js", import.meta.url);
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
    const message = event.message || "Pyodide worker failed";
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
  }
}

export function createPyodideClient(): PyodideClient {
  return new WorkerPyodideClient();
}
