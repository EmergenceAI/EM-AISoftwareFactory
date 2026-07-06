# EM AI Software Factory

A comprehensive Claude Code plugin powered by AI agents for automating and enhancing the Software Development Lifecycle (SDLC).

## Installation

### Requirements

- **Claude Code v2.1.81 or later** — required for plugin support
- Install or update: https://docs.anthropic.com/en/docs/claude-code/getting-started

### Option 1: Install from Private Marketplace (Easiest)

```bash
# In Claude Code
/plugin install em-software-factory@em-plugins
```

This installs the plugin from the private EmergenceAI marketplace. All skills will be available immediately without additional configuration.

### Option 2: Install as Git Submodule (Recommended for Development)

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

### Option 4: Use Relative Path

If both repos are in the same parent directory:

```bash
# From your working repository
claude --plugin-dir ../em-aisoftwarefactory
```

## Quick Start

### 1. Launch Claude Code

```bash
claude --plugin-dir .claude/plugins/em-software-factory
```

### 2. Configure Atlassian (Optional)

If using Jira/Confluence integration:

```bash
export JIRA_URL=https://your-company.atlassian.net
export JIRA_EMAIL=your-email@company.com
export JIRA_API_TOKEN=your_api_token
export JIRA_PROJECT_KEY=YOUR_PROJECT
```

**Get API Token:** https://id.atlassian.com/manage-profile/security/api-tokens

### 3. Install UV (for MCP server)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 4. Verify Setup

In Claude Code:
```
/mcp
```

## Available Skills

**Core Development:**
- `/create-plan` - Generate implementation plans
- `/implement-plan` - Execute implementation plans
- `/validate-plan` - Validate implementation plans
- `/code-review` - Comprehensive code review
- `/describe-pr` - Generate PR descriptions
- `/create-pr` - Create pull requests
- `/commit` - Smart commit with automated checks

**Research & Testing:**
- `/research-codebase` - Analyze and document codebase
- `/create-e2e-testplan` - Create end-to-end test plans
- `/update-e2e-testplan` - Update existing test plans
- `/dogfood` - Dogfooding workflow and reporting

**Jira Integration:**
- `/create-bug` - Create structured bug reports
- `/create-bug-from-video` - Create bugs from video recordings
- `/create-epic` - Create epic documentation

**Utilities:**
- `/generate-migration` - Generate database migrations
- `/split-pr` - Split large PRs into manageable chunks

## Usage Example

```bash
# Create an implementation plan
/create-plan

# Review your changes
/code-review

# Smart commit
/commit

# Research the codebase
/research-codebase "How does authentication work?"
```

## Documentation

- [Engineering Operating System](docs/engineering-os.md) - Philosophy and workflows
- [Project Structure](docs/project-structure.md) - Directory layout and organization
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions
- [Updating the Plugin](docs/updating.md) - How to update and maintain
- [Development Guide](docs/development.md) - Contributing to the plugin

## Support

- Issues: https://github.com/EmergenceAI/EM-AISoftwareFactory/issues

## License

[Add your license here]
