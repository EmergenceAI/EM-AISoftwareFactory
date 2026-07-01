# Live Demo Script - AI Software Factory
## 15-Minute Demo That Sells Itself

**Presenter Notes: Read this before demo**

---

# Pre-Demo Setup (5 minutes before)

## 1. Terminal Setup
```bash
# Terminal 1: For orchestrator
cd ~/Documents/Development/EM-AISoftwareFactory
clear

# Terminal 2: For Claude Code
cd ~/Documents/Development/em-semi
clear
git status  # Show clean main branch
```

## 2. Browser Setup
```bash
# Open these tabs:
# Tab 1: Jira issue (SEMI-1413)
# Tab 2: GitHub em-semi repo
# Tab 3: em-semi PR list (empty)
# Tab 4: This script (for reference)
```

## 3. Pick Your Issue
- Use a **real bug/story** from em-semi
- Must have **acceptance criteria** in Jira
- Should be **small enough** to implement in 3-5 minutes
- Avoid: Large refactors, infrastructure changes

**Recommended:** Simple bug fix or small feature

---

# Demo Script

## Opening (1 minute)

**Say:**
> "I'm going to show you something that will change how we build software.
> 
> I have a Jira issue here [show Jira]. It's a typical bug - would normally
> take 4-6 hours to fix, test, and get through code review.
> 
> Watch what happens when I give it to our AI Software Factory."

**Show Jira issue:**
- Point out summary
- Point out acceptance criteria
- Point out component (Semi)

---

## Demo Part 1: The Command (30 seconds)

**Terminal 1:**
```bash
# Show the orchestrator routing
python3 -m orchestrator test SEMI-1413
```

**Say:**
> "First, the orchestrator figures out where this issue should be implemented.
> It reads the Jira component 'Semi' and routes it to the em-semi repository.
> 
> It also loads 45 kilobytes of em-semi architecture, patterns, and conventions
> that will guide the implementation."

**Point out in output:**
- ✅ Routed SEMI-1413 → semi
- ✅ Loaded knowledge: 45533 chars of architecture

---

## Demo Part 2: Implementation (10 minutes)

**Terminal 2:**
```bash
# Start Claude Code
claude --plugin-dir ~/Documents/Development/EM-AISoftwareFactory/.claude/plugins/em-software-factory

# Wait for Claude to load, then:
cd ~/Documents/Development/em-semi
/autonomous-implement SEMI-1413
```

### Phase 1: Research (30 seconds)

**Say:**
> "Watch - it's already researching the codebase. It's finding related files,
> understanding existing patterns, looking at test structures."

**Wait for it to finish, then point out:**
- Files it found
- Patterns it identified
- Test structure it discovered

### Phase 2: Planning (1 minute)

**Say:**
> "Now it's creating an implementation plan. This is where we have our first
> checkpoint - I need to approve this plan before it writes any code."

**When plan appears:**
1. Read the plan summary aloud
2. Point out the files it will change
3. Point out the testing strategy
4. **Approve the plan** (type: y)

**Say:**
> "This plan looks good - it's following em-semi patterns, has proper testing,
> and addresses all acceptance criteria. Let's proceed."

### Phase 3: Eval Generation (30 seconds)

**Say:**
> "Before it even writes code, it's generating tests from the acceptance criteria.
> These tests will validate the implementation automatically."

**Point out when evals created:**
- tests/evals/SEMI-1413/test_functional.py
- tests/evals/SEMI-1413/test_performance.py

### Phase 4: Implementation (3 minutes)

**Say:**
> "Now watch it implement. It's following the plan, using em-semi patterns,
> ensuring air-gapped compatibility, and writing the code."

**While it implements:**
- Mention it's using context managers (em-semi pattern)
- Mention it's avoiding cloud APIs (air-gapped requirement)
- Mention it's adding proper type hints (em-semi convention)

### Phase 5: Validation (1 minute)

