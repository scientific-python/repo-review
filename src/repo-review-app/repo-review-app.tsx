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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Snackbar,
  Alert,
} from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import Heading from "./components/Heading";
import Results from "./components/Results";
import MyThemeProvider from "./components/MyThemeProvider";
import { injectFonts } from "./utils/injectFonts";
import { fetchRepoRefs } from "./utils/github";
import { sanitizePackageDir, parseRefType } from "./utils/url";
import { PyodideClient } from "./utils/pyodideClient";
import type { KnownChecksData } from "./utils/pyodideClient";
import type { SelectChangeEvent } from "@mui/material";

const DEFAULT_MSG =
  "Enter a GitHub repo and branch/tag to review. Runs Python entirely in your browser using WebAssembly. Built with React, MaterialUI, and Pyodide.";

// Build the "About" HTML message. `deps` is app-configured (not user input),
// so interpolating it into HTML is safe.
function buildAboutMsg(deps: string[]): string {
  const deps_str = `<pre><code>${deps.join("\n")}</code></pre>`;
  return `<p>${DEFAULT_MSG}</p><h4>Packages:</h4> ${deps_str}`;
}

export interface CheckItem {
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

export interface AppProps {
  deps: string[];
  header?: boolean;
  pyodideBaseUrl?: string;
  /** Disable reading/writing window.location (e.g. when embedded as a widget) */
  disableUrlSync?: boolean;
}

interface AppState {
  show: string;
  results: Record<string, CheckItem[]> | null;
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
  /** App-level error banner text (always plain text, rendered as text content) */
  err_msg: string;
  /** Render err_msg in a monospace <pre><code> block (e.g. exception text) */
  err_is_code: boolean;
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

export class App extends React.Component<AppProps, AppState> {
  client: PyodideClient | null;
  readyPromise: Promise<void> | null;

