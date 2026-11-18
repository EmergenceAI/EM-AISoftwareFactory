# Port-workflow skill: Factory support for porting em-semi workflows to craft

Date: 2026-11-03
Status: draft, awaiting approval

## Intent

em-semi's analysis workflows (Prefect, running on the em-semi platform) are moving to craft,
the new platform (DBOS runtime, bundles, governed components). One epic covers five workflows:
Cross Product Analysis (CPA), Yield Process Insights (YPI), Yield Excursion v2, Test RCA
(`rca_demo`) and Feedback & Learning. They all go into the same semiconductor Pack as the
already-ported `craft/bundles/analog-trim/`.

We want the EM-AISoftwareFactory to do the porting. **This design covers only the Factory
update**: a new skill, plus the harness and configuration changes that let it run. Running the
five ports is later work, done by invoking the skill. It is not part of this deliverable.

Success for a port is **functional parity**: given the same inputs, the craft workflow produces
the same results as the em-semi one, and that is shown by static tests and evals, not asserted.

## The porting model

craft does not run workflows the way em-semi does, which is why a port is not a plain copy:

| | em-semi | craft |
|---|---|---|
| Orchestration | Prefect `@semi_flow` in `flow.py`, tasks in one worker process | Workflow graph in `bundle.yaml`; each node is a job pod or WASM component |
| Steps | `@semi_task` functions sharing memory | Components exchanging declared inputs/outputs |
| Platform services | Direct imports: `get_database()`, GCS storage, LLM service, Iceberg data views, inbox, `FlowContext` | Declared capabilities (`resource.read`, `file.emit`, `llm.complete`, connectors); everything else blocked |
| Data access | Open network | Inputs prefetched, then network locked |
| Results | DB rows + inbox message | Node output, rendered by a bundle app |

So for one workflow, the skill does three things:

1. **Copies the workflow's Python code into craft unchanged.** Every `.py` file in the
   workflow's em-semi package (and the em-semi tests for it) except `flow.py`.
2. **Rewrites `flow.py` as `bundle.yaml` workflow nodes**, with small node entry-point modules
   that call the copied code.
3. **Swaps each em-semi platform call for its craft equivalent**, through redirected imports to
   small craft-side modules that keep em-semi's names and interfaces.

### Reference: how analog-trim was done

`craft/bundles/analog-trim/` is the worked example, and the skill must follow its approach.
Read it, and its design doc at
`craft/docs/superpowers/specs/2026-09-15-analog-trim-port-and-workflow-ui-design.md`.

- `job/scripts/vendor_trim_opt.sh` copies em-semi's `workflow/app/trim_optimization/` (minus
  `flow.py`) and its tests into `job/src/craft_trim/vendor/` and `job/tests/vendor/`. It reads
  through `git show <ref>:<path>`, never a checkout, from a **pinned em-semi commit**
  (`EM_SEMI_REF` defaults to a fixed sha, bumped deliberately in its own commit).
- The only changes to copied code are **mechanical import rewrites (sed) plus a numbered patch
  series** in `job/patches/`. Hand edits to vendored files are forbidden; that is what keeps the
  parity claim checkable and a re-vendor reproducible.
- Shims (`vendor/_flows.py`, `_observe.py`, `_run_config.py`, `_report_models.py`, `_otel.py`)
  stand in for em-semi platform modules. `craft_trim/context.py` (`CraftContext`) gives the
  copied code `FlowContext`'s method names, backed by the craft job SDK.
- `bundle.yaml` declares the components (job and WASM), the workflow DAG (including a fan-out),
  `inputSchema`, and an app that renders the report.
- Parity evidence: em-semi's own tests run against the vendored code; golden node outputs and a
  golden report (generated from craft's nodes) are compared in tests and CI; equivalence tests
  cover the patches; quarantine tests keep the vendor tree self-contained. Analog-trim has no LLM
  steps and no evals; the skill adds evals (see step 7).

### Missing craft capabilities

The remaining workflows depend on em-semi platform pieces craft does not provide yet. Examples:
Iceberg/DuckDB data views (CPA, YPI, Yield Excursion), product catalog and attributes (CPA),
sandboxed agent SQL (Test RCA), knowledge update and guardrails (Feedback & Learning), and
DB-backed queues. These are being built as separate tracks (data ingestion is its own epic).
**Ports do not wait for them.** Instead:

- The skill puts each such dependency behind a **narrow craft-side interface that keeps
  em-semi's shape**.
- Until the real craft capability exists, that interface is backed by a **stand-in that reads
  fixture data** committed in the bundle. Parity is proven against fixtures.
- Stand-ins are written so they can be reused by later ports (e.g. the data-view stand-in built
  for CPA is reused by YPI and Yield Excursion).
- Every stand-in is recorded as an **open dependency** in a gap report (below), so missing
  platform work stays visible. When the real capability lands, the interface is switched over
  without touching workflow code, and parity is checked again on real data.

Fixture data comes from the synthetic/demo data em-semi's tests and demos already use. **Never
real customer lots.**

## Goals

- A `port-workflow` skill in the Factory that takes an em-semi workflow name and produces a craft
  PR with the ported workflow, parity tests, and a gap report.
- Usable both interactively (`/port-workflow <name>` with the Factory plugin loaded) and
  headlessly through the harness.
- Follows the analog-trim approach: unchanged copy, pinned ref, mechanical rewrites and patches
  only, shims, `bundle.yaml` orchestration, em-semi tests as the parity oracle.
- Fits the Factory's existing conventions: `SKILL.md` format, fully autonomous (no confirmation
  prompts), provenance events, `/verify-and-fix` gates, `/create-pr`.

