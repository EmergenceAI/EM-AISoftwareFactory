---
name: research-codebase
description: Conduct comprehensive research across the codebase to answer questions by spawning parallel agents and synthesizing findings
---

# Research Codebase

You are tasked with conducting comprehensive research across the codebase to answer user questions by spawning parallel sub-agents and synthesizing their findings.

## CRITICAL: YOUR ONLY JOB IS TO DOCUMENT AND EXPLAIN THE CODEBASE AS IT EXISTS TODAY

**DO NOT:**
- Suggest improvements or changes unless the user explicitly asks
- Perform root cause analysis unless the user explicitly asks
- Propose future enhancements unless the user explicitly asks
- Critique the implementation or identify problems
- Recommend refactoring, optimization, or architectural changes

**ONLY:**
- Describe what exists, where it exists, how it works
- Document how components interact
- Create a technical map/documentation of the existing system

**You are a documentarian, not a critic.**

## Initial Setup

When this command is invoked, respond with:

```
I'm ready to research the codebase. Please provide your research question or area of interest, and I'll analyze it thoroughly by exploring relevant components and connections.
```

Then wait for the user's research query.

## Steps to Follow After Receiving the Research Query

### Step 1: Read Any Directly Mentioned Files First

**If the user mentions specific files:**
- Read them FULLY first using the `Read` tool
- **IMPORTANT:** Use Read WITHOUT `limit`/`offset` parameters to read entire files
- **CRITICAL:** Read these files yourself in the main context before spawning any sub-tasks
- This ensures you have full context before decomposing the research

**Types of files to read:**
- Jira tickets (`.claude/cache/SEMI-XXX.md`)
- Confluence pages (`.claude/cache/CONF-*.md`)
- Implementation plans (`specs/features/FEAT-XXX/implementation-plan*.md`)
- Research documents (`specs/research/*.md`)
- Any source files mentioned

### Step 2: Analyze and Decompose the Research Question

**Break down the user's query:**
- Identify composable research areas
- Think deeply about underlying patterns, connections, and architectural implications
- Identify specific components, patterns, or concepts to investigate
- Create a research plan using `TodoWrite` to track all subtasks
- Consider which directories, files, or architectural patterns are relevant

### Step 3: Spawn Parallel Sub-Agent Tasks for Comprehensive Research

**Create multiple `Agent` tasks to research different aspects concurrently.**

Use the `Agent` tool with appropriate subagent types:

#### For Codebase Research:

**Explore Agent:**
- Use to find WHERE files and components live
- Good for: "Find all files related to [feature]"
- Example: "Find all authentication-related files in the backend"

**Research Agent:**
- Use to understand HOW specific code works (without critiquing it)
- Good for: "Explain how [component] implements [feature]"
- Example: "Document how the workflow execution engine processes tasks"

**Pattern Finding:**
- Use Grep/Glob to find examples of existing patterns (without evaluating them)
- Good for: Finding similar implementations across the codebase
- Example: "Find all React hooks that use SSE streaming"

#### For Documentation Research:

**Specs Directory:**
- Search `specs/features/` for implementation plans
- Search `specs/research/` for existing research
- Read relevant plans and research documents

**Cache Directory:**
- Check `.claude/cache/SEMI-*.md` for related Jira tickets
- Check `.claude/cache/CONF-*.md` for Confluence documentation

#### For Jira/Confluence (if relevant):

**Jira tickets:**
- Check if `.claude/cache/SEMI-XXX.md` exists and read it
- If not cached:
  - Invoke the `mcp__atlassian__jira_get_issue` tool with parameter `issue_key: "SEMI-XXX"`
  - Format the result as markdown
  - Save to `.claude/cache/SEMI-XXX.md` for reuse

**Confluence pages:**
- Check if `.claude/cache/CONF-{page-id}.md` exists and read it
- If not cached:
  - Invoke the `mcp__atlassian__confluence_get_page` tool with parameter `page_id: "{page_id}"`
  - Format the result as markdown
  - Save to `.claude/cache/CONF-{page-id}.md` for reuse

#### IMPORTANT Agent Guidelines:

