---
name: implement-workflow
description: Generate a conformant em-semi workflow from a spec file — creates the 4-file pattern (enum, tasks, flow, spec/ENTRY), Plotly charts following house style, and a PR
---

# Implement Workflow

> **⚠ FULLY AUTONOMOUS — NO CONFIRMATIONS EVER**
> This skill runs non-interactively via `claude -p`. There is no human on the other end.
> **Never** ask "Shall I proceed?", "Ready to implement?", or any other confirmation question.
> Execute every step without pausing.

Generate a fully conformant em-semi Prefect workflow from a structured spec `.md` file.
Produces the 4-file pattern, conformant Plotly charts in the em-semi house style, and a PR.

## Usage

```bash
# From a spec file only (no Jira ticket)
/implement-workflow --spec-file my_workflow.md

# Spec file + Jira key (links PR back to ticket)
/implement-workflow --spec-file my_workflow.md --jira-key SEMI-1234

# With harness knowledge context injection
/implement-workflow --spec-file my_workflow.md --context-file .knowledge_context_semi.md

# Full harness invocation (all options)
/implement-workflow \
  --spec-file my_workflow.md \
  --jira-key SEMI-1234 \
  --context-file .knowledge_context_semi.md \
  --provenance-file .harness-results/provenance-events.jsonl
```

### Parameters

- `--spec-file <path>` (required): Path to a workflow spec `.md` file (see `templates/workflow_spec.md`)
- `--jira-key <key>` (optional): Jira issue key — links PR and posts comment when provided
- `--context-file <path>` (optional): Harness-injected knowledge context (architecture, patterns, output style)
- `--provenance-file <path>` (optional): JSONL file for live progress events (harness monitoring)
- `--branch <name>` (optional): Existing branch to use instead of creating a new one

## Process Flow

```
Step 0  Load context
Step 1  Parse spec file
Step 2  Find reference implementation
Step 3  Create branch
Step 4  Implement 4-file pattern
Step 5  Implement chart tasks
Step 6  Verify (lint + type check)
Step 7  Create PR
Step 8  Update Jira (if --jira-key provided)
```

---

## Step 0 — Load Context

If `--context-file` was provided, read it immediately. It contains:
- Repository architecture overview
- Coding patterns (including the `@semi_flow` / `@semi_task` 4-file pattern)
- Output style guide (Plotly palette, chart types, artifact pipeline)
- Foundations standards (air-gap, coverage, gitleaks)

If no context file, read these files directly:
- `knowledge/repositories/semi/patterns.md`
- `knowledge/repositories/semi/output_style.md`

Emit provenance event: `{"event": "step_start", "step": "load_context"}`

---

## Step 1 — Parse Spec File

Read `--spec-file`. Extract:

| Field | Where in spec | Used for |
|---|---|---|
| `workflow_name` | YAML frontmatter | enum value, deployment_name |
| `display_name` | YAML frontmatter | `WorkflowVersionMeta.name` |
| `version` | YAML frontmatter | `@semi_flow(version=...)` |
| `lifecycle` | YAML frontmatter | `WorkflowLifecycleStageEnum` |
| `category` | YAML frontmatter | `WorkflowCategoryEnum` |
| `jira_key` | YAML frontmatter | PR linking (overridden by `--jira-key` flag) |
| Inputs table | `## Inputs` section | `@semi_flow` function parameters with `Field(...)` |
| Data sources | `## Data Sources` section | task implementation details |
| Analysis steps | `## Analysis Steps` section | one `@semi_task` per step |
| Charts | `## Outputs / charts` YAML | chart task implementation |
| Report sections | `## Outputs / sections` YAML | `context.add_sections_to_report()` calls |
| Acceptance criteria | `## Acceptance Criteria` section | used to verify completeness |

Derive the branch slug from `workflow_name`:
```python
slug = workflow_name.lower().replace("_", "-")
branch = f"feat/workflow-{slug}"
```

Emit provenance event: `{"event": "step_complete", "step": "parse_spec", "workflow_name": "<name>"}`

---

## Step 2 — Find Reference Implementation

Run these searches to find the closest existing workflow:

```bash
# Find all workflow spec files
find workflow/app/workflow_specs -name "*.py" | head -20

# Read the yield excursion spec (canonical reference)
cat workflow/app/workflow_specs/yield_excursion_v2.py

# Read the yield excursion flow
cat workflow/app/workflows_v2/yield_excursion_v2.py

# Find existing tasks similar to what the spec needs
grep -r "semi_task" workflow/app/tasks/ -l
```

Read the reference flow and its tasks in full. You will model all generated code on these.
Note which existing `@semi_task` functions can be reused directly vs. which need new implementations.

Emit provenance event: `{"event": "step_complete", "step": "find_reference"}`

---

## Step 3 — Create Branch

```bash
git fetch origin
git checkout main && git pull origin main
git checkout -b feat/workflow-<slug>
```

If `--branch` was provided, use that branch instead:
```bash
git checkout <branch> 2>/dev/null || git checkout -b <branch>
```

