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
      results: [],
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

      this.setState({
        results: results,
        families: families,
        progress: false,
        err_msg: "",
        url: "",
        infoOpen: false,
      });

      results_list.destroy();
      families_dict.destroy();
    });
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
                <Typography variant="h6" sx={{ px: 2, pt: 1 }}>
                  {resultsHeading}
                </Typography>
                <Results results={displayResults} families={displayFamilies} />
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
