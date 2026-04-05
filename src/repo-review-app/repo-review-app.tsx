import React from "react";
import ReactDOM from "react-dom/client";
import {
  Box,
  CssBaseline,
  CircularProgress,
  Stack,
  TextField,
  Autocomplete,
  Paper,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Icon,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Snackbar,
  Alert,
} from "@mui/material";
import Heading from "./components/Heading";
import Results from "./components/Results";
import MyThemeProvider from "./components/MyThemeProvider";
import { fetchRepoRefs } from "./utils/github";
import {
  prepare_pyodide,
  run_process,
  load_known_checks,
  generate_html,
  prefetch,
  collect_checks,
} from "./utils/pyodide";
import type { PyodideInterface } from "pyodide";
import type { PyProxy } from "pyodide/ffi";
import type { SelectChangeEvent } from "@mui/material";

const DEFAULT_MSG =
  "Enter a GitHub repo and branch/tag to review. Runs Python entirely in your browser using WebAssembly. Built with React, MaterialUI, and Pyodide.";

// Sanitize a package subdirectory path: strip leading slashes, reject any
// segment that is ".." (path traversal). Returns empty string for invalid input.
function sanitizePackageDir(raw: string): string {
  const trimmed = raw.trim().replace(/^\/+/, "");
  if (trimmed.split("/").some((seg) => seg === "..")) return "";
  return trimmed;
}

interface CheckItem {
  name: string;
  description?: string;
  state?: boolean | null | undefined;
  err_msg?: string;
  url?: string;
  skip_reason?: string;
}

interface Refs {
  branches: { name: string }[];
  tags: { name: string }[];
}

interface Option {
  label: string;
  value: string;
  type: "branch" | "tag";
}

interface AppProps {
  deps: string[];
  header?: boolean;
}

interface AppState {
  show: string;
  results: Record<string, CheckItem[]> | CheckItem[];
  pyFamilies: PyProxy | null;
  pyChecks: PyProxy | null;
  snackbarOpen: boolean;
  snackbarMsg: string;
  snackbarSeverity: "info" | "error" | "warning" | "success";
  repo: string;
  ref: string;
  refInputValue: string;
  packageDir: string;
  refType: "branch" | "tag";
  refs: Refs;
  msg: string;
  progress: boolean;
  loadingRefs: boolean;
  err_msg: string;
  skip_reason: string;
  url: string;
  knownChecks: Record<string, CheckItem[]> | null;
  families: Record<string, { name: string; description?: string }>;
  knownFamilies: Record<string, { name: string; description?: string }>;
  infoOpen: boolean;
  pyodideProgress: number;
  pyodideLoading: boolean;
  pyodideMessage?: string;
  completedRepo: string;
  completedRef: string;
  completedRefType: "branch" | "tag";
}

function parseRefType(value: string | null): "branch" | "tag" {
  return value === "tag" ? "tag" : "branch";
}

class App extends React.Component<AppProps, AppState> {
  pyodide_promise: Promise<PyodideInterface> | null;

  constructor(props: AppProps) {
    super(props);
    const inner_deps_str = props.deps.join("\n");
    const deps_str = `<pre><code>${inner_deps_str}</code></pre>`;
    const params = new URLSearchParams(window.location.search);
    const initialRef = params.get("ref") || "HEAD";
    const initialRefInput = params.get("ref") || "";
    this.state = {
      show: params.get("show") || "all",
      results: [],
      pyFamilies: null,
      pyChecks: null,
      snackbarOpen: false,
      snackbarMsg: "",
      snackbarSeverity: "info",
      repo: params.get("repo") || "",
      ref: initialRef,
      refInputValue: initialRefInput,
      packageDir: sanitizePackageDir(params.get("packageDir") || ""),
      refType: parseRefType(params.get("refType")),
      refs: { branches: [], tags: [] },
      msg: `<p>${DEFAULT_MSG}</p><h4>Packages:</h4> ${deps_str}`,
      progress: false,
      loadingRefs: false,
      err_msg: "",
      skip_reason: "",
      url: "",
      knownChecks: null,
      families: {},
      knownFamilies: {},
      infoOpen: true,
      pyodideProgress: 0,
      pyodideLoading: true,
      pyodideMessage: "",
      completedRepo: "",
      completedRef: "",
      completedRefType: "branch",
    };
    this.pyodide_promise = null;
  }