Emit provenance event: `{"event": "step_complete", "step": "create_branch", "branch": "<branch>"}`

---

## Step 4 — Implement the 4-File Pattern

Implement the four files in this exact order. Do not create any file until the preceding one is complete.

### 4a — Enum entry: `common/common_semi/model/workflow_names.py`

Read the current file. Find the `SemiconductorWorkflow` class. Add the new entry in alphabetical order:

```python
MY_NEW_WORKFLOW = "MY_NEW_WORKFLOW"
```

**Validation:** grep the file to confirm the new entry is present before proceeding.

### 4b — Tasks: `workflow/app/tasks/<workflow_snake_case>.py`

Create one `@semi_task` per analysis step listed in the spec. Rules:

- Import `semi_task` and `get_flow_context` from `app.flows.base`
- Import `get_logger` from `common_semi.utils.logging`
- Each task is `async def`
- Each task calls `context = get_flow_context()` as its first line
- Use `auto_clean=True` unless the task writes files consumed by a downstream task
- Logging: `log.info("event_name", key=value)` — never f-strings in the message
- Never pass `db`, `storage`, or `context` as task parameters — always via `get_flow_context()`
- For parallel execution: `task.submit()` + `await asyncio.to_thread(wait, futures)` — never `asyncio.gather`

For chart-producing tasks:
- Create a `charts/` subdirectory under `context.workspace_dir`
- Build Plotly figures using `plotly.graph_objects` (`go`) with the palette from `output_style.md`
- Save via `json.dump(fig.to_dict(), f, cls=NumpyEncoder)` to `charts/<chart_name>.json`
- Call `await context.add_artifact(chart_path)` for each chart file

For the report generation task:
- Call `_load_charts_from_output_dir` pattern from `workflow/app/tasks/report_generation.py` as reference
- Assemble sections list with `{"id": ..., "title": ..., "content": ..., "charts": [...]}`
- Call `await context.add_sections_to_report(sections)`

### 4c — Flow: `workflow/app/workflows_v2/<workflow_snake_case>.py`

```python
@semi_flow(
    name=SemiconductorWorkflow.<WORKFLOW_NAME>,
    version="<version from spec>",
    db=get_database(settings),
    storage=get_storage_service(settings),
    auto_clean=True,
)
async def <workflow_snake_case>(
    # One parameter per row in the spec Inputs table
    product_id: str = Field(..., json_schema_extra={"x-ui-widget": "product-picker"}),
    ...
    config: WorkflowRunConfig = Field(...),
) -> None:
    """<display_name>. <Description from spec>."""
    context = get_flow_context()
    await context.log_progress(0, "Starting...")
    # Call tasks in order, use submit() + asyncio.to_thread(wait, futures) for parallel groups
    ...
    await context.log_progress(100, "Complete")
```

### 4d — Spec / ENTRY: `workflow/app/workflow_specs/<workflow_snake_case>.py`

```python
from common_semi.model.product import WorkflowCategoryEnum, WorkflowLifecycleStageEnum
from common_semi.model.workflow_names import SemiconductorWorkflow
from app.workflow_registry import WorkflowRegistryEntry, WorkflowVersionMeta
from app.workflows_v2.<workflow_snake_case> import <workflow_func>

ENTRY = WorkflowRegistryEntry(
    flow=<workflow_func>,
    deployment_name=SemiconductorWorkflow.<WORKFLOW_NAME>.value,
    category=WorkflowCategoryEnum.SEMI_WORKFLOW,
    version=WorkflowVersionMeta(
        version_label="<version>.0",
        name="<display_name>",
        description="<description from spec>",
        outputs_description="<outputs section summary>",
        processing_summary="<processing_summary from analysis steps>",
        lifecycle_stage=WorkflowLifecycleStageEnum.<ACTIVE|BETA>,
        dag=WorkflowDag(nodes=[...], edges=[...]),
    ),
)
```

Emit provenance event: `{"event": "step_complete", "step": "implement_4_files"}`

---

## Step 5 — Implement Chart Tasks (em-semi house style)

For each chart in the spec's `## Outputs / charts` section, generate the Plotly figure
using the exact palette and trace patterns from `output_style.md`:

| Chart type | Plotly pattern | Key colors |
|---|---|---|
| `cdf` | `go.Scatter` traces, one per population | bad=`#d62728`, good=`#aec7e8`; USL/LSL via `fig.add_hline(line_color="#d62728", line_dash="dash")` |
| `box_plot` | `go.Box(boxmean="sd")` per lot | excursion=`#d62728`, normal=`#aec7e8` |
| `bar_pareto` | `go.Bar(marker_color="#dc2626")` + `go.Scatter(line={"color":"#1d4ed8"})` dual Y | — |
| `wafer_heatmap` | `go.Heatmap(colorscale="RdBu_r")` in `make_subplots` | shared `coloraxis` |
| `scatter` | `go.Scatter(mode="markers", marker={"color":"#aec7e8","opacity":0.6})` + OLS `go.Scatter(line={"color":"red"})` | — |
| `stacked_bar_yield` | `go.Bar` stacked per bin + `go.Scatter(line={"color":"blue","width":4})` dual Y | BIN_COLORS palette |

