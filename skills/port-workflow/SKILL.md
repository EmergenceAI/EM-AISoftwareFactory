---
name: port-workflow
description: Port an em-semi Prefect workflow into a craft bundle with functional parity — vendors em-semi's code unchanged from a pinned ref, rewrites the orchestration as bundle.yaml nodes, swaps em-semi platform calls for craft capabilities or fixture-backed stand-ins, proves parity with static tests and evals, writes a gap report, and opens a PR to craft
---

# Port Workflow

> **⚠ FULLY AUTONOMOUS — NO CONFIRMATIONS EVER**
> This skill runs non-interactively via `claude -p`. Never ask "Shall I proceed?",
> "Ready to implement?", or any confirmation question. Execute every step without pausing.

Given an em-semi workflow name, bring that workflow into craft with the same behaviour, the way
`craft/bundles/analog-trim/` was ported: em-semi's analysis code is copied unchanged, only the
orchestration and the platform plumbing are replaced, and parity is proven by tests rather than
asserted.

Run from the **craft** repository root. em-semi is read-only: read it only through
`git show <ref>:<path>` / `git ls-tree`, never a checkout, never a write.

Read these before Step 1. They are binding:
- `references/porting-model.md`: the model, workflow shapes, where copying stops, rules,
  write boundary, parity layers
- `references/analog-trim-walkthrough.md`: what each analog-trim file does and what a port takes
  from it
- `references/platform-call-map.md`: em-semi platform call → craft equivalent / shim / stand-in
- `references/gap-report-template.md`: the gap report every run produces

## Usage

```bash
# Full port, PR to craft
/port-workflow cross_product_analysis --jira-key SEMI-1234

# Map only: inventory of the import closure, no branch, no PR
/port-workflow yield_excursion_v2 --jira-key SEMI-1234 --stop-after map

# Full port committed locally, nothing pushed (trial runs)
/port-workflow trim_optimization --jira-key SEMI-1234 \
  --target-bundle bundles/_dryrun-analog-trim --no-pr --branch dryrun/port-workflow-trim

# Harness invocation (python -m harness port ... builds this)
/port-workflow cross_product_analysis --jira-key SEMI-1234 \
  --context-file .knowledge_context_craft.md \
  --provenance-file .harness-results/provenance-events.jsonl
```

### Parameters

- `<workflow>` (required, positional; `--workflow-name <name>` is accepted as an alias): the
  em-semi workflow, by package or spec name (e.g. `cross_product_analysis`).
