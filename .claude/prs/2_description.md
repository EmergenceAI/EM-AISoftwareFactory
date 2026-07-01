## What does this PR do?

Adds batch epic creation capability to the `create-epic` skill, enabling users to create multiple Jira epics from structured tables (CSV, Excel, Markdown, JSON) in a single operation.

## Why are we doing this?

When planning roadmaps or organizing large initiatives, teams often define multiple epics in spreadsheets or planning documents. Previously, each epic had to be created individually through an interactive process. This enhancement streamlines the workflow by allowing batch creation directly from table data.

## What problem does it solve?

**Problem:** Creating multiple epics individually is time-consuming and repetitive when working with:
- Roadmap planning documents with 10+ epics
- Initiative breakdowns from planning sessions
- Epic backlogs maintained in spreadsheets
- Migrating epics from other systems

**Solution:** Batch import epics from structured tables while maintaining the same quality and template structure as single epic creation.

## How does it solve the problem?

### Key Implementation

1. **Table Parsing:**
   - Supports CSV, Excel (.xlsx, .xls), TSV, Markdown tables, and JSON
   - Validates required columns (Title, Vision, Overview, Current State, Desired State, Impact, Success Criteria, User Value, Business Impact, Strategic Alignment)
   - Preserves multi-line content, bullet points, and formatting within cells

2. **Batch Processing:**
   - Shows preview of all epics before creation
   - Creates epics sequentially with progress tracking
   - Handles failures gracefully and continues with remaining epics
   - Reports summary with success/failure status for each epic

3. **Template Compliance:**
   - Maintains same epic template structure as single mode
   - Supports optional columns (Project, Priority, Labels, Assignee)
   - Applies consistent formatting and validation

### Files Changed

- **`skills/create-epic/SKILL.md`** (+286 lines)
  - Added "Table Format for Batch Epic Creation" section
  - Added batch creation process documentation
  - Added comprehensive examples with CSV structure
  - Updated usage instructions

- **`skills/create-epic/example-epics-template.csv`** (+109 lines)
  - New: Example CSV template with complete epic structure
  - Demonstrates proper formatting for multi-line content
  - Shows all required and optional columns

- **`TESTING.md`** (+192 lines)
  - New: Complete testing guide for batch epic creation
  - Step-by-step verification instructions
  - Small and large batch test scenarios
  - Expected behavior documentation

- **`TEST-EPIC-PREVIEW.md`** (+120 lines)
  - New: Preview of what created epics look like
  - Shows fully formatted epic structure
  - Reference for validating epic quality

- **`README.md`** (+23 lines)
  - Updated to document batch creation capability
  - Added usage examples
  - Added link to testing guide

- **`.claude-plugin/plugin.json`** (+1 line)
  - Updated skill description to mention batch capability

## What are the changes?

### User-Facing Changes
- ✨ New: Create multiple epics from CSV/Excel files with `--from-table` flag
- ✨ New: Inline table support (paste table data directly)
- ✨ New: Preview all epics before creation with confirmation prompt
- ✨ New: Progress tracking and summary report for batch operations
- 📖 New: Comprehensive testing guide (`TESTING.md`)
- 📖 New: CSV template example (`skills/create-epic/example-epics-template.csv`)

### Internal/Technical Changes
- Enhanced skill documentation with batch creation process
- Added table format specifications and examples
- Created reusable CSV template for teams
- Added preview and testing documentation

### Breaking Changes
- [ ] None - This is a backwards-compatible feature addition

## How to verify it

### Automated Verification
- [ ] Tests: Not applicable (skill-based feature)
- [ ] Linting: Not applicable
- [ ] Type checking: Not applicable

### Manual Verification

Follow the testing guide in `TESTING.md`:

1. **Small batch test (3 epics):**
   ```bash
   /create-epic --from-table craft-mvp-epics-sample.csv
   ```
   - Verify preview shows all 3 epics correctly
   - Confirm creation
   - Check all 3 epics created in Jira

2. **Large batch test (34 epics):**
   ```bash
   /create-epic --from-table craft-mvp-epics-remaining.csv
   ```
   - Verify preview shows all epics
   - Confirm creation
   - Verify summary report shows success/failure for each

3. **Verify epic structure:**
   - Open created epics in Jira
   - Check all sections present (Vision, Overview, Problem Statement, Success Criteria, Business Value)
   - Verify formatting preserved (bullet points, line breaks)
   - Confirm labels and metadata applied correctly

4. **Compare with reference:**
   - Check `TEST-EPIC-PREVIEW.md` for expected structure
   - Validate epics match template quality

## Related Documents

- Testing Guide: `TESTING.md`
- CSV Template: `skills/create-epic/example-epics-template.csv`
- Example Preview: `TEST-EPIC-PREVIEW.md`
- Skill Documentation: `skills/create-epic/SKILL.md`

## Checklist

- [x] Tests added/updated - Testing guide provided in `TESTING.md`
- [x] Documentation updated - README, SKILL.md, TESTING.md, example files
- [x] No breaking changes - Backwards compatible feature addition
- [x] Security implications considered - No new security concerns
- [x] Performance implications considered - Batch creation is more efficient than individual

## Screenshots/Examples

See `TEST-EPIC-PREVIEW.md` for complete example of created epic structure.

**CSV Format Example:**
```csv
Title,Vision,Overview,Current State,Desired State,Impact,Success Criteria,User Value,Business Impact,Strategic Alignment,Project,Priority,Labels
"Epic Title","Vision statement","Overview paragraph","Current state description","- Bullet 1
- Bullet 2","Customer/Business/Strategic impact","- Criteria 1
- Criteria 2","User benefits","Business outcomes","Strategic alignment",SEMI,High,"label1,label2"
```

## Additional Notes

### Usage Patterns

**Quick batch creation:**
```bash
/create-epic --from-table epics.csv
```

**Review before creating:**
1. Preview shows full content of all epics
2. Confirmation required before creation
3. Summary report after completion

### Benefits

- **Time savings:** Create 30+ epics in minutes vs hours
- **Consistency:** All epics follow template structure
- **Traceability:** CSV source serves as planning artifact
- **Collaboration:** Teams can prepare epics in spreadsheets collaboratively

### Future Enhancements

Potential follow-ups (not in this PR):
- Epic linking/dependencies from CSV
- Epic hierarchy (parent/child) support
- Validation warnings for incomplete data
- Dry-run mode to preview without creating