Always set:
```python
fig.update_layout(
    template="plotly_white",
    title={"text": title, "x": 0.5, "xanchor": "center"},
    font={"color": "#1f2937"},
    width=1200,
    height=600,
)
```

Emit provenance event: `{"event": "step_complete", "step": "implement_charts"}`

---

## Step 6 — Verify

Run linter and type checker on **only the new files**:

```bash
# Lint new files
ruff check \
  common/common_semi/model/workflow_names.py \
  workflow/app/tasks/<name>.py \
  workflow/app/workflows_v2/<name>.py \
  workflow/app/workflow_specs/<name>.py

# Auto-fix safe issues
ruff check --fix \
  workflow/app/tasks/<name>.py \
  workflow/app/workflows_v2/<name>.py \
  workflow/app/workflow_specs/<name>.py

# Type check new files
mypy \
  workflow/app/tasks/<name>.py \
  workflow/app/workflows_v2/<name>.py \
  workflow/app/workflow_specs/<name>.py \
  --ignore-missing-imports
```

Fix all errors before proceeding. If `ruff` or `mypy` report errors, fix them and re-run.
Do not proceed to PR creation until both pass cleanly.

**Also verify the spec acceptance criteria manually:**
- [ ] `@semi_flow` and `@semi_task` decorators used — no bare `@flow` / `@task`
- [ ] No `asyncio.gather` for Prefect tasks
- [ ] All log calls use structured key=value format
- [ ] All chart files saved as `fig.to_dict()` JSON
- [ ] `await context.add_artifact(path)` called for every chart JSON
- [ ] `await context.add_sections_to_report(sections)` called in the report task
- [ ] Enum entry present in `workflow_names.py`
- [ ] `ENTRY` object present in `workflow_specs/<name>.py`

Emit provenance event: `{"event": "step_complete", "step": "verify", "lint_passed": true, "mypy_passed": true}`

---

## Step 7 — Create PR

```bash
git add \
  common/common_semi/model/workflow_names.py \
  workflow/app/tasks/<name>.py \
  workflow/app/workflows_v2/<name>.py \
  workflow/app/workflow_specs/<name>.py

git commit -m "feat(workflow): add <display_name> workflow

Implements <workflow_name> following the 4-file em-semi pattern:
enum entry, @semi_task functions, @semi_flow, and WorkflowRegistryEntry ENTRY.

Charts use Plotly with em-semi house style (plotly_white template,
#d62728/#aec7e8 population palette, RdBu_r heatmap colorscale)."

git push -u origin <branch>
```

Then invoke `/create-pr` with:
- Title: `feat(workflow): add <display_name>`
- Body includes: spec summary, analysis steps, chart list, acceptance criteria checklist

If `--jira-key` was provided, include the Jira key in the PR description and branch name.

Emit provenance event: `{"event": "step_complete", "step": "create_pr", "pr_url": "<url>"}`

---

## Step 8 — Update Jira (if --jira-key provided)

Invoke `/jira-update` with:
- Issue key from `--jira-key`
- PR URL
- Summary of what was implemented
- Status transition: move to "In Review"

Emit provenance event: `{"event": "run_complete", "outcome": "success", "pr_url": "<url>"}`

---

## Provenance Event Schema

Append each event as a JSON line to `--provenance-file` (if provided):

```json
{"event": "step_start",    "step": "<name>", "timestamp": "<iso>"}
{"event": "step_complete", "step": "<name>", "timestamp": "<iso>", ...extra}
{"event": "step_failed",   "step": "<name>", "timestamp": "<iso>", "error": "<msg>"}
{"event": "run_complete",  "outcome": "success|partial|failed", "pr_url": "<url>|null", "timestamp": "<iso>"}
```

---

## Error Handling

| Situation | Action |
|---|---|
| Spec file missing required section | Print clear error listing missing sections; exit without creating files |
| Enum value already exists in `workflow_names.py` | Check if it's the same workflow (idempotent re-run) or a conflict; abort if conflict |
| `ruff` errors after auto-fix | Fix manually, re-run ruff, do not proceed until clean |
| `mypy` errors on imports | Add `# type: ignore[import]` only for third-party stubs that are genuinely missing |
| PR creation fails | Save branch and commit; report the branch name so the user can create the PR manually |

## Common Mistakes to Avoid

- Using `asyncio.gather` instead of `task.submit()` + `asyncio.to_thread(wait, futures)`
- Passing `db` or `storage` as task function parameters
- Using `@flow` or `@task` instead of `@semi_flow` / `@semi_task`
- Logging f-strings: `log.info(f"done {x}")` → must be `log.info("done", x=x)`
- Forgetting `await context.add_artifact(chart_path)` — charts not uploaded to MinIO
- Not calling `await context.add_sections_to_report(sections)` — report has no content
- Skipping `template="plotly_white"` on any chart layout
- Using wrong population colors — bad/excursion must be `#d62728`, good must be `#aec7e8`
