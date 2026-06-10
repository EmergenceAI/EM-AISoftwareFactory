---
name: create-epic
description: Create epics in Jira using the team's standard epic template - single interactive mode or batch from CSV/Excel tables
---

# Create Epic

Create structured epics in Jira based on the team's standard epic template, collaborating with the user section by section before submitting.

## When to Use This Skill

Use this skill to:
- Create new epics in Jira with full context
- Follow the team's standard epic template (Vision, Overview, Problem Statement, Success Criteria, Business Value)
- Collaborate on epic content before creating (single epic mode)
- Batch create multiple epics from a structured table (CSV, Excel, Markdown, JSON)
- Import epic definitions from planning documents or spreadsheets
- Efficiently create a roadmap of epics in one operation

## Usage

### Single Epic Creation
```bash
/create-epic "Epic title or topic"
```

### Batch Epic Creation from Table
```bash
/create-epic --from-table path/to/epics.csv
```

Or provide the table data inline:
```bash
/create-epic --from-table
# Then paste or provide the table data
```

## Epic Template

The following template defines the standard structure for all epics. Each section has a purpose and guidance for what to include.

### Section 1: Vision

A concise 1-2 sentence statement describing the aspirational outcome of this epic.

**Guidance:**
- What does the world look like when this is done?
- Focus on the user/customer impact, not the technical solution
- Keep it short and inspiring

**Example:**
> Enable semiconductor customers to build, customize, and automate their own analysis workflows without sharing proprietary processes with Emergence — building trust while accelerating time-to-value.

### Section 2: Overview

A paragraph describing the initiative — what will be built, how it works at a high level, and what capabilities it enables.

**Guidance:**
- What are we building?
- How does it work at a high level?
- What capabilities does it unlock?

**Example:**
> Build a composable workflow automation platform that enables users to create, customize, and automate semiconductor workflows. Refactor existing Yield Excursion workflows into reusable agentic building blocks that can be composed, orchestrated, and monitored. Enable "Build Your Own Workflow" (BYOW) capabilities where users assemble semiconductor domain-specific workflows from pre-built tools/agents or generate code at runtime with safety guardrails as a fallback.

### Section 3: Problem Statement

Three sub-sections describing the gap between where we are and where we need to be.

**Current State** — What exists today and its limitations:
- What is the current implementation?
- What are its shortcomings?
- Why can't we stay here?

**Desired State** — What the end state looks like (as bullet points):
- What capabilities will exist?
- What can users do that they can't today?
- What technical properties does the solution have?

**Impact** — Why this matters:
- Customer impact (pain points addressed)
- Business impact (revenue, cost, competitive)
- Strategic impact (market positioning, trust)

**Example:**
> **Current State:** We have a yield excursion workflow implementation that is static, non-reusable, and difficult to extend for other workflows. The workflow is a bespoke implementation with logic for data loading, analysis, RCA visualization, reporting and eval. Users cannot create custom workflows or combine capabilities across different analyses.
>
> **Desired State:**
> - Core capabilities (data ingestion, ML analysis, visualization) are modular agents
> - Users can compose workflows via UI using drag-and-drop or YAML/JSON definitions
> - Workflows are versioned, saved, reused, and scheduled
> - Unsupported analysis triggers safe code generation with eval validation as a fallback
> - All workflows emit standardized metrics to observability stack
>
> **Impact:** Customers in the semiconductor industry are hesitant to share their processes with partners due to IP concerns. BYOW allows them to build their own custom workflows without sharing those processes with Emergence, building trust.

### Section 4: Success Criteria

Measurable outcomes that define when this epic is complete. Each criterion should be verifiable.

**Guidance:**
- What must be true for this to be considered done?
- Include both functional and non-functional criteria
- Make criteria specific and testable
- Include proof/validation criteria where possible

**Example:**
> - Existing Yield Excursion workflow is refactored into composable agents with no functionality regression
> - Users can create and save custom workflows using reusable agent blocks and platform
> - Workflow orchestration supports scheduling, versioning, and dependency management
> - Code generation fallback implemented with isolated execution + eval harness validation
> - Workflow execution metrics (duration, success rate, agent usage) in logs and existing observability system

### Section 5: Business Value

Three sub-sections connecting the work to business outcomes.

**User Value** — How users directly benefit:
- Time savings, new capabilities, improved experience

