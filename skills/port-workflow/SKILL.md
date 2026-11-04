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
Step 5   Write shims and stand-ins            shims
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
`.claude/skills/craft-bundle/SKILL.md`. Confirm `$EM_SEMI` is a git checkout, and resolve and
verify the pinned ref (`git -C $EM_SEMI rev-parse --verify "<ref>^{commit}"`).

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
  component only the capabilities its node calls.
- **`inputSchema`** comes from the workflow's inputs and run config. Files get `prefetch`.
- **The report** is the last node's output, plus an app (`apps:` with `runSource.nodeId`) if
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

Lay the bundle out as analog-trim does: `job/` is a uv project, the package is `craft_<slug>`, and
the only runtime dependency is `craft-job-sdk`.

Copy `templates/vendor_workflow.sh.tmpl` to `<bundle>/job/scripts/vendor_workflow.sh` and fill in
the tokens:
- `{{EM_SEMI_REF}}`: the pinned sha.
- `{{SRC_ROOTS}}`: the copy and both modules, as em-semi paths, space-separated. List whole
  packages as directories.
- `{{TEST_ROOTS}}`: the em-semi test paths.
- `{{EXCLUDED_REGEX}}`: the orchestration file(s) only. A large orchestration module that holds
  real logic is **not** excluded; it is vendored as-is.
- `{{VENDOR_PKG}}`: `craft_<slug>.vendor`.
- `{{IMPORT_REWRITES}}`: one `perl` substitution per redirect, e.g.
  `s{^from common_semi\.observe import }{from craft_<slug>.vendor._observe import };`.

Run it.

**Never hand-edit a vendored file.** A platform call inside a module that has to be vendored is
fixed by an import rewrite or by a numbered patch under `<bundle>/job/patches/` (`git diff` →
`000N-<what>.patch`, then re-run the script). Patch equivalence tests go in `job/tests/patches/`,
never in `tests/vendor/`, which a re-vendor wipes.

Emit provenance event: `{"event": "step_complete", "step": "vendor", "files": N, "em_semi_ref": "<sha>"}`

---

## Step 5 — Write Shims and Stand-ins

Write one module per redirect, following the call map. Shims live at the vendor top level
(`vendor/_*.py`; the vendor script preserves them). `CraftContext` and node helpers live in the
package proper. Where craft has a real capability, use it: `JobContext.log` / `progress` / `group`
/ `file_emit` / `resource_read`, and `llm.complete` through `JobContext.llm_complete` for every
LLM call, with the real model and no record/replay.

Where craft has no equivalent yet, write a **fixture-backed stand-in** with em-semi's interface
that reads committed fixtures. It must never return empty data to make a test pass. Put
stand-ins later ports can reuse where they can import them, following craft's Pack conventions.
List every stand-in for the gap report.

Fixtures are em-semi's synthetic/demo test data. **Never real customer lots**, and nothing copied
from a customer environment.

Emit provenance event: `{"event": "step_complete", "step": "shims", "shims": N, "stand_ins": M}`

---

## Step 6 — Write bundle.yaml and Node Modules

Write `<bundle>/bundle.yaml` from the Step 2 plan. Write one thin `craft_<slug>/nodes/<node>.py`
per node: bind inputs, build the context, call vendored functions, return the node output. No
analysis logic lives in nodes.

The bundle must build: `craft bundle build <bundle>` (see craft's `craft-bundle` skill).

Emit provenance event: `{"event": "step_complete", "step": "bundle", "nodes": N}`

---

## Step 7 — Fixtures and Parity Checks

Two layers (see *Parity* in `references/porting-model.md`).

**Static tests**
- The vendored em-semi tests run against the vendored code; they are the oracle. A test that
  already fails at the pinned ref is quarantined by nodeid in `job/tests/conftest.py` with
  `xfail(strict=True)` and listed in the gap report.
- `scripts/make_fixtures.py` and `tests/_golden.py` generate `fixtures/golden-node-outputs.json`
  from craft's own nodes over the fixtures. Fill in `templates/test_golden.py.tmpl` as
  `job/tests/test_<slug>_golden.py` (`{{PKG}}`, `{{NODES}}`). LLM text goes in `LLM_TEXT_PATHS`,
  compared by structure only.
- Fill in `templates/test_vendor_quarantine.py.tmpl` as `job/tests/test_vendor_is_self_contained.py`.
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
- every stand-in
- anything outside the write boundary
- pre-existing em-semi test failures
- evals, ported vs generated
- what was not ported

The skill writes only inside its bundle and shared Pack-level stand-ins. Runner-image packages,
SDK changes and plane changes are **recorded here, not made**.

Emit provenance event: `{"event": "step_complete", "step": "gap_report", "stand_ins": N, "outside_boundary": M}`

---

## Step 9 — Verify

From `<bundle>/job`: `uv run ruff format --check .`, `uv run ruff check .`, `uv run pytest -q`,
then run the evals. Then `craft bundle build <bundle>`. Run
`/verify-and-fix <JIRA-KEY> --gates linter,tests,evals,code-review` with those commands. Fixes go
into craft-side code, shims, stand-ins or patches, **never into vendored files**.

Commit: `[Jira:<KEY>] port(<workflow>): vendor em-semi <sha7>, bundle, parity tests`.

`--stop-after port` or `--no-pr`: emit `run_complete` (`success` if all gates passed, otherwise
`partial`) with `pr_url: null`, and stop.

Emit provenance event: `{"event": "gate", "step": "verify", "gate": "<name>", "passed": true|false}` per gate, then `{"event": "step_complete", "step": "verify"}`

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
- **Pre-existing em-semi test failures** at the pinned ref: quarantine them by nodeid
  (`xfail(strict=True)`), list them in the gap report, and finish `partial` if any are in code
  this workflow uses. Never make them pass by editing vendored code.
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
- Write only inside the bundle and shared Pack stand-ins.
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
