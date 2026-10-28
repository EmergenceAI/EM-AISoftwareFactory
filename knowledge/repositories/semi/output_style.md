<!--
MAINTAINED: em-semi chart and report output conventions
Last updated: 2026-09-01
Source truth: workflow/app/services/plot_service.py
              workflow/app/visualizations_agent/
              workflow/app/reports/json_report.py
DO NOT EDIT via sync_knowledge.sh — this file is curated manually.
-->

# em-semi Output Style Guide

## Chart Format

All charts are **Plotly JSON** stored as `.json` files via `fig.to_dict()`.
The report builder (`workflow/app/reports/json_report.py`) discovers these files
and embeds them as `chart["figure"]["plotly_json"]`.

**Never generate raw HTML, inline SVG, or custom chart renderers.**
The report builder renders everything — generate Plotly figure dicts only.

---

## Color Palette

Source: `workflow/app/services/plot_service.py`

| Role | Value | Usage |
|---|---|---|
| Bad / low-yield / excursion population | `#d62728` | bars, lines, box outlines for the "bad" group |
| Good / high-yield population | `#aec7e8` | bars, lines, box outlines for the "good" group |
| Histogram fill | `rgba(100, 149, 237, 0.7)` | histogram bars |
| Affected / enriched bar | `#dc2626` | pareto bars for enriched bins |
| Cumulative % line (pareto) | `#1d4ed8` | secondary Y-axis line on pareto charts |
| Regression / trend line | `"red"` | OLS/polynomial fit lines |
| Box plot default (non-highlighted) | `"steelblue"` | box plots without excursion split |
| Yield trend line (combo charts) | `"blue"`, width 4 | yield line overlaid on bar charts |
| Highlighted category shading | `rgba(214, 39, 40, 0.1)` | vrect for highlighted categories |
| Dark font | `#1f2937` | axis labels, annotation text |
| Heatmap / wafer map colorscale | `"RdBu_r"` | `go.Heatmap(colorscale="RdBu_r")` |
| KDE colorscale | `"Blues"` | 2-D KDE density plots |
| Spec limit lines (LSL / USL) | `fig.add_hline(line_color="#d62728", line_dash="dash")` | spec limits on box/CDF plots |

**Multi-bin color palette** (22-color cycle for stacked bin charts, from
`workflow/app/visualizations_agent/excursion_yield_trend.py`):
```python
BIN_COLORS = [
    "#808080", "#0000FF", "#FF0000", "#008000", "#800080",
    "#FFA500", "#FFC0CB", "#A52A2A", "#00FFFF", "#808000",
    "#FF00FF", "#008080", "#FFD700", "#00FF00", "#000080",
    "#800000", "#00FFFF", "#4B0082", "#FF7F50", "#D2691E",
    "#DC143C", "#BDB76B",
]
```

---

## Plotly Template and Layout Defaults

```python
import plotly.graph_objects as go

fig.update_layout(
    template="plotly_white",          # always — never None or default
    title={"text": title, "x": 0.5, "xanchor": "center"},
    font={"color": "#1f2937"},
    width=1200,                       # default; use 1400 for wide multi-panel charts
    height=600,                       # default; use 800 for complex charts
)
```

---

## Chart Types and Plotly Patterns

### Box plot per lot / parameter (most common)

```python
fig = go.Figure()
fig.add_trace(go.Box(
    y=values,
    name=label,
    boxmean="sd",                     # always include mean + SD whisker
    marker_color="#aec7e8",           # or "#d62728" for excursion group
))
fig.add_hline(y=usl, line_color="#d62728", line_dash="dash",
              annotation_text="USL", annotation_position="top right")
fig.add_hline(y=lsl, line_color="#d62728", line_dash="dash",
              annotation_text="LSL", annotation_position="bottom right")
```

### Stacked bar + yield trend (dual Y-axis)

```python
from plotly.subplots import make_subplots

fig = make_subplots(specs=[[{"secondary_y": True}]])
for bin_name, color in zip(bin_names, BIN_COLORS):
    fig.add_trace(go.Bar(name=bin_name, x=lots, y=fail_rates,
                         marker_color=color, yaxis="y2"), secondary_y=True)
fig.add_trace(go.Scatter(x=lots, y=yield_pct, name="Yield",
                          line={"color": "blue", "width": 4}, yaxis="y"),
              secondary_y=False)
fig.update_layout(barmode="stack")
```

### Wafer fail heatmap