**Business Impact** — Quantifiable business outcomes:
- Cost reduction, revenue impact, efficiency gains
- Use numbers where possible (e.g., "reduce by 80%")

**Strategic Alignment** — Connection to broader company strategy:
- GTM motions, competitive positioning, platform strategy
- How this enables other initiatives

**Example:**
> **User Value:** Faster time to build custom analysis workflows with pre-built building blocks
>
> **Business Impact:**
> - Reduce workflow development cost by 80% through composition vs. custom builds
> - Accelerate customer onboarding
>
> **Strategic Alignment:**
> - Necessary capability for the Agent Packs GTM motion
> - Reduces need for white-glove treatment for less valuable and non-mission-critical workflows as customers can self-serve

## Table Format for Batch Epic Creation

When using `--from-table`, the table should contain the following columns:

### Required Columns
- **Title**: Epic title/summary
- **Vision**: 1-2 sentence aspirational outcome
- **Overview**: Paragraph describing what will be built
- **Current State**: What exists today and its limitations
- **Desired State**: What the end state looks like (bullet points)
- **Impact**: Why this matters (customer, business, strategic)
- **Success Criteria**: Measurable outcomes (functional, performance, eval-based validation, observability)
- **User Value**: How users directly benefit
- **Business Impact**: Quantifiable business outcomes
- **Strategic Alignment**: Connection to broader company strategy

### Optional Columns
- **Project**: Jira project key (default: SEMI)
- **Priority**: Epic priority (default: Medium)
- **Labels**: Comma-separated labels
- **Assignee**: Name or email of assignee

### Supported Formats
- CSV files (`.csv`)
- Excel files (`.xlsx`, `.xls`)
- TSV files (`.tsv`)
- Markdown tables (pasted inline)
- JSON arrays

### Example CSV Structure

A complete example CSV template is provided in [`example-epics-template.csv`](./example-epics-template.csv).

**Simplified CSV structure:**
```csv
Title,Vision,Overview,Current State,Desired State,Impact,Success Criteria,User Value,Business Impact,Strategic Alignment,Project,Priority,Labels,Assignee
"CSV/Parquet API Connector","Enable data scientists to programmatically upload large datasets...","Build API-based data connector workflows...","Current platform lacks CSV connector...","- New CSV/Parquet connector
- Chunked upload support
- Standard workflows","Customer/Business/Strategic impact...","Functional/Performance/Eval criteria...","User benefits...","Business outcomes...","Strategic alignment...",SEMI,High,"data-connectors,csv",
```

**Tips for CSV formatting:**
- Use double quotes for cells containing commas, newlines, or special characters
- Preserve bullet points and formatting within cells using newlines
- Leave optional columns (Assignee, Labels) empty if not needed
- Multi-line content is supported and will be preserved in Jira

### Example Markdown Table (Inline)

```markdown
| Title | Vision | Overview | Current State | Desired State | Impact | Success Criteria | User Value | Business Impact | Strategic Alignment |
|-------|--------|----------|---------------|---------------|--------|------------------|------------|-----------------|---------------------|
| Epic 1 | Vision text | Overview text | Current state | Desired state | Impact | Criteria | User value | Business impact | Strategic alignment |
| Epic 2 | Vision text | Overview text | Current state | Desired state | Impact | Criteria | User value | Business impact | Strategic alignment |
```

### Complete Example (Full Epic Structure)

Here's a complete example showing how to structure a full epic in table format:

**Title:** CSV/Parquet API Connector for Large Dataset Ingestion

**Vision:**
```
Enable data scientists and engineers to programmatically upload and process large CSV/Parquet datasets (300 MB - 1 GB) through robust API-based connectors with automated quality validation, eliminating manual upload bottlenecks and enabling reliable data pipeline integration.
```

**Overview:**
```
Build API-based data connector workflows that enable programmatic ingestion, profiling, validation, and optimization of large CSV/Parquet datasets. The system will provide four core workflow types: (1) Ingestion Workflows that extract comprehensive metadata from CSV sources including schema, columns, data types, and constraints; (2) Profiling Workflows that generate column-level statistical profiles using Python/PySpark processing; (3) DQ Query Generation workflows that create data quality rule templates from CSV analysis; and (4) DQ Execution Workflows that validate data against quality rules end-to-end. Additionally, an ETL staging workflow will convert and optimize uploaded CSV/Parquet files for efficient large-scale data access.
```

