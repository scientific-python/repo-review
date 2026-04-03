import type { PyodideInterface } from "pyodide";
import type { PyProxy } from "pyodide/ffi";

declare global {
  interface Window {
    loadPyodide?: () => Promise<PyodideInterface>;
  }
}

export async function prepare_pyodide(
  deps: string[],
  onProgress?: (p: number, m?: string) => void,
): Promise<PyodideInterface> {
  const deps_str = deps.map((i) => `\"${i}\"`).join(", ");
  try {
    if (onProgress) onProgress(5, "Initializing Pyodide runtime");
    // loadPyodide is provided by the Pyodide script at runtime
    const pyodide: PyodideInterface = await (window as Window).loadPyodide!();
    if (onProgress) onProgress(50, "Core Pyodide loaded");

    if (onProgress) onProgress(65, "Loading micropip");
    await pyodide.loadPackage("micropip");
    if (onProgress) onProgress(80, "Installing Python packages");

    await pyodide.runPythonAsync(`
      import micropip
      await micropip.install([${deps_str}])
    `);

    if (onProgress) onProgress(100, "Ready");
    return pyodide;
  } catch (e) {
    if (onProgress) onProgress(100, "Error during load");
    throw e;
  }
}

export async function prefetch(
  pyodide: PyodideInterface,
  repo: string,
  branch: string,
): Promise<PyProxy | null> {
  pyodide.globals.set("repo", repo);
  pyodide.globals.set("branch", branch);
  const packagePy = await pyodide.runPythonAsync(`
    from repo_review.files import collect_prefetch_files, process_prefetch_files
    from repo_review.ghpath import GHPath

    package = await GHPath.async_from_repo(repo, branch)
    prefetch_files = collect_prefetch_files()
    await process_prefetch_files(package, prefetch_files)
    package
  `);

  // package can be None in Python land -> map to null
  return packagePy === undefined ? null : (packagePy as PyProxy | null);
}

// Package can be None
export function collect_checks(
  pyodide: PyodideInterface,
  pyPackage: PyProxy | null,
): PyProxy {
  pyodide.globals.set("package", pyPackage);
  const collected = pyodide.runPython(`
    from repo_review.processor import collect_all

    collect_all(package)
  `);
  return collected as PyProxy;
}

export function run_process(
  pyodide: PyodideInterface,
  pyPackage: PyProxy | null,
  collected: PyProxy,
): PyProxy {
  pyodide.globals.set("package", pyPackage);
  pyodide.globals.set("collected", collected);
  const checks = pyodide.runPython(`
    from repo_review.processor import process, md_as_html

    families, checks = process(package, collected=collected)

    for v in families.values():
        if v.get("description"):
            v["description"] = md_as_html(v["description"])
    [res.md_as_html() for res in checks]
    `);
  return checks;
}

export function load_known_checks(
  pyodide: PyodideInterface,
): Record<string, unknown> {
  const dataStr = pyodide.runPython(`
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

  // pyodide may return a PyProxy; ensure string
  return JSON.parse(dataStr.toString ? dataStr.toString() : dataStr);
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

  const htmlOut = await pyodide.runPythonAsync(`
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

  return htmlOut.toString ? htmlOut.toString() : htmlOut;
}
