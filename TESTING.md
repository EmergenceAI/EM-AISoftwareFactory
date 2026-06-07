# Testing the Batch Epic Creation Feature

## ✅ Plugin Validation

First, verify the plugin is valid:

```bash
cd /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory
claude plugin validate .
# Should show: ✔ Validation passed
```

## Prerequisites

1. **MCP Atlassian Server Configured**
   - Ensure environment variables are set:
     ```bash
     export JIRA_URL=https://your-company.atlassian.net
     export JIRA_EMAIL=your-email@company.com
     export JIRA_API_TOKEN=your_api_token
     ```

2. **Plugin Loaded**
   - Use the `--plugin-dir .` flag when launching Claude Code
   - The plugin includes `"skills": "./skills"` in plugin.json (fixed in this commit)

## How to Test

### Step 1: Launch Claude Code with Plugin

#### Option A: Test from EM-AISoftwareFactory repository (Simplest)

```bash
# You're already here!
cd /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory

# Launch Claude Code with the current directory as the plugin
claude --plugin-dir .
```

#### Option B: Test from another repository (e.g., em-talk2data)

```bash
cd /Users/malamunisamy/Documents/Development/em-talk2data

# Launch Claude Code with the plugin
claude --plugin-dir /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory
```

### Step 2: Verify Skills Loaded

**Quick CLI test (non-interactive):**
```bash
echo "What skills are available?" | claude --plugin-dir . -p | grep create-epic
```

You should see:
```
- **create-epic** - Create epics using the team's standard template (single or batch from CSV/Excel)
```

**Interactive test:**
In Claude Code session, type `/` and you should see `create-epic` in the autocomplete list.

### Step 3: Test Single Epic Mode (Original Feature)

```bash
/create-epic "Test Epic for ABI"
```

Claude will guide you through the sections interactively.

### Step 4: Test Batch Mode (New Feature)

#### Option A: Using the example template

If testing from EM-AISoftwareFactory:
```bash
/create-epic --from-table skills/create-epic/example-epics-template.csv
```

If testing from another repository:
```bash
/create-epic --from-table /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory/skills/create-epic/example-epics-template.csv
```

#### Option B: Create your own CSV

Create a file `test-epics.csv`:

```csv
Title,Vision,Overview,Current State,Desired State,Impact,Success Criteria,User Value,Business Impact,Strategic Alignment,Project,Priority,Labels
"Test Epic 1","Short vision statement","Overview paragraph","Current state description","- Bullet 1
- Bullet 2","Impact description","- Criteria 1
- Criteria 2","User value","Business impact","Strategic alignment",ABI,Medium,"test,epic"
"Test Epic 2","Another vision","Another overview","Current state","- Desired state","Impact","- Success criteria","User value","Business value","Strategy",ABI,Low,"test"
```

Then run:
```bash
/create-epic --from-table test-epics.csv
```

### Expected Behavior

1. **Parse**: Claude reads and validates the CSV
2. **Preview**: Shows full content of all epics that will be created
3. **Confirm**: Asks "Create these N epics in Jira? [Y/n]"
4. **Create**: If confirmed, creates each epic sequentially
5. **Report**: Shows summary with issue keys and URLs

Example output:
```
Found 2 epics in table. Here's what will be created:

1. Test Epic 1 (ABI, Medium priority)
2. Test Epic 2 (ABI, Low priority)

PREVIEW: Epic 1 of 2
[... full epic preview ...]

PREVIEW: Epic 2 of 2
[... full epic preview ...]

Create all 2 epics in Jira? [Y/n]

✓ Created: ABI-123 - Test Epic 1
✓ Created: ABI-124 - Test Epic 2

Successfully created 2/2 epics
```

## Troubleshooting

### Skill not appearing

**Problem**: `/create-epic` doesn't show up after launching with `--plugin-dir`

**Solution**: 
1. Verify plugin.json has `"skills": "./skills"` (fixed in this commit)
2. Check SKILL.md has proper frontmatter:
   ```yaml
   ---
   name: create-epic
   description: ...
   ---
   ```
3. Restart Claude Code

### MCP not connected

**Problem**: "MCP server not available" or Jira API errors

**Solution**:
1. Run `/mcp` to check server status
2. Verify environment variables: `echo $JIRA_URL`
3. Test MCP manually in Claude Code

### CSV parsing issues

**Problem**: "Invalid CSV format" or missing columns

**Solution**:
1. Ensure all required columns are present (see SKILL.md)
2. Use double quotes for cells with commas or newlines
3. Check example-epics-template.csv for reference format

### Permission errors in Jira

**Problem**: "403 Forbidden" or "Cannot create epic"

**Solution**:
1. Verify you have epic creation permissions in the ABI project
2. Check project key is correct (ABI vs SEMI vs PLAT)
3. Confirm API token has not expired

## Success Criteria

- ✅ `/create-epic` appears in skill list
- ✅ Interactive mode works for single epic creation
- ✅ Batch mode parses CSV correctly
- ✅ Preview shows all epics with full content
- ✅ Epics are created in ABI project with correct metadata
- ✅ Issue keys and URLs are returned
- ✅ Multi-line content (bullet points) is preserved in Jira

## Notes

- The example template is configured for **ABI** project
- All epics use the standard template structure (Vision, Overview, Problem Statement, Success Criteria, Business Value)
- CSV format supports multi-line content with proper quoting
- Batch creation processes epics sequentially (not parallel)