**Current State:**
```
The em-data-readiness platform has connectors for databases (PostgreSQL, Snowflake) but lacks an API-based connector for CSV/Parquet files. The Infineon analog trimming workflow and Broadcom requires ingestion of large CSV/Parquet datasets (300 MB - 1 GB), but there's no standardized connector to handle file-based data sources. Without this connector, workflows cannot programmatically ingest, profile, validate, or optimize CSV/Parquet files through the same API-based interface used for database connectors.
```

**Desired State:**
```
- New CSV/Parquet API-based connector in em-data-readiness alongside existing database connectors
- Connector supports chunked/streaming upload of large files (300 MB - 1 GB) with progress tracking
- Implements standard connector workflows: Ingestion (metadata extraction), Profiling (statistical analysis), DQ Generation (rule templates), DQ Execution (validation)
- ETL staging workflow optimizes uploaded files (e.g., converts to partitioned Parquet) for efficient agent access
- Infineon analog trimming workflow can consume CSV/Parquet data through this connector using the same API patterns as database connectors
- All workflows follow eval-based development with automated quality gates
- Connector integrates with existing em-data-readiness architecture and observability
```

**Impact:**
```
Customer Impact: Enables Infineon and other customers to integrate file-based data sources into their workflows using the same reliable connector patterns they use for databases, eliminating custom integration work.

Business Impact: Unblocks Infineon analog trimming workflow deployment. Expands addressable data sources beyond databases to include file-based pipelines common in semiconductor manufacturing.

Strategic Impact: Completes the data connector ecosystem (database + file-based sources), enabling agent workflows to consume data from any source. Demonstrates consistent eval-based quality across all connector types.
```

**Success Criteria:**
```
Functional Criteria:
- CSV/Parquet API-based connector implemented in em-data-readiness with same architectural patterns as PostgreSQL/Snowflake connectors
- Connector supports chunked upload for files 300 MB - 1 GB with progress tracking and resumable uploads
- All four workflow types operational: Ingestion, Profiling, DQ Generation, DQ Execution
- ETL staging workflow converts CSV to optimized Parquet with appropriate partitioning strategy
- Infineon analog trimming workflow successfully consumes data through the connector with no regressions

Performance Criteria:
- 500 MB CSV file uploads complete in < 5 minutes with < 5% failure rate
- 1 GB Parquet file uploads complete in < 10 minutes with < 5% failure rate
- Profiling workflow completes for 1 GB dataset in < 15 minutes
- Optimized staging reduces query time by ≥ 50% vs. raw CSV

Eval-Based Validation (Automated Tests):
- Eval 1: Upload Integrity — Upload 500 MB CSV, verify row count and checksum match source (100% accuracy required)
- Eval 2: Schema Detection — Ingestion workflow correctly identifies all column types for 20-column CSV with mixed types (100% accuracy)
- Eval 3: Profile Completeness — Profiling workflow generates nulls, cardinality, min/max, distribution for all columns (100% coverage)
- Eval 4: DQ Rule Generation — DQ Generation creates valid rules for common patterns (NOT NULL, range checks, format validation) with ≥ 90% precision
- Eval 5: DQ Execution Accuracy — DQ Execution correctly flags known quality issues in test dataset (100% recall on planted defects)
- Eval 6: Parquet Optimization — Staged Parquet file size ≤ 70% of original CSV, query performance ≥ 2x faster
- Eval 7: Infineon Workflow Integration — End-to-end test: upload Infineon sample data → validate → consume in analog trimming workflow (0 errors)

Observability & Monitoring:
- All workflows emit metrics (duration, success rate, data volume) to existing observability stack
- Failed uploads provide clear error messages and recovery guidance
```

**User Value:**
```
Infineon data engineers can programmatically integrate CSV/Parquet data sources into their analog trimming workflows using the same reliable API patterns they use for database connectors, eliminating hours of custom integration work and manual file handling.
```

**Business Impact:**
```
- Unblocks Infineon analog trimming workflow deployment, enabling critical customer use case
- Reduces data onboarding time by ~80% through automated ingestion, profiling, and validation
- Expands addressable market to customers with file-based data pipelines (common in semiconductor manufacturing)
- Reduces support burden by providing standardized connector with automated quality gates
```

