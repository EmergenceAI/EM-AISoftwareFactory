<!--
MAINTAINED: em-semi workflow authoring patterns
Last updated: 2026-09-01
Repository: EmergenceAI/em-semi
DO NOT EDIT via sync_knowledge.sh — this file is curated manually.
-->

# em-semi Workflow Coding Patterns

## Overview

em-semi workflows run on Prefect. Every workflow is a `@semi_flow`-decorated async function
backed by `@semi_task`-decorated async functions. **Never use bare `@flow` or `@task`.**
Discovery is automatic: drop a spec file in `workflow_specs/` and the registry picks it up.

---

## The 4-File Pattern

Every new workflow requires exactly these four files, created in this order:

```
common/common_semi/model/workflow_names.py   ← 1. Add enum entry
workflow/app/tasks/<name>.py                 ← 2. Write @semi_task functions
workflow/app/workflows_v2/<name>.py          ← 3. Write @semi_flow function
workflow/app/workflow_specs/<name>.py        ← 4. Create ENTRY (auto-discovered)
```

---

## 1. Enum Entry — `common/common_semi/model/workflow_names.py`

```python
class SemiconductorWorkflow(StrEnum):
    # existing entries ...
    MY_NEW_WORKFLOW = "MY_NEW_WORKFLOW"
```

- Use `UPPER_SNAKE_CASE`
- The string value must match exactly what is used in `@semi_flow(name=...)`
- Changes to `common/` affect ALL Python services — never introduce breaking changes

---

## 2. Tasks — `workflow/app/tasks/<name>.py`

```python
from app.flows.base import semi_task, get_flow_context

@semi_task(
    auto_clean=True,            # True = workspace dir deleted after task
    name="my_task_name",        # human-readable, shown in Prefect UI
    # timeout_seconds=600,      # optional
    # retries=1,                # optional
    # tags=["data", "analysis"],# optional
)
async def my_task(input_arg: str, threshold: float = 0.05) -> dict:
    context = get_flow_context()  # ALWAYS use this — never accept db/storage as params
    # context.db       → AppDatabase
    # context.storage  → Storage (MinIO)
    # context.workspace_dir → Path  (isolated temp dir for this task)
    # context.config.organization_id
    # context.config.user_id
    # context.config.extra_config
    log = get_logger(component="workflow.my_task_name")
    log.info("task_started", input_arg=input_arg)   # structured key=value, never f-strings
    ...
    return {"result": ...}
```

**`auto_clean` rules:**
- `auto_clean=True` — task produces no files consumed by downstream tasks (safe default)
- `auto_clean=False` — task writes artifacts that a downstream task must read from disk

**Parallel execution (Prefect pattern — do NOT use `asyncio.gather`):**
```python
from prefect.futures import wait
import asyncio

futures = [my_task.submit(item) for item in items]
results = await asyncio.to_thread(wait, futures)
values  = [f.result() for f in futures]
```

---

## 3. Flow — `workflow/app/workflows_v2/<name>.py`

```python
from pydantic import Field
from typing import Optional
from app.flows.base import semi_flow, get_flow_context
from app.factories.db import get_database
from app.factories.storage import get_storage_service
from app.factories.llm import get_llm_service
from app.settings import settings
from common_semi.model import WorkflowRunConfig
from common_semi.model.workflow_names import SemiconductorWorkflow
from app.tasks.my_task import my_task

@semi_flow(
    name=SemiconductorWorkflow.MY_NEW_WORKFLOW,   # must match the enum string
    version="1.0",
    db=get_database(settings),
    storage=get_storage_service(settings),
    auto_clean=True,
    # task_runner=ThreadPoolTaskRunner(max_workers=settings.my_workflow_max_workers),
)
async def my_new_workflow(
    product_id: str = Field(..., description="Product identifier",
                            json_schema_extra={"x-ui-widget": "product-picker"}),
    lot_start_date: Optional[str] = Field(default=None, description="ISO 8601 start date"),
    config: WorkflowRunConfig = Field(..., description="Standard workflow config"),
) -> None:
    """Docstring is shown as the Prefect deployment description. Keep it clear."""
    context = get_flow_context()

    # UI progress reporting
    await context.log_progress(10, "Loading data...")

    group_id = await context.create_ui_group("Data Loading")
    result = await my_task(product_id)
    await context.complete_ui_group(group_id)

    await context.log_progress(80, "Generating report...")

    # Register output artifacts for MinIO upload
    report_path = context.workspace_dir / "report.json"
    report_path.write_text(...)
    await context.add_artifact(report_path, name="report", artifact_type="report")

    await context.log_progress(100, "Complete")
```

**Key `FlowContext` attributes and methods:**
```python
context = get_flow_context()
context.workflow_run_id          # str UUID
context.workspace_dir            # pathlib.Path — isolated per run
context.db                       # AppDatabase
context.storage                  # Storage (MinIO)
context.config                   # WorkflowRunConfig
context.config.organization_id
context.config.user_id
context.config.extra_config      # dict of caller-supplied extras
context.report_id                # str, set after report is created in DB
await context.log_progress(pct: int, message: str)
await context.log_ui_message(message: str, level: str = "info")
await context.create_ui_group(title: str) -> str   # returns group_id
await context.complete_ui_group(group_id: str)
await context.add_artifact(path: Path, name: str = "", artifact_type: str = "file")
await context.add_sections_to_report(sections: list)
```

