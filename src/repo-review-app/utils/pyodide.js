export async function prepare_pyodide(deps, onProgress) {
  const deps_str = deps.map((i) => `\"${i}\"`).join(", ");
  try {
    if (onProgress) onProgress(5, "Initializing Pyodide runtime");
    const pyodide = await loadPyodide();
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
