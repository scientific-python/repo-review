const DEFAULT_MSG =
  "Enter a GitHub repo and branch/tag to review. Runs Python entirely in your browser using WebAssembly. Built with React, MaterialUI, and Pyodide.";

const urlParams = new URLSearchParams(window.location.search);
const baseurl = window.location.pathname;

function Heading(props) {
  return (
    <MaterialUI.Box sx={{ flexGrow: 1, mb: 2 }}>
      <MaterialUI.AppBar position="static">
        <MaterialUI.Toolbar>
          <MaterialUI.Typography
            variant="h6"
            component="div"
            sx={{ flexGrow: 1 }}
          >
            Repo-Review
          </MaterialUI.Typography>
          <MaterialUI.Button
            href="https://github.com/scientific-python/repo-review"
            color="inherit"
          >
            Source
          </MaterialUI.Button>
        </MaterialUI.Toolbar>
      </MaterialUI.AppBar>
    </MaterialUI.Box>
  );
}

function IfUrlLink({ name, url, color }) {
  if (url) {
    return (
      <MaterialUI.Typography
        sx={{ display: "inline" }}
        variant="body2"
        color={color}
        component="a"
        href={url}
        target="_blank"
      >
        {name}
      </MaterialUI.Typography>
    );
  }
  return (
    <MaterialUI.Typography
      sx={{ display: "inline" }}
      component="span"
      variant="body2"
      color={color}
    >
      {name}
    </MaterialUI.Typography>
  );
}

function Results(props) {
  const output = [];
  for (const key in props.results) {
    const inner_results = props.results[key];
    const results_components = inner_results.map((result) => {
      const text_color =
        result.state === false
          ? "error.main"
          : result.state === true
            ? "text.primary"
            : "info.main";
      const details =
        result.state === false ? (
          <span dangerouslySetInnerHTML={{ __html: result.err_msg }} />
        ) : null;
      const color =
        result.state === false
          ? "error"
          : result.state === true
            ? "success"
            : "info";
      const icon = (
        <MaterialUI.Icon color={color}>
          {result.state === false
            ? "report"
            : result.state === true
              ? "check_box"
              : "info"}
        </MaterialUI.Icon>
      );

      const skipped = (
        <MaterialUI.Typography
          sx={{ display: "inline" }}
          component="span"
          variant="body2"
          color="text.disabled"
        >
          {` [skipped] ${result.skip_reason}`}
        </MaterialUI.Typography>
      );
      const msg = (
        <React.Fragment>
          <IfUrlLink name={result.name} url={result.url} color={text_color} />
          <IfUrlLink name={": "} url={""} color={text_color} />
          <React.Fragment>
            <MaterialUI.Typography
              sx={{ display: "inline" }}
              component="span"
              color={text_color}
            >
              {result.description}
            </MaterialUI.Typography>
          </React.Fragment>
          {result.state === undefined && skipped}
        </React.Fragment>
      );
      return (
        <MaterialUI.ListItem disablePadding key={result.name}>
          <MaterialUI.ListItemIcon>{icon}</MaterialUI.ListItemIcon>
          <MaterialUI.ListItemText
            primary={msg}
            secondary={details}
            href={result.url}
          />
        </MaterialUI.ListItem>
      );
    });

    output.push(
      <li key={`section-${key}`}>
        <ul>
          <MaterialUI.ListSubheader>
            {props.families[key].name}
          </MaterialUI.ListSubheader>
          {props.families[key].description && (
            <MaterialUI.ListItem>
              <span
                dangerouslySetInnerHTML={{
                  __html: props.families[key].description,
                }}
              />
            </MaterialUI.ListItem>
          )}
          {results_components}
        </ul>
      </li>,
    );
  }

  return (
    <MaterialUI.Box sx={{ bgcolor: "background.paper" }}>
      <MaterialUI.List subheader={<li />} overflow="auto">
        {output}
      </MaterialUI.List>
    </MaterialUI.Box>
  );
}

async function fetchRepoRefs(repo) {
  if (!repo) return { branches: [], tags: [] };
  try {
    // Fetch both branches and tags from GitHub API
    const [branchesResponse, tagsResponse] = await Promise.all([
      fetch(`https://api.github.com/repos/${repo}/branches`),
      fetch(`https://api.github.com/repos/${repo}/tags`),
    ]);

    if (!branchesResponse.ok || !tagsResponse.ok) {
      console.error("Error fetching repo data");
      return { branches: [], tags: [] };
    }

    const branches = await branchesResponse.json();
    const tags = await tagsResponse.json();

    return {
      branches: branches.map((branch) => ({
        name: branch.name,
        type: "branch",
      })),
      tags: tags.map((tag) => ({
        name: tag.name,
        type: "tag",
      })),
    };
  } catch (error) {
    console.error("Error fetching repo references:", error);
    return { branches: [], tags: [] };
  }
}