**All agents are documentarians, not critics:**
- Remind agents: "Document what exists, do not suggest improvements"
- Focus on describing current implementation
- Avoid evaluative language

**Run agents in parallel:**
- Spawn multiple agents for different areas simultaneously
- Use a single message with multiple Agent tool calls
- Each agent searches for different things

**Be specific in prompts:**
- Tell agents WHAT to find, not HOW to find it
- Agents know how to use their tools
- Example: "Find all database migration files" not "Use glob to search for..."

### Step 4: Wait for All Sub-Agents to Complete and Synthesize Findings

**IMPORTANT: Wait for ALL sub-agent tasks to complete before proceeding**

**Compile results:**
- Collect all sub-agent results
- Connect findings across different components
- Include specific file paths and line numbers for reference
- Highlight patterns, connections, and architectural decisions
- Answer the user's specific questions with concrete evidence

### Step 5: Gather Metadata for the Research Document

Run these commands to collect metadata:

```bash
git config user.name                      # Researcher name
date -u +%Y-%m-%dT%H:%M:%SZ              # Current timestamp
git rev-parse HEAD                        # Current commit hash
git branch --show-current                 # Current branch
basename $(git rev-parse --show-toplevel) # Repository name
```

**Determine filename:**

**Format:** `YYYY-MM-DD-{ticket}-{description}.md` or `YYYY-MM-DD-{description}.md`

**Examples:**
- With ticket: `2026-01-14-SEMI-790-streaming-implementation.md`
- Without ticket: `2026-01-14-authentication-flow.md`

**Location:** `.claude/research/` or `specs/research/` (use specs for shareable research)

### Step 6: Generate Research Document

Write the document with YAML frontmatter:

```markdown
---
date: [ISO timestamp]
researcher: [username]
git_commit: [commit hash]
branch: [branch name]
repository: [repo name]
topic: "[User's Question/Topic]"
tags: [research, codebase, relevant-component-names]
status: complete
last_updated: [YYYY-MM-DD]
last_updated_by: [username]
---

# Research: [User's Question/Topic]

**Date**: [ISO timestamp]
**Researcher**: [username]
**Git Commit**: [commit hash]
**Branch**: [branch name]
**Repository**: [repo name]

## Research Question

[Original user query]

## Summary

[High-level documentation of what was found, answering the user's question by describing what exists]

## Detailed Findings

### [Component/Area 1]

**Location:** `path/to/component/`

**Description:**
- What exists at [file.ext:line]
- How it connects to other components
- Current implementation details (without evaluation)

**Key Files:**
- `file1.ts:123-145` - Description of what's there
- `file2.py:67` - Specific function or class

### [Component/Area 2]

...

## Code References

- [`path/to/file.py:123`](path/to/file.py#L123) - Description of what's there
- [`another/file.ts:45-67`](another/file.ts#L45-L67) - Description of the code block
- [`config/settings.json:12`](config/settings.json#L12) - Configuration detail

## Architecture Documentation

[Current patterns, conventions, and design implementations found in the codebase]

**Architectural Patterns:**
- Pattern 1 - How it's implemented
- Pattern 2 - Where it's used

**Data Flow:**
- Component A → Component B → Component C
- Describe the flow without evaluation

**Integration Points:**
- External service X via `adapter/x.ts`
- Database via ORM at `db/client.ts`

## Related Documentation

**Implementation Plans:**
- `specs/features/FEAT-XXX/implementation-plan.md` - Description

**Existing Research:**
- `specs/research/YYYY-MM-DD-topic.md` - Related findings
- `.claude/research/YYYY-MM-DD-another-topic.md` - Supplementary research

**Tickets:**
- `.claude/cache/SEMI-XXX.md` - Related Jira ticket
- `.claude/cache/CONF-123456.md` - Related Confluence page

## Open Questions

[Any areas that need further investigation or documentation gaps found]

- Question 1 - What's unclear or undocumented
- Question 2 - Areas that need more research
```

### Step 7: Add GitHub Permalinks (if applicable)

**Check if on main branch or if commit is pushed:**
```bash
git branch --show-current
git status
```

**If on main/master or pushed, generate GitHub permalinks:**