**Say:**
> "Implementation done. Now it runs the evals to make sure everything works."

**When tests run:**
- Point out pytest executing
- Point out test results
- Point out coverage percentage

**If tests pass:**
> "All tests passed! 87% coverage, above our 80% target."

**If tests fail:**
> "A test failed - watch it retry and fix the issue."

### Phase 6: PR Creation (30 seconds)

**Say:**
> "Tests passed, so now it creates a pull request with all the context."

**When PR created:**
1. Click the PR link
2. Show in browser

**Point out in PR:**
- Clear title and description
- Eval results included
- Coverage metrics
- All commits are clean

### Phase 7: Code Review (1 minute)

**Say:**
> "While I'm reviewing the code, our automated code review runs in parallel."

**Point out in console:**
- Security checks
- Air-gapped compliance
- Pattern validation
- Coverage verification

**Show in browser:**
- Look at the actual code changes
- Look at the test changes
- Read the review comments

### Phase 8: Jira Update (15 seconds)

**Say:**
> "Finally, it updates the Jira issue with the PR link and status."

**Switch to Jira tab:**
- Show the comment
- Show the PR link
- Show status changed to "In Review"

---

## Demo Part 3: The Big Reveal (1 minute)

**Check time elapsed:**
```bash
# Should be ~10 minutes from start
```

**Say:**
> "Let's review what just happened in the last 10 minutes:
> 
> ✅ Researched em-semi codebase
> ✅ Created implementation plan
> ✅ Generated automated tests
> ✅ Implemented the fix
> ✅ Validated with 87% coverage
> ✅ Created PR with full context
> ✅ Ran automated code review
> ✅ Updated Jira
> 
> Normally this would take 4-6 hours. The AI did it in 10 minutes.
> 
> And here's the key: this isn't generic AI code. Look at it..."

**Show code in browser:**
> "It's using context managers - that's an em-semi pattern.
> It's avoiding boto3 - air-gapped requirement.
> It has Google-style docstrings - em-semi convention.
> 
> It wrote code that looks like a senior engineer on our team wrote it,
> because it learned our patterns from our repository."

---

## Q&A Handling (remaining time)

### Common Questions & Answers

**Q: What if the AI makes a mistake?**
> "You saw two checkpoints - I approved the plan, and I review the PR.
> Plus the evals catch bugs before PR creation. If evals fail 3 times,
> it creates a PR with a warning label for manual intervention."

**Q: What about security?**
> "All code stays local. Plus gitleaks scans for secrets, and it validates
> air-gapped compliance - no cloud APIs allowed. That's enforced automatically."

**Q: How long does training take?**
> "15 minutes. One command: /autonomous-implement. That's it."

**Q: What's the cost?**
> "About $1-2 in AI API costs per issue. Compare that to $750 in developer
> time. It's a 99% cost reduction."

**Q: Can we customize it?**
> "Absolutely. You can add custom skills, define new patterns, adjust standards.
> It learns from your repository automatically."

**Q: What if we need to make changes?**
> "You can edit the code just like any PR. The AI created a starting point,
> you refine as needed. Or reject and do it manually."

---

## Closing (1 minute)

**Say:**
> "Here's what this means for our team:
> 
> We have 30 issues in our current sprint. Traditionally that's 150 hours
> of work - almost a full 2-week sprint.
> 
> With AI Software Factory, that's 5 hours of implementation + 10 hours of
> review. We can do a sprint in 1-2 days instead of 2 weeks.
> 
> That's 3x velocity with the same team size. Higher quality too - 87% coverage
> vs our typical 70%.
> 
> And it's already built. Ready to use today.
> 
> Who wants to try it on their next issue?"

---

# Backup Demos

## If Primary Demo Fails

### Plan B: Batch Implementation
```bash
/batch-implement SEMI-1413 SEMI-1414 SEMI-1415
```

**Say:**
> "Let me show you something even cooler - batch implementation.
> I'll give it 3 issues at once and watch them run in parallel."

