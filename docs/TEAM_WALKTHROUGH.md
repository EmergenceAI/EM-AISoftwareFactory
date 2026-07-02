# Team Walkthrough Guide

**How to demo AI Software Factory to your team in 30 minutes.**

---

## Demo Flow

### 1. Overview (5 min)

Start with **[README.md](../README.md#what-is-this)**

- Show the "What Is This?" section
- Highlight the 5 key value propositions:
  - ✅ Single-Command SDLC
  - ✅ Multi-Repo Orchestration  
  - ✅ Knowledge-Driven
  - ✅ Quality Enforced
  - ✅ 80% Autonomous
- Quick context: Why this matters (4-6 hours → 10 minutes per issue)

---

### 2. Quick Start Demo (10 min)

#### Show Single Repository First

**[README.md → Quick Start → Single Repository](../README.md#single-repository)**

```bash
cd ~/Documents/Development/em-semi
/autonomous-implement SEMI-1413
```

**Walk through what happens:**
- [README.md → What happens](../README.md#single-repository) (scroll to "What happens:" list)
- Show the 9 automated steps from Jira → PR

**Key point:** "Just one command. No setup. Works immediately."

---

#### Then Show Multi-Repository with Orchestrator

**[README.md → Quick Start → Multi-Repository](../README.md#multi-repository-with-orchestrator)**

```bash
python3 -m orchestrator implement SEMI-1413
```

**Show the difference:**
- [README.md → What the orchestrator adds](../README.md#multi-repository-with-orchestrator-1) (scroll to "What the orchestrator adds:")
- Auto-routing to correct repository
- 45KB knowledge injection
- Foundations standards enforcement

**Key point:** "Same workflow, but now with repository knowledge and compliance built in."

---

### 3. Deep Dive (15-20 min)

Jump to sections based on team interest:

#### A. Orchestrator Usage

**[README.md → Orchestrator Usage](../README.md#orchestrator-usage)**

Show:
- Single vs Multi-repository comparison
- Routing logic from workspace.yaml
- What gets automated vs what you decide

**Clickable sections:**
- [Single Repository](../README.md#single-repository-1)
- [Multi-Repository with Orchestrator](../README.md#multi-repository-with-orchestrator-1)
- [Batch Multi-Repository](../README.md#batch-multi-repository)

---

#### B. Skills Reference

**[README.md → Skills Reference](../README.md#skills-reference)**

Show the skills table:
- [Autonomous Skills](../README.md#autonomous-skills-end-to-end) - End-to-end workflows
- [Core Development Skills](../README.md#core-development-skills) - Building blocks
- [Research & Planning](../README.md#research--planning) - Investigation tools

**Key skills to highlight:**
- `/autonomous-implement` - The main workflow
- `/autonomous-sprint` - Batch automation
- `/code-review` - Quality enforcement

---

#### C. Knowledge System

**[README.md → Knowledge System](../README.md#knowledge-system)**

Show:
- [What Gets Extracted](../README.md#what-gets-extracted) - The knowledge structure
- [Automatic Sync](../README.md#automatic-sync) - How it stays current
- [Pointing to Specific Knowledge](../README.md#pointing-to-specific-knowledge) - ADR references

**Demo the ADR referencing:**
- [Option 1: Add to knowledge extraction](../README.md#referencing-adrs)
- [Option 2: Link in workspace.yaml](../README.md#referencing-adrs)
- [Option 3: Direct reference in prompts](../README.md#referencing-adrs)

---

### 4. Hands-On (Optional)

If they want to try it immediately:

**For quick start:**
- **[docs/guides/QUICKSTART.md](guides/QUICKSTART.md)** - 5-minute hands-on guide
  - [Option 1: Single Repository](guides/QUICKSTART.md#option-1-single-repository-fastest)
  - [Option 2: Multi-Repository](guides/QUICKSTART.md#option-2-multi-repository-with-orchestrator)

**For complete reference:**
- **[docs/guides/ORCHESTRATOR_GUIDE.md](guides/ORCHESTRATOR_GUIDE.md)** - Complete orchestrator guide
  - [Single Repository Mode](guides/ORCHESTRATOR_GUIDE.md#single-repository-mode)
  - [Multi-Repository Mode](guides/ORCHESTRATOR_GUIDE.md#multi-repository-mode)
  - [Knowledge System](guides/ORCHESTRATOR_GUIDE.md#knowledge-system)
  - [Configuration](guides/ORCHESTRATOR_GUIDE.md#configuration)

---

## Quick Reference Links

### Essential Docs

| Doc | Link | Purpose |
|-----|------|---------|
| **Main README** | [README.md](../README.md) | Overview, quick start, all features |
| **Quick Start** | [docs/guides/QUICKSTART.md](guides/QUICKSTART.md) | 5-minute hands-on |
| **Orchestrator Guide** | [docs/guides/ORCHESTRATOR_GUIDE.md](guides/ORCHESTRATOR_GUIDE.md) | Complete reference |
| **Architecture** | [docs/architecture/ENGINEERING_OS_ARCHITECTURE.md](architecture/ENGINEERING_OS_ARCHITECTURE.md) | System design |

---

### Key Sections for Demo

| Topic | Link |
|-------|------|
| **What Is This?** | [README.md#what-is-this](../README.md#what-is-this) |
| **Quick Start** | [README.md#quick-start](../README.md#quick-start) |
| **Orchestrator Usage** | [README.md#orchestrator-usage](../README.md#orchestrator-usage) |
| **Skills Reference** | [README.md#skills-reference](../README.md#skills-reference) |
| **Knowledge System** | [README.md#knowledge-system](../README.md#knowledge-system) |
| **Workspace Configuration** | [README.md#workspace-configuration](../README.md#workspace-configuration) |
| **Troubleshooting** | [README.md#troubleshooting](../README.md#troubleshooting) |

---

## Demo Tips

### Before the Demo

1. **Test the demo** - Run through it once on your own
2. **Pick a real issue** - Use actual Jira issue for authenticity
3. **Have backup** - Know where docs are if demo fails
4. **Prep questions** - Anticipate "What about...?" questions

### During the Demo

1. **Start with why** - Problem → Solution → Value
2. **Show, don't tell** - Run actual commands
3. **Keep it moving** - 5 min per section max
4. **Invite questions** - But defer deep dives to docs

### After the Demo

1. **Share links** - Post in Slack with key docs
2. **Offer help** - "Office hours" for hands-on
3. **Track adoption** - Who tries it? What issues?
4. **Gather feedback** - What's confusing? What's missing?

---

## Common Questions & Answers

### "What if it makes a mistake?"

**Answer:** Two checkpoints - you approve the plan, and you review the PR before merge. Plus automated tests catch bugs before PR creation.

**Show:** [README.md → Orchestrator Usage → What happens](../README.md#single-repository-1)

---

### "How do I point it to our ADRs?"

**Answer:** Three methods - edit knowledge files, link in workspace.yaml, or mention in plan approval.

**Show:** [README.md → Referencing ADRs](../README.md#referencing-adrs)

---

### "What about our coding standards?"

**Answer:** The knowledge system extracts patterns, conventions, and architecture from your repository. It automatically applies your team's style.

**Show:** [README.md → What Gets Extracted](../README.md#what-gets-extracted)

---

### "Can it work with our Jira?"

**Answer:** Yes, configure Jira MCP. Also works with mock data for testing.

**Show:** [README.md → Jira MCP Setup](../README.md#jira-mcp-setup-optional)

---

### "How do I add a new repository?"

**Answer:** Add to workspace.yaml, sync knowledge, test routing. Takes 5 minutes.

**Show:** [README.md → Adding a New Repository](../README.md#adding-a-new-repository)

---

### "What if routing goes to the wrong repo?"

**Answer:** Test routing first, check component mapping, use troubleshooting guide.

**Show:** [README.md → Troubleshooting](../README.md#troubleshooting)

---

## Presentation Order

### 30-Minute Walkthrough

```
0:00 - 0:05   Overview (What Is This?)
0:05 - 0:15   Quick Start Demo (Single + Multi-repo)
0:15 - 0:25   Deep Dive (Orchestrator OR Skills OR Knowledge - pick one)
0:25 - 0:30   Q&A + Next Steps
```

### 15-Minute Lightning Talk

```
0:00 - 0:03   Overview (Just the 5 value props)
0:03 - 0:10   Quick Start Demo (Show single-repo only)
0:10 - 0:12   One Deep Dive (Pick Skills Reference)
0:12 - 0:15   Q&A
```

### 45-Minute Workshop

```
0:00 - 0:05   Overview
0:05 - 0:15   Quick Start Demo
0:15 - 0:30   All Deep Dives (Orchestrator, Skills, Knowledge)
0:30 - 0:40   Hands-On (They try it)
0:40 - 0:45   Q&A + Follow-up
```

---

## Follow-Up Resources

After the demo, share in Slack:

```
🎉 AI Software Factory Demo - Resources

**Start Here:**
📘 Quick Start (5 min): docs/guides/QUICKSTART.md
📖 Complete Guide: README.md

**Key Links:**
- Orchestrator Guide: docs/guides/ORCHESTRATOR_GUIDE.md
- Architecture: docs/architecture/ENGINEERING_OS_ARCHITECTURE.md
- All Docs: docs/README.md

**Try It:**
1. Pick a Jira issue
2. Run: /autonomous-implement YOUR-ISSUE-123
3. Review the plan, approve, watch it work

**Questions?**
Reply in thread or DM me for 1-on-1 walkthrough

**Office Hours:**
[Your availability - e.g., Tuesday 2-3pm, Thursday 10-11am]
```

---

## Success Metrics

Track after demo:

- **Attendance:** How many showed up?
- **Engagement:** Questions asked? Interest level?
- **Adoption:** Who tried it in the next sprint?
- **Issues:** What blockers did they hit?
- **Feedback:** What resonated? What confused?

---

**The demo sells itself when you show real automation on real issues.** 🚀
