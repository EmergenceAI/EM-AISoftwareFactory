# AI Software Factory - Engineering Operating System

**Autonomous software delivery orchestrator** for multi-repository workspaces.

> Transform Jira issues into tested, reviewed pull requests across 7 repositories with 80% automation and 20% strategic human checkpoints.

---

## 📖 Documentation

**Complete documentation:** [docs/README.md](docs/README.md)

### Quick Links

- **[Quickstart Guide](docs/guides/QUICKSTART.md)** - Get started in 5 minutes
- **[Architecture](docs/architecture/ENGINEERING_OS_ARCHITECTURE.md)** - System design
- **[Testing Guide](docs/guides/TESTING_GUIDE.md)** - Run your first workflow
- **[Setup Guides](docs/setup/)** - Knowledge extraction & silent mode

---

## What Is This?

An **Engineering Operating System** that orchestrates software delivery across multiple repositories:

### Key Features

✅ **Automated Knowledge Management**
- Extracts from README.md and docs/ automatically
- Syncs before each run (only if changed)
- Zero maintenance

✅ **80/20 Autonomous Mode**
- 9 skills run with 0 prompts (100% autonomous)
- 3 skills with 1 checkpoint (95% autonomous)
- 3 skills with 2-3 strategic checkpoints (80% autonomous)

✅ **Multi-Repository Support**
- Routes issues to correct repository automatically
- Handles 7 repositories (runtime, runtime-ui, talk2data, data-readiness, semi, connectors, sdk)
- Cross-repo dependency awareness

✅ **Platform Standards Enforcement**
- Air-gapped compatibility (CRITICAL)
- 80% test coverage requirement
- Pacto contract validation
- gitleaks secret detection

### The Architecture

```
Jira Issue → Router → Knowledge Engine → Planner → Executor → Reporter
                ↓           ↓               ↓         ↓          ↓
          Repository   Architecture    Task Graph  Multi-    Sprint
          Selection    Patterns        Dependencies Agent     Metrics
                       Conventions                 Parallel
```

**See [Architecture Docs](docs/architecture/) for complete system design.**

---

## Quick Start

### Current Plugin (Still Works)

A comprehensive Claude Code plugin powered by AI agents for automating and enhancing the Software Development Lifecycle (SDLC).

## Requirements

- **Claude Code v2.1.81 or later** — required for plugin support. Install or update via: https://docs.anthropic.com/en/docs/claude-code/getting-started

## Installation

### Option 1: Install from EmergenceAI Marketplace (Easiest)

If you have access to the EmergenceAI private plugin marketplace:

```bash
# Add the marketplace (first time only)
/plugin marketplace add EmergenceAI/em-claude-plugins

# Install the plugin
/plugin install em-software-factory@em-plugins
```

Once installed, all skills are immediately available in any Claude Code session.

### Option 2: Install as Git Submodule

This plugin can be installed in any repository as a git submodule:

```bash
# Navigate to your target repository
cd /path/to/your/repo

# Add as submodule
git submodule add https://github.com/EmergenceAI/EM-AISoftwareFactory.git .claude/plugins/em-software-factory

# Initialize and update
git submodule update --init --recursive

# Commit the submodule
git add .gitmodules .claude/plugins/em-software-factory
git commit -m "Add EM Software Factory plugin"
```

### Option 3: Clone Directly

```bash
# Navigate to your project's .claude directory
cd /path/to/your/repo/.claude

# Create plugins directory if needed
mkdir -p plugins

# Clone the plugin
git clone https://github.com/EmergenceAI/EM-AISoftwareFactory.git plugins/em-software-factory
```

## Launching Claude Code

**If installed from marketplace (Option 1):** Skills are automatically available in all Claude Code sessions. No additional flags needed.

**If installed as submodule/clone (Options 2-3):** Launch Claude Code with the `--plugin-dir` flag:

```bash
claude --plugin-dir .claude/plugins/em-software-factory
```

This loads all skills, hooks, MCP servers, and templates defined in the plugin. Skills are available as slash commands (e.g., `/create-pr`, `/code-review`).

## Setup

### 1. Configure Atlassian Credentials (Optional)

If you're using Jira/Confluence integration, set these environment variables:

