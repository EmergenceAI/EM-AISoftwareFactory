---
name: run-code-review
description: Run a focused code review for blockers only and write a structured JSON result to --output
---

# Run Code Review

Run a focused parallel code review on the current branch diff, extracting only **blockers** (bugs, security issues, linter errors, failing tests). Write a structured JSON result to `--output` for the harness.

This is a harness-optimised variant of `/code-review`. Suggestions and nits are collected but do not affect the `passed` verdict.

**The target repo's own review rules win.** If the repo ships its own reviewer (review lens agents plus a review contract — e.g. Craft's `craft-review`), this skill runs that reviewer (Step 2A). Otherwise it runs the generic agents with the repo's review rules attached (Step 2B). Either way the JSON output schema is identical.

## Usage

```bash
# Called by the harness
/run-code-review --output .harness-results/code-review.json

# With the harness knowledge context file (supplies the Review Rules section)
/run-code-review --output .harness-results/code-review.json --context-file .knowledge_context_craft.md

# Standalone (prints full review, no output file)
/run-code-review
```

### Parameters

- `--output <path>`: File path to write the JSON result.
- `--context-file <path>` *(optional)*: Harness knowledge context file. If omitted, use the repo root's `.knowledge_context_*.md` if one exists.

---

## Instructions

### Step 1: Determine diff scope

```bash
# On a feature branch — review all changes vs main
git diff main...HEAD

# On main — review staged changes
git diff --staged

# Fallback — latest commit
git show HEAD
```

### Step 2: Choose the reviewer

The repo **has its own reviewer** when it contains both:
- one or more `.claude/agents/review-*.md` lens agents, and
- a review contract: `.claude/skills/<name>/contract.md` for a review skill (e.g. `.claude/skills/craft-review/`), usually with `units/*.md` rule files and a `REVIEW.md` at the root.

If it does → **Step 2A**. Otherwise → **Step 2B**.

### Step 2A: Run the repo's own reviewer

Follow the repo's review skill (`.claude/skills/<name>/SKILL.md`) and contract, adapted for the harness:

1. **Collect inputs** into a scratch dir outside the repo (`SCRATCH=$(mktemp -d)`):
   ```bash
   git fetch -q origin main
   git diff origin/main > "$SCRATCH/diff.patch"            # committed + uncommitted
   git diff --name-only origin/main > "$SCRATCH/files.txt"
   { git branch --show-current; echo; git log --format='%s%n%n%b' origin/main..HEAD; } > "$SCRATCH/description.md"
   ```
   If the Jira ticket summary/acceptance criteria are known, append them to `description.md`. If the diff is empty, write a passing result and stop.
2. **Work out the units** the way the repo's skill says (Craft: the first directory of each path in `files.txt`; `repo-wide` always applies).
3. **Launch in a single parallel call:**
   - **Agent 1 — Test & Linter Runner** (as in Step 2B), and
   - **every** `.claude/agents/review-*.md` lens, with `subagent_type` set to the agent's name (skip any lens the repo's skill says to skip, e.g. `review-performance` for a docs/config-only diff). If a lens is not available as a subagent type, run a `general-purpose` agent told to read that agent file and follow it read-only.

   Give each lens exactly what the contract names:
   ```
   Review this change as your lens, following <contract path> exactly.
   - Diff: <SCRATCH>/diff.patch
   - Tree (read-only): <repo root>
   - Title and description: <SCRATCH>/description.md
   - Units: <units, including repo-wide>
   Return only the findings list, or exactly "No findings."
   ```
4. **Merge and verify** — you are the main reviewer; lenses never decide the verdict:
   - merge duplicates (same defect, same `file:line`), keeping the most severe severity;
   - **verify every `important` finding yourself**: open the cited `file:line` and confirm the defect from the code. Downgrade to `nit` (or drop) one you cannot confirm — a false blocker sends the fix loop chasing nothing;
   - apply the repo's `REVIEW.md` (e.g. at most five nits, pre-existing never charged to the author, nothing CI already catches).
5. **Map severities** into the Step 4 schema:

   | Repo severity | JSON list | `severity` |
   |---|---|---|
   | `important` | `blockers` | `HIGH` |
   | `nit` | `suggestions` | `LOW` |
   | `pre_existing` | `suggestions` (title prefixed `[pre-existing]`) | `LOW` |

   `category`: `security` for review-security, `performance` for review-performance, `quality` for review-repo-invariant, `correctness` for the rest. `description` = the lens's evidence plus `(lens: <agent name>)`. Agent 1 failures are blockers as usual. `agents_run` = `test-runner` plus the lens names.

