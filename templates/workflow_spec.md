---
# Workflow Specification — fill in all fields before running the factory
workflow_name: MY_NEW_WORKFLOW          # UPPER_SNAKE_CASE — becomes a SemiconductorWorkflow enum value
display_name: "My New Workflow"         # Human-readable name shown in UI
version: "1.0"
lifecycle: active                       # active | beta | deprecated
category: semi_workflow                 # semi_workflow | system
jira_key: SEMI-XXXX                    # optional — links PR back to ticket; omit if no Jira ticket
---

## Description

One paragraph explaining what this workflow does, why it exists, and what decision it informs.
This text becomes the Prefect deployment description and the report intro.

## Inputs

| Parameter | Type | Required | UI Widget | Description |
|---|---|---|---|---|
| product_id | str | yes | product-picker | Product identifier |
| lot_start_date | str | no | date-picker | Filter lots on or after this date (ISO 8601). Leave blank for all lots. |
| lot_end_date | str | no | date-picker | Filter lots on or before this date (ISO 8601). Leave blank for all lots. |

<!-- Add or remove rows. UI Widget options: product-picker, date-picker, text, number, boolean -->

## Data Sources

<!-- One block per data source. -->

- **Table:** `yield.wafer_sort` (Iceberg)
  - Required columns: `lot_id`, `wafer_id`, `yield_pct`, `test_date`, `bin_number`, `bin_name`, `die_x`, `die_y`
  - Critical note: de-duplicate retests on `(wafer_id, die_x, die_y)` keeping the last record per die before any analysis

- **Table:** `yield.parametric_measurements` (Iceberg)
  - Required columns: `lot_id`, `wafer_id`, `parameter_name`, `value`, `site_num`
  - Critical note: aggregate to wafer-level means before joining to sort data

## Analysis Steps

<!-- Ordered list — these become @semi_task functions, one per step. -->

1. **Load & clean** — ingest Iceberg tables, de-duplicate retests, apply date filters
2. **Excursion removal** — remove outlier lots (robust z-score on lot mean yield, cutoff −3.5)
3. **Population split** — classify bottom 10% as low-yield, top 10% as high-yield
4. **Parametric screen** — Mann-Whitney U per parameter, Benjamini-Hochberg FDR correction per family (MON separate from WAT)
5. **Bin enrichment** — compute enrichment ratio per hard bin (share of gap ÷ share of all failures)
6. **Spatial analysis** — stack die fail maps for bad vs good populations; classify wafer spatial signatures
7. **Confounder checks** — C1 (equipment/site), C3 (lot/time), C4 (collinearity)
8. **Yield opportunity estimate** — LASSO + PLS cross-validated R², per-parameter bootstrap band
9. **Report generation** — assemble sections, save Plotly JSON charts, call `context.add_sections_to_report()`

## Outputs

### Report sections (in order)
```yaml
sections:
  - executive_summary
  - findings_table          # P1/P2/P3 tiers with enrichment ratio and yield opportunity
  - confounder_panel        # C1–C5 checks, pass/fail/not-run
  - parametric_screen       # BH funnel + full parameter table
  - bin_pareto              # hard bin enrichment chart
  - spatial_maps            # wafer heatmaps, bad vs good
  - capability_section      # CDF curves vs spec limits
  - yield_opportunity       # LASSO model R², per-parameter bootstrap bands
  - time_artifact_guard     # yield-vs-time scatter + partial correlation
```

### Charts
```yaml
charts:
  - type: cdf
    parameters: [MON_RC_MON_V1, MON_RC_MON_V4]
    populations: [low, high]
    spec_limits: true
    notes: "One CDF chart per surviving parameter; bad population in #d62728, good in #aec7e8"

  - type: box_plot
    dimension: lot_id
    parameters: [MON_RC_MON_V1, MON_RC_MON_V4]
    show_spec_limits: true
    notes: "Box per lot, boxmean='sd', excursion lots highlighted with red marker_color"

  - type: bar_pareto
    dimension: hard_bin
    metric: enrichment_ratio
    top_n: 10
    secondary_y: cumulative_pct
    notes: "Bars #dc2626, cumulative line #1d4ed8"

  - type: wafer_heatmap
    metric: die_fail_rate
    populations: [low, high]
    colorscale: RdBu_r
    notes: "Side-by-side subplots, shared coloraxis"

  - type: scatter
    x: parameter_wafer_mean
    y: soft_bin_fail_rate
    fit_line: ols
    per_parameter: true
    notes: "Markers #aec7e8 opacity 0.6, OLS line red"

  - type: stacked_bar_yield
    x_axis: lot_id
    bars: [bin_fail_rates]
    secondary_y: lot_yield_pct
    yield_line_color: "blue"
    yield_line_width: 4
```

### Artifacts
```yaml
artifacts:
  - name: report
    type: report                    # assembled by workflow/app/reports/json_report.py
    format: json                    # plotly_json embedded per section
  - name: findings
    type: segment_json
    schema: excursion_findings_v2   # array of FindingRecord objects
  - name: charts
    type: chart_bundle
    format: json_per_chart          # one <chart_name>.json per chart in workspace_dir/charts/
```

## Reference Workflow

<!-- Point to the closest existing workflow as a reference implementation. -->

Closest existing workflow: `workflow/app/workflows_v2/yield_excursion_v2.py`

Differences from reference:
- [ ] Uses a different parametric family (describe here)
- [ ] Adds a new analysis step (describe here)
- [ ] Targets a different data source (describe here)

## Acceptance Criteria

<!-- These become the eval tests generated by /eval-generator -->

### Functional
- [ ] Workflow completes without error on dataset with 50 lots, 1000 wafers
- [ ] Produces at least one P1 or P2 finding when planted excursion parameters present
- [ ] All specified chart JSON files are present in output artifacts
- [ ] Report sections are persisted to DB via `context.add_sections_to_report()`

### Quality
- [ ] No bare `@flow` or `@task` decorators — only `@semi_flow` / `@semi_task`
- [ ] No `asyncio.gather` for Prefect tasks — uses `task.submit()` + `asyncio.to_thread(wait, futures)`
- [ ] All logging uses `get_logger(component=...)` with structured key=value, no f-strings
- [ ] All chart output is Plotly JSON via `fig.to_dict()`, saved to `context.workspace_dir/charts/`
- [ ] `await context.add_artifact(path)` called for every chart and the findings JSON
- [ ] New enum entry added to `SemiconductorWorkflow` in `common/common_semi/model/workflow_names.py`
- [ ] `WorkflowRegistryEntry` ENTRY present in `workflow/app/workflow_specs/<name>.py`
- [ ] `ruff check` passes with zero errors
- [ ] `mypy` passes on new files