  constructor(props: AppProps) {
    super(props);
    const params = props.disableUrlSync
      ? new URLSearchParams()
      : new URLSearchParams(window.location.search);
    const initialRef = params.get("ref") || "HEAD";
    const initialRefInput = params.get("ref") || "";
    this.state = {
      show: params.get("show") || "all",
      results: null,
      snackbarOpen: false,
      snackbarMsg: "",
      snackbarSeverity: "info",
      repo: params.get("repo") || "",
      ref: initialRef,
      refInputValue: initialRefInput,
      packageDir: sanitizePackageDir(params.get("packageDir") || ""),
      refType: parseRefType(params.get("refType")),
      refs: { branches: [], tags: [] },
      msg: buildAboutMsg(props.deps),
      progress: false,
      loadingRefs: false,
      err_msg: "",
      err_is_code: false,
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
    this.client = null;
    this.readyPromise = null;
  }

  componentWillUnmount() {
    this.client?.terminate();
    this.client = null;
  }

  async fetchRepoReferences(repo: string) {
    if (!repo) return;
    // Refs are reset whenever the repo changes, so non-empty refs means we
    // already fetched them for this repo; don't waste the GitHub rate limit.
    if (
      this.state.loadingRefs ||
      this.state.refs.branches.length > 0 ||
      this.state.refs.tags.length > 0
    ) {
      return;
    }

    this.setState({ loadingRefs: true });
    const refs = await fetchRepoRefs(repo);
    // Drop stale responses if the user switched repos while we were fetching.
    if (this.state.repo !== repo) {
      this.setState({ loadingRefs: false });
      return;
    }
    this.setState({ refs: refs, loadingRefs: false });
  }

  handleRepoChange(repo: string) {
    this.setState({ repo, refs: { branches: [], tags: [] } });
  }

  handleRefChange(ref: string, refType: "branch" | "tag") {
    this.setState({ ref, refType });
  }

  async handleCompute() {
    if (this.state.progress) return;
    if (!this.state.repo || !this.state.ref) {
      this.setState({ results: null, msg: buildAboutMsg(this.props.deps) });
      if (!this.props.disableUrlSync) {
        window.history.replaceState(null, "", window.location.pathname);
      }
      this.setState({
        snackbarOpen: true,
        snackbarMsg: `Please enter a repo and branch/tag`,
        snackbarSeverity: "warning",
      });
      return;
    }
    if (!this.props.disableUrlSync) {
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
    }
    this.setState({ results: null, progress: true, infoOpen: false });
    const packageDir = sanitizePackageDir(this.state.packageDir);
    const { repo, ref, refType } = this.state;
    try {
      // Surfaces init failures with their original message; the actual run
      // happens entirely inside the worker, returning plain data.
      await this.readyPromise!;
      const data = await this.client!.runChecks(repo, ref, packageDir);

      const results: Record<string, CheckItem[]> = {};
      const families: Record<string, { name: string; description?: string }> =
        {};
      for (const [key, family] of Object.entries(data.families)) {
        results[key] = [];
        families[key] = {
          name: family.name,
          description: family.description ?? undefined,
        };
      }
      for (const res of data.results) {
        results[res.family].push({
          name: res.name,
          description: res.description,
          state: res.result,
          err_msg: res.err_msg,
          url: res.url,
          skip_reason: res.skip_reason,
        });
      }

      this.setState({
        results: results,
        families: families,
        progress: false,
        err_msg: "",
        err_is_code: false,
        url: "",
        infoOpen: false,
        completedRepo: repo,
        completedRef: ref,
        completedRefType: refType,
      });
    } catch (e: unknown) {
      const emsg = (e as Error)?.message || String(e);
      if (emsg.includes("KeyError: 'tree'")) {
        this.setState({
          progress: false,
          err_msg: "Invalid repository or branch/tag. Please try again.",
          err_is_code: false,
        });
      } else {
        // Stored as plain text and rendered as React text content (never as
        // raw HTML) — exception messages can echo unsanitized URL input.
        this.setState({
          progress: false,
          err_msg: emsg,
          err_is_code: true,
        });
      }
    }
  }

  async handleCopyHtml() {
    if (!this.state.results) {
      this.setState({
        snackbarOpen: true,
        snackbarMsg: "No results to copy — please run the checks first",
        snackbarSeverity: "warning",
      });
      return;
    }

    let htmlOut: string;
    try {
      // The worker stores the most recent run, which is always the run the
      // displayed results came from; regenerating HTML from it is cheap.
      htmlOut = await this.client!.generateHtml(this.state.show || "all");
    } catch (e: unknown) {
      console.error("Error generating HTML:", e);
      const emsg = (e as Error)?.message || String(e);
      this.setState({
        snackbarOpen: true,
        snackbarMsg: "Error generating HTML: " + emsg,
        snackbarSeverity: "error",
      });
      return;
    }

    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(htmlOut);
        this.setState({
          snackbarOpen: true,
          snackbarMsg: "HTML output copied to clipboard",
          snackbarSeverity: "success",
        });
      } else {
        // Fallback: open in new window for manual copy
        const w = window.open("", "repo-review-html");
        if (w) {
          w.document.write(htmlOut);
          w.document.close();
        }
      }
    } catch (e: unknown) {
      console.error("Error copying HTML:", e);
      const emsg = (e as Error)?.message || String(e);
      this.setState({
        snackbarOpen: true,
        snackbarMsg: "Could not copy to clipboard: " + emsg,
        snackbarSeverity: "error",
      });
    }
  }

