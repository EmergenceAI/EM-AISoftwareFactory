# port-workflow v2: use craft's real data paths, and finish the CPA port

Status: plan, 2026-11-19. Follows the first skill (`specs/2026-11-03-port-workflow-skill`, PR #12)
and the CPA trial port (craft branch `feat/CPE-1643-port-cross-product-analysis`, commit
`289597a72`, not pushed).

The first trial port runs CPA end to end, but on fixture stand-ins, with a text-only run form and no
report view. Since then craft has gained:
- the local `semi` data: CPE-1680, PR #1487;
- run-time grants, filtered exports and the bundle database: CPE-1677, PR #1495.

This plan updates the platform table, then changes the skill to use those paths, then re-runs CPA
on them.

## 1. Platform needs by workflow (updated)

✅ = craft has it, ⚠️ = partly, ❌ = platform change needed, — = not needed.
"#1487" and "#1495" mean the open craft PRs above.

| # | Need | CPA | YPI | YE v2 | Craft now | Evidence |
|---|---|---|---|---|---|---|
| 1 | Per-product Iceberg tables picked at run time | ✔ | ✔ | ✔ | ✅ in #1495 | `dataScope.resolve` from `input.product_ids`, named `<kind>__<8 hex>` as `data-init` registers them (#1487). Phase 4 (identity table) deferred |
| 2 | Newest snapshot, and pin one for reproducibility | ✔ | ✔ | ✔ | ❌ Ticket 2 | Not in CPE-1677 |
| 3 | Bulk reads past 10,000 rows / 30 s | ✔ | ✔ heavy | ✔ heavy | ✅ in #1495 | `data.export_lot` by lot list, time window or whole table, on any registered dataset, then `prefetch` and local DuckDB |
| 4 | Product metadata in Postgres (`products`, `product_attribute_revisions`) | ✔ | ✔ | ✔ | ⚠️ | Local: the `semi` DB with em-semi's schema (#1487), read with `db_query` (#1495). Deployment: the metadata copy still has no PR |
| 5 | Knowledge store (types per workflow version, effective version per product, report → version link) | ✔ | ✔ | ✔ | ⚠️ | The tables can live in the `semi` DB and be read with `db_query`. em-semi's "effective version" logic is analysis code and can be vendored. Seeding the knowledge rows is still open. Craft's semantic-graph `KnowledgeType` serves the assistant, not steps |
| 6 | Bundle-owned database with writes | 1 table | — | 3 tables | ✅ in #1495 | `db.query` / `db.write` / `db.delete` under `executorConfig.bundleDb`. Provisioning at bundle creation is out of scope |
| 7 | YE v2 `user_status` on the run | — | — | ✔ | ❌ | `runLabel` is write-once (`run_label IS NULL` guard) and no route sets it. Workaround: a status column in a bundle DB table via `db_write`, with no run-list UI |
| 8 | Hyperparameter definitions and overrides per workflow type | — | — | ✔ | ⚠️ | No settings concept in craft. Definitions become `inputSchema` defaults; overrides become a bundle DB table read with `db_query`. No UI to edit them |
| 9 | Report: sections, Plotly, attachments, explainability | ✔ | ✔ | ✔ | ⚠️ | `@craft/report-renderer` draws Plotly (`components/chart/Chart.tsx`, `figure_json`). Explainability metadata is ❌ (`report-types.ts:7-8`) |
| 10 | Exports: PDF / DOCX / PPTX | ✔ | ✔ | ✔ | ⚠️ | PDF via `bundles/report-to-pdf`. DOCX and PPTX ❌ |
| 11 | Inbox messages (deep link, metadata) | — | ✔ | ✔ | ❌ | `notification` table, kinds `workflow_run` / `chat_run` only, written by the server. No step capability, no metadata column |
| 12 | Run-finished notifications and email | ✔ | ✔ | ✔ | ⚠️ | In-app on run start and finish (`run/run_notification.py`, `NotificationBell`). No email or webhook |
| 13 | LLM calls, two tiers, usage | — | — | ✔ | ✅ | `llm_complete` with project aliases; `llm_usage_events` |
| 14 | Run LLM-written Python in a sandbox (120 s, memory limit) | — | — | ✔ | ⚠️ | The `sandbox` executor has a read-only container, 2g memory and `timeoutMs`, but only for a pinned, deployed snippet. Code written by the LLM during a run is ❌ (D1) |
| 15 | Run form widgets (data-driven pickers, linked and hidden fields) | ✔ | ❓ | ❓ | ❌ | Only `text`, `string-list`, `file-upload` (`craft-app/src/domain/workflows/input-schema.ts:17-19`) |
| 16 | Logs, UI groups, progress | ✔ | ✔ | ✔ | ✅ | `JobContext.log` / `group` / `progress` |
| 17 | Task retries and timeouts | ✔ | — | ✔ | ✅ | `retry: {maxAttempts, delayMs}` (2 retries = `maxAttempts: 3`) and `timeoutMs` on a node (`ir/skeleton_ir_schema.py:117-154`) |
| 18 | Parallel work and DuckDB spill inside a step | ✔ | ✔ | ✔ | ⚠️ | The job pod needs enough memory and local disk; sized per deployment |
| 19 | Iceberg writes (`wafer_sort_wide`, flag off by default) | — | — | flag only | ⚠️ | `data.write_iceberg_lot`; #1495 makes it work under a multi-dataset grant. Not blocking while the flag is off |

**What blocks each workflow**, counting only ❌ rows and not the ⚠️ workarounds:
- **CPA:** 2 and 15.
- **YPI:** 2, 11 and 15.
- **YE v2:** 2, 7, 11, 15 and the run-time half of 14.

Rows 1, 3 and 6 stop being blockers once #1495 merges.

## 2. Skill changes (EM-AISoftwareFactory `skills/port-workflow/`)

**Status (2026-11-20):** done after the CPA port ran live (craft `a21b76f888`): S1, S2, S3, S4, S5,
S7 and S8. Also added: the package-marker step in the vendor template, the `data.query` cast rules,
the per-run artefact name, and a table of live-run failures and their causes. Not done: S6
(workflow metadata and node diagram).

Each change says which table rows it uses and which file it touches.

| # | Change | Rows | Files |
|---|---|---|---|
| S1 | **Call map: real paths replace stand-ins.** Data views and `wf3_lot_dataset` go to `data_query(sql, dataset=)` under a `resolve` grant, or `data_export` + `prefetch` + DuckDB for bulk reads. `product_catalog` and `context.db` repositories go to `db_query`, and their writes to `db_write`. Knowledge reads go to `db_query` over the knowledge tables. Feature flags and hyperparameters become `inputSchema` defaults, with an optional settings table. `post_inbox_message` stays dropped (row 11) | 1, 3, 4, 5, 6, 8 | `references/platform-call-map.md`, `porting-model.md` |
| S2 | **Two data sources per interface.** Each redirected interface gets a craft adapter, a thin class with em-semi's interface over `JobContext`, which the node uses at run time. A fixture stand-in with the same interface stays for the static tests, so parity runs offline. A stand-in is a gap only when no craft adapter exists. The gap report lists both | 1, 3, 4, 5, 6 | `SKILL.md` Step 5, `gap-report-template.md` |
| S3 | **Grants and retries in `bundle.yaml`.** `dataScope` gets `datasets` plus `resolve: [{kind, products: {from: input.product_ids}}]`. `bundleDb` lists the read and write tables the adapters touch. em-semi `@semi_task(retries=, timeout_seconds=)` maps to `retry.maxAttempts` (retries + 1) and `timeoutMs` | 1, 6, 17 | `SKILL.md` Steps 2 and 6 |
| S4 | **Run form.** Map em-semi's widgets to the closest supported `x-ui-widget`: pickers become `text` with `x-placeholder` and a `pattern`, and lists become `string-list`. Record every unmapped widget as a row-15 gap. Default input names to the `resolve` path (`product_ids`) | 15 | `SKILL.md` Step 2, call map |
| S5 | **Report app.** Generate `<bundle>/app` from `claude-usage-report/app` (the `Section[]` renderer with Plotly), and add `apps:` with `runSource.nodeId`. Widen the write boundary to allow the one-line additions to the root `pnpm-workspace.yaml` and `pnpm-lock.yaml` | 9 | `SKILL.md` Steps 6 and 8, `porting-model.md` (write boundary) |
| S6 | **Workflow metadata.** Carry em-semi's display name, description, version and a node diagram (mermaid from the node plan) into the bundle's README and `bundle.yaml` description fields | — | `SKILL.md` Step 6 |
| S7 | **Live smoke run as a gate.** After the static gates: `craft local up`, `craft local data-init`, `craft bundle register local <bundle>`, then one run with a seeded product id, checking it ends `succeeded` with a non-empty report. A missing local stack makes the outcome `partial`, not `failed` | 1, 3, 4, 6 | `SKILL.md` Step 9 |
| S8 | **Small boundary fixes.** Add the bundle to `control-plane/apps/ctl/test/bundles/bundle-yaml-schema.test.ts`'s list. The bundle job CI job stays recorded in the gap report | — | `SKILL.md` Step 8, `porting-model.md` |

The skill keeps its rules: no hand-edits of vendored files, a pinned ref, synthetic fixtures only,
a real `llm.complete`, never auto-merge, never `nojira`.

## 3. Finish CPA on the existing branch

Work on `feat/CPE-1643-port-cross-product-analysis`. Run with the updated skill as a re-run of an
existing bundle (vendored code, patches and goldens kept), plus these CPA-specific steps:

| Step | What | Needs |
|---|---|---|
| C1 | Rebase onto `main` once #1487 and #1495 merge, or stack on #1495 to start sooner | #1487, #1495 |
| C2 | `lot_dataset` adapter: `LotDataset` over `data_export` of the per-product lot tables (`lot_yield_wide` / `wf3` lots) for the chosen quarters, read with local DuckDB. The fixture stand-in stays for the tests | rows 1, 3 |
| C3 | `product_catalog` + `database` adapters: `products` and `product_attribute_revisions` via `db_query`. `append_revisions`, `link_policy_versions` and `product_yield_summary` via `db_write`. They come off the node output | rows 4, 6 |
| C4 | `knowledge` adapter: D0 targets via `db_query` over the knowledge tables. It falls back to the vendored `DEFAULT_D0_CSV` only when no row exists, as em-semi does | row 5, plus seeding knowledge rows into `semi` |
| C5 | `bundle.yaml`: `resolve` grant, `bundleDb` grant, `prepare_product` retry (`maxAttempts: 3`) and `timeoutMs: 600000` | rows 1, 6, 17 |
| C6 | Report app (S5) and widget fallbacks (S4) | row 9; row 15 stays a gap |
| C7 | Live smoke run (S7) against the local `semi` data; update `PORT_GAPS.md`, then open a PR (draft if anything is `partial`) | local stack, `BUNDLE_DATABASE_URL` set to `semi` |

## 4. Order

1. Merge craft #1487 and #1495.
2. Then, in parallel:
   - **Skill changes** S1–S8 on a Factory branch from `main`, with a dry run against the trim port.
   - **The seed and config follow-up:** knowledge rows into `semi`, and `BUNDLE_DATABASE_URL` in the local `.env`.
3. CPA C1–C7, then YPI and YE v2 with the updated skill.

Platform tickets still needed, outside the skill:
- Row 2: snapshot pin.
- Row 7: run status.
- Row 11: step-created inbox messages.
- Row 12: email.
- Row 14: run-time sandbox (D1).
- Row 15: widgets.
- Explainability (row 9).
- DOCX and PPTX (row 10).
- The deployment metadata copy (row 4).
