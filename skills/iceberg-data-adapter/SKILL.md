---
name: iceberg-data-adapter
description: Convert prototype CSV/parquet data loading to em-semi Iceberg queries — maps prototype column names to the canonical Iceberg schema and generates @semi_task data loading code using DuckDBIcebergDataView
---

# Iceberg Data Adapter

Given a prototype workflow that reads CSV or parquet files, generate the equivalent
em-semi data loading code using `DuckDBIcebergDataView` and the canonical Iceberg schema.

This skill is called as a sub-step of `/integrate-prototype` (Step 5), or standalone
when you need to add Iceberg data loading to an existing workflow.

## Usage

```bash
# As a sub-step during prototype integration (called by integrate-prototype)
/iceberg-data-adapter \
  --prototype-file workflow/prototypes/wf2_yield_insights/wf2_core.py \
  --output-task workflow/app/tasks/yield_process_insights_v2_load.py \
  --workflow-name YIELD_PROCESS_INSIGHTS_V2

# Standalone — add Iceberg loading to an existing workflow
/iceberg-data-adapter \
  --prototype-file workflow/prototypes/my_prototype/core.py \
  --output-task workflow/app/tasks/my_workflow_load.py
```

### Parameters

- `--prototype-file <path>` (required): the prototype `.py` file containing data loading code
- `--output-task <path>` (required): where to write the generated `@semi_task` file
- `--workflow-name <NAME>` (optional): workflow name for logging context
- `--dataset-class <name>` (optional): name of the Dataset class in the prototype (default: `Dataset`)

---

## Step 1 — Read the Iceberg Schema

Before writing a single line of code, read the canonical column definitions:

```bash
cat common/common_semi/data/iceberg_schema.py
```

This is the authoritative source for all table names and column names.
Never guess column names — always verify against this file.

Key tables and their Iceberg names:

| Data | Table name | Class |
|---|---|---|
| Wafer Sort / CP (die-level) | `wafer_sort` | `WaferSort` |
| Wafer Sort wide (pivoted parametrics) | `wafer_sort_wide` | `WaferSortWide` |
| Wafer Acceptance Test / PCM | `wafer_acceptance` | `WaferAcceptance` |
| Final Test | `final_test` | `FinalTest` |

Also read:
- `workflow/app/data_views/duckdb_iceberg_data_view.py` — the DuckDB query API
- `workflow/app/data_views/factory.py` — `create_iceberg_data_view()` factory
- `workflow/app/workflows_v2/yield_excursion_v2.py` — reference implementation

---

## Step 2 — Map Prototype CSV Files to Iceberg Tables

Read the prototype file identified by `--prototype-file`. Find every data loading call:
- `pd.read_csv(...)`, `pd.read_parquet(...)`
- Custom loaders: `load_wafer_sort(...)`, `load_wat(...)`, `load_mon(...)`
- Any function that opens files or reads from object storage

For each, determine the Iceberg equivalent using this mapping:

### PRR.csv (Part Results Record — die-level sort outcomes)

```
PRR.csv column    →  Iceberg wafer_sort column
─────────────────────────────────────────────
LOT_ID            →  lot_id
WAFER_ID          →  wafer_id
X_COORD / DIE_X   →  die_x
Y_COORD / DIE_Y   →  die_y
PART_FLG          →  pass_flag   (1=pass, 0=fail)
HARD_BIN          →  bin_number
BIN_DESC          →  bin_name
TEST_DATE / time  →  test_date
SITE_NUM          →  site_num
```

### PTR.csv / LibPM / in-die monitors (Parametric Test Records)

PTR records are die-level parametric measurements stored in `wafer_sort` (long format)
or `wafer_sort_wide` (pivoted). Check `wafer_sort_wide` for prototype code that
expects one column per parameter.

```
PTR.csv column    →  Iceberg wafer_sort column
─────────────────────────────────────────────
LOT_ID            →  lot_id
WAFER_ID          →  wafer_id
TEST_TXT / name   →  param_name
RESULT            →  value
LO_LIMIT          →  lo_limit
HI_LIMIT          →  hi_limit
SITE_NUM          →  site_num
X_COORD           →  die_x
Y_COORD           →  die_y
```

