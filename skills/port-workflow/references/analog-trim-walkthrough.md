# analog-trim: the worked example

`craft/bundles/analog-trim/` is em-semi's `workflow/app/trim_optimization/` ported to craft. Every
new port follows its approach. Its full design is
`craft/docs/superpowers/specs/2026-09-15-analog-trim-port-and-workflow-ui-design.md`, with
follow-ups beside it (`2026-09-15-analog-trim-increments-2-3-run-visibility-design.md`,
`2026-09-29-analog-trim-infineon-scale-datasets-design.md`, `2026-10-07-analog-trim-app-ui-components-design.md`).

Read the real files. This page tells you what each one is for and what a new port takes from it.

| File | What it does | What a new port takes from it |
|---|---|---|
| `bundle.yaml` | Declares `components` (job: `executor: job`, `confinement: host-mediated`, `entrypoint`, `capabilities`, `prefetch`; WASM: `executor: wasm`), `workflows` (DAG incl. the `models` fan-out over `ingest.byKey`, timeouts), `inputSchema` (file uploads with `x-ui-widget`), `presentation`, `runLabel`, `templates`, `apps` (`runSource.nodeId`) | The manifest shape. Grant each job component only the capabilities its node calls. A new Python port is job components only, unless something is genuinely better as WASM |
| `job/pyproject.toml` | uv project; only runtime dep is `craft-job-sdk`; numpy/pandas/etc come from the runner image; ruff excludes the vendor tree | Same layout. Don't add runtime deps the runner image lacks; record them in the gap report instead |
| `job/scripts/vendor_trim_opt.sh` | Copies em-semi code + tests at pinned `EM_SEMI_REF` via `git ls-tree`/`git show`, excludes `flow.py`, applies `perl -pe` import rewrites (`rewrite()`), then `git apply`s `patches/*.patch`, failing hard if one doesn't apply | The template `templates/vendor_workflow.sh.tmpl` is this script generalised. Its header comments explain every guarantee. Keep them |
| `job/patches/0001-*.patch`, `0002-*.patch` | craft's own changes to vendored code, carried as patches so a re-vendor reapplies them | Any non-import change to vendored code goes here, numbered, never as a hand edit |
| `job/src/craft_trim/vendor/` | The vendored tree (committed; nobody needs em-semi to build) | Same, as `<pkg>/vendor/` |
| `job/src/craft_trim/vendor/_flows.py` | No-op `@semi_task` / `@semi_flow`: craft's job lane already gives span, workspace and input staging | Copy the idea for every port |
| `vendor/_observe.py`, `_otel.py`, `_run_config.py`, `_report_models.py` | Shims for `common_semi.observe`, `opentelemetry.trace`, `common_semi.model` run config, report models | Reuse/extend; one shim per redirected em-semi module |
| `job/src/craft_trim/context.py` | `CraftContext`: `FlowContext`'s method names, parameters and sync/async shape, backed by `JobContext.log/progress/group` and `file_emit`; the report is the node output, not a DB row | Every port needs one. Factor it to a shared place if a second port would copy it verbatim |
| `job/src/craft_trim/nodes/{ingest,select,sections}.py` | Node entry points (`run`) that bind inputs, build a `CraftContext`, call vendored functions, return the node output | One per node in the plan. Thin; no analysis logic |
| `job/src/craft_trim/inputs.py`, `universal.py`, `typed_ingest.py`, `columnar.py` | Input binding and parsing for uploads (large-file work) | Only what the new workflow's inputs need |
| `job/scripts/make_fixtures.py` + `job/tests/_golden.py` | Writes committed demo fixtures and `fixtures/golden-node-outputs.json` from the nodes' real output; one definition shared with the golden test | Same pattern. Goldens come from craft's nodes |
| `job/tests/test_craft_trim_golden.py` | Holds live node output to the golden file | Template `templates/test_golden.py.tmpl` |
| `job/tests/vendor/` | em-semi's own trim tests, vendored and rewritten by the script: the parity oracle | Same |
| `job/tests/conftest.py` + `test_craft_trim_vendor_quarantine.py` | Suppresses specific vendored tests by nodeid (`xfail(strict=True)`) and checks each entry still names a real test | How pre-existing em-semi failures are carried |
| `job/tests/test_vendor_is_self_contained.py` | Every vendored import is satisfied by the vendor tree, shims, or the runner image's `requirements.txt` | Template `templates/test_vendor_quarantine.py.tmpl` |
| `job/tests/patches/` | Equivalence tests for the patch series (live outside `tests/vendor`, which a re-vendor wipes) | Same, if the port carries patches |
| `job/scripts/compare_report_fixture.py` | Structural diff of `golden-report.json` in CI | Optional: use if the workflow produces a report |
| `fixtures/` | Demo inputs, `golden-node-outputs.json`, `golden-report.json` | Synthetic/demo data only |
| `app/` | Vite/React report renderer (`App.tsx`) for the report node | Only if the workflow has a report UI; may reuse trim-report's pattern |
| `guest/` | Rust WASM guests (`trim-codegen`, `trim-report`) | Trim-specific. A Python port normally has none |

## Not ported for trim

em-semi's chat side for trim (`agent/app/prompt_sections/profiles/analog-trim-optimization/`,
`mcp/app/skills/analog-trim-*`, `common/common_semi/agent_profile/profiles/analog-trim-optimization.yaml`)
and the inbox message. Ports follow suit: chat/agent pieces are out of scope.