  async loadKnownChecks() {
    let data: KnownChecksData = {};
    try {
      data = await this.client!.knownChecks();
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
    this.client = new PyodideClient((p: number, m?: string) =>
      this.setState({
        pyodideProgress: p,
        pyodideLoading: p < 100,
        pyodideMessage: m || "",
      }),
    );
    this.readyPromise = this.client.init(
      this.props.deps,
      this.props.pyodideBaseUrl,
    );
    // Surface load failures in the error banner instead of failing silently.
    this.readyPromise.catch((e: unknown) => {
      const emsg = (e as Error)?.message || String(e);
      this.setState({
        pyodideLoading: false,
        progress: false,
        err_msg: `Failed to load Pyodide: ${emsg}`,
        err_is_code: true,
      });
    });
    if (!this.props.disableUrlSync) {
      const params = new URLSearchParams(window.location.search);
      if (params.get("repo")) {
        this.fetchRepoReferences(params.get("repo")!);
      }
      if (params.get("repo") && params.get("ref")) {
        this.handleCompute();
      }
    }
    // Always load the list of available checks, even if an auto-run from the
    // URL parameters is in flight (or fails). Errors are reported above.
    this.readyPromise.then(
      () => this.loadKnownChecks(),
      () => {},
    );
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

    const hasResults = this.state.results !== null;
    const displayResults =
      this.state.results ??
      (!this.state.progress ? this.state.knownChecks : null);
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
      const newResults: Record<string, CheckItem[]> = {};
      for (const fam of Object.keys(displayResults)) {
        const items = displayResults[fam];
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
      for (const k of Object.keys(displayFamilies)) {
        if (
          knownFamilies.has(k) ||
          (displayFamilies[k] && displayFamilies[k].description)
        ) {
          newFamilies[k] = displayFamilies[k];
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
            sx={{ alignItems: { xs: "stretch", sm: "stretch" }, m: 1, mb: 3 }}
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
                  sx={{ flexGrow: 2, minWidth: 170 }}
                  slotProps={{
                    input: {
                      ...params.slotProps.input,
                      endAdornment: (
                        <>
                          {this.state.loadingRefs ? (
                            <CircularProgress color="inherit" size={20} />
                          ) : null}
                          {params.slotProps.input.endAdornment}
                        </>
                      ),
                    },
                  }}
                />
              )}
            />
            <Box
              sx={{
                display: "flex",
                flexDirection: "row",
                gap: 2,
                alignItems: "center",
                flexGrow: 1,
                minWidth: { xs: 240, sm: 180 },
              }}
            >
              <Stack
                direction={{ xs: "row", sm: "column" }}
                spacing={1}
                sx={{ flexGrow: 1 }}
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
                      MenuProps={
                        this.props.disableUrlSync
                          ? { disablePortal: true }
                          : undefined
                      }
                      onChange={(e: SelectChangeEvent<string>) => {
                        const val = e.target.value as string;
                        this.setState({ show: val });
                        if (!this.props.disableUrlSync) {
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
                          if (
                            !params.get("packageDir") &&
                            this.state.packageDir
                          )
                            params.set("packageDir", this.state.packageDir);
                          window.history.replaceState(
                            null,
                            "",
                            `${window.location.pathname}?${params}`,
                          );
                        }
                      }}
                      size="small"
                    >
                      <MenuItem value="all">All</MenuItem>
                      <MenuItem value="errskip">Errors & Skips</MenuItem>
                      <MenuItem value="err">Errors only</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
              </Stack>
              <Button
                onClick={() => this.handleCompute()}
                variant="contained"
                size="large"
                aria-label="Run checks"
                disabled={
                  this.state.progress || !this.state.repo || !this.state.ref
                }
                sx={{ alignSelf: "stretch", minWidth: 64 }}
              >
                <PlayArrowIcon />
              </Button>
            </Box>
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
                expandIcon={<ExpandMoreIcon />}
                sx={{ bgcolor: "primary.main", color: "primary.contrastText" }}
              >
                <Typography sx={{ fontWeight: "medium" }}>About</Typography>
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
                {this.state.err_is_code ? (
                  <Box
                    component="pre"
                    sx={{ m: 0, whiteSpace: "pre-wrap", overflowX: "auto" }}
                  >
                    <code>{this.state.err_msg}</code>
                  </Box>
                ) : (
                  this.state.err_msg
                )}
              </Typography>
            )}
            {filteredResults && (
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
                      aria-label="Copy HTML results"
                      disabled={
                        this.state.progress || this.state.pyodideLoading
                      }
                    >
                      <ContentCopyIcon />
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
            severity={this.state.snackbarSeverity}
            sx={{ width: "100%" }}
          >
            {this.state.snackbarMsg}
          </Alert>
        </Snackbar>
      </MyThemeProvider>
    );
  }
}

export function mountApp(opts: Partial<AppProps> & { el?: HTMLElement } = {}) {
  injectFonts();
  const { el, ...appOpts } = opts;
  const target = el ?? document.getElementById("root");
  const root = ReactDOM.createRoot(target!);
  const props: AppProps = { deps: [], ...appOpts };
  root.render(<App {...props} />);
  return () => root.unmount();
}
