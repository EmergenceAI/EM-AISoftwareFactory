# Claude Code Skills & Commands

Custom skills and commands for the EM-AISoftwareFactory development workflow with Jira and Confluence integration via MCP.

## Requirements

- **Claude Code v2.1.81 or later** — required for plugin support. Install or update via: https://docs.anthropic.com/en/docs/claude-code/getting-started

## Launching Claude Code

To use the em-software-factory plugin, launch Claude Code with the `--plugin-dir` flag pointing to the plugin directory:

```bash
claude --plugin-dir .claude/plugins/em-software-factory
```

This loads all skills, hooks, MCP servers, and templates defined in the plugin. Skills are then available as `/em-software-factory:<skill>` (e.g., `/em-software-factory:create-pr`).

## Setup

### 1. Configure Atlassian Credentials

Set these environment variables in your shell profile (`~/.zshrc`, `~/.bashrc`) or via `direnv`:

```bash
# Jira Configuration
export JIRA_URL=https://your-company.atlassian.net
export JIRA_EMAIL=your-email@company.com
export JIRA_API_TOKEN=your_api_token
export JIRA_PROJECT_KEY=EMAI  # Your Jira project key

# Confluence Configuration (same Atlassian token)
export CONFLUENCE_URL=https://your-company.atlassian.net/wiki
export CONFLUENCE_EMAIL=your-email@company.com
export CONFLUENCE_API_TOKEN=your_api_token
```

**Getting an Atlassian API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "Claude Code")
4. Copy the token and set it as both `JIRA_API_TOKEN` and `CONFLUENCE_API_TOKEN`

### 2. MCP Server

The Atlassian MCP server (`mcp-atlassian`) is configured in `.mcp.json` at the project root. It requires `uvx` (from the `uv` Python package manager).

Install `uv` if not already installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

The MCP server starts automatically when Claude Code launches. No additional setup needed.

### 3. Verify Setup

In Claude Code, run `/mcp` to verify the `atlassian` server is connected and healthy.

## Available Skills

**13 SDLC skills** - See [skills.md](../skills.md) for comprehensive documentation.

**Core Development:** create-plan, implement-plan, validate-plan, code-review, describe-pr, create-pr, commit

**Research & Testing:** research-codebase, create-e2e-testplan, update-e2e-testplan, create-bug, dogfood

**Database:** generate-migration

## Project Structure

```
EM-AISoftwareFactory/
├── .mcp.json                          ← MCP server configuration (Atlassian)
├── skills.md                          ← Skills documentation (comprehensive)
├── .claude/
│   ├── README.md                      ← This file (plugin setup guide)
│   ├── settings.local.json           ← Permissions (gitignored)
│   ├── cache/                         ← Cached Jira tickets & Confluence pages
│   │   ├── EMAI-XXX.md
│   │   └── CONF-XXXXX.md
│   ├── templates/
│   │   └── pr_description.md
│   ├── bugs/                          ← Bug reports created via create-bug
│   ├── reviews/                       ← Code reviews
│   ├── prs/                           ← PR descriptions
│   └── plugins/
│       └── em-software-factory/       ← SDLC Plugin (skills, hooks, scripts)
│           ├── .claude-plugin/plugin.json
│           ├── .mcp.json
│           ├── hooks/                 ← Security checks, linting
│           ├── scripts/               ← Helper scripts
│           ├── templates/             ← PR templates
│           └── skills/                ← 13 SDLC skills
├── specs/
│   ├── features/                      ← Implementation plans
│   ├── research/                      ← Research documents
│   └── testing/e2e/                   ← E2E test plans
├── dogfood-output/                    ← Dogfood testing reports (gitignored)
│   ├── report.md
│   ├── screenshots/
│   └── videos/
└── tests/e2e/                         ← Automated E2E tests
```

## How It Works

All Jira and Confluence integration is handled via the **Atlassian MCP server** (`sooperset/mcp-atlassian`). When Claude needs ticket or page data, it calls MCP tools like `mcp__atlassian__jira_get_issue` or `mcp__atlassian__confluence_get_page` — no Python scripts or manual API calls needed.

Results are cached to `.claude/cache/` for performance. Subsequent requests read from cache unless you delete the cached file.

## Troubleshooting

### MCP server not connected
- Run `/mcp` in Claude Code to check server status
- Ensure `uv` is installed: `which uvx`
- Check env vars are set: `echo $JIRA_URL $JIRA_EMAIL $JIRA_API_TOKEN`

### "401 Unauthorized" from Jira/Confluence
- Verify your API token is correct and hasn't expired
- Check that the email matches your Atlassian account
- Regenerate token at https://id.atlassian.com/manage-profile/security/api-tokens

### "404 Not Found" when fetching ticket
- Check that the ticket key is correct (e.g., `EMAI-123`)
- Verify you have access to the ticket in Jira
- Confirm `JIRA_URL` points to the correct Atlassian instance

### Stale cached data
- Delete the cached file: `rm .claude/cache/EMAI-XXX.md`
- Re-invoke the skill to fetch fresh data

---

## Plugin Roadmap

This plugin is currently **inline** (lives inside the EM-AISoftwareFactory repository at `.claude/plugins/em-software-factory/`).

### Next Steps

**Extract to Separate Repository:**
- Create new repo: `EmergenceAI/claude-sdlc-tools`
- Move plugin contents to new repo
- Version and release (v1.0.0)

**Enable Cross-Repo Usage:**
- Install as git submodule in EM-AISoftwareFactory and other EmergenceAI projects
- Consistent SDLC workflows across all company repositories
- Centralized updates: update plugin once, all repos benefit

**Future Usage (any repo):**
```bash
# Install plugin as submodule
git submodule add git@github.com:EmergenceAI/claude-sdlc-tools.git .claude/plugins/claude-sdlc-tools

# Update plugin to latest
git submodule update --remote

# All 13 SDLC skills now available in any repo
```

**Benefits:**
- ✅ Single source of truth for SDLC skills
- ✅ Share improvements across all projects
- ✅ Version control for plugin updates
- ✅ Easy rollback if issues