**Strategic Alignment:**
```
Completes the data connector ecosystem alongside database connectors, positioning the platform as a comprehensive data engineering solution. Demonstrates eval-based development methodology that builds customer confidence in platform reliability and quality. Enables the broader "Build Your Own Workflow" (BYOW) strategy by providing file-based data sources as foundational building blocks for custom workflows.
```

## Process

### Process for Batch Epic Creation (--from-table)

1. **Parse the table data** from file or inline input
2. **Validate** that all required columns are present
3. **Show preview** of all epics to be created with their full content
4. **Confirm** with user before creating (show count: "About to create 5 epics. Continue? [Y/n]")
5. **Create epics** one by one in Jira using the standard epic template
6. **Report results** with a summary table showing:
   - Epic title
   - Issue key
   - URL
   - Status (✓ created / ✗ failed with reason)

### Example Batch Creation Flow

```markdown
Found 3 epics in table. Here's what will be created:

1. CSV/Parquet API Connector (SEMI, High priority)
2. Real-time Data Streaming (SEMI, Medium priority)  
3. Advanced Query Engine (SEMI, Medium priority)

PREVIEW: Epic 1 of 3

Project: SEMI
Priority: High
Labels: data-connectors, infineon, csv

Epic: CSV/Parquet API Connector

## Vision
Enable data scientists and engineers to programmatically upload and process large CSV/Parquet datasets...

## Overview
Build API-based data connector workflows that enable programmatic ingestion...

[... full epic preview ...]

---

[Show previews for epics 2 and 3...]

Create all 3 epics in Jira? [Y/n/e]
```

**If user confirms:**
- Create each epic sequentially
- Show progress indicator (e.g., "Creating epic 1/3...")
- Handle failures gracefully and continue with remaining epics

**Output summary:**
```markdown
Batch epic creation complete!

Results:
✓ SEMI-1234: CSV/Parquet API Connector
✓ SEMI-1235: Real-time Data Streaming
✗ SEMI-xxxx: Advanced Query Engine (Failed: Invalid project key)

Successfully created: 2/3 epics

Next steps:
- Review created epics in Jira
- Break down into stories: /create-plan SEMI-1234
```

### Step 1: Collaborate on Each Section (Single Epic Mode)

Work through the epic sections **one at a time** with the user using the template above. For each section:

1. **Propose** a draft based on what the user has shared about the epic topic
2. **Ask** the user to confirm or adjust
3. **Lock in** the section before moving to the next

**Present sections in this order:**

```
I'll help you create an epic for "{topic}". Let's go section by section.

### Vision
> {Propose a 1-2 sentence vision statement}

Does that capture the intent, or would you adjust it?
```

Once confirmed, move to:

```
### Overview
> {Propose a paragraph describing the initiative}

Does this still reflect the current thinking, or has the scope evolved?
```

Then:

```
### Problem Statement

**Current State:**
> {What exists today and its limitations}

**Desired State:**
> {What the end state looks like, as bullet points}

**Impact:**
> {Why this matters — customer, business, or strategic impact}

Anything to add or change here?
```

Then:

```
### Success Criteria
> {Measurable outcomes as bullet points}

Are these the right measures of success?
```

Finally:

```
### Business Value

**User Value:**
> {How users benefit}

**Business Impact:**
> {Quantifiable business outcomes}

**Strategic Alignment:**
> {Connection to broader company strategy}

What's the connection to broader company strategy?
```

### Step 2: Gather Metadata

**Default project key is SEMI.** Common project keys: SEMI, ABI, PLAT. If the user specifies a different project, use that instead.

**Ask for priority (optional):**
```
Priority? [default: Medium]
```

**Ask for labels (optional):**
```
Labels? (comma-separated, or Enter to skip)
```

**Ask for assignee (optional):**
```
Assign to? (name or email, or Enter to skip)
```

If an assignee is provided, look up the user via `mcp__atlassian__confluence_search_user` to resolve the correct email/account before assigning.

### Step 3: Show Preview

**Complete epic preview before creating:**