async function prepare_pyodide(deps) {
  const deps_str = deps.map((i) => `"${i}"`).join(", ");
  const pyodide = await loadPyodide();

  await pyodide.loadPackage("micropip");
  await pyodide.runPythonAsync(`
        import micropip
        await micropip.install([${deps_str}])
    `);
  return pyodide;
}

function MyThemeProvider(props) {
  const prefersDarkMode = MaterialUI.useMediaQuery(
    "(prefers-color-scheme: dark)",
  );

  const theme = React.useMemo(
    () =>
      MaterialUI.createTheme({
        palette: {
          mode: prefersDarkMode ? "dark" : "light",
        },
      }),
    [prefersDarkMode],
  );

  return (
    <MaterialUI.ThemeProvider theme={theme}>
      {props.children}
    </MaterialUI.ThemeProvider>
  );
}

class App extends React.Component {
  constructor(props) {
    super(props);
    const inner_deps_str = props.deps.join("\n");
    const deps_str = `<pre><code>${inner_deps_str}</code></pre>`;
    this.state = {
      results: [],
      repo: urlParams.get("repo") || "",
      ref: urlParams.get("ref") || "",
      refType: urlParams.get("refType") || "branch",
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
    };
    this.pyodide_promise = prepare_pyodide(props.deps);
    this.refInputDebounce = null;
  }

  async fetchRepoReferences(repo) {
    if (!repo) return;

    this.setState({ loadingRefs: true });
    const refs = await fetchRepoRefs(repo);
    this.setState({
      refs: refs,
      loadingRefs: false,
    });
  }

  handleRepoChange(repo) {
    this.setState({ repo });

    // debounce the API call to avoid too many requests
    clearTimeout(this.refInputDebounce);
    this.refInputDebounce = setTimeout(() => {
      this.fetchRepoReferences(repo);
    }, 500);
  }

  handleRefChange(ref, refType) {
    this.setState({ ref, refType });
  }