---

## 4. Spec / Registry Entry — `workflow/app/workflow_specs/<name>.py`

```python
from common_semi.model.product import (
    WorkflowCategoryEnum,
    WorkflowLifecycleStageEnum,
)
from common_semi.model.workflow_names import SemiconductorWorkflow
from app.workflow_registry import WorkflowRegistryEntry, WorkflowVersionMeta
from app.workflows_v2.my_new_workflow import my_new_workflow
# Optional for scheduled workflows:
# from prefect.schedules import CronSchedule

ENTRY = WorkflowRegistryEntry(
    flow=my_new_workflow,
    deployment_name=SemiconductorWorkflow.MY_NEW_WORKFLOW.value,
    category=WorkflowCategoryEnum.SEMI_WORKFLOW,
    version=WorkflowVersionMeta(
        version_label="1.0.0",
        name="My New Workflow",
        description="One-sentence description shown in the UI workflow list.",
        outputs_description="What artifacts the workflow produces (PDF report, segment JSON, etc.).",
        processing_summary="Brief summary of the analytical method used.",
        lifecycle_stage=WorkflowLifecycleStageEnum.ACTIVE,  # or BETA / DEPRECATED
        dag=WorkflowDag(
            nodes=[
                WorkflowDagNode(id="load", label="Load Data"),
                WorkflowDagNode(id="analyze", label="Analyze"),
                WorkflowDagNode(id="report", label="Generate Report"),
            ],
            edges=[
                WorkflowDagEdge(source="load", target="analyze"),
                WorkflowDagEdge(source="analyze", target="report"),
            ],
        ),
        knowledge_types=[],   # optional: list of KnowledgeTypeEnum values
    ),
    # schedule=CronSchedule(cron="0 6 * * 1", timezone="America/New_York"),  # optional
    # parameters={"lot_start_date": None},  # optional default params
    # tags=["yield", "excursion"],           # optional
)
```

**Registration is automatic** — `registry_discovery.py` scans `workflow_specs/` at startup
and collects every module-level `ENTRY` object. No manual registration step needed.

---

## Logging Convention

```python
from common_semi.utils.logging import get_logger

log = get_logger(component="workflow.my_module_name")

# CORRECT: structured key=value pairs, literal string message
log.info("analysis_complete", parameter_count=15, duration_ms=320)
log.warning("parameter_skipped", reason="insufficient_data", parameter="MON_RC_MON_V1")
log.error("task_failed", error=str(e), workflow_run_id=context.workflow_run_id)

# WRONG: f-strings in message
log.info(f"Analysis complete for {product_id}")  # ← never do this
```

---

## Factory Pattern — Dependency Instantiation

Always use factories, never direct construction:

```python
from app.factories.db import get_database
from app.factories.storage import get_storage_service
from app.factories.llm import get_llm_service, get_llm_service_light
from app.factories.secrets import get_secrets_service
from app.settings import settings

db      = get_database(settings)         # → AppDatabase
storage = get_storage_service(settings)  # → Storage
llm     = get_llm_service(settings)      # → LlmService (full)
llm_l   = get_llm_service_light(settings)# → LlmService (faster/cheaper)
```

Pass `db` and `storage` to `@semi_flow` — tasks access them only via `get_flow_context()`.

---

## Naming Conventions

| Entity | Convention | Example |
|---|---|---|
| Module files | `lowercase_with_underscores` | `yield_excursion_v2.py` |
| Classes | `PascalCase` | `FlowContext`, `WorkflowRegistryEntry` |
| Functions / variables | `snake_case` | `get_flow_context`, `workflow_run_id` |
| Constants | `UPPER_SNAKE_CASE` | `SemiconductorWorkflow.YIELD_EXCURSION_V2` |
| Spec file | Must match workflow module name | `yield_excursion_v2.py` → `workflow_specs/yield_excursion_v2.py` |
| Workflow name enum | `UPPER_SNAKE_CASE` string | `"YIELD_EXCURSION_V2"` |
| Branch for new workflow | `feat/workflow-<slug>` | `feat/workflow-analog-trim-v2` |

---

## Reference Implementation

The canonical reference for all data-analysis workflows is:

- **Flow:** `workflow/app/workflows_v2/yield_excursion_v2.py`
- **Spec:** `workflow/app/workflow_specs/yield_excursion_v2.py`
- **Tasks:** `workflow/app/tasks/excursion_*.py`

When in doubt, read these files first — they demonstrate every pattern above in production use.

---

## Common Mistakes to Avoid

| Mistake | Correct pattern |
|---|---|
| `@flow` or `@task` directly | `@semi_flow` / `@semi_task` |
| `asyncio.gather(task1(), task2())` | `task.submit()` + `asyncio.to_thread(wait, futures)` |
| Passing `db` or `storage` into a task | `context = get_flow_context()` inside the task |
| Adding `db` or `storage` to task function signature | Never — always via context |
| Log `f"message {var}"` | `log.info("event_name", var=value)` |
| Creating workflow enum string inline | Must add to `SemiconductorWorkflow` enum in `common/` |
| Forgetting `await context.add_artifact(path)` | All output files must be registered for MinIO upload |