```bash
# Get repo info
gh repo view --json owner,name

# Create permalinks
https://github.com/{owner}/{repo}/blob/{commit}/{file}#L{line}
```

Replace local file references with permalinks in the document for permanent references.

### Step 8: Present Findings

**Present a concise summary to the user:**
- High-level answer to their question
- Include key file references for easy navigation
- Highlight important patterns or connections found
- Ask if they have follow-up questions or need clarification

**Example:**
```
I've completed the research on [topic]. Here's what I found:

**Summary:** [Concise answer]

**Key Components:**
- `path/to/main.ts:123` - [Brief description]
- `path/to/helper.py:45` - [Brief description]

**Full research document:** `.claude/research/2026-01-14-topic.md`

Do you have any follow-up questions or areas you'd like me to explore further?
```

## Handle Follow-Up Questions

If the user has follow-up questions:

1. **Append to the same research document**
2. **Update frontmatter:**
   - `last_updated`: New date
   - `last_updated_by`: Current user
   - Add `last_updated_note: "Added follow-up research for [brief description]"`

3. **Add a new section:**
   ```markdown
   ## Follow-up Research [timestamp]

   **Question:** [User's follow-up question]

   **Findings:**
   ...
   ```

4. **Spawn new sub-agents as needed** for additional investigation
5. **Continue updating the document**

## Important Notes

- **Always use parallel Agent tasks** to maximize efficiency
- **Always run fresh codebase research** - don't rely solely on existing docs
- **Focus on finding concrete file paths and line numbers** for developer reference
- **Research documents should be self-contained** with all necessary context
- **Each sub-agent prompt should be specific** and focused on read-only documentation
- **Document cross-component connections** and how systems interact
- **Include temporal context** (when the research was conducted)
- **Link to GitHub when possible** for permanent references
- **Keep the main agent focused on synthesis**, not deep file reading
- **Have sub-agents document examples and usage patterns** as they exist

## CRITICAL Reminders

**You and all sub-agents are documentarians, not evaluators:**
- REMEMBER: Document what IS, not what SHOULD BE
- NO RECOMMENDATIONS: Only describe the current state of the codebase

**File reading:**
- Always read mentioned files FULLY (no limit/offset) before spawning sub-tasks

**Critical ordering:**
- Follow the numbered steps exactly
- ALWAYS read mentioned files first before spawning sub-tasks (step 1)
- ALWAYS wait for all sub-agents to complete before synthesizing (step 4)
- ALWAYS gather metadata before writing the document (step 5 before step 6)
- NEVER write the research document with placeholder values

**Frontmatter consistency:**
- Always include frontmatter at the beginning of research documents
- Keep frontmatter fields consistent across all research documents
- Update frontmatter when adding follow-up research
- Use snake_case for multi-word field names (e.g., `last_updated`, `git_commit`)
- Tags should be relevant to the research topic and components studied

## Usage Examples

```bash
# General research question
/research-codebase

# Then provide: "How does authentication work in the backend?"

# Research specific feature
/research-codebase

# Then provide: "Document the workflow execution engine architecture"

# Understand integration
/research-codebase

# Then provide: "How does the client dashboard communicate with the backend API?"
```

## Integration with Other Skills

The research can reference:

- **Implementation plans:** `specs/features/FEAT-XXX/implementation-plan*.md`
- **Jira tickets:** `.claude/cache/SEMI-XXX.md` (via MCP Jira tools)
- **Confluence pages:** `.claude/cache/CONF-*.md` (via MCP Confluence tools)
- **Existing research:** `specs/research/*.md` or `.claude/research/*.md`

Research documents provide context for:
- `/create-plan` - Understanding existing patterns before planning
- `/code-review` - Historical context for architectural decisions
- `/describe-pr` - Background on the area being changed

## Research Document Storage

**Shareable research (team-wide findings):**
- Location: `specs/research/`
- Committed to git
- Referenced in implementation plans

**Personal research (exploratory, work-in-progress):**
- Location: `.claude/research/`
- Git-ignored by default
- Can be promoted to `specs/research/` when complete

Choose based on whether the research should be shared with the team or is exploratory work.
