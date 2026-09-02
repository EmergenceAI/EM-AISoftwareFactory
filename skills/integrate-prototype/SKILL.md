---
name: integrate-prototype
description: Integrate an existing Python workflow prototype into em-semi — reads prototype .py files, derives a spec from the code, wraps analysis logic into @semi_flow/@semi_task, converts charts to Plotly em-semi house style, and creates a PR
---

# Integrate Prototype

> **⚠ FULLY AUTONOMOUS — NO CONFIRMATIONS EVER**
> This skill runs non-interactively via `claude -p`. Never ask "Shall I proceed?",
> "Ready to implement?", or any confirmation question. Execute every step without pausing.

Given a directory of prototype `.py` files, integrate them into em-semi as a conformant
Prefect workflow: read the code, derive a spec if none was provided, wrap the analysis
logic verbatim into `@semi_task` functions, convert charts to Plotly with em-semi house
style, wire up data loading to `context.db` / Iceberg, and create a PR.

## Usage

```bash
# Prototype only — spec is derived from code (most common)
/integrate-prototype --prototype-dir workflow/prototypes/wf2_yield_insights/

# Prototype + existing spec (spec takes precedence over derived spec)
/integrate-prototype \
  --prototype-dir workflow/prototypes/wf2_yield_insights/ \
  --spec-file templates/yieldprocessinsights.md

# With Jira key (links PR back to ticket)
/integrate-prototype \
  --prototype-dir workflow/prototypes/wf2_yield_insights/ \
  --jira-key SEMI-1234

# Full harness invocation
/integrate-prototype \
  --prototype-dir workflow/prototypes/wf2_yield_insights/ \
  --context-file .knowledge_context_semi.md \
  --provenance-file .harness-results/provenance-events.jsonl
```

### Parameters

- `--prototype-dir <path>` (required): directory containing prototype `.py` files
- `--workflow-name <NAME>` (optional): UPPER_SNAKE_CASE name override — use this to integrate an existing prototype under a new name (e.g. for testing or creating a variant). When provided, skips name derivation in Step 2 and uses this value directly for the enum entry, deployment name, branch slug, and package directory name.
- `--spec-file <path>` (optional): pre-written workflow spec `.md`; if absent the skill derives one
- `--jira-key <key>` (optional): Jira issue key for PR linking and status update
- `--context-file <path>` (optional): harness-injected knowledge context (patterns, output style)
- `--provenance-file <path>` (optional): JSONL file for live progress events
- `--branch <name>` (optional): existing branch to use instead of creating a new one

## Process Flow

```
Step 0   Load context
Step 1   Read and map prototype files
Step 2   Derive spec from code (skip if --spec-file provided)
Step 3   Create branch
Step 4   Create workflow/app/<name>/ core package (verbatim copy)
Step 5   Write @semi_task wrappers
Step 6   Write @semi_flow
Step 7   Create ENTRY spec file + enum entry
Step 8   Convert charts to Plotly em-semi house style
Step 9   Convert report sections to em-semi report builder format
Step 10  Verify (ruff + mypy)
Step 11  Create PR
Step 12  Update Jira (if --jira-key provided)
```

---

## Step 0 — Load Context

If `--context-file` is provided, read it immediately. It contains the em-semi coding
patterns (`@semi_flow`/`@semi_task` 4-file pattern) and output style guide (Plotly palette,
chart types, artifact pipeline). If not provided, read directly:
- `knowledge/repositories/semi/patterns.md`
- `knowledge/repositories/semi/output_style.md`

The prototype source files are also embedded in the context file (as `## Prototype Source Files`).
Read them all now — you will reference them throughout.

Emit provenance event: `{"event": "step_start", "step": "load_context"}`

---

## Step 1 — Read and Map Prototype Files

Read every `.py` file in `--prototype-dir`. Build a map of:

**Analysis functions** — functions that compute results (typically named `m_*`, `compute_*`,
`analyse_*`, `run_*`, or similar). For each, record:
- Name and signature
- What data it consumes (input parameters / dataframes)
- What it produces (return value / output dict keys)
- Whether it can run independently or depends on a prior function's output

**Data loading** — how raw data is ingested:
- Local file reads: `pd.read_csv`, `pd.read_parquet`, `open(...)`, `Path(...).read_text()`
- Storage clients: custom `make_storage()`, env-var-based backends
- Schema: what columns/tables are accessed