  destroyProxy(proxy: PyProxy | null): void {
    if (proxy) {
      try {
        proxy.destroy();
      } catch (e) {
        // ignore destroy errors
      }
    }
  }

  componentWillUnmount() {
    this.destroyProxy(this.state.pyFamilies);
    this.destroyProxy(this.state.pyChecks);
  }

  async fetchRepoReferences(repo: string) {
    if (!repo) return;

    this.setState({ loadingRefs: true });
    const refs = await fetchRepoRefs(repo);
    this.setState({ refs: refs, loadingRefs: false });
  }

  handleRepoChange(repo: string) {
    this.destroyProxy(this.state.pyFamilies);
    this.destroyProxy(this.state.pyChecks);
    this.setState({
      repo,
      refs: { branches: [], tags: [] },
      pyFamilies: null,
      pyChecks: null,
    });
  }

  handleRefChange(ref: string, refType: "branch" | "tag") {
    this.destroyProxy(this.state.pyFamilies);
    this.destroyProxy(this.state.pyChecks);
    this.setState({ ref, refType, pyFamilies: null, pyChecks: null });
  }

  async handleCompute() {
    if (!this.state.repo || !this.state.ref) {
      this.setState({ results: [], msg: DEFAULT_MSG });
      window.history.replaceState(null, "", window.location.pathname);
      this.setState({
        snackbarOpen: true,
        snackbarMsg: `Please enter a repo and branch/tag`,
        snackbarSeverity: "warning",
      });
      return;
    }
    const local_params = new URLSearchParams({
      repo: this.state.repo,
      ref: this.state.ref,
      refType: this.state.refType,
      show: this.state.show,
    });
    const packageDir = sanitizePackageDir(this.state.packageDir);
    if (packageDir) {
      local_params.set("packageDir", packageDir);
    }
    window.history.replaceState(
      null,
      "",
      `${window.location.pathname}?${local_params}`,
    );
    this.setState({ results: [], progress: true, infoOpen: false });
    const state = this.state;
    let pyPackage: PyProxy | null = null;
    let collected: PyProxy | null = null;
    let families_dict: any = null;
    let results_list: any = null;
    try {
      const pyodide = await this.pyodide_promise!;
      pyPackage = await prefetch(pyodide, state.repo, state.ref, packageDir);
      collected = collect_checks(pyodide, pyPackage, packageDir);
      results_list = run_process(
        pyodide,
        pyPackage,
        collected,
        packageDir,
      ) as any;
      families_dict = (collected as any).families.copy();

      const results: Record<string, CheckItem[]> = {};
      const families: Record<string, { name: string; description?: string }> =
        {};
      for (const val of families_dict) {
        const descr = families_dict.get(val).get("description");
        results[val] = [];
        families[val] = {
          name: families_dict.get(val).get("name").toString(),
          description: descr && descr.toString(),
        };
      }
      for (const val of results_list) {
        results[val.family].push({
          name: val.name.toString(),
          description: val.description.toString(),
          state: val.result,
          err_msg: val.err_msg.toString(),
          url: val.url.toString(),
          skip_reason: val.skip_reason.toString(),
        });
      }

      // Destroy any previously stored PyProxies for a different run
      if (this.state.pyFamilies && this.state.pyFamilies !== families_dict) {
        this.destroyProxy(this.state.pyFamilies);
      }
      if (this.state.pyChecks && this.state.pyChecks !== results_list) {
        this.destroyProxy(this.state.pyChecks);
      }

      this.setState({
        results: results,
        families: families,
        progress: false,
        err_msg: "",
        url: "",
        infoOpen: false,
        pyFamilies: families_dict,
        pyChecks: results_list,
        completedRepo: state.repo,
        completedRef: state.ref,
        completedRefType: state.refType,
      });
      // Proxies are now owned by state; clear locals to avoid destroying them in catch
      families_dict = null;
      results_list = null;
    } catch (e: unknown) {
      // Destroy any proxies from this run that were not saved to state
      this.destroyProxy(families_dict);
      this.destroyProxy(results_list);
      const emsg = (e as Error)?.message || String(e);
      if (emsg.includes("KeyError: 'tree'")) {
        this.setState({
          progress: false,
          err_msg: "Invalid repository or branch/tag. Please try again.",
        });
      } else {
        this.setState({
          progress: false,
          err_msg: `<pre><code>${emsg}</code></pre>`,
        });
      }
    } finally {
      // prefetch and collected are run-scoped only; release them after processing
      this.destroyProxy(collected);
      this.destroyProxy(pyPackage);
    }
  }