- `--jira-key <KEY>` (**required**): craft requires a Jira task for all work. Commit messages and
  the PR title start with `[Jira:KEY]` (enforced by craft's `pr-title.yml`). Never add the
  `nojira` label.
- `--em-semi-ref <sha>` (optional): em-semi commit to pin. Default: resolve em-semi
  `origin/main` to a sha at run start (`git -C $EM_SEMI rev-parse origin/main`). That sha is then
  the pin, everywhere.
- `--target-bundle <path>` (optional): craft-relative path for the bundle. Default:
  `bundles/<kebab-case workflow name>`.
- `--stop-after map|plan|port` (optional): `map` stops after Step 1, `plan` after Step 2, `port`
  after Step 9 (no PR). Each writes what it has and emits `run_complete` with `outcome: success`
  and `pr_url: null`.
- `--no-pr` (optional): run through Step 9, commit on the branch, then skip push, PR and Jira.
- `--branch <name>` (optional): use this branch in craft instead of creating one.
- `--context-file <path>` (optional): harness-injected craft knowledge context.
- `--provenance-file <path>` (optional): JSONL file for progress events (schema at the end).

`EM_SEMI` (env, optional): path to the em-semi checkout. Default: `../em-semi` relative to
craft.

## Process Flow

```
Step 0   Load context                         load_context
Step 1   Locate and map the workflow          map_workflow     (--stop-after map ends here)
Step 2   Plan the craft shape                 plan_shape       (--stop-after plan ends here)
Step 3   Create branch                        create_branch
Step 4   Write and run the vendor script      vendor
Step 5   Write shims, adapters, stand-ins     shims
Step 6   Write bundle.yaml and node modules   bundle
Step 7   Fixtures and parity checks           parity
Step 8   Gap report                           gap_report
Step 9   Verify                               verify           (--stop-after port / --no-pr end here)
Step 10  Open PR                              create_pr
Step 11  Update Jira, finish                  jira_update
```

---

## Step 0 — Load Context

Read `--context-file` if given, otherwise `knowledge/repositories/craft/*.md` in the Factory.
Read the four reference files listed above, and craft's own guidance: `CLAUDE.md`,
`bundles/README.md`, `bundles/docs/02-authoring-a-bundle.md`,
`.claude/skills/craft-bundle/SKILL.md`, `.claude/skills/craft-local/SKILL.md`,
`docs/semi-local-data-setup.md` (how em-semi's data reaches a local stack) and
`compute-plane-python/docs/authoring-a-job.md` (grants and `JobContext`). Confirm `$EM_SEMI` is a
git checkout, and resolve and verify the pinned ref
(`git -C $EM_SEMI rev-parse --verify "<ref>^{commit}"`).

Emit provenance event: `{"event": "step_complete", "step": "load_context", "em_semi_ref": "<sha>"}`

---

## Step 1 — Locate and Map the Workflow

1. Find the workflow's spec in `workflow/app/workflow_specs/` at the pinned ref (match the
   package name, spec module name, enum entry or display name). From it, find the
   **orchestration module**. Do not assume `flow.py`; see *Workflow shapes* in
   `references/porting-model.md`.
2. Walk the full import closure from the orchestration module (AST over `git show` output).
   Classify every em-semi module as **copy**, **redirect** or **both**, per *Where copying stops*.
   Map every redirect to a row of `references/platform-call-map.md`. Anything with no row gets
   one, as a stand-in.
3. Find the workflow's em-semi tests (under `workflow/tests/`, or inside the package) and its eval
   suites (`workflow/tests/eval_harness/`, `workflow/app/evaluation/`,
   `workflow/app/rca_agent/eval/`, `workflow/app/excursion_scripts/eval/`).
4. Write the inventory to `.harness-results/port-inventory.md`:
   - shape
   - orchestration module
   - copy/redirect/both table with the call-map row for each redirect
   - tests
   - evals
   - LLM call sites
   - third-party imports not in `compute-plane-python/python-runner/requirements.txt`

Emit provenance event: `{"event": "step_complete", "step": "map_workflow", "modules": N, "redirects": M}`

---

## Step 2 — Plan the Craft Shape

From the orchestration module:
- **Stages become nodes.** A loop over independent items becomes a fan-out, like analog-trim's
  `models` over `ingest.byKey`.
- **Executor.** A Python node is `executor: job` with `confinement: host-mediated`. Grant each
  component only the capabilities its node calls, and list them in the workflow's `profile`.
- **Grants.** Every dataset an adapter reads goes in the component's
  `executorConfig.dataScope` (`ops: [read]`, `datasets: [...]`, or `resolve` from
  `input.product_ids` for per-product tables). Every bundle database table goes in
  `executorConfig.bundleDb` (`read`, `write`). Name only what the adapters touch.
- **Retries and timeouts.** `@semi_task(retries=N, timeout_seconds=S)` on a task that is a whole
  node becomes `retry: {maxAttempts: N + 1}` and `timeoutMs: S * 1000`.
- **`inputSchema`** comes from the workflow's inputs and run config. Files get `prefetch`. em-semi's
  widgets map to `text` (with `x-placeholder` and a `pattern`) or `string-list`; the org is never an
  input.
- **The report** is the last node's output, plus an app (`apps:` with `runSource.nodeId`) whenever
  em-semi renders it.

Append the node plan (nodes, edges, capabilities per node, inputs) to the inventory.

Emit provenance event: `{"event": "step_complete", "step": "plan_shape", "nodes": N}`

---

## Step 3 — Create Branch

Use `--branch` if given. Otherwise create `feat/<JIRA-KEY>-port-<workflow-slug>` from craft's
`main`.

Emit provenance event: `{"event": "step_complete", "step": "create_branch", "branch": "<name>"}`

---

## Step 4 — Write and Run the Vendor Script

**Existing bundle** (a re-run): do not regenerate the script, nodes, shims or tests. Follow
*Failure handling → Target bundle already exists*.

Lay the bundle out as analog-trim does: `job/` is a uv project, the package is `craft_<slug>`, and
the only runtime dependency is `craft-job-sdk`.

Copy `templates/vendor_workflow.sh.tmpl` to `<bundle>/job/scripts/vendor_workflow.sh` and fill in
the tokens:
- `{{EM_SEMI_REF}}`: the pinned sha.
- `{{SRC_ROOTS}}`: the copy and both modules, as em-semi paths, space-separated. List whole
  packages as directories.
- `{{TEST_ROOTS}}`: the em-semi test paths.
- `{{EXCLUDED_REGEX}}`: the orchestration file(s) only, anchored on the full path, e.g.
  `/cross_product_analysis/flow\.py$`. It also applies to test paths, so a loose `flow\.py` would
  drop `test_flow.py`. A large orchestration module that holds real logic is **not** excluded; it
  is vendored as-is. If nothing is excluded, leave the regex empty.
- `{{VENDOR_PKG}}`: `craft_<slug>.vendor`.
- `{{IMPORT_REWRITES}}`: one `perl` substitution per redirect, e.g.
  `s{^from common_semi\.observe import }{from craft_<slug>.vendor._observe import };`.

The script already rewrites `app.` → `craft_<slug>.vendor.`, `common_semi.` →
`craft_<slug>.vendor.common_semi.`, and, in tests, `tests.` → `vendor.`. It drops test-tree
`__init__.py` files. It gives every vendored directory a package marker and writes each empty
module as one comment line naming its own path: craft's snippet store refuses an empty module and
keeps one snippet per checksum, so an empty or duplicate module never reaches the pod. Craft-side
modules follow the same rule: no empty `__init__.py` (give it a docstring). The rules sit inside a single-quoted `perl -pe '…'`, so never use a `'` in
them. Run it. It refuses a root that doesn't exist at the ref, and warns if it vendored 0 tests;
record that in the gap report.

**Never hand-edit a vendored file.** A platform call inside a module that has to be vendored is
fixed by an import rewrite or by a numbered patch under `<bundle>/job/patches/` (`git diff` →
`000N-<what>.patch`, then re-run the script). Patch equivalence tests go in `job/tests/patches/`,
never in `tests/vendor/`, which a re-vendor wipes.

Emit provenance event: `{"event": "step_complete", "step": "vendor", "files": N, "em_semi_ref": "<sha>"}`

---

## Step 5 — Write Shims, Adapters and Stand-ins

**Existing bundle**: add only the shims and stand-ins the new pin needs, and keep the rest. See
*Failure handling*.

Write one module per redirect, following the call map. Shims live at the vendor top level
(`vendor/_*.py`; the vendor script preserves them). `CraftContext` and node helpers live in the
package proper. Where craft has a real capability, use it: `JobContext.log` / `progress` / `group`
/ `file_emit` / `resource_read`, and `llm.complete` through `JobContext.llm_complete` for every
LLM call, with the real model and no record/replay. `CraftContext.add_artifact` emits
`<run id>-<basename>`, never the bare basename.

Data interfaces are **adapters over a source layer** (*Two data sources* in
`references/porting-model.md`):
- **`<pkg>/source.py`:** `CraftSource(job)` reads the granted datasets (`data_query`, or
  `data_export` for bulk reads) and bundle database tables (`db_query`). `FixtureSource` reads the
  committed fixture.
- **Adapters** keep em-semi's interface and call `source.active()`, never the fixture directly.
  Anything constructed before the node selects its source reads it lazily.
- **SQL:** name columns from the fixture's column contract and apply the casts in the call map's
  *data.query pitfalls* (`DECIMAL` → `DOUBLE`, `TIMESTAMPTZ` → `VARCHAR`). Hold any id put into
  SQL to `[A-Za-z0-9_-]+`.
- **Bundle database:** read em-semi's schema as it is, filtering on `org_id = :org` with the run's
  org.

Where craft has no path at all, write a **fixture-backed stand-in** with em-semi's interface. It
must never return empty data to make a test pass. Put modules later ports can reuse where they can
import them, following craft's Pack conventions. List every adapter and stand-in for the gap
report.

Fixtures are em-semi's synthetic/demo test data. **Never real customer lots**, and nothing copied
from a customer environment.

Emit provenance event: `{"event": "step_complete", "step": "shims", "shims": N, "stand_ins": M}`

---

## Step 6 — Write bundle.yaml and Node Modules

**Existing bundle**: edit `bundle.yaml` and nodes only where the new pin requires it. Never
regenerate them. See *Failure handling*.

Write `<bundle>/bundle.yaml` from the Step 2 plan. Write one thin `craft_<slug>/nodes/<node>.py`
per node: bind inputs, build the context with `organization_id=job.invocation.org_id`, select
`CraftSource(job)`, call vendored functions, and return the node output. No analysis logic lives in
nodes.

**Report app.** When em-semi renders the report, copy `bundles/claude-usage-report/app/` to
`<bundle>/app/`, excluding `node_modules` and `dist`. It is the generic `Section[]` renderer with
Plotly and attachment previews.
- Rename the package to `<bundle>-app` and set the page title.
- Point `src/App.test.tsx`'s golden import at this bundle's own golden node output.
- Add `apps: [{name, title, entry: index.html, runSource: {nodeId: <report node>}}]` to
  `bundle.yaml`.
- Register it: `<bundle>/app` in the root `pnpm-workspace.yaml`, then `pnpm install
  --lockfile-only`.
- Check it with `pnpm run typecheck && pnpm run test && pnpm run build` from `<bundle>/app`.

Add `<bundle>/bundle.yaml` to the list in
`control-plane/apps/ctl/test/bundles/bundle-yaml-schema.test.ts`, and run that test.

The bundle must build: `craft bundle build <bundle>` (see craft's `craft-bundle` skill).

Emit provenance event: `{"event": "step_complete", "step": "bundle", "nodes": N}`

---

## Step 7 — Fixtures and Parity Checks

Two layers (see *Parity* in `references/porting-model.md`). **Existing bundle**: keep the
existing tests and fixtures. Regenerate goldens only through `make_fixtures.py`, and only when the
pin changed. See *Failure handling*.

**Static tests**
- The vendored em-semi tests run against the vendored code; they are the oracle. A failing
  vendored test is a **port defect** unless it is proven pre-existing (see *Failure handling*).
  Only a proven one is quarantined, by nodeid, in `job/tests/conftest.py` with
  `xfail(strict=True)`.
- `scripts/make_fixtures.py` and `tests/_golden.py` generate `fixtures/golden-node-outputs.json`
  from craft's own nodes over the fixtures. Fill in `templates/test_golden.py.tmpl` as
  `job/tests/test_<slug>_golden.py` (`{{PKG}}`, `{{NODES}}`). LLM text goes in `LLM_TEXT_PATHS`,
  compared by structure only.
- Fill in `templates/test_vendor_quarantine.py.tmpl` as `job/tests/test_vendor_is_self_contained.py`.
- The test channel (`tests/_<slug>_fakes.py`) answers `data.query` and `db.query` from the
  fixture, the way craft answers them for the datasets `data-init` registers, and the test
  invocation's org is the fixture's. Node tests and goldens then run `CraftSource`.
- `job/tests/test_<slug>_source.py` pins the adapters: which datasets and tables are read, the
  casts, refused ids, the bundle database rows used when present and em-semi's default when not,
  and that a repository built before the source is selected still reads the active source.
- em-semi itself is never run.

**Evals**
- Port the workflow's em-semi eval suites found in Step 1 into `job/evals/` and run them against
  the craft workflow's outputs.
- If none exist, generate a suite from the workflow spec and em-semi behaviour, the way the
  Factory's `eval-generator` derives evals from acceptance criteria, and mark it *generated* in
  the gap report.

Emit provenance event: `{"event": "step_complete", "step": "parity", "static_passed": N, "static_total": T, "evals_passed": E, "evals_total": F}`

---

## Step 8 — Gap Report

Fill in `references/gap-report-template.md` as `<bundle>/PORT_GAPS.md`:
- pinned ref
- the data sources: how the local data gets in, and each adapter's craft path and grant
- every stand-in
- the live run: inputs, bundle version, outcome, and the report against the golden
- anything outside the write boundary, including platform gaps the bundle works around
- pre-existing em-semi test failures
- evals, ported vs generated
- what was not ported

The skill writes only inside its bundle, shared Pack-level modules and the three registrations in
*Write boundary* (`references/porting-model.md`). Runner-image packages, SDK, CLI, plane and
deployment-config changes are **recorded here, not made**.

Emit provenance event: `{"event": "step_complete", "step": "gap_report", "stand_ins": N, "outside_boundary": M}`

---

## Step 9 — Verify

From `<bundle>/job`: `uv run ruff format --check .`, `uv run ruff check .`, `uv run mypy`,
`uv run pytest -q`, then run the evals. From `<bundle>/app`: `pnpm run typecheck`,
`pnpm run test`. Then `craft bundle build <bundle>`. Never commit `.harness-results/`. Run
`/verify-and-fix <JIRA-KEY> --gates linter,tests,evals,review` with those commands. Fixes go
into craft-side code, adapters, shims, stand-ins or patches, **never into vendored files**.

**Live run (the last gate).** Run it from the craft checkout:

1. **Start the stack.** Run `craft local up` and read `BOOTSTRAP_ORG_ID` from
   `compute-plane-python/.env`. `up` regenerates that file and creates a new org every time, so
   read it after `up`, and repeat steps 2 and 3 after any later `up`.
2. **Load the data.** In em-semi, `ORG_ID=<BOOTSTRAP_ORG_ID> make data-export-craft PROFILE=<wf3 |
   small | large> OUT=/tmp/pack-<slug>`, then `craft local data-init --reset --pack /tmp/pack-<slug>`.
   Without `ORG_ID` the rows carry em-semi's dev org and the workflow finds no products.
3. **Publish.** `craft bundle register local <bundle> --org local-org`. A version is published
   once: bump `version:` in `bundle.yaml` before every re-register, or the old build is reused.
   Wait until `GET /v1/workflows` shows the new digest.
4. **Run.** `POST /v1/runs {"workflow": "<name>", "input": {...}}` with the dev headers
   (`x-craft-user-id: $BOOTSTRAP_ADMIN_USER_ID`, `x-craft-org-id: $BOOTSTRAP_ORG_ID`,
   `x-craft-project-id` from `GET /governance/projects`), using the inputs of a golden case. Poll
   `GET /v1/runs/{id}` to a terminal status.
5. **Compare.** The run must succeed. Its node output must match the golden for those inputs:
   section titles, chart and attachment counts, and the summary text.

What each failure has meant:

| Error | Cause | Fix |
|---|---|---|
| `component_refused`: granted capabilities not declared by the manifest | The deployment's `RUNTIME_SNIPPET_CAPABILITY_CEILING` lacks a capability | `craft local up` adds `data.query`/`db.query`. Anything else: outside write boundary |
| `SnippetContentMismatchError` | An empty module | Package markers (Step 4) |
| `no snippet registered for uri` | Two modules with identical bytes | Unique markers (Step 4) |
| `capability "data.query" failed` | A `DECIMAL` or `TIMESTAMPTZ` column, or a dataset not loaded | The casts (Step 5); check `data-init` output |
| No products / wrong organization | Pack org ≠ run org, or a repository that read the fixture | `ORG_ID` on export; lazy source reads |

The server hides a capability's exception from the tenant. To see it locally, add the exception to
the `"capability %s failed"` warning in `executor/job/capability_server.py`, then restart only the
server (`make server` in `compute-plane-python`; databases and the org survive). Revert it after.

With no local stack available, the live run is `not run`: say so in the gap report and finish
`partial`.

Commit: `[Jira:<KEY>] port(<workflow>): vendor em-semi <sha7>, bundle, parity tests`.

`--stop-after port` or `--no-pr`: emit `run_complete` (`success` if all gates passed, otherwise
`partial`) with `pr_url: null`, and stop.

Emit provenance event: `{"event": "gate", "step": "verify", "gate": "<name>", "passed": true|false}` per gate (the live run is gate `live_run`, with `"run_id"` and `"bundle_version"`), then `{"event": "step_complete", "step": "verify"}`

---

## Step 10 — Open PR

Push the branch and invoke `/create-pr` with:
- Title: `[Jira:<KEY>] port(<workflow>): <display name> to craft`
- Body: what was vendored (ref, shape), the node plan, parity results, and the full contents of
  `PORT_GAPS.md`

**Never auto-merge. Never add `nojira`.** If the outcome is `partial`, open the PR as a draft.

Emit provenance event: `{"event": "step_complete", "step": "create_pr", "pr_url": "<url>"}`

---

## Step 11 — Update Jira, Finish

Invoke `/jira-update <KEY>` with the PR URL and a summary that includes the stand-in list, then
move the ticket to "In Review".

Emit provenance event: `{"event": "step_complete", "step": "jira_update"}` then `{"event": "run_complete", "outcome": "success|partial", "pr_url": "<url>"}`

---

## Failure handling

- **Unknown workflow**: no spec or package matches the name at the pinned ref. Stop before
  creating a branch. Emit `step_failed` for `map_workflow` naming the spec files searched and
  the closest matches, then `run_complete` with `outcome: failed`.
- **em-semi checkout missing, or the pinned ref doesn't resolve**: stop in Step 0 with
  `outcome: failed`. The vendor script also refuses before writing anything.
- **Pre-existing em-semi test failures** at the pinned ref. "Em-semi itself is never run"
  applies to the parity checks, not to this proof. Prove a failure is pre-existing by running
  the same test in an export of em-semi's own tree at the pinned ref (`git archive`):
  `git -C $EM_SEMI archive <sha> workflow common | tar -x -C /tmp/em-semi-<sha>`, then run it there
  with em-semi's test setup. That keeps em-semi read-only. Or cite em-semi CI for that sha.
  Record the evidence in the gap report.
  - Never treat an ImportError or a collection error as pre-existing. Those come from the
    rewrites or shims, and must be fixed with a rewrite, shim or patch.
  - Never make a failure pass by editing vendored code.
  - With proof: quarantine it by nodeid (`xfail(strict=True)`), list it, and finish `partial`.
  - Without proof: it's a port defect. Fix it, or finish `partial` with it failing and listed.
- **Target bundle already exists** (a re-run): don't wipe it. Re-run its vendor script, bumping
  `EM_SEMI_REF` in its own commit if the pin changes. Keep `patches/`, `nodes/`, shims and
  stand-ins, and regenerate goldens only through `make_fixtures.py`. A patch that no longer
  applies is a hard failure: record it and finish `partial`.
- **No reasonable stand-in**, or a need outside the write boundary that blocks the port: record
  it in the gap report, commit what exists, open a **draft** PR (unless `--no-pr`), and finish
  `partial`.
- **Gates still failing after `/verify-and-fix` retries**: same as above, `partial`, draft PR.

## Rules

- Never hand-edit a vendored file. Only import rewrites in the vendor script and numbered patches.
- Never rewrite analysis code, including large orchestration modules.
- Always pin the em-semi ref. Read em-semi only via `git show` / `git ls-tree`.
- Never hide a missing capability; every stand-in is in the gap report.
- Fixtures are synthetic/demo data, never customer data.
- LLM calls go through `llm.complete`, with the real model. No record/replay.
- Write only inside the bundle, shared Pack modules and the three registrations (workspace, lockfile,
  bundle.yaml parse test).
- Data reads go through the source layer; the node tests run `CraftSource` over the fixture.
- A port is not done until a live run on the local stack succeeds and matches the golden, or the
  gap report says why it could not run.
- Never auto-merge; never add `nojira`.

## Provenance Event Schema

Append each event as a JSON line to `--provenance-file` (if provided):
```json
{"event": "step_start",    "step": "<name>", "timestamp": "<iso>"}
{"event": "step_complete", "step": "<name>", "timestamp": "<iso>", ...extra}
{"event": "step_failed",   "step": "<name>", "timestamp": "<iso>", "error": "<msg>"}
{"event": "gate",          "step": "verify", "gate": "<name>", "passed": true}
{"event": "run_complete",  "outcome": "success|partial|failed", "pr_url": "<url>|null"}
```
Emit `step_start` at the top of every step. The harness waits for `run_complete`; always emit it,
including on failure.