**Chart generation** — functions or code blocks that produce visualisations:
- Library: matplotlib, SVG string generation, plotly, seaborn
- What each chart shows (axes, series, title patterns)
- Color values already in use

**Report assembly** — how the HTML/PDF report is built:
- Section headings and order
- How charts are embedded
- What content is narrative vs tabular

**Configuration** — top-of-file constants that are tuneable parameters
(e.g. `HIGH_LOW_PCT = 0.10`, `EXCURSION_Z = 3.5`, `MIN_N_PER_SIDE = 30`)

Emit provenance event: `{"event": "step_complete", "step": "map_prototype", "function_count": N}`

---

## Step 2 — Determine Workflow Name and Derive Spec

**Workflow name resolution (in priority order):**
1. `--workflow-name` flag provided → use it exactly as-is (UPPER_SNAKE_CASE)
2. `--spec-file` provided → read `workflow_name` from frontmatter
3. Neither → derive from module docstring title or prototype dir name (convert to UPPER_SNAKE_CASE)

Derive `workflow_snake_case` from the resolved name: `YIELD_PROCESS_INSIGHTS_V2` → `yield_process_insights_v2`.
Derive `display_name`: replace underscores with spaces and title-case: `"Yield Process Insights V2"`.
Derive branch slug: lowercase, underscores → hyphens: `feat/workflow-yield-process-insights-v2`.

**If `--workflow-name` is provided, skip to spec derivation using that name — do NOT check whether a workflow with that name already exists in `workflow_names.py`. The caller explicitly chose this name; proceed with full integration.**

### Derive Spec from Code (skip if --spec-file provided)

If `--spec-file` was given, use it. Otherwise derive a `workflow_spec.md` by filling
in the template from what Step 1 found:

```markdown
---
workflow_name: <UPPER_SNAKE_CASE derived from prototype dir name or module docstring>
display_name: "<human name from module docstring title line>"
version: "1.0"
lifecycle: active
category: semi_workflow
---

## Description
<module docstring of the main file>

## Inputs
<derive from CLI argparse arguments or top-of-file config constants>

## Data Sources
<derive from data loading code — table names, required columns>

## Analysis Steps
<one step per m_* function group, in dependency order>

## Outputs
### Charts
<one entry per chart-generating code block>
### Report sections
<one entry per HTML section heading found in the report generator>

## Acceptance Criteria
<derive from any assert statements, ground-truth checks, or success criteria in the code>
```

Write the derived spec to `workflow/prototypes/<name>/_generated_spec.md` in the target repo.
This is auditable — a human can review it before the PR is merged.

