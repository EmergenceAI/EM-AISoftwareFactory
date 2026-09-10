# TODO

Backlog of tasks, improvements, and areas to investigate for the Dark Factory.

---

## Literature & Projects to Review

- [ ] https://github.com/kubestellar/hive
- [ ] https://github.com/snarktank/ralph-loop
- [ ] https://github.com/shadcn/improve
- [ ] Claude Code dynamic workflows — multi-agent orchestration harness built into Claude Code (`Workflow` tool, `pipeline()`, `parallel()`, `phase()`); evaluate for replacing the current Python harness loop with a declarative workflow script
- [ ] https://github.com/paperclipai/paperclip — plant management; review for patterns applicable to factory floor scheduling and resource orchestration
- [ ] [Why Software Factories Fail — Dex Horthy, HumanLayer](https://www.developersdigest.tech/blog/software-factories-fail-harness-engineering) — harness engineering is necessary but not sufficient; models lack reliable mechanisms to optimise for maintainability; feedback loop and human-in-the-loop arguments directly relevant to dark factory design
- [ ] [Harness Engineering — OpenAI, Feb 2026](https://openai.com/index/harness-engineering/) — OpenAI shipped ~1M LOC / 1,500 PRs with 3 engineers using Codex + a well-designed harness; treats `AGENTS.md` as a table of contents pointing to a structured `docs/` knowledge base; 88 AGENTS.md files across subcomponents in monorepo

---

## Features & Improvements

### Spec Creation Superpowers

- [ ] **Semantic codebase indexing (RAG)** — embed the codebase for vector search so `/research-codebase` surfaces relevant patterns without knowing the right grep terms
- [ ] **Cross-repo impact analysis** — automatically surface blast radius (SDK, downstream services, contracts) before implementation starts
- [ ] **Contract-first spec validation** — validate the spec against live OpenFGA schema, OpenAPI contracts, and Alembic migration state at plan time, not gate time
- [ ] **Historical PR pattern mining** — mine merged PRs for team patterns and inject into the spec context alongside static knowledge docs

### Harness Architecture

- [ ] **Migrate gate loop to Claude Code Workflow script** — replace the imperative Python loop in `harness/harness.py` with a declarative `Workflow` script using `pipeline()` and `parallel()`; gets parallelism, observability, and resume for free from the Claude Code runtime instead of hand-rolling it

### Implementation Superpowers

- [ ] **Parallel file-level implementation (worktree fan-out)** — fan out N agents per module (entity, router, service, tests), merge results; reduces wall-clock to slowest single step
- [ ] **Live incremental test loop** — run relevant unit tests after each file write during implementation, not just at gate time
- [ ] **Automatic migration generation** — when spec adds/changes a SQLAlchemy entity, auto-run `alembic revision --autogenerate` and include the migration in the plan
- [ ] **Knowledge base self-update after merge** — after a PR merges, extract new patterns and update `knowledge/` so each successful run improves future runs

---

## Known Gaps

*(Tracked issues that aren't yet Jira tickets)*
