import type { CheckItem } from "../repo-review-app";

// pyproject.toml config that ignores every failed check, or "" if none failed.
export function ignoreToml(results: Record<string, CheckItem[]>): string {
  const failed = Object.values(results)
    .flat()
    .filter((r) => r.state === false)
    .map((r) => `"${r.name}"`);
  if (failed.length === 0) return "";
  return `[tool.repo-review]\nignore = [${failed.join(", ")}]`;
}
