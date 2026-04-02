export async function prepare_pyodide(
  deps: string[],
  onProgress?: (p: number, m?: string) => void,
) {
  const deps_str = deps.map((i) => `\"${i}\"`).join(", ");
  try {
    if (onProgress) onProgress(5, "Initializing Pyodide runtime");
    // loadPyodide is provided by the Pyodide script at runtime
    const pyodide: any = await (window as any).loadPyodide();
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

export async function prefetch(pyodide: any, repo: string, branch: string) {
  pyodide.globals.set("repo", repo);
  pyodide.globals.set("branch", branch);
  const package = pyodide.runPythonAsync(`
    import asyncio
    from repo_review.files import collect_prefetch_files, process_prefetch_files
    from repo_review.ghpath import GHPath

    package = await GHPath.async_from_repo(repo, branch)
    prefetch_files = collect_prefetch_files()
    await process_prefetch_files(package, prefetch_files)
    package
  `);
  return package;
}

// Package can be None
export function collect_checks(pyodide: any, package: any) {
  pyodide.globals.set("package", package);
  const collected = pyodide.runPython(`
    from repo_review.processor import process, md_as_html

    collect_all(package)
    `);
    return collected;
}

export function run_process(pyodide: any, package: any, collected: any) {
  pyodide.globals.set("package", package);
  pyodide.globals.set("collected", collected);
  const families_checks = pyodide.runPython(`
    from repo_review.processor import process, md_as_html

    families, checks = process(package, collected=collected)

    for v in families.values():
        if v.get("description"):
            v["description"] = md_as_html(v["description"])
    checks = [res.md_as_html() for res in checks]

    (families, checks)
    `);
  return families_checks;
}

export function load_known_checks(pyodide: any) {
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
  pyodide: any,
  familiesPy: any,
  checksPy: any,
  show: string = "all",
) {
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
