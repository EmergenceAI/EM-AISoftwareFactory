# Porting model: em-semi workflow → craft bundle

The binding source is the design doc
`docs/superpowers/specs/2026-11-03-port-workflow-skill-design.md` in the Factory. This file is the
working summary the skill follows.

## Why a port is not a plain copy

| | em-semi | craft |
|---|---|---|
| Orchestration | Prefect `@semi_flow` (in `flow.py` or a `workflows*/` module), tasks in one worker process | Workflow graph in `bundle.yaml`; each node is a job pod or WASM component |
| Steps | `@semi_task` functions sharing memory | Components exchanging declared inputs/outputs |
| Platform services | Direct imports: `get_database()`, GCS storage, LLM service, Iceberg data views, inbox, `FlowContext` | Declared capabilities on `JobContext` (`resource_read`, `file_emit`, `data_query`, `llm_complete`, `ledger_*`, …); everything else blocked |
| Data access | Open network | Inputs prefetched (`prefetch:`), then network locked |
| Results | DB rows + inbox message | Node output, rendered by a bundle app (`apps:` + `runSource`) |

## The three jobs

1. **Copy the workflow's code unchanged.** Every module in the workflow's import closure that is
   analysis code, plus em-semi's tests for it, via a vendor script reading `git show <ref>:<path>`
   at a pinned sha. Only the Prefect orchestration is left out.
2. **Rewrite the orchestration as `bundle.yaml`.** Stages become nodes; loops over independent
   items become fan-outs; the workflow's inputs become `inputSchema`. Small node entry-point
   modules (`<pkg>/nodes/<node>.py`, `entrypoint: <pkg>.nodes.<node>:run`) call the vendored code.
3. **Swap every em-semi platform call** for its craft equivalent through import rewrites in the
   vendor script, pointing at shims/stand-ins that keep em-semi's names and signatures. See
   `platform-call-map.md`.

## Workflow shapes

Find the orchestration module from the workflow's `workflow/app/workflow_specs/` entry; do not
assume `flow.py`.

| Shape | Examples | How to port |
|---|---|---|
| Package with `flow.py` | CPA (`cross_product_analysis/`), YPI (`yield_process_insights/`), trim (`trim_optimization/`) | Exactly as analog-trim: vendor the package minus `flow.py` |
| Flow module beside a package | Test RCA: `workflows_v2/rca_demo.py` + `rca_demo/` (tests inside the package) | Vendor the package (with its in-package tests); the flow module is the orchestration |
| Large orchestration module with real logic | Yield Excursion v2: `workflows_v2/yield_excursion_v2.py` (1.7k lines); Feedback & Learning: `workflows/feedback_learning.py` | Vendor the module **as-is**. Node entry points call its functions. Only the `@semi_flow` function itself is replaced by `bundle.yaml` wiring. Never rewrite it |

## Where copying stops

Classify every module in the import closure (this is the step-1 inventory):

- **copy**: analysis code — the workflow package, shared analysis modules under `app/`, the
  analysis parts of `common_semi` (schemas, pure data transforms).
- **redirect**: anything that talks to em-semi's platform — DB, storage, data views / Iceberg,
  LLM service, inbox, feature flags, observability, run config, Prefect.
- **both**: a module that does analysis *and* platform calls. Vendor it, and fix the platform
  calls through import rewrites or a numbered patch. Never by hand.

## Rules (from the spec's anti-goals)

- **Never hand-edit a vendored file.** Changes come only from the vendor script's mechanical
  import rewrites and numbered patches in `patches/`. A re-vendor wipes hand edits silently and
  voids the parity claim.
- **Never rewrite analysis code** as fresh craft-native code, including large orchestration
  modules.
- **Always pin** the em-semi ref in the vendor script (`EM_SEMI_REF` default = a sha). Never copy
  from a moving `main`. Read through `git show`, never a checkout; em-semi is read-only.
- **Never hide a missing capability.** A stand-in that returns empty data so tests pass is a
  failure. Every stand-in is listed in the gap report.
- **Fixtures are em-semi's synthetic/demo test data. Never real customer lots.**
- **Never auto-merge**, never add `nojira`.

## Write boundary

The skill writes only inside its target bundle and shared Pack-level stand-ins. It does not change
craft's planes, SDKs or runner images (`compute-plane-python/python-runner/requirements.txt`,
`Dockerfile.toolchain`). A port that needs one of those records it under *Outside write boundary*
in the gap report and finishes `partial` where it blocks.

## Missing craft capabilities: stand-ins

When a platform call has no craft equivalent yet:

1. Define a narrow interface that keeps em-semi's shape (same function names, arguments, return
   types the vendored code uses).
2. Back it with a **fixture-backed stand-in** reading committed fixture files (Parquet/CSV/JSON)
   from the bundle's `fixtures/`.
3. Put reusable stand-ins where later ports can import them (follow craft's Pack conventions) so
   CPA's data-view stand-in serves YPI and Yield Excursion too.
4. Record it in the gap report: interface, stand-in file, craft capability needed, tests to re-run
   on real data.

When the real capability lands, the interface is switched over without touching workflow code.

## Parity: two layers

1. **Static tests**, analog-trim style:
   - em-semi's own tests, vendored, run against the vendored code (the oracle). Known pre-existing
     failures at the pinned ref are quarantined by nodeid in `conftest.py` with
     `xfail(strict=True)` and listed in the gap report, never fixed by editing vendored code.
   - Goldens generated **from craft's own nodes** over the fixtures (`scripts/make_fixtures.py` +
     `tests/_golden.py` pattern), compared in tests and CI (`rel_tol=1e-6` default).
   - Self-containment/quarantine tests: vendored code imports nothing outside the vendor package,
     the shims, and the runner image's packages.
   - em-semi itself is never run.
2. **Evals**: port em-semi's existing eval suites for the workflow where they exist
   (`workflow/tests/eval_harness/`, `workflow/app/evaluation/`, `workflow/app/rca_agent/eval/`,
   `workflow/app/excursion_scripts/eval/`) and run them against the craft workflow's outputs.
   Where none exist, generate one from the workflow's spec and em-semi behaviour, and say so in the
   gap report.

**LLM steps** call the real model through craft's `llm.complete` (`JobContext.llm_complete`). There
is no record/replay. LLM output is never compared exactly. Static tests check its structure, and
evals judge its quality and correctness.