Delete the scratch dir, then continue at **Step 4** (Step 3's triage is already done by the mapping).

### Step 2B: Generic review — assess diff size and launch parallel agents

**Review rules.** Read the `## Review Rules` section of the context file (if any), plus the repo's `REVIEW.md` and the `CLAUDE.md` files for the touched directories. Pass that text to every reviewer agent (2–6) with this instruction: *"A diff that breaks a rule marked **I** (Important), or a `CLAUDE.md` rule, is a blocker — cite the rule and the `file:line`. **N** rules are suggestions."*

**Small diff** (≤100 lines / ≤3 files): launch agents 1–4 only.
**Medium/large diff** (>100 lines or >3 files): launch all agents.

Launch in a single parallel call:

- **Agent 1 — Test & Linter Runner**: run tests and linter for changed files; report failures
- **Agent 2 — Code Reviewer**: up to 5 issues ranked by impact; focus on bugs and incorrect logic
- **Agent 3 — Security Reviewer**: injection, auth, secrets, error-handling leaks
- **Agent 4 — Quality Reviewer**: complexity, dead code, architectural pattern violations
- **Agent 5 — Performance Reviewer** *(large diff only)*: N+1, blocking ops, memory leaks
- **Agent 6 — Dependency Reviewer** *(large diff only)*: new deps, API contract breaks, deployment safety

### Step 3: Triage findings into blockers vs suggestions

**Blockers** (anything that must be fixed before merge):
- Bugs or logic errors that fail in production
- Security vulnerabilities with a realistic exploit path
- Linter errors (not warnings)
- Failing tests surfaced by Agent 1
- Clear architectural violations from the project style guide
- A violated **I** (Important) review rule or `CLAUDE.md` rule for a unit the diff touches

**Suggestions**: everything else (style, minor performance, nice-to-haves).

### Step 4: Write JSON result to --output

```json
{
  "passed": true,
  "verdict": "Approve",
  "blockers": [],
  "suggestions": [
    {
      "severity": "MED",
      "category": "quality",
      "title": "Redundant null check",
      "file": "src/api/handler.py",
      "line": 88,
      "description": "Variable is never null at this point — check is dead code."
    }
  ],
  "agents_run": ["test-runner", "code-reviewer", "security-reviewer", "quality-reviewer"],
  "diff_stats": { "files_changed": 3, "lines_added": 87, "lines_removed": 12 }
}
```

Failure example:

```json
{
  "passed": false,
  "verdict": "Needs Work",
  "blockers": [
    {
      "severity": "HIGH",
      "category": "security",
      "title": "SQL injection via unsanitised input",
      "file": "src/db/queries.py",
      "line": 34,
      "description": "user_id is interpolated directly into the SQL string. Use parameterised queries."
    },
    {
      "severity": "HIGH",
      "category": "correctness",
      "title": "Off-by-one in pagination",
      "file": "src/api/list.py",
      "line": 71,
      "description": "offset = page * limit should be offset = (page - 1) * limit; page 1 skips first item."
    }
  ],
  "suggestions": [],
  "agents_run": ["test-runner", "code-reviewer", "security-reviewer", "quality-reviewer"],
  "diff_stats": { "files_changed": 5, "lines_added": 210, "lines_removed": 45 }
}
```

**`passed` is `true` only when `blockers` is empty.**

### Step 5: Print summary

```
🔎 Code review (4 agents)
   Blockers: 0  |  Suggestions: 1
   Verdict: ✅ Approve
```

---

## Output Schema

```json
{
  "passed": true | false,
  "verdict": "Approve | Needs Work",
  "blockers": [
    {
      "severity": "HIGH | MED | LOW",
      "category": "security | correctness | performance | quality",
      "title": "...",
      "file": "src/...",
      "line": 42,
      "description": "..."
    }
  ],
  "suggestions": [ ... ],
  "agents_run": ["..."],
  "diff_stats": { "files_changed": 0, "lines_added": 0, "lines_removed": 0 }
}
```

## Calibration

- **Only blockers affect `passed`** — suggestions are recorded but don't gate the loop.
- Calibrate severity as a senior engineer would: internal tooling, controlled inputs, and low-blast-radius code get lower severity than user-facing authentication or payment flows.
- Do not include nits or style preferences in blockers.

## Exit Behaviour

- Exit 0 when `passed == true`.
- Exit 1 when `passed == false`.
- Always write the result file.
