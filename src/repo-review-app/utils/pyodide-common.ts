export interface CheckItem {
  name: string;
  description?: string;
  state?: boolean | null;
  err_msg?: string;
  url?: string;
  skip_reason?: string;
}

export interface FamilyInfo {
  name: string;
  description?: string;
}

export interface KnownCheckDefinition {
  name: string;
  family: string;
  description: string;
  url: string;
}

export interface KnownChecksData {
  families: Record<string, { name: string }>;
  results: KnownCheckDefinition[];
}

export interface ReviewRunData {
  token: string;
  families: Record<string, FamilyInfo>;
  results: Record<string, CheckItem[]>;
}

export type WorkerRequest =
  | { id: number; type: "prepare"; deps: string[] }
  | { id: number; type: "loadKnownChecks" }
  | { id: number; type: "runReview"; repo: string; ref: string; subdir: string }
  | { id: number; type: "generateHtml"; token: string; show: string };

export type WorkerResponse =
  | { id: number; type: "progress"; progress: number; message?: string }
  | { id: number; type: "success"; payload?: unknown }
  | { id: number; type: "error"; error: string };
