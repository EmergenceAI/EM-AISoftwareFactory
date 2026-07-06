/**
 * Autonomous Sprint Skill
 *
 * Wrapper skill that invokes the autonomous-sprint workflow
 * for parallel implementation of multiple Jira issues.
 */

// Parse arguments
const jql = args.jql
const project = args.project
const sprint = args.sprint
const component = args.component
const maxConcurrent = args.maxConcurrent || args['max-concurrent'] || 8
const dryRun = args.dryRun || args['dry-run'] || false
const includeAll = args.includeAll || args['include-all'] || false

// Validate arguments
if (!jql && !project) {
  throw new Error('Either --jql or --project must be provided')
}

// Build workflow args
const workflowArgs = {
  jql,
  project,
  sprint,
  component,
  maxConcurrent,
  dryRun,
  includeAll
}

// Invoke the autonomous-sprint workflow
const result = await workflow('autonomous-sprint', workflowArgs)

// Return result
return result