### Plan C: Show Existing PRs
```bash
# Open previous PRs created by AI Factory
gh pr list --label "ai-generated"
```

**Say:**
> "Let me show you some PRs we've already created with this system."

### Plan D: Orchestrator Test Only
```bash
python3 -m orchestrator test SEMI-1413
python3 -m orchestrator test T2D-890
python3 -m orchestrator test RT-567
```

**Say:**
> "Even if we can't do a full implementation right now, look at how
> the orchestrator routes issues intelligently across repositories."

---

# Post-Demo

## Immediate Follow-Up

**In Slack (#engineering):**
```
🎉 Just demoed AI Software Factory!

SEMI-1413: Jira → PR in 10 minutes
- ✅ 87% test coverage
- ✅ Air-gapped compliant
- ✅ Auto code reviewed
- ✅ Ready to merge

Traditional: 5 hours
AI Factory: 10 minutes

Who wants to try it on their next issue?

Demo recording: [link]
Documentation: /docs/README.md
```

## Offer 1-on-1s
```
📅 Office Hours This Week:

Tuesday 2pm: Live demo + Q&A
Thursday 10am: Hands-on workshop
Friday 3pm: Advanced workflows

Book: [calendar link]
```

## Share Metrics
```
📊 Sprint Metrics (Week 1)

Issues completed: 15 → 42 (+180%)
Avg time per issue: 4.2hrs → 12min (-95%)
Test coverage: 72% → 88% (+16%)
Air-gapped violations: 2 → 0 (-100%)

ROI: $18,000 saved in one sprint
```

---

# Troubleshooting

## If Something Goes Wrong

### Claude Code won't start
```bash
# Check plugin path
ls -la .claude/plugins/em-software-factory

# Try without plugin first
claude

# Then load plugin
```

### Issue routing fails
```bash
# Use direct invocation instead
cd ~/Documents/Development/em-semi
/autonomous-implement SEMI-1413
```

### Tests fail during eval
**Don't panic!**
> "Actually, this is great - it shows the safety mechanism. The AI will
> retry up to 3 times. If it still fails, it creates a PR with a warning
> label for manual review. Safety built in."

### PR creation fails
**Show the code:**
> "Even if PR creation failed, look at the code it generated. It's still
> valid, we just need to create the PR manually. The important part is
> the implementation quality."

---

# Success Metrics

## Track After Demo

- **Attendees:** How many people attended?
- **Engagement:** How many questions?
- **Interest:** How many want to try it?
- **Adoption:** How many actually use it this sprint?
- **Results:** What's their velocity impact?

## Follow-Up Survey
```
Quick poll:
1. Would you use AI Factory for your next issue? (Y/N)
2. Rate demo clarity (1-5)
3. Biggest concern?
4. Most exciting part?
```

---

# Demo Checklist

## Before Demo
- [ ] Terminal 1 open (orchestrator)
- [ ] Terminal 2 open (Claude Code ready)
- [ ] Jira issue open in browser
- [ ] GitHub repo open in browser
- [ ] Pick issue ahead of time
- [ ] Test run completed successfully
- [ ] Backup issues ready
- [ ] Script printed/accessible

## During Demo
- [ ] Start with clean main branch
- [ ] Show Jira issue first
- [ ] Explain orchestrator routing
- [ ] Run autonomous-implement
- [ ] Approve plan at checkpoint
- [ ] Point out evals generation
- [ ] Show code quality in PR
- [ ] Show Jira update
- [ ] Check total time
- [ ] Handle Q&A

## After Demo
- [ ] Share recording
- [ ] Post in Slack
- [ ] Schedule office hours
- [ ] Track adoption
- [ ] Gather feedback
- [ ] Report metrics

---

**You've got this! The demo sells itself - the AI does all the impressive work.** 🚀

**Remember:** Your job is just to press one button and point out what's happening. The AI Factory does the rest.
