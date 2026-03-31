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
} from "@mui/material";
import Heading from "./components/Heading";
import Results from "./components/Results";
import MyThemeProvider from "./components/MyThemeProvider";
import { fetchRepoRefs } from "./utils/github";
import {
  prepare_pyodide,
  run_process,
  load_known_checks,
} from "./utils/pyodide";

const DEFAULT_MSG =
  "Enter a GitHub repo and branch/tag to review. Runs Python entirely in your browser using WebAssembly. Built with React, MaterialUI, and Pyodide.";

class App extends React.Component<any, any> {
  pyodide_promise: Promise<any> | null;
  refInputDebounce: any;

  constructor(props: any) {
    super(props);
    const inner_deps_str = props.deps.join("\n");
    const deps_str = `<pre><code>${inner_deps_str}</code></pre>`;
    this.state = {
      show: new URLSearchParams(window.location.search).get("show") || "all",
      results: [],
      pyFamilies: null,
      pyChecks: null,
      pyFamiliesRepo: "",
      pyFamiliesRef: "",
      repo: new URLSearchParams(window.location.search).get("repo") || "",
      ref: new URLSearchParams(window.location.search).get("ref") || "",
      refType:
        new URLSearchParams(window.location.search).get("refType") || "branch",
      refs: { branches: [], tags: [] },
      msg: `<p>${DEFAULT_MSG}</p><h4>Packages:</h4> ${deps_str}`,
      progress: false,
      loadingRefs: false,
      err_msg: "",
      skip_reason: "",
      url: "",
      knownChecks: null,
      knownFamilies: {},
      infoOpen: true,
      pyodideProgress: 0,
      pyodideLoading: true,
      pyodideMessage: "",
    };
    this.pyodide_promise = prepare_pyodide(
      props.deps,
      (p: number, m?: string) =>
        this.setState({
          pyodideProgress: p,
          pyodideLoading: p < 100,
          pyodideMessage: m || "",
        }),
    );
    this.refInputDebounce = null;
  }

  async fetchRepoReferences(repo: string) {
    if (!repo) return;

    this.setState({ loadingRefs: true });
    const refs = await fetchRepoRefs(repo);
    this.setState({ refs: refs, loadingRefs: false });
  }

  handleRepoChange(repo: string) {
    this.setState({ repo });

    clearTimeout(this.refInputDebounce);
    this.refInputDebounce = setTimeout(() => {
      this.fetchRepoReferences(repo);
    }, 500);
  }

  handleRefChange(ref: string, refType: string) {
    this.setState({ ref, refType });
  }