**Key derivation rules:**
- `workflow_name`: convert prototype dir name or main module docstring title to `UPPER_SNAKE_CASE`
- Analysis steps: order by data dependency (a function that uses another's output comes after it)
- Inputs: top-of-file tuneable constants become optional `WorkflowRunConfig.extra_config` fields
- Charts: one spec entry per distinct chart-producing call

Emit provenance event: `{"event": "step_complete", "step": "derive_spec", "spec_path": "..."}`

---

## Step 3 — Create Branch

```bash
git fetch origin
git checkout main && git pull origin main
git checkout -b feat/workflow-<slug>
```

Where `<slug>` is the `workflow_name` lowercased with underscores replaced by hyphens.
If `--branch` was provided, use that branch instead.

Emit provenance event: `{"event": "step_complete", "step": "create_branch", "branch": "<name>"}`

---

## Step 4 — Create Core Package (verbatim copy)

Create `workflow/app/<workflow_snake_case>/` and copy the prototype analysis files into it,
**changing only the minimum necessary to make them importable**:

```
workflow/app/<workflow_snake_case>/
    __init__.py          ← empty, makes it a package
    core.py              ← main analysis file verbatim (or split if multiple)
    models.py            ← dataclasses / result types if in a separate file
```

**What NOT to change in core.py:**
- Analysis functions (`m_*`) — zero changes, the math is already correct
- Statistical methods (`cliffs_delta`, `bh`, `capability`, etc.) — verbatim
- Configuration constants — keep at top of file, they become tunable params
- Domain logic, scoring, threshold logic — untouched

**What to change (only):**
- Remove any `sys.path` manipulation that was needed to run standalone
- Remove `if __name__ == "__main__"` CLI blocks
- Remove `import data_source` — data loading moves to the task layer
- Any `from data_source import ...` → will be replaced in Step 5

After copying: run `ruff check workflow/app/<name>/core.py --fix` to fix import ordering.
Do not fix any substantive logic, only format.

Emit provenance event: `{"event": "step_complete", "step": "create_core_package"}`

---

## Step 5 — Write @semi_task Wrappers

Create `workflow/app/tasks/<workflow_snake_case>.py`.

One `@semi_task` per logical phase identified in Step 1. The task:
1. Calls `get_flow_context()` to get db/storage/workspace
2. **Swaps data loading to Iceberg** (see below — this is mandatory, not optional)
3. Calls the verbatim core analysis function(s)
4. Returns results as a dict

### The plumbing boundary — this is the most important rule

**Do NOT treat data loading functions as untouchable analysis.** The boundary is:

| Type | Rule | Examples in WF2 |
|---|---|---|
| **Analysis (untouchable)** | Statistical logic, guards, ranking, chart computation | `m_high_low`, `m_parametric_contrast`, `m_capability`, `m_drift`, `m_spatial` |
| **Plumbing (swap to Iceberg)** | Anything reading files, CSVs, parquet, or object storage | `load_wafer_sort`, `load_wat`, `load_mon`, `load_dataset`, `pd.read_csv`, `pd.read_parquet` |

The `m_*` analysis functions take a `Dataset`/`DataFrame` object — they do not care how it was built.
The `load_*` functions build that object from files. **Replace the file reads with Iceberg queries.**
The `Dataset` object itself (the dataclass/class) is fine to keep — just populate it from Iceberg instead of CSVs.

### Iceberg data loading — mandatory for all prototype integrations

**Invoke `/iceberg-data-adapter` as a sub-step before writing tasks.** It maps the
prototype's CSV column names to the canonical Iceberg schema and generates the query code.

If running without the sub-skill, follow this pattern manually:

```python
from app.data_views.factory import create_iceberg_data_view
from app.flows.base import semi_task, get_flow_context

@semi_task(auto_clean=False, name="<workflow>_load_data")
async def load_data(product_id: str, start_date: str | None, end_date: str | None) -> dict:
    context = get_flow_context()
    log = get_logger(component="workflow.<name>.load_data")

    # Build Iceberg data view (replaces all pd.read_csv / pd.read_parquet calls)
    data_view = create_iceberg_data_view(
        db=context.db,
        product_id=product_id,
        date_range=(start_date, end_date) if start_date else None,
        lot_ids=None,
    )

    # Pull wafer-sort data (replaces load_wafer_sort / PRR.csv + HBR.csv + SBR.csv)
    # Columns: lot_id, wafer_id, die_x, die_y, pass_flag, bin_number, bin_name, test_date, site_num
    prr_df = await asyncio.to_thread(
        data_view.get_wafer_sort_summary          # or get_die_results for die-level
    )

    # Pull parametric data (replaces load_mon / PTR.csv)
    # Columns: lot_id, wafer_id, die_x, die_y, param_name, value, site_num, lo_limit, hi_limit
    ptr_df = await asyncio.to_thread(
        data_view.get_parametric_results
    )

    # Pull WAT data (replaces load_wat / WAT.csv)
    # Columns: lot_id, wafer_id, parameter_name, value, site_num, lower_limit, upper_limit
    wat_df = await asyncio.to_thread(
        data_view.get_wafer_acceptance_results
    )

    # Build the Dataset object the core analysis expects — same class, Iceberg data
    from app.<workflow_snake_case>.core import Dataset
    ds = Dataset(prr=prr_df, ptr=ptr_df, wat=wat_df, name=product_id)

    # Now call core analysis verbatim
    from app.<workflow_snake_case>.core import m_ingestion
    R = {}
    m_ingestion(ds, R)

    # Pickle Dataset for downstream tasks (DataFrames don't serialise through Prefect)
    import pickle
    pkl_path = context.workspace_dir / "dataset.pkl"
    pkl_path.write_bytes(pickle.dumps(ds))
    log.info("data_loaded", lots=len(prr_df["lot_id"].unique()), wafers=len(prr_df))
    return {"ds_pkl": str(pkl_path), "R": R}
```

**Column name mapping — prototype CSV → Iceberg:**

| Prototype CSV file | Iceberg table | Key column differences |
|---|---|---|
| `PRR.csv` | `wafer_sort` | `PART_FLG` → `pass_flag`; `HARD_BIN` → `bin_number`; `X_COORD`/`Y_COORD` → `die_x`/`die_y` |
| `PTR.csv` (in-die monitors / LibPM) | `wafer_sort` parametric | `TEST_TXT` → `param_name`; `RESULT` → `value`; `LO_LIMIT`/`HI_LIMIT` preserved |
| `WAT.csv` / `PCM` | `wafer_acceptance` | `parameter_name`, `value`, `site_num`; `lower_limit`/`upper_limit` |
| `HBR.csv` / `SBR.csv` | aggregated from `wafer_sort` | bin counts computed from die-level `bin_number` |

Always read `common_semi/data/iceberg_schema.py` for the authoritative column list before writing queries.

### Other plumbing swap rules

| Prototype pattern | em-semi replacement |
|---|---|
| `open("output/results.json")` | `context.workspace_dir / "results.json"` |
| `os.makedirs("output/charts")` | `context.workspace_dir / "charts"` |
| `make_storage()` / custom storage client | `context.storage` |
| `print("step done")` | `log.info("step_done", key=value)` |
| Top-of-file config constants | `context.config.extra_config.get("HIGH_LOW_PCT", 0.10)` |

### Task template

```python
from app.flows.base import semi_task, get_flow_context
from app.<workflow_snake_case>.core import m_ingestion, m_excursion, m_high_low
from common_semi.utils.logging import get_logger

log = get_logger(component="workflow.<workflow_snake_case>")

@semi_task(auto_clean=False, name="<workflow>_load_and_clean")
async def load_and_clean(product_id: str, start_date: str, end_date: str) -> dict:
    context = get_flow_context()
    log.info("load_started", product_id=product_id)

    # ← Plumbing swap: query Iceberg instead of reading local CSV/parquet
    prr_df = await _query_wafer_sort(context.db, product_id, start_date, end_date)
    wat_df = await _query_wat(context.db, product_id, start_date, end_date)

    # ← Core logic verbatim — no changes
    from app.<workflow_snake_case>.core import Dataset, load_dataset
    ds = Dataset(prr=prr_df, wat=wat_df, name=product_id)
    R = {}
    m_ingestion(ds, R)
    return {"ds_pickle_path": str(_pickle_ds(ds, context.workspace_dir)), "R": R}

@semi_task(auto_clean=False, name="<workflow>_run_analysis")
async def run_analysis(load_result: dict) -> dict:
    context = get_flow_context()
    ds = _unpickle_ds(load_result["ds_pickle_path"])
    R = load_result["R"]

    m_excursion(ds, R)
    m_high_low(ds, R)
    m_parametric_contrast(ds, R)
    m_capability(ds, R)
    m_drift(ds, R)
    m_spatial(ds, R)
    return R
```

**Note on passing large DataFrames between tasks:** pickle the `Dataset` object to
`context.workspace_dir / "dataset.pkl"` and pass the path. Do not pass raw DataFrames
as task return values — they don't serialise cleanly through Prefect's result storage.

Emit provenance event: `{"event": "step_complete", "step": "write_tasks"}`

---

## Step 6 — Write @semi_flow

Create `workflow/app/workflows_v2/<workflow_snake_case>.py`.

```python
@semi_flow(
    name=SemiconductorWorkflow.<WORKFLOW_NAME>,
    version="<version from spec>",
    db=get_database(settings),
    storage=get_storage_service(settings),
    auto_clean=True,
)
async def <workflow_snake_case>(
    product_id: str = Field(..., json_schema_extra={"x-ui-widget": "product-picker"}),
    start_date: str = Field(..., description="Analysis window start (ISO 8601)"),
    end_date: str = Field(..., description="Analysis window end (ISO 8601)"),
    # Optional tuneable params from prototype config constants:
    high_low_pct: float = Field(default=0.10, description="Percentile split fraction"),
    excursion_exclusion: bool = Field(default=True, description="Remove test-artifact excursions"),
    config: WorkflowRunConfig = Field(...),
) -> None:
    """<display_name>. <Description from spec/docstring>."""
    context = get_flow_context()

    await context.log_progress(5,  "Loading and cleaning data...")
    load_result = await load_and_clean(product_id, start_date, end_date)

    await context.log_progress(35, "Running analysis...")
    results = await run_analysis(load_result)

    await context.log_progress(65, "Building charts...")
    chart_paths = await generate_charts(results)

    await context.log_progress(90, "Generating report...")
    await generate_report(results, chart_paths)

    await context.log_progress(100, "Complete")
```

Emit provenance event: `{"event": "step_complete", "step": "write_flow"}`

---

## Step 7 — Enum Entry + ENTRY Spec File

**Add to `common/common_semi/model/workflow_names.py`:**
```python
class SemiconductorWorkflow(StrEnum):
    <WORKFLOW_NAME> = "<WORKFLOW_NAME>"
```

**Create `workflow/app/workflow_specs/<workflow_snake_case>.py`:**
```python
ENTRY = WorkflowRegistryEntry(
    flow=<workflow_func>,
    deployment_name=SemiconductorWorkflow.<WORKFLOW_NAME>.value,
    category=WorkflowCategoryEnum.SEMI_WORKFLOW,
    version=WorkflowVersionMeta(
        version_label="1.0.0",
        name="<display_name>",
        description="<from spec/docstring>",
        outputs_description="<from spec outputs section>",
        processing_summary="<from spec analysis steps>",
        lifecycle_stage=WorkflowLifecycleStageEnum.ACTIVE,
        dag=WorkflowDag(nodes=[...], edges=[...]),
    ),
)
```

Emit provenance event: `{"event": "step_complete", "step": "write_entry"}`

---

## Step 8 — Convert Charts to Plotly em-semi House Style

For each chart-generating code block found in Step 1, create a Plotly equivalent.

**Read `knowledge/repositories/semi/output_style.md`** for the exact palette and trace
patterns before writing a single line of chart code.

### Conversion rules by source library

**SVG string generation (most common in prototypes):**
Read what the SVG draws — axes, series, colors, labels. Implement the equivalent
`go.Figure` with em-semi palette.

**matplotlib / seaborn:**
Each `ax.*` call maps to a `go.Figure.add_trace(...)`. Common mappings:
```python
ax.bar(x, y, color="red")      → go.Bar(x=x, y=y, marker_color="#d62728")
ax.plot(x, y, color="blue")    → go.Scatter(x=x, y=y, line={"color":"#1d4ed8"})
ax.scatter(x, y)               → go.Scatter(x=x, y=y, mode="markers")
ax.set_xlabel("label")         → fig.update_layout(xaxis_title="label")
ax.axhline(y=usl, color="r")  → fig.add_hline(y=usl, line_color="#d62728", line_dash="dash")
```

**Always apply:**
```python
fig.update_layout(
    template="plotly_white",
    title={"text": title, "x": 0.5, "xanchor": "center"},
    font={"color": "#1f2937"},
    width=1200, height=600,
)
```

**Always use these population colors:**
- Bad / low-yield: `#d62728`
- Good / high-yield: `#aec7e8`
- Heatmap colorscale: `"RdBu_r"`
- Pareto enrichment bar: `#dc2626`
- Cumulative % line: `#1d4ed8`

**Save each chart:**
```python
charts_dir = context.workspace_dir / "charts"
charts_dir.mkdir(exist_ok=True)
chart_path = charts_dir / f"{chart_id}.json"
with chart_path.open("w") as f:
    json.dump(fig.to_dict(), f, cls=NumpyEncoder)
await context.add_artifact(chart_path)
```

Place chart generation in a `@semi_task(auto_clean=True, name="generate_charts")` task.

Emit provenance event: `{"event": "step_complete", "step": "convert_charts", "chart_count": N}`

---

## Step 9 — Convert Report Sections

Map each section from the prototype's HTML/PDF report generator into an em-semi
report section dict. The section order follows the spec (or the HTML heading order).

```python
# In @semi_task(auto_clean=True, name="generate_report")
async def generate_report(results: dict, chart_paths: list[Path]) -> None:
    context = get_flow_context()
    sections = []

    # One block per report section
    sections.append({
        "id": "executive_summary",
        "title": "Executive Summary",
        "content": _executive_summary_md(results),   # markdown string
        "charts": [
            {
                "id": "differentiator_ranking",
                "title": "Ranked Parameters by Effect Size",
                "figure": {"plotly_json": _load_chart(charts_dir / "ranking.json")},
                "comments": [],
            }
        ],
        "attachments": [],
        "explainability_metadata": {},
    })
    # ... repeat for each section

    await context.add_sections_to_report(sections)
```

**Content conversion:** prototype HTML strings → markdown. Strip HTML tags.
Use `### ` for subsection headings, `**bold**`, `- bullet` lists.
Tables: use markdown table syntax.

Emit provenance event: `{"event": "step_complete", "step": "convert_report"}`

---

## Step 10 — Verify

```bash
# Lint and auto-fix new files only
ruff check \
  common/common_semi/model/workflow_names.py \
  workflow/app/<name>/ \
  workflow/app/tasks/<name>.py \
  workflow/app/workflows_v2/<name>.py \
  workflow/app/workflow_specs/<name>.py \
  --fix

# Type check new files
mypy \
  workflow/app/<name>/core.py \
  workflow/app/tasks/<name>.py \
  workflow/app/workflows_v2/<name>.py \
  workflow/app/workflow_specs/<name>.py \
  --ignore-missing-imports
```

**Verify integration checklist:**
- [ ] `@semi_flow` / `@semi_task` decorators used — no bare `@flow` / `@task`
- [ ] No `asyncio.gather` for Prefect tasks
- [ ] All log calls use `get_logger(component=...)` with structured key=value
- [ ] All chart files: `fig.to_dict()` JSON saved to `context.workspace_dir/charts/`
- [ ] `template="plotly_white"` on every `fig.update_layout()`
- [ ] `await context.add_artifact(path)` called for every chart JSON
- [ ] `await context.add_sections_to_report(sections)` called
- [ ] `workflow/app/<name>/core.py` analysis functions are **unchanged** from prototype
- [ ] Enum entry present in `workflow_names.py`
- [ ] `ENTRY` object present in `workflow_specs/<name>.py`
- [ ] `_generated_spec.md` written to `workflow/prototypes/<name>/` (if spec was derived)

Emit provenance event: `{"event": "step_complete", "step": "verify", "lint_passed": true}`

---

## Step 11 — Create PR

```bash
git add \
  common/common_semi/model/workflow_names.py \
  workflow/app/<name>/ \
  workflow/app/tasks/<name>.py \
  workflow/app/workflows_v2/<name>.py \
  workflow/app/workflow_specs/<name>.py \
  workflow/prototypes/<name>/_generated_spec.md   # if derived

git commit -m "feat(workflow): integrate <display_name> prototype

Wraps workflow/prototypes/<name>/ into the em-semi 4-file pattern.
Analysis logic in workflow/app/<name>/core.py is verbatim from the
prototype — zero changes to the math. Plumbing swapped to Iceberg/
FlowContext; charts converted to Plotly with em-semi house style."

git push -u origin feat/workflow-<slug>
```

Then invoke `/create-pr` with:
- Title: `feat(workflow): integrate <display_name> prototype`
- Body: prototype origin, what was changed vs preserved, chart list, derived spec path

Emit provenance event: `{"event": "step_complete", "step": "create_pr", "pr_url": "<url>"}`

---

## Step 12 — Update Jira (if --jira-key provided)

Invoke `/jira-update` with the PR URL and a summary of what was integrated.
Move ticket to "In Review".

Emit provenance event: `{"event": "run_complete", "outcome": "success", "pr_url": "<url>"}`

---

## Provenance Event Schema

Append each event as a JSON line to `--provenance-file` (if provided):
```json
{"event": "step_start",    "step": "<name>", "timestamp": "<iso>"}
{"event": "step_complete", "step": "<name>", "timestamp": "<iso>", ...extra}
{"event": "step_failed",   "step": "<name>", "timestamp": "<iso>", "error": "<msg>"}
{"event": "run_complete",  "outcome": "success|partial|failed", "pr_url": "<url>|null"}
```

---

## The Core Principle

**Never change analysis logic.** The prototype was written by a domain expert and may
already be validated against ground truth (e.g. `m_ground_truth` in WF2). Changing it
introduces regression risk. Change only:
1. How data gets in (plumbing swap)
2. How results get out (charts → Plotly, report → sections)
3. How the function is called (wrapped in `@semi_task`)

If you catch yourself editing an `m_*` function body for any reason other than removing
a `sys.path` hack or a `from data_source import` line — stop. That is out of scope.