  handleCompute() {
    if (!this.state.repo || !this.state.ref) {
      this.setState({ results: [], msg: DEFAULT_MSG });
      window.history.replaceState(null, "", baseurl);
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
    window.history.replaceState(null, "", `${baseurl}?${local_params}`);
    this.setState({
      results: [],
      progress: true,
      infoOpen: false,
    });
    const state = this.state;
    this.pyodide_promise.then((pyodide) => {
      var families_checks;
      try {
        families_checks = pyodide.runPython(`
          from repo_review.processor import process, md_as_html
          from repo_review.ghpath import GHPath
          from dataclasses import replace

          package = GHPath(repo="${state.repo}", branch="${state.ref}")
          families, checks = process(package)

          for v in families.values():
              if v.get("description"):
                  v["description"] = md_as_html(v["description"])
          checks = [res.md_as_html() for res in checks]

          (families, checks)
          `);
      } catch (e) {
        if (e.message.includes("KeyError: 'tree'")) {
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

      const results = {};
      const families = {};
      for (const val of families_dict) {
        const descr = families_dict.get(val).get("description");
        results[val] = [];
        families[val] = {
          name: families_dict.get(val).get("name").toString(),
          description: descr && descr.toString(),
        };
      }
      console.log(families);
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
    let data;
    try {
      data = JSON.parse(
        pyodide.runPython(`
import json
from repo_review.processor import collect_all
from repo_review.checks import get_check_url

collected = collect_all()
families_out = {
    k: {"name": v.get("name", k)}
    for k, v in collected.families.items()
}
results_out = [
    {
        "name": name,
        "family": check.family,
        "description": (check.__doc__ or "").format(self=check, name=name).strip(),
        "url": get_check_url(name, check),
    }
    for name, check in collected.checks.items()
]
json.dumps({"families": families_out, "results": results_out})
        `),
      );
    } catch (e) {
      console.error("Error loading known checks:", e);
      return;
    }

    const knownResults = {};
    const knownFamilies = {};

    for (const [key, fam] of Object.entries(data.families)) {
      knownResults[key] = [];
      knownFamilies[key] = {
        name: fam.name,
      };
    }

    for (const check of data.results) {
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

    this.setState({
      knownChecks: knownResults,
      knownFamilies: knownFamilies,
    });
  }

  componentDidMount() {
    if (urlParams.get("repo")) {
      this.fetchRepoReferences(urlParams.get("repo"));
    }
    if (urlParams.get("repo") && urlParams.get("ref")) {
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

    let availableOptions = [];

    // If no repo is entered or API hasn't returned any branches/tags yet,
    // show all five priority branches.
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
          // Remove from map so it doesn't get added twice.
          branchMap.delete(branchName);
        }
      });

      const otherBranches = [];
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
        <MaterialUI.CssBaseline />
        <MaterialUI.Box>
          {this.props.header && <Heading />}
          <MaterialUI.Stack
            direction="row"
            spacing={2}
            alignItems="top"
            sx={{ m: 1, mb: 3 }}
          >
            <MaterialUI.TextField
              id="repo-select"
              label="Org/Repo"
              helperText="e.g. scikit-hep/hist"
              variant="outlined"
              autoFocus={true}
              onKeyDown={(e) => {
                if (e.keyCode === 13)
                  document.getElementById("ref-select").focus();
              }}
              onInput={(e) => this.handleRepoChange(e.target.value)}
              defaultValue={urlParams.get("repo")}
              sx={{ flexGrow: 3 }}
            />
            <MaterialUI.Autocomplete
              disablePortal
              id="ref-select"
              options={availableOptions}
              loading={this.state.loadingRefs}
              freeSolo={true}
              onKeyDown={(e) => {
                if (e.keyCode === 13) this.handleCompute();
              }}
              getOptionLabel={(option) =>
                typeof option === "string" ? option : option.label
              }
              renderOption={(props, option) => (
                <li {...props}>{option.label}</li>
              )}
              onInputChange={(e, value) => {
                // If the user enters free text, treat it as a branch
                if (typeof value === "string") {
                  this.handleRefChange(value, "branch");
                }
              }}
              onChange={(e, option) => {
                if (option) {
                  if (typeof option === "object") {
                    this.handleRefChange(option.value, option.type);
                  } else {
                    this.handleRefChange(option, "branch");
                  }
                }
              }}
              defaultValue={urlParams.get("ref")}
              renderInput={(params) => (
                <MaterialUI.TextField
                  {...params}
                  label="Branch/Tag"
                  variant="outlined"
                  helperText="e.g. HEAD, main, or v1.0.0"
                  sx={{ flexGrow: 2, minWidth: 200 }}
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <React.Fragment>
                        {this.state.loadingRefs ? (
                          <MaterialUI.CircularProgress
                            color="inherit"
                            size={20}
                          />
                        ) : null}
                        {params.InputProps.endAdornment}
                      </React.Fragment>
                    ),
                  }}
                />
              )}
            />

            <MaterialUI.Button
              onClick={() => this.handleCompute()}
              variant="contained"
              size="large"
              disabled={
                this.state.progress || !this.state.repo || !this.state.ref
              }
            >
              <MaterialUI.Icon>start</MaterialUI.Icon>
            </MaterialUI.Button>
          </MaterialUI.Stack>
          <MaterialUI.Paper elevation={3}>
            <MaterialUI.Accordion
              expanded={this.state.infoOpen}
              onChange={(e, open) => this.setState({ infoOpen: open })}
              elevation={0}
              disableGutters
              square
              sx={{ borderBottom: 1, borderColor: "divider" }}
            >
              <MaterialUI.AccordionSummary
                expandIcon={<MaterialUI.Icon>expand_more</MaterialUI.Icon>}
                sx={{ bgcolor: "primary.main", color: "primary.contrastText" }}
              >
                <MaterialUI.Typography fontWeight="medium">
                  About
                </MaterialUI.Typography>
              </MaterialUI.AccordionSummary>
              <MaterialUI.AccordionDetails sx={{ bgcolor: "primary.50" }}>
                <MaterialUI.Typography variant="body1" component="div">
                  <span dangerouslySetInnerHTML={{ __html: this.state.msg }} />
                </MaterialUI.Typography>
              </MaterialUI.AccordionDetails>
            </MaterialUI.Accordion>
            {this.state.progress && <MaterialUI.LinearProgress />}
            {this.state.err_msg && (
              <MaterialUI.Typography
                variant="body1"
                component="div"
                color="error"
                sx={{ p: 2 }}
              >
                <span
                  dangerouslySetInnerHTML={{ __html: this.state.err_msg }}
                />
              </MaterialUI.Typography>
            )}
            {displayResults && (
              <React.Fragment>
                <MaterialUI.Typography variant="h6" sx={{ px: 2, pt: 1 }}>
                  {resultsHeading}
                </MaterialUI.Typography>
                <Results results={displayResults} families={displayFamilies} />
              </React.Fragment>
            )}
          </MaterialUI.Paper>
        </MaterialUI.Box>
      </MyThemeProvider>
    );
  }
}