```bash
# Jira Configuration
export JIRA_URL=https://your-company.atlassian.net
export JIRA_EMAIL=your-email@company.com
export JIRA_API_TOKEN=your_api_token
export JIRA_PROJECT_KEY=YOUR_PROJECT  # Your Jira project key

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

The Atlassian MCP server (`mcp-atlassian`) is configured in `.mcp.json`. It requires `uvx` (from the `uv` Python package manager).

Install `uv` if not already installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

The MCP server starts automatically when Claude Code launches. No additional setup needed.

### 3. Verify Setup

In Claude Code, run `/mcp` to verify the `atlassian` server is connected and healthy.

## Features & Components

### SDLC Skills (16 Available)

**Core Development:**
- `/create-plan` - Generate implementation plans
- `/implement-plan` - Execute implementation plans
- `/validate-plan` - Validate implementation plans
- `/code-review` - Comprehensive code review
- `/describe-pr` - Generate PR descriptions
- `/create-pr` - Create pull requests with automation
- `/commit` - Smart commit with automated checks

**Research & Documentation:**
- `/research-codebase` - Analyze and document codebase

**Testing:**
- `/create-e2e-testplan` - Create end-to-end test plans
- `/update-e2e-testplan` - Update existing test plans
- `/dogfood` - Dogfooding workflow and reporting

**Bug Tracking & Epic Management:**
- `/create-bug` - Create structured bug reports
- `/create-bug-from-video` - Create bugs from video recordings
- `/create-epic` - Create epic documentation (single or batch from table)

**Database:**
- `/generate-migration` - Generate database migrations

**PR Management:**
- `/split-pr` - Split large PRs into manageable chunks

### Development Hooks

Pre and post-execution hooks for:
- Linting changed files (`lint-changed.sh`)
- Secret detection (`check-secrets.sh`)
- Automated quality gates

### Templates

Standardized templates for:
- PR descriptions (`templates/pr_description.md`)
- Dogfood reports (`templates/dogfood-report-template.md`)

### MCP Integration

The plugin includes MCP (Model Context Protocol) configuration for:
- Atlassian (Jira & Confluence) integration
- Extended capabilities and custom tools

## Project Structure

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
├── dogfood-output/                    ← Dogfood testing reports (gitignored)
│   ├── report.md
│   ├── screenshots/
│   └── videos/
└── tests/e2e/                         ← Automated E2E tests
```

## How It Works

All Jira and Confluence integration is handled via the **Atlassian MCP server** (`sooperset/mcp-atlassian`). When Claude needs ticket or page data, it calls MCP tools like `mcp__atlassian__jira_get_issue` or `mcp__atlassian__confluence_get_page` — no Python scripts or manual API calls needed.

Results are cached to `.claude/cache/` for performance. Subsequent requests read from cache unless you delete the cached file.

## Usage Examples

### Creating an Implementation Plan
```bash
# In Claude Code
/create-plan

# Then describe your feature or reference a Jira ticket
"Create a plan for PROJ-123"
```

### Code Review
```bash
# After making changes
/code-review

# Claude will review your diff and provide feedback
```

### Smart Commit
```bash
# Stage your changes
git add .

# Use the commit skill
/commit

# Claude will analyze changes and create an appropriate commit message
```

### Research Codebase
```bash
/research-codebase

# Then ask your question
"How does authentication work in this codebase?"
```

### Create Epic (Single)
```bash
# Interactive epic creation
/create-epic "Build Your Own Workflow"

# Claude will guide you through each section collaboratively
```

### Create Epics (Batch from Table)
```bash
# From CSV file
/create-epic --from-table roadmap-q2-2026.csv

# From Excel spreadsheet
/create-epic --from-table epic-planning.xlsx

# Claude will preview all epics before creating them in Jira
```

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
- Check that the ticket key is correct (e.g., `PROJ-123`)
- Verify you have access to the ticket in Jira
- Confirm `JIRA_URL` points to the correct Atlassian instance

### Stale cached data
- Delete the cached file: `rm .claude/cache/PROJ-XXX.md`
- Re-invoke the skill to fetch fresh data

### Plugin not loading
- Ensure Claude Code v2.1.81 or later
- Verify plugin directory structure is correct
- Check `.claude-plugin/plugin.json` exists and is valid
- Launch with `--plugin-dir` flag

## Updating the Plugin

### If installed from marketplace:
```bash
# Update to latest version
/plugin marketplace update em-plugins
```

### If installed as git submodule:
```bash
# Update to latest version
git submodule update --remote .claude/plugins/em-software-factory

# Commit the update
git add .claude/plugins/em-software-factory
git commit -m "Update EM Software Factory plugin"
```

### If cloned directly:
```bash
cd .claude/plugins/em-software-factory
git pull origin main
```

## Development

This repository serves as the source of truth for the EM Software Factory plugin. Changes made here can be propagated to other repositories using the submodule update mechanism.

### Benefits of Submodule Approach:
- ✅ Single source of truth for SDLC skills
- ✅ Share improvements across all projects
- ✅ Version control for plugin updates
- ✅ Easy rollback if issues
- ✅ Consistent SDLC workflows across all company repositories

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues, feature requests, or questions:
- Create an issue: https://github.com/EmergenceAI/EM-AISoftwareFactory/issues
- Internal: Contact the AI/DevOps team