  async handleCopyHtml() {
    if (!this.state.repo || !this.state.ref) {
      this.setState({
        snackbarOpen: true,
        snackbarMsg: `Please enter a repo and branch/tag`,
        snackbarSeverity: "warning",
      });
      return;
    }

    try {
      const pyodide = await this.pyodide_promise!;

      let htmlOut: string;

      // Reuse previously stored PyProxy results if they correspond to the
      // same repo/ref to avoid rerunning the expensive `process(package)`.
      if (this.state.pyFamilies && this.state.pyChecks) {
        // Use stored pyFamilies/pyChecks; they are cleared when repo/ref change
        htmlOut = await generate_html(
          pyodide,
          this.state.pyFamilies,
          this.state.pyChecks,
          this.state.show || "all",
        );
      } else {
        // Shouldn't be possible: if we have a copy button, we should have
        // a stored run result for that repo/ref. Show an error instead of
        // rerunning the expensive process.
        this.setState({
          snackbarOpen: true,
          snackbarMsg:
            "Stored results do not match current repo/ref — please run the checks first",
          snackbarSeverity: "error",
        });
        return;
      }

      const htmlStr = htmlOut.toString ? htmlOut.toString() : htmlOut;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(htmlStr);
        this.setState({
          snackbarOpen: true,
          snackbarMsg: "HTML output copied to clipboard",
          snackbarSeverity: "success",
        });
      } else {
        // Fallback: open in new window for manual copy
        const w = window.open("", "repo-review-html");
        if (w) {
          w.document.write(htmlStr);
          w.document.close();
        }
      }
    } catch (e: unknown) {
      console.error("Error generating HTML:", e);
      const emsg = (e as Error)?.message || String(e);
      this.setState({
        snackbarOpen: true,
        snackbarMsg: "Error generating HTML: " + emsg,
        snackbarSeverity: "error",
      });
    }
  }

  async loadKnownChecks() {
    const pyodide = await this.pyodide_promise!;
    let data: { families?: Record<string, { name: string }>; results?: any[] } =
      {};
    try {
      data = load_known_checks(pyodide);
    } catch (e) {
      console.error("Error loading known checks:", e);
      return;
    }

    const knownResults: Record<string, CheckItem[]> = {};
    const knownFamilies: Record<string, { name: string }> = {};

    const knownFamiliesInput = data.families || {};

    for (const key of Object.keys(knownFamiliesInput)) {
      knownResults[key] = [];
      knownFamilies[key] = {
        name: knownFamiliesInput[key].name,
      };
    }

    for (const check of data.results || []) {
      if (knownResults[check.family] !== undefined) {
        knownResults[check.family].push({
          name: check.name,
          description: check.description,
          state: null,
          err_msg: "",
          url: check.url,
          skip_reason: "",
        });
      }
    }

    this.setState({ knownChecks: knownResults, knownFamilies: knownFamilies });
  }

  componentDidMount() {
    this.pyodide_promise = prepare_pyodide(
      this.props.deps,
      (p: number, m?: string) =>
        this.setState({
          pyodideProgress: p,
          pyodideLoading: p < 100,
          pyodideMessage: m || "",
        }),
    );
    const params = new URLSearchParams(window.location.search);
    if (params.get("repo")) {
      this.fetchRepoReferences(params.get("repo")!);
    }
    if (params.get("repo") && params.get("ref")) {
      this.handleCompute();
    } else {
      this.pyodide_promise.then(() => this.loadKnownChecks());
    }
  }

  render() {
    const priorityBranches = ["HEAD", "main", "master", "develop", "stable"];
    const branchMap = new Map(
      this.state.refs.branches.map((branch) => [branch.name, branch]),
    );

    let availableOptions: Option[] = [];

    if (
      this.state.repo === "" ||
      (this.state.refs.branches.length === 0 &&
        this.state.refs.tags.length === 0)
    ) {
      availableOptions = [
        { label: "HEAD (default branch)", value: "HEAD", type: "branch" },
        { label: "main (branch)", value: "main", type: "branch" },
        { label: "master (branch)", value: "master", type: "branch" },
        { label: "develop (branch)", value: "develop", type: "branch" },
        { label: "stable (branch)", value: "stable", type: "branch" },
      ];
    } else {
      const prioritizedBranches: Option[] = [
        { label: "HEAD (default branch)", value: "HEAD", type: "branch" },
      ];

      priorityBranches.slice(1).forEach((branchName) => {
        if (branchMap.has(branchName)) {
          prioritizedBranches.push({
            label: `${branchName} (branch)`,
            value: branchName,
            type: "branch",
          });
          branchMap.delete(branchName);
        }
      });

      const otherBranches: Option[] = [];
      branchMap.forEach((branch) => {
        otherBranches.push({
          label: `${branch.name} (branch)`,
          value: branch.name,
          type: "branch",
        });
      });
      otherBranches.sort((a, b) => a.value.localeCompare(b.value));

      const tagOptions = this.state.refs.tags.map((tag) => ({
        label: `${tag.name} (tag)`,
        value: tag.name,
        type: "tag" as const,
      }));
      tagOptions.sort((a, b) => a.value.localeCompare(b.value));

      availableOptions = [
        ...prioritizedBranches,
        ...otherBranches,
        ...tagOptions,
      ];
    }

    const hasResults = !Array.isArray(this.state.results);
    const displayResults = hasResults
      ? this.state.results
      : !this.state.progress && this.state.knownChecks
        ? this.state.knownChecks
        : null;
    const displayFamilies = hasResults
      ? this.state.families
      : this.state.knownFamilies;
    const resultsHeading = hasResults
      ? `Results for ${this.state.completedRepo}@${this.state.completedRef} (${this.state.completedRefType})`
      : "Available checks";

    // Apply CLI-like --show filtering: all | err | errskip
    let filteredResults = displayResults;
    let filteredFamilies = displayFamilies;
    if (displayResults && this.state.show && this.state.show !== "all") {
      const groupedResults = displayResults as Record<string, CheckItem[]>;
      const groupedFamilies = displayFamilies as Record<
        string,
        { name: string; description?: string }
      >;
      const newResults: Record<string, CheckItem[]> = {};
      for (const fam of Object.keys(groupedResults)) {
        const items = groupedResults[fam];
        // first keep items that are not passing (i.e., state !== true)
        let kept = items.filter((it: CheckItem) => it.state !== true);
        // if 'err', then keep only failing checks
        if (this.state.show === "err") {
          kept = kept.filter((it: CheckItem) => it.state === false);
        }
        if (kept.length > 0) {
          newResults[fam] = kept;
        }
      }

      const knownFamilies = new Set(Object.keys(newResults));
      const newFamilies: Record<
        string,
        { name: string; description?: string }
      > = {};
      for (const k of Object.keys(groupedFamilies)) {
        if (
          knownFamilies.has(k) ||
          (groupedFamilies[k] && groupedFamilies[k].description)
        ) {
          newFamilies[k] = groupedFamilies[k];
        }
      }

      filteredResults = newResults;
      filteredFamilies = newFamilies;
    }

    return (
      <MyThemeProvider>
        <CssBaseline />
        <Box>
          {this.props.header && <Heading />}
          <Stack
            direction={{ xs: "column", sm: "row" }}
            spacing={2}
            alignItems={{ xs: "stretch", sm: "stretch" }}
            sx={{ m: 1, mb: 3 }}
          >
            <TextField
              id="repo-select"
              label="Org/Repo"
              helperText="e.g. scikit-hep/hist"
              autoFocus={true}
              onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => {
                if (e.key === "Enter") this.handleCompute();
              }}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                this.handleRepoChange(e.target.value)
              }
              value={this.state.repo}
              sx={{ flexGrow: 3 }}
            />
            <Autocomplete<Option, false, false, true>
              disablePortal
              id="ref-select"
              options={availableOptions}
              loading={this.state.loadingRefs}
              freeSolo={true}
              onKeyDown={(e: React.KeyboardEvent) => {
                if (e.key === "Enter") this.handleCompute();
              }}
              getOptionLabel={(option) =>
                typeof option === "string" ? option : option.label
              }
              renderOption={(props, option) => {
                const { key, ...rest } =
                  props as React.HTMLAttributes<HTMLLIElement> & {
                    key: React.Key;
                  };
                return (
                  <li key={key} {...rest}>
                    {option.label}
                  </li>
                );
              }}
              inputValue={this.state.refInputValue}
              onInputChange={(_e, value, reason) => {
                this.setState({ refInputValue: value });
                if (reason === "input") {
                  this.handleRefChange(value || "HEAD", "branch");
                }
              }}
              onChange={(_e, option) => {
                if (option === null) {
                  this.handleRefChange("", "branch");
                } else if (typeof option === "object") {
                  this.handleRefChange(option.value, option.type);
                } else {
                  this.handleRefChange(option, "branch");
                }
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Branch/Tag"
                  helperText="e.g. HEAD, main, or v1.0.0"
                  onFocus={() => this.fetchRepoReferences(this.state.repo)}
                  sx={{ flexGrow: 2, minWidth: 200 }}
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {this.state.loadingRefs ? (
                          <CircularProgress color="inherit" size={20} />
                        ) : null}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
            />
            <Stack
              direction={{ xs: "row", sm: "column" }}
              spacing={1}
              sx={{ flexGrow: 1, minWidth: { xs: 240, sm: 180 } }}
            >
              <TextField
                id="package-dir-select"
                label="Package dir (if not at root)"
                value={this.state.packageDir}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  this.setState({ packageDir: e.target.value })
                }
                sx={{ flexGrow: 1 }}
              />
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "row",
                  gap: 1,
                  alignItems: "center",
                  justifyContent: "flex-end",
                  flexGrow: 1,
                }}
              >
                <FormControl sx={{ minWidth: 140 }}>
                  <InputLabel id="show-select-label">Show</InputLabel>
                  <Select
                    labelId="show-select-label"
                    id="show-select"
                    value={this.state.show}
                    label="Show"
                    onChange={(e: SelectChangeEvent<string>) => {
                      const val = e.target.value as string;
                      this.setState({ show: val });
                      // update query string to persist show selection
                      const params = new URLSearchParams(
                        window.location.search,
                      );
                      if (val && val !== "all") {
                        params.set("show", val);
                      } else {
                        params.delete("show");
                      }
                      // preserve repo/ref/refType/packageDir if present
                      if (!params.get("repo") && this.state.repo)
                        params.set("repo", this.state.repo);
                      if (!params.get("ref") && this.state.ref)
                        params.set("ref", this.state.ref);
                      if (!params.get("refType") && this.state.refType)
                        params.set("refType", this.state.refType);
                      if (!params.get("packageDir") && this.state.packageDir)
                        params.set("packageDir", this.state.packageDir);
                      window.history.replaceState(
                        null,
                        "",
                        `${window.location.pathname}?${params}`,
                      );
                    }}
                    size="small"
                  >
                    <MenuItem value="all">All</MenuItem>
                    <MenuItem value="err">Errors only</MenuItem>
                    <MenuItem value="errskip">Errors + Skips</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Stack>
            <Button
              onClick={() => this.handleCompute()}
              variant="contained"
              size="large"
              disabled={
                this.state.progress || !this.state.repo || !this.state.ref
              }
              sx={{ alignSelf: "stretch", minWidth: 64 }}
            >
              <Icon>start</Icon>
            </Button>
          </Stack>
          <Paper elevation={3}>
            <Accordion
              expanded={this.state.infoOpen}
              onChange={(e: React.SyntheticEvent, open: boolean) =>
                this.setState({ infoOpen: open })
              }
              elevation={0}
              disableGutters
              square
              sx={{ borderBottom: 1, borderColor: "divider" }}
            >
              <AccordionSummary
                expandIcon={<Icon>expand_more</Icon>}
                sx={{ bgcolor: "primary.main", color: "primary.contrastText" }}
              >
                <Typography fontWeight="medium">About</Typography>
              </AccordionSummary>
              <AccordionDetails sx={{ bgcolor: "transparent" }}>
                <Typography variant="body1" component="div">
                  <span dangerouslySetInnerHTML={{ __html: this.state.msg }} />
                </Typography>
              </AccordionDetails>
            </Accordion>
            {(this.state.pyodideLoading || this.state.progress) && (
              <Box sx={{ m: 2 }}>
                <LinearProgress
                  variant={
                    this.state.pyodideLoading ? "determinate" : "indeterminate"
                  }
                  value={
                    this.state.pyodideLoading
                      ? this.state.pyodideProgress
                      : undefined
                  }
                />
                <Typography variant="caption" sx={{ display: "block", mt: 1 }}>
                  {this.state.pyodideLoading
                    ? this.state.pyodideMessage
                      ? `${this.state.pyodideMessage} — ${this.state.pyodideProgress}%`
                      : `Pyodide loading: ${this.state.pyodideProgress}%`
                    : "reading repository"}
                </Typography>
              </Box>
            )}
            {this.state.err_msg && (
              <Typography
                variant="body1"
                component="div"
                color="error"
                sx={{ p: 2 }}
              >
                <span
                  dangerouslySetInnerHTML={{ __html: this.state.err_msg }}
                />
              </Typography>
            )}
            {displayResults && (
              <>
                <Box
                  sx={{ display: "flex", alignItems: "center", px: 2, pt: 1 }}
                >
                  <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    {resultsHeading}
                  </Typography>
                  {hasResults && (
                    <Button
                      onClick={() => this.handleCopyHtml()}
                      size="small"
                      disabled={
                        this.state.progress || this.state.pyodideLoading
                      }
                    >
                      <Icon>content_copy</Icon>
                    </Button>
                  )}
                </Box>
                <Results
                  results={filteredResults}
                  families={filteredFamilies}
                />
              </>
            )}
          </Paper>
        </Box>
        <Snackbar
          open={this.state.snackbarOpen}
          autoHideDuration={4000}
          onClose={() => this.setState({ snackbarOpen: false })}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert
            onClose={() => this.setState({ snackbarOpen: false })}
            severity={this.state.snackbarSeverity as any}
            sx={{ width: "100%" }}
          >
            {this.state.snackbarMsg}
          </Alert>
        </Snackbar>
      </MyThemeProvider>
    );
  }
}

export function mountApp(opts: Partial<AppProps> = {}) {
  const root = ReactDOM.createRoot(document.getElementById("root")!);
  const props: AppProps = { deps: [], ...opts };
  root.render(<App {...props} />);
}

export default App;
