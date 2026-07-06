/**
 * Autonomous Sprint Workflow
 *
 * Autonomously implement Jira sprint issues with parallel execution,
 * eval-based validation, and automated PR creation.
 *
 * Usage:
 *   /autonomous-sprint --jql "project = ABI AND sprint = 'Sprint 23' AND component = 'Talk2Data'"
 *   /autonomous-sprint --project ABI --sprint "Sprint 23" --component "Talk2Data"
 *   /autonomous-sprint --jql "key IN (ABI-123, ABI-124, ABI-125)"
 */

export const meta = {
  name: 'autonomous-sprint',
  description: 'Autonomous parallel implementation of Jira sprint issues with eval validation',
  phases: [
    { title: 'Setup', detail: 'Query Jira and create branches' },
    { title: 'Audit', detail: 'Filter out completed work' },
    { title: 'Implement', detail: 'Parallel autonomous implementation with evals' }
  ]
}

// Parse arguments
const jql = args.jql || constructJQL(args)
const maxConcurrent = args.maxConcurrent || 8
const dryRun = args.dryRun || false

log(`Starting autonomous sprint with JQL: ${jql}`)
if (dryRun) {
  log('DRY RUN MODE: No changes will be made')
}

// ============================================================================
// Phase 1: Setup - Query Jira and Create Branches
// ============================================================================

phase('Setup')

log('Querying Jira for issues...')

const setupResult = await agent(
  `Use /jira-to-branches skill with JQL: "${jql}"

  This will:
  1. Query Jira for matching issues
  2. Create standardized GitHub branches
  3. Update Jira with branch links

  Return the list of issues with their branches.`,
  {
    label: 'jira-setup',
    schema: {
      type: 'object',
      properties: {
        issues: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              key: { type: 'string' },
              summary: { type: 'string' },
              type: { type: 'string' },
              branch: { type: 'string' },
              created: { type: 'boolean' }
            }
          }
        },
        summary: {
          type: 'object',
          properties: {
            total: { type: 'number' },
            created: { type: 'number' },
            skipped: { type: 'number' }
          }
        }
      }
    }
  }
)

const issues = setupResult.issues || []

if (issues.length === 0) {
  log('No issues found matching JQL query')
  return {
    status: 'completed',
    totalIssues: 0,
    message: 'No issues to implement'
  }
}

log(`Found ${issues.length} issues. Created ${setupResult.summary.created} new branches.`)

if (dryRun) {
  log('DRY RUN: Stopping before audit phase')
  return {
    status: 'dry-run',
    issues: issues,
    message: `Would implement ${issues.length} issues`
  }
}

// ============================================================================
// Phase 2: Audit - Filter Out Completed Work
// ============================================================================

phase('Audit')

log('Auditing issues for existing implementations...')

const auditResults = await parallel(
  issues.map(issue => () =>
    agent(
      `Use /research-codebase to check if issue ${issue.key} is already implemented.

      Search for:
      - Existing PRs mentioning ${issue.key}
      - Commits referencing ${issue.key}
      - Code comments with ${issue.key}

      Return:
      - status: 'needs-implementation' if not implemented
      - status: 'has-pr' if PR exists (open or merged)
      - status: 'implemented' if code exists
      - reason: explanation`,
      {
        label: `audit-${issue.key}`,
        schema: {
          type: 'object',
          properties: {
            issueKey: { type: 'string' },
            status: {
              type: 'string',
              enum: ['needs-implementation', 'has-pr', 'implemented']
            },
            reason: { type: 'string' },
            prUrl: { type: 'string' }
          }
        }
      }
    )
  )
)

// Filter issues that need implementation
const needsWork = issues.filter((issue, index) => {
  const auditResult = auditResults[index]
  return auditResult && auditResult.status === 'needs-implementation'
})

const skippedCount = issues.length - needsWork.length

log(`Audit complete: ${needsWork.length} need implementation, ${skippedCount} skipped`)

if (skippedCount > 0) {
  const skipped = issues.filter((issue, index) => {
    const auditResult = auditResults[index]
    return auditResult && auditResult.status !== 'needs-implementation'
  })

  log('Skipped issues:')
  skipped.forEach((issue, index) => {
    const auditResult = auditResults[issues.indexOf(issue)]
    log(`  - ${issue.key}: ${auditResult.reason}`)
  })
}

if (needsWork.length === 0) {
  log('All issues already implemented!')
  return {
    status: 'completed',
    totalIssues: issues.length,
    implemented: 0,
    skipped: skippedCount,
    message: 'No new work needed'
  }
}

// ============================================================================
// Phase 3: Implement - Parallel Autonomous Implementation
// ============================================================================

phase('Implement')

log(`Starting parallel implementation of ${needsWork.length} issues (max ${maxConcurrent} concurrent)...`)