```markdown
PREVIEW: Epic for Jira

Project: SEMI
Priority: Medium
Labels: byow, epic
Assignee: Deepak Akkil

Epic: Build Your Own Workflow (BYOW)

## Vision
{vision content}

## Overview
{overview content}

## Problem Statement

### Current State
{current state}

### Desired State
{desired state}

### Impact
{impact}

## Success Criteria
{criteria as bullets}

## Business Value

### User Value
{user value}

### Business Impact
{business impact}

### Strategic Alignment
{strategic alignment}

Create this epic in Jira? [Y/n/e]
```

### Step 4: Create in Jira

**If user confirms:**

```markdown
Invoke `mcp__atlassian__jira_create_issue` tool:

Parameters:
  project_key: "SEMI"
  summary: "{Epic title}"
  issue_type: "Epic"
  description: {Full epic markdown from preview}
  additional_fields: {
    "priority": {"name": "{priority}"},
    "labels": ["{labels}"]
  }
```

**If assignee was provided:**

```markdown
Invoke `mcp__atlassian__jira_update_issue` tool:

Parameters:
  issue_key: "{created issue key}"
  fields: {"assignee": "{resolved email}"}
```

### Step 5: Output Summary

```markdown
Epic created in Jira!

**Issue:** SEMI-1116
**URL:** https://emergenceai.atlassian.net/browse/SEMI-1116
**Priority:** Medium
**Assignee:** Deepak Akkil
**Labels:** byow, epic

**Next steps:**
- Break down into stories: /create-plan SEMI-1116
- Add child issues in Jira
```

## Success Criteria

### Single Epic Mode
- [x] Uses embedded template (no Confluence dependency at runtime)
- [x] Collaborates section by section with the user
- [x] Proposes drafts for each section based on user input
- [x] Shows full preview before creating
- [x] Creates epic in Jira with all sections
- [x] Resolves assignee if provided
- [x] Returns issue key and URL

### Batch Epic Mode
- [ ] Parses table data from CSV, Excel, TSV, Markdown, and JSON formats
- [ ] Validates all required columns before processing
- [ ] Shows preview of all epics with full content before creating
- [ ] Creates epics sequentially with progress indicators
- [ ] Handles failures gracefully and continues with remaining epics
- [ ] Reports clear success/failure summary with issue keys and URLs
- [ ] Preserves formatting in multi-line cells (bullet points, paragraphs)
- [ ] Supports batches of 10+ epics efficiently
- [ ] Validates project keys and resolves assignees for all epics

## Integration with Other Skills

### Single Epic Workflow
```bash
# Create single epic interactively
/create-epic "Build Your Own Workflow" → SEMI-1116 created

# Break down into plan
/create-plan SEMI-1116

# Implement
/implement-plan SEMI-1116
```

### Batch Epic Workflow
```bash
# Create multiple epics from CSV file
/create-epic --from-table roadmap-q2-2026.csv
→ SEMI-1234, SEMI-1235, SEMI-1236 created

# Create multiple epics from Excel spreadsheet
/create-epic --from-table epic-planning.xlsx
→ SEMI-1237, SEMI-1238 created

# Bulk create plans for all epics
/create-plan SEMI-1234 SEMI-1235 SEMI-1236

# Or create plans one by one
/create-plan SEMI-1234
/create-plan SEMI-1235
```

## Notes

**Collaborative approach (Single Epic Mode):**
- Always propose content, never create silently
- Go section by section — don't dump everything at once
- Let the user confirm each section before moving on
- If the user provides all info upfront, propose all sections together for faster flow

**Batch Mode (--from-table):**
- Parse table data from CSV, Excel, TSV, Markdown, or JSON format
- Validate all required columns are present before processing
- Show comprehensive preview of ALL epics before creating any
- Create epics sequentially with progress indicators
- Handle failures gracefully and report clear success/failure summary
- Support large batches (10+ epics) efficiently
- Preserve formatting in multi-line cells (e.g., bullet points in Desired State)

**Table Data Parsing:**
- CSV/TSV: Use standard parsing libraries, handle quoted strings with commas
- Excel: Read first sheet by default, support column headers in row 1
- Markdown tables: Parse pipe-separated format
- JSON: Expect array of objects with column names as keys
- Multi-line content: Preserve newlines and bullet point formatting within cells

**Jira-specific:**
- Uses MCP for all Jira operations
- Default project: SEMI
- Resolves user names via Confluence user search before assigning
- In batch mode, validate project keys before creating epics
- Rate limiting: Add small delay between epic creations if batch size > 5
