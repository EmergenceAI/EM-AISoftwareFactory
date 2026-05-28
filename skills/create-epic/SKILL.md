---
name: create-epic
description: Create epics in Jira using the team's standard epic template with collaborative section-by-section refinement
---

# Create Epic

Create structured epics in Jira based on the team's standard epic template, collaborating with the user section by section before submitting.

## When to Use This Skill

Use this skill to:
- Create new epics in Jira with full context
- Follow the team's standard epic template (Vision, Overview, Problem Statement, Success Criteria, Business Value)
- Collaborate on epic content before creating

## Usage

```bash
/create-epic "Epic title or topic"
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

## Process

### Step 1: Collaborate on Each Section

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

**Default project key is SEMI.** If the user specifies a different project, use that instead.

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

- [x] Uses embedded template (no Confluence dependency at runtime)
- [x] Collaborates section by section with the user
- [x] Proposes drafts for each section based on user input
- [x] Shows full preview before creating
- [x] Creates epic in Jira with all sections
- [x] Resolves assignee if provided
- [x] Returns issue key and URL

## Integration with Other Skills

```bash
# Create epic
/create-epic "Build Your Own Workflow" → SEMI-1116 created

# Break down into plan
/create-plan SEMI-1116

# Implement
/implement-plan SEMI-1116
```

## Notes

**Collaborative approach:**
- Always propose content, never create silently
- Go section by section — don't dump everything at once
- Let the user confirm each section before moving on
- If the user provides all info upfront, propose all sections together for faster flow

**Jira-specific:**
- Uses MCP for all Jira operations
- Default project: SEMI
- Resolves user names via Confluence user search before assigning
