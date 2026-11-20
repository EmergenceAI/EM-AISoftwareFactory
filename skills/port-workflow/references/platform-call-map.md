# em-semi platform call → craft

Kinds:
- **real**: a craft capability or SDK call does the same job.
- **adapter**: a module keeping em-semi's names that reads through the bundle's **source layer**:
  craft capabilities at run time, the committed fixture in tests (see *Two data sources* in
  `porting-model.md`). Not a gap.
- **shim**: a small module keeping em-semi's names, doing what craft's job lane needs (often
  nothing).
- **stand-in**: a fixture-backed stand-in with no craft path yet, recorded as a gap until the real
  craft capability exists.

Every redirect is an import rewrite in the vendor script, pointing at a module in
`<pkg>/vendor/_*.py`, `<pkg>/standins/` or a shared Pack-level module. Verify the craft side against
the current `craft/compute-plane-python/packages/craft_job_sdk/src/craft_job_sdk/context.py` before
relying on it. `JobContext` exposes:
- resources and files: `resource_read`, `resource_presign_read`, `file_emit`;
- data: `data_query(sql, dataset=None)`, `data_export(dataset, column=, values=, time_column=,
  start=, end=)`, `data_migrate`, `data_seed_read`;
- the bundle database: `db_query(sql, params)`, `db_write(table, rows, mode=, key=)`,
  `db_delete(table, where)`;
- LLMs and ledger: `llm_complete`, `llm_models_list`, `ledger_record`, `ledger_read`;
- the rest: `project_read`, `invocation` (`org_id`, `run_id`), `log`, `progress`, `group`.

| em-semi module / call | craft equivalent | Kind | Notes |
|---|---|---|---|
| `app.flows.base` `@semi_flow` / `@semi_task` | `vendor/_flows.py` no-op decorators | shim | As analog-trim. The flow function itself is replaced by `bundle.yaml` |
| `FlowContext` (`app.flows.context`: `log_ui_message`, `create_ui_group`, `log_progress`, `create_report`) | `CraftContext` over `JobContext.log` / `progress` / `group` / `file_emit` | real (via shim) | Report = node output, read by the bundle app through `runSource`. `add_artifact` emits `<run id>-<basename>`: one active artefact per (org, project, name) refuses a bare name on every run after the first, and the app shell joins the attachment on the `-<basename>` suffix |
| `common_semi.observe` | `vendor/_observe.py` | shim | Keep log sanitization behaviour |
| `opentelemetry` `trace` | `vendor/_otel.py` | shim | Craft's step journal is the span |
| `WorkflowRunConfig` / `common_semi.model` run config, `extra_config` | `vendor/_run_config.py`, values from node args / `inputSchema` | shim | The org is `job.invocation.org_id`, never an input |
| `app.models.models`, `common_semi.model.product` report models | `vendor/_report_models.py` | shim | |
| `create_iceberg_data_view` / `app.data_views` / `common_semi.data.wf3_lot_dataset` / pyiceberg reads of per-product or per-org tables | `data_query(sql, dataset=)` over the datasets `craft local data-init` registers (`<kind>__<8 hex>` per product, `<table>` per org, `wf3_<stem>`). Past 10,000 rows / 30 s: `data_export` + `prefetch` + local DuckDB in a later node | adapter | Grant: `executorConfig.dataScope` (`datasets`, or `resolve` from `input.product_ids`). See *data.query pitfalls* below. Craft has no snapshot pin: name tables by the read's `snapshot_id` and record the unchecked pin as a gap |
| `product_catalog` / `read_catalog` | The catalog dataset via `data_query` | adapter | `append_revisions` (writes to a catalog mirror): stand-in that raises, gap |
| `get_database` / `common_semi.db.app_database` repositories (products, `product_attribute_revisions`, report rows) | Reads: `db_query` over the `semi` tables. Writes: `db_write` / `db_delete` to a bundle results table | adapter | Grant: `executorConfig.bundleDb` (`read`, `write`). em-semi's schema as it is: filter on `org_id = :org` in the SQL. A write with no `semi` table for it stays on the node output and is a gap |
| `app.common_utils.policy_utils.fetch_knowledge_for_workflow` / `knowledge_*` repositories | `db_query` over `knowledges`, `knowledge_types`, `knowledge_versions` (org-wide, active, current version); em-semi's seeded default when none | adapter | The filter on the knowledge types the em-semi workflow version accepts has no craft run row; record it |
| DB-backed queues (e.g. Feedback & Learning's pending feedback) | none | stand-in, gap | |
| `get_storage_service` / `common_semi.storage` (GCS/MinIO) | Inputs: `prefetch` + `resource_read` / `resource_presign_read`. Outputs: `file_emit` | real | |
| `post_inbox_message` | none: notifications are server-written, kinds `workflow_run` / `chat_run` only | dropped | List under *Not ported* |
| `app.factories.llm` / `common_semi.service.llm_service` / `litellm.acompletion` | `JobContext.llm_complete(model_alias, messages, **options)` | real | Real model, no record/replay. `model` is a project alias; `None` = project default. Tool-use loops need `tool_names`; check what the gateway supports and record gaps |
| `sql_guard.validate_agent_sql` / DuckDB `lock_down` (Test RCA), LLM-written Python | none for code written during a run (the `sandbox` executor runs only a pinned, deployed snippet) | stand-in, gap | Pure validation logic is copied; the run-time sandbox is the gap |
| `common_semi.service.knowledge_update` / `knowledge_guardrails` (Feedback & Learning approval) | none yet | stand-in, gap | |
| Feature flags, hyperparameter definitions | Node args / `inputSchema` defaults; overrides from a bundle DB table via `db_query` | shim | Pin the values em-semi uses by default; list them in the gap report |
| `@semi_task(retries=, timeout_seconds=)` | Node `retry: {maxAttempts: retries + 1, delayMs}` and `timeoutMs` | real | Only when the node is one task; a whole-node retry repeats every stage |
| em-semi run-form widgets (`technology-node-picker`, `quarter-picker`, …) | `x-ui-widget: text` with `x-placeholder` and `pattern`, or `string-list` | shim | craft renders only `text`, `string-list`, `file-upload`. Record each unmapped widget as a gap |
| `app.prompts` (prompt templates) | Copy | copy | Analysis content, not platform |
| `common_semi.agent_profile` / chat agent pieces | none | out of scope | List under *Not ported* |

## data.query pitfalls (found on the CPA live run)

`data.query` returns rows over the job channel, and two column types do not survive it on craft
today. Read them as another type in the adapter's SQL, and record each in the gap report:

| Column type | Failure | Read it as |
|---|---|---|
| `DECIMAL` | `canonicalize: unsupported value type "Decimal"` (craft's audit hash) | `CAST(c AS DOUBLE)`; the vendored code reads floats |
| `TIMESTAMPTZ` | DuckDB's `Required module 'pytz' failed to import` on the server | `CAST(c AS VARCHAR)` (keeps the UTC offset), parsed back with `pd.to_datetime(..., utc=True, format="ISO8601")` |

So the adapter names its columns (from the fixture's column contract) instead of `SELECT *`. Any id
it puts in SQL is held to `[A-Za-z0-9_-]+` first, because `data_query` has no bound parameters.
