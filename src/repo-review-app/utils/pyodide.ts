import type { PyodideInterface } from "pyodide";
import type { PyProxy } from "pyodide/ffi";
import pyodidePackage from "pyodide/package.json";

// Version resolved from the npm package at build time; runtime files loaded from CDN
const DEFAULT_PYODIDE_BASE_URL = `https://cdn.jsdelivr.net/pyodide/v${pyodidePackage.version}/full`;

export async function prepare_pyodide(
  deps: string[],
  pyodideBaseUrl?: string,
  onProgress?: (p: number, m?: string) => void,
): Promise<PyodideInterface> {
  // On failure the promise rejects; callers are responsible for surfacing
  // the error (the app shows it in the error banner).
  if (onProgress) onProgress(5, "Initializing Pyodide runtime");
  const baseUrl = pyodideBaseUrl ?? DEFAULT_PYODIDE_BASE_URL;
  const { loadPyodide } = (await import(`${baseUrl}/pyodide.mjs`)) as {
    loadPyodide: () => Promise<PyodideInterface>;
  };
  const pyodide: PyodideInterface = await loadPyodide();
  if (onProgress) onProgress(50, "Core Pyodide loaded");

  if (onProgress) onProgress(65, "Loading micropip");
  await pyodide.loadPackage("micropip");
  if (onProgress) onProgress(80, "Installing Python packages");

  // Pass deps via globals instead of string interpolation for safety
  pyodide.globals.set("_rr_deps_to_install", deps);
  await pyodide.runPythonAsync(`
    import micropip
    await micropip.install(list(_rr_deps_to_install))
  `);
  pyodide.globals.delete("_rr_deps_to_install");

  if (onProgress) onProgress(100, "Ready");
  return pyodide;
}

export async function prefetch(
  pyodide: PyodideInterface,
  repo: string,
  branch: string,
  subdir: string = "",
): Promise<PyProxy | null> {
  pyodide.globals.set("repo", repo);
  pyodide.globals.set("branch", branch);
  pyodide.globals.set("subdir", subdir);
  const packagePy = await pyodide.runPythonAsync(`
    from repo_review.files import collect_prefetch_files, process_prefetch_files
    from repo_review.ghpath import GHPath

    package = await GHPath.async_from_repo(repo, branch)
    prefetch_files = collect_prefetch_files()
    await process_prefetch_files(package, prefetch_files, subdir=subdir)
    package
  `);

  // package can be None in Python land -> map to null
  return packagePy === undefined ? null : (packagePy as PyProxy | null);
}

// Package can be None
export function collect_checks(
  pyodide: PyodideInterface,
  pyPackage: PyProxy | null,
  subdir: string = "",
): PyProxy {
  pyodide.globals.set("package", pyPackage);
  pyodide.globals.set("subdir", subdir);
  const collected = pyodide.runPython(`
    from repo_review.processor import collect_all

    collect_all(package, subdir=subdir)
  `);
  return collected as PyProxy;
}

export function run_process(
  pyodide: PyodideInterface,
  pyPackage: PyProxy | null,
  collected: PyProxy,
  subdir: string = "",
): PyProxy {
  pyodide.globals.set("package", pyPackage);
  pyodide.globals.set("collected", collected);
  pyodide.globals.set("subdir", subdir);
  const checks = pyodide.runPython(`
    from repo_review.processor import process, md_as_html

    families, checks = process(package, collected=collected, subdir=subdir)

    for v in families.values():
        if v.get("description"):
            v["description"] = md_as_html(v["description"])
    [res.md_as_html() for res in checks]
    `);
  return checks;
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

export function load_known_checks(pyodide: PyodideInterface): KnownChecksData {
  const dataStr: string = pyodide.runPython(`
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

  // Python `str` converts directly to a JS string
  return JSON.parse(dataStr) as KnownChecksData;
}

export async function generate_html(
  pyodide: PyodideInterface,
  familiesPy: PyProxy | Record<string, unknown>,
  checksPy: PyProxy | unknown[],
  show: string = "all",
): Promise<string> {
  pyodide.globals.set("families_for_html", familiesPy);
  pyodide.globals.set("checks_for_html", checksPy);
  pyodide.globals.set("show_for_html", show || "all");

  const htmlOut: string = await pyodide.runPythonAsync(`
    from repo_review.html import to_html

    match show_for_html:
        case "all":
            filtered = checks_for_html
        case "err":
            filtered = [c for c in checks_for_html if c.result is False]
        case "errskip":
            filtered = [c for c in checks_for_html if c.result is not True]
        case _:
            filtered = checks_for_html

    to_html(families_for_html, filtered)
    `);

  // Python `str` converts directly to a JS string
  return htmlOut;
}