## Non-goals

- Running the five ports. That happens after this lands.
- Building the missing craft platform capabilities (data views, sandboxed SQL, knowledge
  approval, ingestion). The skill stubs and reports them; it does not build them.
- Porting em-semi's chat/agent side (agent profiles, MCP skills). Analog-trim did not either.
- Deleting or changing anything in em-semi. em-semi is read-only to this skill.

## Anti-goals (would be a failure even if it "works")

- Rewriting the analysis code as a fresh craft-native implementation. That breaks the parity
  claim.
- Hand-editing vendored files, or making changes that a re-run of the vendor script would
  silently wipe.
- Hiding a missing capability, e.g. a stand-in that returns empty data so tests pass, or a
  dependency that isn't recorded in the gap report.
- Copying from em-semi's moving `main` without a pin.
- Using real customer data as fixtures.
- Auto-merging into craft.

## What gets built

### 1. `skills/port-workflow/`

```
skills/port-workflow/
  SKILL.md
  references/
    porting-model.md        # the em-semi -> craft mapping table and rules above
    analog-trim-walkthrough.md   # what each analog-trim file does and why; points at the real files
    platform-call-map.md    # em-semi platform module -> craft equivalent | shim | stand-in
    gap-report-template.md
  templates/                # optional: vendor script, shim and test skeletons
```

`SKILL.md` frontmatter: `name: port-workflow` and a `description`. The body follows the
`integrate-prototype` style: Usage, Parameters, Process Flow, then one section per step, each
ending with its provenance event.

**Parameters**

- `<workflow>` / `--workflow-name <name>` (required): the em-semi workflow, by its package or
  spec name (e.g. `cross_product_analysis`).
- `--em-semi-ref <sha>` (optional): em-semi commit to pin. Default: em-semi `origin/main`
  resolved to a sha at run start, then recorded as the pin.
- `--target-bundle <path>` (optional): where in craft the port lands.
- `--jira-key <KEY>` (**required**): craft's `CLAUDE.md` requires a Jira task for all work, and
  commit and PR titles must start with `[Jira:KEY]` (enforced by `pr-title.yml`). The skill
  never adds the `nojira` label.
- `--context-file`, `--provenance-file`, `--branch` (optional): same meaning as in
  `integrate-prototype`.

**Steps** (the skill runs in the craft repo; it reads em-semi via `git show`)

0. Load context (craft knowledge pack, references).
1. **Locate and map** the em-semi workflow. Find its orchestration module from its
   `workflow_specs/` entry, then its package, its tests and its full import closure. Not every
   workflow is "a package with a `flow.py`" (see *Workflow shapes* below). Classify every import as
   *inside the workflow* (copy), *shared em-semi analysis code* (copy too), or *em-semi platform*
   (redirect). Write this as an inventory.
2. **Plan the craft shape** from `flow.py`: stages become nodes; loops over independent items
   become fan-outs; decide job vs WASM per node (job is the default for Python); define
   `inputSchema` from the workflow's inputs.
3. **Create a branch** in craft.
4. **Write the vendor script** (modelled on `vendor_trim_opt.sh`) with the pinned ref, and run
   it. It copies code and tests and applies the import rewrites.
5. **Write shims and stand-ins** for every platform import, per `platform-call-map.md`. Real
   craft equivalents where they exist (e.g. `llm.complete` for LLM calls, job SDK for
   logging/progress/artifacts); fixture-backed stand-ins where they don't.
6. **Write `bundle.yaml`** (components, workflow, inputSchema, app if the workflow has a report)
   and the node entry-point modules.