```python
from plotly.subplots import make_subplots

fig = make_subplots(rows=1, cols=2, shared_yaxes=True,
                    subplot_titles=["Bad Population", "Good Population"])
for col, (title, z_data) in enumerate([(bad_title, bad_z), (good_title, good_z)], start=1):
    fig.add_trace(
        go.Heatmap(z=z_data, colorscale="RdBu_r",
                   coloraxis="coloraxis",         # shared color axis
                   showscale=(col == 1)),
        row=1, col=col,
    )
fig.update_layout(coloraxis={"colorscale": "RdBu_r"})
```

### Pareto bar + cumulative % (enrichment chart)

```python
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=categories, y=enrichment_vals,
                     marker_color="#dc2626", name="Enrichment ratio"),
              secondary_y=False)
fig.add_trace(go.Scatter(x=categories, y=cumulative_pct,
                          line={"color": "#1d4ed8"}, name="Cumulative %",
                          mode="lines+markers"),
              secondary_y=True)
```

### Scatter with regression line

```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="markers",
                          marker={"color": "#aec7e8", "opacity": 0.6},
                          name="Wafers"))
# OLS / polynomial fit
import numpy as np
coeffs = np.polyfit(x_vals, y_vals, deg=1)
x_fit  = np.linspace(min(x_vals), max(x_vals), 200)
fig.add_trace(go.Scatter(x=x_fit, y=np.polyval(coeffs, x_fit),
                          mode="lines", line={"color": "red"}, name="OLS fit"))
```

### Scatter with highlighted groups (express)

```python
import plotly.express as px

fig = px.scatter(
    df, x="parameter", y="yield_pct",
    color="group",
    color_discrete_map={"Excursion": "#d62728", "Normal": "#aec7e8", "Other": "lightgrey"},
    template="plotly_white",
)
```

---

## Saving Charts (required pattern)

```python
import json
from common_semi.utils.json_utils import NumpyEncoder   # handles np.float32 etc.

def save_chart(fig: go.Figure, output_path: Path, name: str) -> Path:
    chart_path = output_path / f"{name}.json"
    with chart_path.open("w") as f:
        json.dump(fig.to_dict(), f, cls=NumpyEncoder)
    return chart_path
```

The report builder (`_load_charts_from_output_dir`) discovers `.json` files
that contain a `"data"` key (the Plotly traces list). It **skips** files whose
stems are in `_NON_CHART_JSON_STEMS` and `"analysis_summary.json"`.

---

## Chart-to-Report Pipeline

```
@semi_task writes:
  context.workspace_dir/charts/<chart_name>.json   ← fig.to_dict() via json.dump(NumpyEncoder)

report_generation task calls:
  _load_charts_from_output_dir(charts_dir)
    → finds *.json with "data" key present
    → sanitizes NaN/Inf via _sanitize_plotly_json()
    → ModelChart(title=stem.replace("_"," ").title(), figure_json=plotly_data)

context.add_sections_to_report(sections)
    → ReportSection + Chart rows in DB
    → chart["figure"]["plotly_json"] = fig.to_dict()

context.add_artifact(chart_path)
    → uploads .json (and optional .png) to MinIO via @semi_flow on completion
```

**Always call `await context.add_artifact(path)` for every chart JSON.**
Static PNG export (via Kaleido) is handled automatically by the report renderer
when a PDF/DOCX is generated — do not call `pio.write_image` from workflow code.

---

## Report Sections Structure

A section passed to `context.add_sections_to_report()` has this shape:

```python
{
    "id": "parametric_screen",
    "title": "Parametric Screen",
    "content": "Markdown text describing findings...",   # supports markdown
    "charts": [
        {
            "id": "cdf_mon_rc_v1",
            "title": "MON_RC_MON_V1 — CDF by population",
            "figure": {"plotly_json": fig.to_dict()},
            "comments": [],
        }
    ],
    "attachments": [],
    "explainability_metadata": {},
}
```

Standard section IDs used by yield excursion (match these for consistency):
- `executive_summary`
- `findings_table`
- `confounder_panel`
- `parametric_screen`
- `spatial_maps`
- `capability_section`
- `bin_pareto`
- `yield_opportunity`
- `time_artifact_guard`
- `parameter_bin_relationships`
- `excluded_parameters`

---

## Reference Implementations

- **PlotService** (all chart methods): `workflow/app/services/plot_service.py`
- **Wafer pattern maps**: `workflow/app/visualizations_agent/excursion_wafer_pattern_maps.py`
- **Yield trend charts**: `workflow/app/visualizations_agent/excursion_yield_trend.py`
- **Report builder**: `workflow/app/reports/json_report.py`
- **Report task**: `workflow/app/tasks/report_generation.py` — see `_load_charts_from_output_dir` (line ~716)
