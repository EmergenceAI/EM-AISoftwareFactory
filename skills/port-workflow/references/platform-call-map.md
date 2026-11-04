# em-semi platform call → craft

Kinds:
- **real**: a craft capability or SDK call does the same job.
- **shim**: a small module keeping em-semi's names, doing what craft's job lane needs (often
  nothing).
- **stand-in**: a fixture-backed stand-in, recorded as a gap until the real craft capability
  exists.

Every redirect is an import rewrite in the vendor script, pointing at a module in
`<pkg>/vendor/_*.py` or a shared Pack-level stand-in. Verify the craft side against the current
`craft/compute-plane-python/packages/craft_job_sdk/src/craft_job_sdk/context.py` before relying on
it; `JobContext` exposes `resource_read`, `resource_presign_read`, `file_emit`, `data_query`,
`data_migrate`, `data_seed_read`, `llm_complete`, `llm_models_list`, `ledger_record`, `ledger_read`,
`project_read`, `log`, `progress`, `group`.

| em-semi module / call | craft equivalent | Kind | Notes |
|---|---|---|---|
| `app.flows.base` `@semi_flow` / `@semi_task` | `vendor/_flows.py` no-op decorators | shim | As analog-trim. The flow function itself is replaced by `bundle.yaml` |
| `FlowContext` (`app.flows.context`: `log_ui_message`, `create_ui_group`, `log_progress`, `create_report`) | `CraftContext` over `JobContext.log` / `progress` / `group` / `file_emit` | real (via shim) | Report = node output, read by the bundle app through `runSource` |
| `common_semi.observe` | `vendor/_observe.py` | shim | Keep log sanitization behaviour |
| `opentelemetry` `trace` | `vendor/_otel.py` | shim | Craft's step journal is the span |
| `WorkflowRunConfig` / `common_semi.model` run config, `extra_config` | `vendor/_run_config.py`, values from node args / `inputSchema` | shim | |
| `app.models.models`, `common_semi.model.product` report models | `vendor/_report_models.py` | shim | |
| `get_database` / `common_semi.db.app_database` (report rows, run config, queues) | Node output; `ledger_record`/`ledger_read` for run-scoped state | real / gap | DB-backed queues (e.g. Feedback & Learning's pending feedback) have no equivalent: stand-in, gap |
| `get_storage_service` / `common_semi.storage` (GCS/MinIO) | Inputs: `prefetch` + `resource_read` / `resource_presign_read`. Outputs: `file_emit` | real | |
| `post_inbox_message` | none | dropped | Analog-trim dropped it. List under *Not ported* |
| `create_iceberg_data_view` / `app.data_views` / `source_resolution` / pyiceberg / DuckDB views | Candidate: `data_query(sql)`, once product data is ingested into craft. Until then: stand-in reading fixture Parquet with the same view interface | stand-in, gap | Waits on the data-ingestion epic. Build once (CPA), reuse for YPI and Yield Excursion |
| `common_semi.data.wf3_lot_dataset` (`load_lot_dataset`) | Same as data views | stand-in, gap | Analysis-only parts of the module are copied |
| `product_catalog` / `read_catalog` / `common_semi.service.product_attributes` | Stand-in over fixture catalog JSON | stand-in, gap | |
| `app.factories.llm` / `common_semi.service.llm_service` / `litellm.acompletion` | `JobContext.llm_complete(model_alias, messages, **options)` | real | Real model, no record/replay. `model` is a project alias; `None` = project default. Tool-use loops need `tool_names`; check what the gateway supports and record gaps |
| `sql_guard.validate_agent_sql` / DuckDB `lock_down` (Test RCA) | none yet (governed SQL sandbox) | stand-in, gap | Pure validation logic is copied; the sandboxed execution is the gap |
| `common_semi.service.knowledge_update` / `knowledge_guardrails` (Feedback & Learning approval) | none yet | stand-in, gap | |
| Feature flags | Node args / `inputSchema` defaults | shim | Pin the flag values em-semi uses by default; list them in the gap report |
| `app.prompts` (prompt templates) | Copy | copy | Analysis content, not platform |
| `common_semi.agent_profile` / chat agent pieces | none | out of scope | List under *Not ported* |
