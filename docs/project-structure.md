# Project Structure

## Directory Layout

```
your-repo/
├── .claude/
│   ├── settings.local.json           ← Permissions (gitignored)
│   ├── cache/                         ← Cached Jira tickets & Confluence pages
│   │   ├── YOUR-PROJECT-XXX.md
│   │   └── CONF-XXXXX.md
│   ├── bugs/                          ← Bug reports created via /create-bug
│   ├── reviews/                       ← Code reviews
│   ├── prs/                           ← PR descriptions
│   └── plugins/
│       └── em-software-factory/       ← This plugin
│           ├── .claude-plugin/plugin.json
│           ├── .mcp.json              ← MCP server configuration
│           ├── README.md
│           ├── hooks/                 ← Security checks, linting
│           ├── scripts/               ← Helper scripts
│           ├── templates/             ← PR templates
│           └── skills/                ← 16 SDLC skills
├── specs/
│   ├── features/                      ← Implementation plans
│   ├── research/                      ← Research documents
│   └── testing/e2e/                   ← E2E test plans
├── dogfood-output/                    ← Dogfooding reports (gitignored)
│   ├── report.md
│   ├── screenshots/
│   └── videos/
└── tests/e2e/                         ← Automated E2E tests
```

## Key Directories

### `.claude/cache/`
MCP-fetched Jira tickets and Confluence pages are cached here for performance. Delete cached files to force a refresh.

### `.claude/bugs/`
Bug reports created via `/create-bug` are stored here before being synced to Jira.

### `.claude/reviews/`
Code review outputs from `/code-review` are saved here.

### `specs/features/`
Implementation plans created by `/create-plan` are stored here.

### `dogfood-output/`
Dogfooding test reports, screenshots, and videos from `/dogfood` workflow.

## Plugin Structure

```
em-software-factory/
├── .claude-plugin/
│   └── plugin.json              ← Plugin manifest
├── .mcp.json                    ← MCP server configuration
├── hooks/
│   ├── hooks.json               ← Hook definitions
│   ├── lint-changed.sh          ← Linting automation
│   └── check-secrets.sh         ← Secret detection
├── scripts/                     ← Helper scripts
├── templates/
│   ├── pr_description.md        ← PR template
│   └── dogfood-report-template.md
└── skills/                      ← All SDLC skills
    ├── create-plan/
    ├── code-review/
    ├── commit/
    └── ... (16 total)
```

## How It Works

All Jira and Confluence integration is handled via the **Atlassian MCP server** (`sooperset/mcp-atlassian`). 

When Claude needs ticket or page data, it calls MCP tools like:
- `mcp__atlassian__jira_get_issue`
- `mcp__atlassian__confluence_get_page`

No Python scripts or manual API calls needed. Results are cached to `.claude/cache/` for performance.
