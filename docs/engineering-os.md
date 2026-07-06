# Engineering Operating System

## Philosophy

The EM AI Software Factory is built on the concept of an "Engineering Operating System" - a standardized, AI-augmented approach to software development that ensures consistency, quality, and efficiency across all projects.

## Core Principles

### 1. Automation First
Automate repetitive tasks to free developers for creative work:
- Automated code reviews
- Smart commit messages
- PR description generation
- Test plan creation

### 2. Knowledge Preservation
Capture and reuse institutional knowledge:
- Structured implementation plans
- Codebase research and documentation
- Standardized templates
- MCP-based caching

### 3. Quality Gates
Built-in quality checks at every stage:
- Pre-commit hooks for linting and secrets
- Code review before merge
- Validation of implementation plans
- E2E test planning

### 4. Integrated Workflows
Seamless integration with existing tools:
- Jira for issue tracking
- Confluence for documentation
- GitHub for code and PRs
- MCP for extensibility

## Workflow Patterns

### Feature Development Flow

```
1. /create-plan          → Generate implementation plan from Jira ticket
2. /implement-plan       → Execute the plan step-by-step
3. /code-review          → Review changes for quality
4. /commit               → Smart commit with automated checks
5. /describe-pr          → Generate comprehensive PR description
6. /create-pr            → Create pull request
```

### Bug Fix Flow

```
1. /create-bug           → Document bug with context
2. /research-codebase    → Understand related code
3. /create-plan          → Plan the fix
4. Fix implementation
5. /code-review          → Verify the fix
6. /commit & /create-pr  → Submit for review
```

### Research & Documentation Flow

```
1. /research-codebase    → Deep dive into codebase
2. /create-epic          → Document findings as epic
3. Update Confluence     → Share knowledge
```

### Testing Flow

```
1. /create-e2e-testplan  → Create comprehensive test plan
2. /dogfood              → Manual testing with reporting
3. /update-e2e-testplan  → Evolve tests based on findings
```

## Knowledge Management

### Caching Strategy

All external data (Jira tickets, Confluence pages) is cached to `.claude/cache/` to:
- Reduce API calls
- Speed up repeated access
- Enable offline work
- Preserve point-in-time snapshots

### Structured Artifacts

All work products are stored in predictable locations:
- `.claude/bugs/` - Bug reports
- `.claude/reviews/` - Code reviews
- `.claude/prs/` - PR descriptions
- `specs/features/` - Implementation plans
- `specs/research/` - Research documents
- `specs/testing/e2e/` - Test plans

This structure enables:
- Easy discovery
- Version control
- Cross-reference
- AI context loading

## Skill Categories

### Planning & Architecture
Skills that help design before implementation:
- `/create-plan` - Structured implementation planning
- `/validate-plan` - Plan review and validation
- `/research-codebase` - Code exploration and documentation

### Implementation
Skills that assist during development:
- `/implement-plan` - Guided implementation
- `/code-review` - Quality assurance
- `/commit` - Automated commit workflow
- `/generate-migration` - Database changes

### Integration & Delivery
Skills for shipping:
- `/describe-pr` - PR documentation
- `/create-pr` - PR creation
- `/split-pr` - Large PR management

### Testing & Quality
Skills for verification:
- `/create-e2e-testplan` - Test strategy
- `/update-e2e-testplan` - Test evolution
- `/dogfood` - Manual testing workflow

### Issue Tracking
Skills for project management:
- `/create-bug` - Bug documentation
- `/create-bug-from-video` - Visual bug reporting
- `/create-epic` - Epic planning

## Measuring Success

The Engineering OS optimizes for:

1. **Velocity** - Faster feature delivery through automation
2. **Quality** - Fewer bugs through systematic reviews
3. **Consistency** - Standardized workflows across teams
4. **Knowledge** - Preserved context and documentation
5. **Scalability** - Repeatable processes that work at any scale

## Evolution

The Engineering OS is designed to evolve:
- Skills can be added as workflows emerge
- Templates adapt to team preferences
- Hooks enforce evolving standards
- MCP integration extends capabilities

This living system grows with your organization's needs.