### WAT.csv / PCM (Wafer Acceptance Test — scribe-line, per-site)

```
WAT.csv column    →  Iceberg wafer_acceptance column
─────────────────────────────────────────────────────
LOT_ID            →  lot_id
WAFER_ID          →  wafer_id
PARAMETER_NAME    →  parameter_name
VALUE             →  value
SITE_NUM          →  site_num
LOWER_LIMIT       →  lower_limit
UPPER_LIMIT       →  upper_limit
TEST_DATE         →  test_date
```

### HBR.csv / SBR.csv (Hard/Soft Bin Records — wafer-level counts)

These are aggregations of `wafer_sort`. Do not query a separate table:
```python
# Compute from die-level wafer_sort data
bin_counts = (
    prr_df
    .groupby(["lot_id", "wafer_id", "bin_number", "bin_name"])
    .size()
    .reset_index(name="count")
)
```

---

## Step 3 — Generate the @semi_task Data Loading File

Write `--output-task` with one `@semi_task` that:
1. Creates a `DuckDBIcebergDataView` (or queries `context.db` directly)
2. Fetches each required table as a pandas DataFrame
3. Builds the prototype's `Dataset` object from those DataFrames
4. Calls `m_ingestion(ds, R)` if present (the first analysis step)
5. Pickles the Dataset to `context.workspace_dir / "dataset.pkl"` for downstream tasks

### Template

```python
"""Iceberg data loading task for <workflow_name>."""
from __future__ import annotations

import asyncio
import pickle
from pathlib import Path

import pandas as pd

from app.data_views.factory import create_iceberg_data_view
from app.flows.base import semi_task, get_flow_context
from common_semi.utils.logging import get_logger

from app.<workflow_snake_case>.core import Dataset  # verbatim from prototype

log = get_logger(component="workflow.<workflow_snake_case>.load")


@semi_task(auto_clean=False, name="<workflow_snake_case>_load_data")
async def load_data(
    product_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    use_wat: bool = True,
) -> dict:
    """Load wafer-sort + WAT data from Iceberg and build the Dataset object."""
    context = get_flow_context()

    # DuckDBIcebergDataView replaces all CSV reads
    data_view = create_iceberg_data_view(
        db=context.db,
        product_id=product_id,
        date_range=(start_date, end_date) if start_date else None,
        lot_ids=None,
    )

    # Wafer-sort die-level results (replaces PRR.csv + HBR.csv + SBR.csv)
    prr_df: pd.DataFrame = await asyncio.to_thread(
        _fetch_wafer_sort, data_view
    )

    # Parametric test results / in-die monitors (replaces PTR.csv / LibPM CSVs)
    ptr_df: pd.DataFrame = await asyncio.to_thread(
        _fetch_parametric, data_view
    )

    # WAT / PCM (replaces WAT.csv) — optional
    wat_df: pd.DataFrame | None = None
    if use_wat:
        try:
            wat_df = await asyncio.to_thread(_fetch_wat, data_view)
        except Exception:
            log.warning("wat_unavailable", product_id=product_id)

    # Build the Dataset the core analysis expects — same class, Iceberg data
    ds = Dataset(prr=prr_df, ptr=ptr_df, wat=wat_df, name=product_id)

    # Run m_ingestion if prototype has it (validates + caches derived fields)
    from app.<workflow_snake_case>.core import m_ingestion  # noqa: PLC0415
    R: dict = {}
    m_ingestion(ds, R)

    # Pickle for downstream tasks — DataFrames must not cross Prefect task boundaries raw
    pkl_path = context.workspace_dir / "dataset.pkl"
    pkl_path.write_bytes(pickle.dumps(ds))

    log.info(
        "data_loaded",
        product_id=product_id,
        lots=prr_df["lot_id"].nunique(),
        wafers=prr_df["wafer_id"].nunique(),
        die_count=len(prr_df),
        has_ptr=len(ptr_df) > 0,
        has_wat=wat_df is not None and len(wat_df) > 0,
    )
    return {"ds_pkl": str(pkl_path), "R": R}


def _fetch_wafer_sort(data_view) -> pd.DataFrame:
    """Pull die-level sort results, normalise column names to prototype expectations."""
    df = data_view.get_die_results().to_pandas()
    # Rename Iceberg → prototype column names if the core analysis expects specific names
    return df.rename(columns={
        "pass_flag":  "PART_FLG",   # adjust per prototype's expected column names
        "bin_number": "HARD_BIN",
        "bin_name":   "BIN_DESC",
        "die_x":      "X_COORD",
        "die_y":      "Y_COORD",
    })


def _fetch_parametric(data_view) -> pd.DataFrame:
    """Pull parametric test results (PTR / in-die monitors)."""
    df = data_view.get_parametric_results().to_pandas()
    return df.rename(columns={
        "param_name": "TEST_TXT",
        "value":      "RESULT",
        "lo_limit":   "LO_LIMIT",
        "hi_limit":   "HI_LIMIT",
    })


def _fetch_wat(data_view) -> pd.DataFrame:
    """Pull WAT / PCM scribe-line parametric data."""
    df = data_view.get_wafer_acceptance_results().to_pandas()
    return df.rename(columns={
        "parameter_name": "PARAMETER_NAME",
        "value":          "VALUE",
        "lower_limit":    "LOWER_LIMIT",
        "upper_limit":    "UPPER_LIMIT",
    })
```

