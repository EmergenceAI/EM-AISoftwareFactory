# Development Guide

## Contributing to EM Software Factory

This repository serves as the source of truth for the EM Software Factory plugin. Changes made here can be propagated to other repositories using the submodule update mechanism.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/EmergenceAI/EM-AISoftwareFactory.git
cd EM-AISoftwareFactory
```

### 2. Create a Development Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Test Locally

```bash
# From any test repository
claude --plugin-dir /path/to/EM-AISoftwareFactory
```

## Adding a New Skill

### 1. Create Skill Directory

```bash
mkdir -p skills/my-new-skill
```

### 2. Create SKILL.md

```markdown
---
name: my-new-skill
description: Brief description of what this skill does
---

# Skill Instructions

[Detailed instructions for Claude on how to execute this skill]

## Usage

[Examples and usage patterns]
```

### 3. Test the Skill

```bash
# Launch with plugin
claude --plugin-dir .

# In Claude Code
/em-software-factory:my-new-skill
```

### 4. Add Documentation

Update README.md to include your new skill in the available skills list.

## Modifying Hooks

Hooks are defined in `hooks/hooks.json`:

```json
{
  "preExec": {
    "bash": ["./hooks/check-secrets.sh", "./hooks/lint-changed.sh"]
  },
  "postExec": {
    "bash": []
  }
}
```

Hook scripts should:
- Exit with code 0 on success
- Exit with non-zero on failure (blocks execution)
- Be executable: `chmod +x hooks/your-script.sh`

## Updating Templates

Templates are in `templates/`:
- `pr_description.md` - PR template
- `dogfood-report-template.md` - Dogfooding report template

Use Jinja2-style placeholders: `{{ variable_name }}`

## MCP Server Configuration

MCP servers are configured in `.mcp.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "${JIRA_URL}",
        "JIRA_EMAIL": "${JIRA_EMAIL}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
      }
    }
  }
}
```

## Testing Changes

### Local Testing

1. Make your changes
2. Launch Claude with plugin: `claude --plugin-dir .`
3. Test affected skills
4. Verify hooks execute correctly

### Testing in Target Repository

```bash
# In target repo
claude --plugin-dir /path/to/your/EM-AISoftwareFactory
```

## Submitting Changes

### 1. Commit Your Changes

```bash
git add .
git commit -m "feat: Add new skill for XYZ"
```

### 2. Push to Remote

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to https://github.com/EmergenceAI/EM-AISoftwareFactory
2. Click "New Pull Request"
3. Select your branch
4. Fill in PR template
5. Request review

## Code Style

### Skills
- Use clear, imperative descriptions
- Include usage examples
- Document all parameters
- Follow existing skill patterns

### Scripts
- Use bash for portability
- Add error handling
- Include comments
- Make executable

### Documentation
- Keep README concise
- Detailed docs go in `docs/`
- Update all relevant docs with changes

## Release Process

1. Update version in `.claude-plugin/plugin.json`
2. Update CHANGELOG.md
3. Create release tag: `git tag v1.2.0`
4. Push tag: `git push origin v1.2.0`
5. Create GitHub release with notes

## Questions?

- Internal: Contact the AI/DevOps team
- Issues: https://github.com/EmergenceAI/EM-AISoftwareFactory/issues