const results = await pipeline(
  needsWork,

  // Stage 1: Autonomous implementation (parallel, each in worktree)
  issue => agent(
    `Use /autonomous-implement skill to implement issue ${issue.key}.

    This will:
    1. Fetch Jira issue details
    2. Research codebase
    3. Create implementation plan
    4. Generate evals from acceptance criteria
    5. Implement the solution
    6. Run evals (retry up to 3 times on failure)
    7. Create PR if evals pass
    8. Run code review
    9. Update Jira

    Work in isolated git worktree to avoid conflicts.

    Return complete implementation results including:
    - status (success/partial/failed)
    - PR URL if created
    - Eval results
    - Timeline`,
    {
      label: `implement-${issue.key}`,
      isolation: 'worktree',  // Isolated worktree per agent
      schema: {
        type: 'object',
        properties: {
          issueKey: { type: 'string' },
          status: {
            type: 'string',
            enum: ['success', 'partial', 'failed']
          },
          pr: {
            type: 'object',
            properties: {
              number: { type: 'number' },
              url: { type: 'string' }
            }
          },
          evalResults: {
            type: 'object',
            properties: {
              passed: { type: 'number' },
              failed: { type: 'number' },
              total: { type: 'number' }
            }
          },
          totalDuration: { type: 'number' },
          error: { type: 'string' }
        }
      }
    }
  )
)

// ============================================================================
// Summary and Results
// ============================================================================

// Filter results
const succeeded = results.filter(r => r && r.status === 'success')
const partial = results.filter(r => r && r.status === 'partial')
const failed = results.filter(r => r && r.status === 'failed')

// Calculate totals
const totalEvalsPassed = results.reduce((sum, r) =>
  sum + (r?.evalResults?.passed || 0), 0
)
const totalEvalsRun = results.reduce((sum, r) =>
  sum + (r?.evalResults?.total || 0), 0
)

const totalDuration = results.reduce((sum, r) =>
  sum + (r?.totalDuration || 0), 0
)

// Log summary
log('')
log('=' .repeat(60))
log('AUTONOMOUS SPRINT COMPLETE')
log('=' .repeat(60))
log('')
log(`Total Issues: ${issues.length}`)
log(`  Implemented: ${succeeded.length} ✓`)
log(`  Partial: ${partial.length} ⚠`)
log(`  Failed: ${failed.length} ✗`)
log(`  Skipped: ${skippedCount} (already done)`)
log('')
log(`Eval Results: ${totalEvalsPassed}/${totalEvalsRun} passed`)
log(`Total Duration: ${Math.round(totalDuration / 60)} minutes`)
log('')

// Successful implementations
if (succeeded.length > 0) {
  log('✓ Successful Implementations:')
  succeeded.forEach(r => {
    log(`  ${r.issueKey}: ${r.pr.url}`)
    log(`    Evals: ${r.evalResults.passed}/${r.evalResults.total} passed`)
  })
  log('')
}

// Partial implementations (evals failed but PR created)
if (partial.length > 0) {
  log('⚠ Partial Implementations (needs review):')
  partial.forEach(r => {
    log(`  ${r.issueKey}: ${r.pr.url} [NEEDS-REVIEW]`)
    log(`    Evals: ${r.evalResults.passed}/${r.evalResults.total} passed`)
    log(`    Failed: ${r.evalResults.failed} tests`)
  })
  log('')
}

// Failed implementations
if (failed.length > 0) {
  log('✗ Failed Implementations:')
  failed.forEach(r => {
    log(`  ${r.issueKey}: ${r.error || 'Unknown error'}`)
  })
  log('')
}

log('Next Steps:')
log('  1. Review PRs for successful implementations')
log('  2. Address eval failures for partial implementations')
log('  3. Investigate and retry failed implementations')

// Return structured results
return {
  status: failed.length === 0 ? 'success' : 'partial',
  totalIssues: issues.length,
  results: {
    succeeded: succeeded.length,
    partial: partial.length,
    failed: failed.length,
    skipped: skippedCount
  },
  evals: {
    passed: totalEvalsPassed,
    total: totalEvalsRun,
    rate: totalEvalsRun > 0 ?
      Math.round((totalEvalsPassed / totalEvalsRun) * 100) : 0
  },
  duration: {
    totalSeconds: totalDuration,
    totalMinutes: Math.round(totalDuration / 60),
    averagePerIssue: needsWork.length > 0 ?
      Math.round(totalDuration / needsWork.length) : 0
  },
  prs: succeeded.concat(partial).map(r => ({
    issueKey: r.issueKey,
    prNumber: r.pr.number,
    prUrl: r.pr.url,
    status: r.status
  }))
}

// ============================================================================
// Helper Functions
// ============================================================================

function constructJQL(args) {
  // Construct JQL from --project, --sprint, --component
  let jql = `project = ${args.project}`

  if (args.sprint) {
    jql += ` AND sprint = '${args.sprint}'`
  }

  if (args.component) {
    jql += ` AND component = '${args.component}'`
  }

  // Default status filter
  if (!args.includeAll) {
    jql += ` AND status IN ('To Do', 'In Progress')`
  }

  return jql
}
