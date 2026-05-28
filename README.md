# EM AI Software Factory

A comprehensive software factory platform powered by AI agents for automating and enhancing the Software Development Lifecycle (SDLC).

## Overview

EM AI Software Factory is a collection of intelligent agents and tooling designed to streamline software development processes. This platform provides automated workflows, quality checks, and development assistance across the entire SDLC.

## Components

### Claude Plugin
Located in `.claude/plugins/em-software-factory/`, this plugin provides:

- **SDLC Skills**: Automated workflows for common development tasks
  - Code review and quality checks
  - PR creation and management
  - Epic and bug tracking
  - Test plan generation and validation
  - Database migration generation

- **Development Hooks**: Pre and post-execution hooks for:
  - Linting changed files
  - Secret detection
  - Automated quality gates

- **Templates**: Standardized templates for:
  - PR descriptions
  - Dogfood reports
  - Documentation

### MCP Integration
The plugin includes MCP (Model Context Protocol) configuration for extended capabilities and integrations.

## Features

- **Automated Code Review**: AI-powered code review with configurable quality checks
- **SDLC Automation**: Skills for managing the complete development lifecycle
- **Security Scanning**: Automated secret detection and security checks
- **Test Planning**: E2E test plan creation and validation
- **Migration Support**: Database migration generation and management
- **Codebase Research**: Intelligent codebase analysis and documentation

## Installation

### Using as a Plugin in Other Repositories

This plugin can be installed in other repositories as a git submodule:

```bash
# Navigate to your target repository
cd /path/to/your/repo

# Add as submodule
git submodule add git@github.com:EmergenceAI/em-software-factory-plugin.git .claude/plugins/em-software-factory

# Commit the submodule
git add .gitmodules .claude/plugins/em-software-factory
git commit -m "Add EM Software Factory plugin"
```

## Usage

Once installed, the plugin's skills are available through Claude Code:

- `/commit` - Smart commit with automated checks
- `/code-review` - Comprehensive code review
- `/create-plan` - Generate implementation plans
- `/create-e2e-testplan` - Create end-to-end test plans
- `/create-bug` - Create structured bug reports
- `/create-epic` - Create epic documentation
- `/research-codebase` - Analyze and document codebase
- `/split-pr` - Split large PRs into manageable chunks
- And more...

## Configuration

The plugin uses hooks and MCP configurations defined in:
- `.claude/plugins/em-software-factory/hooks/hooks.json`
- `.claude/plugins/em-software-factory/.mcp.json`

## Development

This repository serves as the source of truth for the EM Software Factory plugin. Changes made here can be propagated to other repositories using the submodule update mechanism.

## Requirements

- Claude Code CLI or compatible environment
- Git (for submodule management)
- Bash (for hook scripts)

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
