// Sanitize a package subdirectory path: strip leading slashes, reject any
// segment that is ".." (path traversal). Returns empty string for invalid input.
export function sanitizePackageDir(raw: string): string {
  const trimmed = raw.trim().replace(/^\/+/, "");
  if (trimmed.split("/").some((seg) => seg === "..")) return "";
  return trimmed;
}

export function parseRefType(value: string | null): "branch" | "tag" {
  return value === "tag" ? "tag" : "branch";
}