7. **Build fixtures and parity checks** (decided: follow the analog-trim model, with two layers):
   - **Static tests.** Vendor em-semi's own tests for the workflow and run them against the
     vendored code (the oracle). Then generate golden node outputs by running *craft's* nodes on
     the fixture data, as analog-trim's `make_fixtures.py` and `tests/_golden.py` do, and compare
     against them in tests and CI. Add quarantine tests that keep the vendor tree self-contained.
     em-semi itself is not run.
   - **Evals.** Port em-semi's existing eval suites for the workflow where they exist
     (`workflow/tests/eval_harness/`, `workflow/app/evaluation/`, `workflow/app/rca_agent/eval/`,
     `workflow/app/excursion_scripts/eval/`) and run them against the craft workflow's outputs.
     Where a workflow has no eval suite, generate one from its spec and em-semi behaviour (as the
     Factory's `eval-generator` does from acceptance criteria) and say so in the gap report.
   - **LLM steps** (decided): call the real model through craft's `llm.complete`; no
     record/replay. Their outputs are not compared exactly. Static tests check structure, and
     evals judge quality and correctness.
8. **Write the gap report**: every stand-in, what real craft capability it waits for, which
   tests would need re-running on real data, and anything the skill could not port.
9. **Verify**: `/verify-and-fix` with craft's lint and test commands; the bundle must build
   (`craft bundle build`; see craft's `craft-bundle` skill).
10. **Open a PR** to craft with the gap report in the description. No auto-merge.
11. Update Jira if `--jira-key` was given; emit `run_complete`.

If a step cannot be completed (e.g. em-semi tests fail at the pinned ref, or the workflow uses
something with no reasonable stand-in), the skill stops, records why in the gap report, and
still opens a draft PR with what it has and `outcome: partial`.

**Workflow shapes** (my call). The skill must handle all five target workflows, not only the
analog-trim shape:

- Package with `flow.py` (CPA, YPI, trim): as analog-trim.
- Flow in a separate module, with a package next to it (Test RCA: `workflows_v2/rca_demo.py` +
  `rca_demo/`, tests inside the package).
- A large orchestration module that also holds real logic (Yield Excursion v2:
  `workflows_v2/yield_excursion_v2.py`, 1.7k lines; Feedback & Learning:
  `workflows/feedback_learning.py`). Vendor the module as-is, and replace only the Prefect
  orchestration with node entry points that call into it. Do not rewrite it.
- **Where copying stops:** copy everything in the import closure that is analysis code, including
  shared modules under `app/` and analysis parts of `common_semi`. Redirect anything that talks
  to em-semi's platform (DB, storage, data views/Iceberg, LLM service, inbox, feature flags,
  observability). When a module does both, vendor it and fix the platform calls through import
  rewrites or patches, never hand edits. The inventory in step 1 records which side every module
  falls on.

**Write boundary** (my call). The skill writes only inside its target bundle, plus shared
Pack-level stand-ins. It does not change craft's planes, SDKs or runner images. If a port needs
one of those (e.g. a new runner-image dependency like duckdb or pyiceberg, or a plane change like
analog-trim's presign work), the skill records it in the gap report and finishes as `partial`
where it blocks.

### 2. Register craft in the Factory

- `workspace.yaml`: add a `craft` repository entry (path `craft`, github, build system, test
  framework, Jira component) and its Jira component mapping.
- `sync_knowledge.sh`: add craft to `REPOS`; run `extract_knowledge.sh` to generate
  `knowledge/repositories/craft/`.
- A craft adapter (`adapters/craft.py`) only if the live path needs one. Today adapters are used
  by `harness/planner.py` only, not by `implement`.

### 3. Harness: run a skill other than `/autonomous-implement`

`harness/executor.py` hard-codes the `/autonomous-implement {issue_key}` prompt in
`execute_with_provenance` (and `_invoke_skill_via_subprocess`). Generalise this so the executor
can launch a given skill with arguments, keeping everything else (knowledge context file,
provenance monitor, watchdog, checkpoint, timeout, `run_complete` handling) the same.

Add a CLI entry point, e.g.

```
python -m harness port <workflow> [--em-semi-ref SHA] [--jira-key KEY] [--branch NAME]
```

It routes straight to the craft repo (no Jira routing needed) and launches `/port-workflow`.
The existing `implement` path must behave exactly as before.

## Acceptance

The Factory update is done when:

- `/port-workflow` exists, follows the conventions above, and its references capture the
  porting model and the analog-trim walkthrough.
- craft is registered and has a knowledge pack.
- `python -m harness port <workflow>` launches the skill in craft with provenance tracking, and
  `python -m harness implement` is unchanged (existing tests pass).
- **Dry run against analog-trim** (my call): run the skill on `trim_optimization` into a
  throwaway branch and compare what it produces with the hand-built
  `craft/bundles/analog-trim/`. The point is not an identical result. The point is that it picks
  the same structure (copied tree, pinned ref, shims for the same platform modules, comparable
  node split) and its parity tests pass. Nothing from this dry run is merged.
- **Mapping-only check on Yield Excursion v2** (my call): run steps 0–2 on Yield Excursion v2 and
  review its inventory and node plan. This covers the hardest shape that the trim dry run does
  not.

## Left to the builder

- Exact wording and layout of `SKILL.md` and its references.
- Whether reusable stand-ins live in a shared location in the Pack or per bundle (pick what
  keeps later ports from duplicating them; follow craft conventions).
- Whether each ported workflow is its own bundle directory or shares one with analog-trim. Check
  how craft defines a Pack versus a bundle and follow that.
- How the harness generalisation is shaped (parameterised prompt vs a new `execute_skill`
  method), as long as `implement` is unaffected.
- Tolerances for golden comparisons (analog-trim uses 1e-6 relative for node outputs).
- How ported evals are run in craft (harness, LLM judge model, pass thresholds), following what
  em-semi's eval suites already do.

## Context for later ports (not part of this deliverable)

Suggested order, easiest first, so each port reuses the stand-ins of the one before:
CPA → YPI → Yield Excursion v2 → Test RCA → Feedback & Learning.