  handleCompute() {
    if (!this.state.repo || !this.state.ref) {
      this.setState({ results: [], msg: DEFAULT_MSG });
      window.history.replaceState(null, "", window.location.pathname);
      alert(
        `Please enter a repo (${this.state.repo}) and branch/tag (${this.state.ref})`,
      );
      return;
    }
    const local_params = new URLSearchParams({
      repo: this.state.repo,
      ref: this.state.ref,
      refType: this.state.refType,
      show: this.state.show,
    });
    window.history.replaceState(
      null,
      "",
      `${window.location.pathname}?${local_params}`,
    );
    this.setState({ results: [], progress: true, infoOpen: false });
    const state = this.state;
    this.pyodide_promise!.then((pyodide: any) => {
      var families_checks;
      try {
        families_checks = run_process(pyodide, state.repo, state.ref);
      } catch (e: any) {
        if (e.message && e.message.includes("KeyError: 'tree'")) {
          this.setState({
            progress: false,
            err_msg: "Invalid repository or branch/tag. Please try again.",
          });
          return;
        }
        this.setState({
          progress: false,
          err_msg: `<pre><code>${e.message}</code><pre>`,
        });
        return;
      }

      const families_dict = families_checks.get(0);
      const results_list = families_checks.get(1);

      const results: any = {};
      const families: any = {};
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
      try {
        if (this.state.pyFamilies && this.state.pyFamilies !== families_dict) {
          this.state.pyFamilies.destroy();
        }
        if (this.state.pyChecks && this.state.pyChecks !== results_list) {
          this.state.pyChecks.destroy();
        }
      } catch (e) {
        // ignore destroy errors
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
        pyFamiliesRepo: state.repo,
        pyFamiliesRef: state.ref,
      });
    });
  }

  async handleCopyHtml() {
    if (!this.state.repo || !this.state.ref) {
      alert(`Please enter a repo (${this.state.repo}) and branch/tag (${this.state.ref})`);
      return;
    }

    try {
      const pyodide = await this.pyodide_promise;

      let htmlOut: any;

      // Reuse previously stored PyProxy results if they correspond to the
      // same repo/ref to avoid rerunning the expensive `process(package)`.
      if (
        this.state.pyFamilies &&
        this.state.pyChecks &&
        this.state.pyFamiliesRepo === this.state.repo &&
        this.state.pyFamiliesRef === this.state.ref
      ) {
        pyodide.globals.set("families_for_html", this.state.pyFamilies);
        pyodide.globals.set("checks_for_html", this.state.pyChecks);
        htmlOut = await pyodide.runPythonAsync(`
from repo_review.html import to_html
to_html(families_for_html, checks_for_html)
        `);
      } else {
        // Fallback: run process(package) (expensive)
        pyodide.globals.set("repo_for_html", this.state.repo);
        pyodide.globals.set("ref_for_html", this.state.ref);
        htmlOut = await pyodide.runPythonAsync(`
from repo_review.processor import process
from repo_review.html import to_html
from repo_review.ghpath import GHPath
package = GHPath(repo=repo_for_html, branch=ref_for_html)
families, checks = process(package)
to_html(families, checks)
        `);
      }

      const htmlStr = htmlOut.toString ? htmlOut.toString() : htmlOut;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(htmlStr);
        alert("HTML output copied to clipboard");
      } else {
        // Fallback: open in new window for manual copy
        const w = window.open("", "repo-review-html");
        if (w) {
          w.document.write(htmlStr);
          w.document.close();
        }
      }
    } catch (e: any) {
      console.error("Error generating HTML:", e);
      alert("Error generating HTML: " + (e?.message || e));
    }
  }

  async loadKnownChecks() {
    const pyodide = await this.pyodide_promise;
    let data: any;
    try {
      data = load_known_checks(pyodide);
    } catch (e) {
      console.error("Error loading known checks:", e);
      return;
    }

    const knownResults: any = {};
    const knownFamilies: any = {};

    for (const key of Object.keys(data.families || {})) {
      knownResults[key] = [];
      knownFamilies[key] = {
        name: data.families[key].name,
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
    const params = new URLSearchParams(window.location.search);
    if (params.get("repo")) {
      this.fetchRepoReferences(params.get("repo")!);
    }
    if (params.get("repo") && params.get("ref")) {
      this.handleCompute();
    } else {
      this.pyodide_promise!.then(() => this.loadKnownChecks());
    }
  }

  render() {
    const priorityBranches = ["HEAD", "main", "master", "develop", "stable"];
    const branchMap = new Map(
      this.state.refs.branches.map((branch: any) => [branch.name, branch]),
    );

    let availableOptions: any[] = [];

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
      const prioritizedBranches = [
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

      const otherBranches: any[] = [];
      branchMap.forEach((branch: any) => {
        otherBranches.push({
          label: `${branch.name} (branch)`,
          value: branch.name,
          type: "branch",
        });
      });
      otherBranches.sort((a, b) => a.value.localeCompare(b.value));

      const tagOptions = this.state.refs.tags.map((tag: any) => ({
        label: `${tag.name} (tag)`,
        value: tag.name,
        type: "tag",
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
      ? `Results for ${this.state.repo}@${this.state.ref} (${this.state.refType})`
      : "Available checks";

    // Apply CLI-like --show filtering: all | err | errskip
    let filteredResults = displayResults;
    let filteredFamilies = displayFamilies;
    if (displayResults && this.state.show && this.state.show !== "all") {
      const newResults: any = {};
      for (const fam of Object.keys(displayResults)) {
        const items = displayResults[fam];
        // first keep items that are not passing (i.e., state !== true)
        let kept = items.filter((it: any) => it.state !== true);
        // if 'err', then keep only those that are not undefined (i.e., errors only)
        if (this.state.show === "err") {
          kept = kept.filter((it: any) => it.state !== undefined);
        }
        if (kept.length > 0) {
          newResults[fam] = kept;
        }
      }

      const knownFamilies = new Set(Object.keys(newResults));
      const newFamilies: any = {};
      for (const k of Object.keys(displayFamilies)) {
        if (knownFamilies.has(k) || (displayFamilies[k] && displayFamilies[k].description)) {
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
            direction="row"
            spacing={2}
            alignItems="flex-start"
            sx={{ m: 1, mb: 3 }}
          >
            <TextField
              id="repo-select"
              label="Org/Repo"
              helperText="e.g. scikit-hep/hist"
              variant="outlined"
              autoFocus={true}
              onKeyDown={(e: any) => {
                if (e.keyCode === 13)
                  document.getElementById("ref-select")!.focus();
              }}
              onInput={(e: any) => this.handleRepoChange(e.target.value)}
              defaultValue={new URLSearchParams(window.location.search).get(
                "repo",
              )}
              sx={{ flexGrow: 3 }}
            />
            <Autocomplete
              disablePortal
              id="ref-select"
              options={availableOptions}
              loading={this.state.loadingRefs}
              freeSolo={true}
              onKeyDown={(e: any) => {
                if (e.keyCode === 13) this.handleCompute();
              }}
              getOptionLabel={(option: any) =>
                typeof option === "string" ? option : option.label
              }
              renderOption={(props, option) => (
                <li {...props}>{option.label}</li>
              )}
              onInputChange={(e: any, value: any) => {
                if (typeof value === "string") {
                  this.handleRefChange(value, "branch");
                }
              }}
              onChange={(e: any, option: any) => {
                if (option) {
                  if (typeof option === "object") {
                    this.handleRefChange(option.value, option.type);
                  } else {
                    this.handleRefChange(option, "branch");
                  }
                }
              }}
              defaultValue={new URLSearchParams(window.location.search).get(
                "ref",
              )}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Branch/Tag"
                  variant="outlined"
                  helperText="e.g. HEAD, main, or v1.0.0"
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
            <FormControl sx={{ minWidth: 140 }}>
              <InputLabel id="show-select-label">Show</InputLabel>
              <Select
                labelId="show-select-label"
                id="show-select"
                value={this.state.show}
                label="Show"
                onChange={(e: any) => {
                  const val = e.target.value;
                  this.setState({ show: val });
                  // update query string to persist show selection
                  const params = new URLSearchParams(window.location.search);
                  if (val && val !== "all") {
                    params.set("show", val);
                  } else {
                    params.delete("show");
                  }
                  // preserve repo/ref/refType if present
                  if (!params.get("repo") && this.state.repo) params.set("repo", this.state.repo);
                  if (!params.get("ref") && this.state.ref) params.set("ref", this.state.ref);
                  if (!params.get("refType") && this.state.refType) params.set("refType", this.state.refType);
                  window.history.replaceState(null, "", `${window.location.pathname}?${params}`);
                }}
                size="small"
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="err">Errors only</MenuItem>
                <MenuItem value="errskip">Errors + Skips</MenuItem>
              </Select>
            </FormControl>

            <Button
              onClick={() => this.handleCompute()}
              variant="contained"
              size="large"
              disabled={
                this.state.progress || !this.state.repo || !this.state.ref
              }
            >
              <Icon>start</Icon>
            </Button>
          </Stack>
          <Paper elevation={3}>
            <Accordion
              expanded={this.state.infoOpen}
              onChange={(e: any, open: boolean) =>
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
                <Box sx={{ display: "flex", alignItems: "center", px: 2, pt: 1 }}>
                  <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    {resultsHeading}
                  </Typography>
                  {hasResults && (
                    <Button
                      onClick={() => this.handleCopyHtml()}
                      variant="outlined"
                      size="small"
                      disabled={this.state.progress || this.state.pyodideLoading}
                    >
                      <Icon>content_copy</Icon>
                    </Button>
                  )}
                </Box>
                <Results results={filteredResults} families={filteredFamilies} />
              </>
            )}
          </Paper>
        </Box>
      </MyThemeProvider>
    );
  }
}

export function mountApp(opts: any = {}) {
  const root = ReactDOM.createRoot(document.getElementById("root")!);
  root.render(<App {...opts} />);
}

export default App;