---

## Step 4 — Verify Column Names Against Prototype

After generating the file, grep the prototype for every column name the analysis
functions access on the DataFrames (e.g. `df["HARD_BIN"]`, `ds.prr["X_COORD"]`).
Ensure the rename maps in Step 3 cover all of them.

```bash
grep -n '"[A-Z_]\{3,\}"' <prototype-file> | grep -v "#" | sort -u
```

Fix any mismatches before proceeding.

---

## Step 5 — Update the @semi_flow to Call the New Task

In `workflow/app/workflows_v2/<workflow_snake_case>.py`, replace any call to
the prototype's `load_dataset()` with the new `load_data` task:

```python
# Before (prototype pattern — reads local CSVs)
# ds = load_dataset(data_path)

# After (Iceberg via @semi_task)
load_result = await load_data(
    product_id=product_id,
    start_date=config.extra_config.get("start_date"),
    end_date=config.extra_config.get("end_date"),
    use_wat=use_wat,
)
```

Downstream tasks that need the Dataset unpickle it:
```python
ds = pickle.loads(Path(load_result["ds_pkl"]).read_bytes())
R  = load_result["R"]
```

---

## Step 6 — Remove the CSV/File-Based Spec Input

If the `@semi_flow` previously had a `dataset_folder_id` parameter (pointing to
uploaded CSV files in MinIO), replace it with `product_id` and date-range inputs
that feed into the Iceberg data view. The `dataset-picker` UI widget becomes
`product-picker`:

```python
# Remove:
dataset_folder_id: str = Field(..., json_schema_extra={"x-ui-widget": "dataset-picker"})

# Replace with:
product_id: str = Field(..., json_schema_extra={"x-ui-widget": "product-picker"})
start_date: str | None = Field(default=None, json_schema_extra={"x-ui-widget": "date-picker"})
end_date:   str | None = Field(default=None, json_schema_extra={"x-ui-widget": "date-picker"})
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Using prototype CSV column names in Iceberg queries | Always rename after fetch — keep prototype column names in the rename map |
| Calling `data_view.get_*()` in an async function without `asyncio.to_thread` | DuckDB calls are synchronous — always wrap in `asyncio.to_thread()` |
| Passing raw DataFrames as task return values | Pickle the Dataset, return the path |
| Assuming WAT is always present | Gate on `use_wat` flag, catch exceptions, log warning |
| Forgetting to call `m_ingestion(ds, R)` | This validates the Dataset and populates derived fields the other `m_*` functions depend on |

---

## Reference Files

| Purpose | File |
|---|---|
| Canonical table/column schema | `common/common_semi/data/iceberg_schema.py` |
| DuckDB query API | `workflow/app/data_views/duckdb_iceberg_data_view.py` |
| Data view factory | `workflow/app/data_views/factory.py` |
| Reference implementation (WF1) | `workflow/app/workflows_v2/yield_excursion_v2.py` |
| Reference load task (WF1) | `workflow/app/tasks/yield_excursion_v2.py` |
