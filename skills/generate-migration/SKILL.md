---
name: generate-migration
description: Generate database migration files from schema change descriptions
---

# Generate Migration

Generate database migration files from schema change descriptions. Understands the project's migration framework, existing schema, and conventions to produce correct, safe migrations.

## When to Use This Skill

Use this skill when:
- You need to add/modify/remove database tables or columns
- A Jira ticket requires schema changes
- You want to generate migration files following project conventions
- You need to update the schema as part of a feature implementation

## Initial Response

When invoked without parameters:

```
I'll help you generate a database migration. Please provide:
1. What schema changes are needed (add table, add column, modify type, etc.)
2. Optional: Jira ticket reference for context (e.g., SEMI-XXX)

Examples:
  /generate-migration Add a "status" column to the workflow_runs table
  /generate-migration SEMI-790 Add indexes for the new query patterns
```

## Process

### Step 1: Understand the Migration Framework

**Research the project's migration setup:**
- Search for existing migration files to understand the framework
- Check for migration configuration (alembic.ini, knex config, etc.)
- Identify the migration directory and naming convention
- Read 2-3 recent migrations to understand patterns

**Common frameworks to look for:**
- **Python/SQLAlchemy:** Alembic migrations in `alembic/versions/`
- **Python/Django:** Migrations in `app/migrations/`
- **Node.js/Knex:** Migrations in `migrations/`
- **Supabase:** SQL migrations in `supabase/migrations/`
- **Prisma:** Migrations in `prisma/migrations/`
- **TypeORM:** Migrations in `src/migrations/`

### Step 2: Understand Current Schema

**Read the current schema:**
- Find and read the current schema definition
- Identify related tables and foreign keys
- Check for existing indexes, constraints, and triggers
- Understand the data model around the change

**If Jira ticket provided:**
- Fetch ticket context via MCP
- Understand why the schema change is needed
- Check if an implementation plan exists with schema details

### Step 3: Design the Migration

**Present the migration plan:**

```
# Migration Plan

## Changes
1. [ADD/MODIFY/DROP] [table/column/index] - [description]
2. ...

## SQL Preview

### Up Migration
```sql
-- Add status column to workflow_runs
ALTER TABLE workflow_runs
  ADD COLUMN status TEXT NOT NULL DEFAULT 'pending';

-- Add index for status queries
CREATE INDEX idx_workflow_runs_status
  ON workflow_runs (status);
```

### Down Migration (Rollback)
```sql
DROP INDEX IF EXISTS idx_workflow_runs_status;
ALTER TABLE workflow_runs DROP COLUMN IF EXISTS status;
```

## Impact
- Tables affected: [list]
- Estimated rows affected: [if modifying existing data]
- Downtime required: No / Yes (brief)
- Data loss risk: None / [describe]

Shall I generate the migration file?
```

**Wait for user approval.**

### Step 4: Generate Migration File

**Follow project conventions exactly:**
- Use the correct framework API
- Follow the project's naming convention for migration files
- Include both up and down migrations
- Add appropriate comments
- Handle data migrations separately from schema migrations

**Safety practices:**
- Always include rollback (down migration)
- Use `IF EXISTS` / `IF NOT EXISTS` for safety
- Set sensible defaults for new NOT NULL columns
- Consider existing data when modifying columns
- Add indexes for frequently queried columns

### Step 5: Verify

**After generating:**
- Read the generated file to verify correctness
- Check that it follows existing migration patterns
- Verify foreign key references are correct
- Ensure the rollback actually reverses the changes
- Run the migration if possible (dry-run or test database)

```
Migration generated at: [file path]

Please verify:
1. Review the migration SQL/code
2. Run on test database: [project-specific command]
3. Test rollback: [rollback command]
4. Verify schema matches expectations
```

## Guidelines

**Safety first:**
- Never drop tables/columns without explicit user confirmation
- Always provide rollback migrations
- Handle existing data gracefully
- Consider the impact on running applications

**Follow conventions:**
- Match the project's migration framework exactly
- Use the same naming patterns as existing migrations
- Follow the same code style and comments

**Think about production:**
- Will this lock tables? For how long?
- Is this backwards compatible?
- Can it be deployed without downtime?
- What happens to existing data?

## Usage Examples

```bash
# Simple column addition
/generate-migration Add an "archived" boolean column to the products table

# With ticket context
/generate-migration SEMI-790 Add schema changes for the new streaming feature

# Complex change
/generate-migration Create a new "audit_logs" table with user_id, action, timestamp, and details columns
```

## Integration with Other Skills

```bash
# 1. Plan the feature (includes schema changes)
/create-plan SEMI-790

# 2. Generate migration first
/generate-migration SEMI-790

# 3. Implement the rest
/implement-plan SEMI-790
```
