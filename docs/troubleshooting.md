# Troubleshooting

## MCP Server Issues

### MCP server not connected

**Symptoms:**
- `/mcp` shows server as disconnected
- Jira/Confluence tools unavailable

**Solutions:**
1. Run `/mcp` in Claude Code to check server status
2. Ensure `uv` is installed: `which uvx`
3. Check env vars are set: `echo $JIRA_URL $JIRA_EMAIL $JIRA_API_TOKEN`
4. Restart Claude Code

### "401 Unauthorized" from Jira/Confluence

**Cause:** Invalid or expired API token

**Solutions:**
1. Verify your API token is correct
2. Check that the email matches your Atlassian account
3. Regenerate token at https://id.atlassian.com/manage-profile/security/api-tokens
4. Re-export the environment variables

### "404 Not Found" when fetching ticket

**Cause:** Incorrect ticket key or insufficient permissions

**Solutions:**
1. Check that the ticket key is correct (e.g., `PROJ-123`)
2. Verify you have access to the ticket in Jira
3. Confirm `JIRA_URL` points to the correct Atlassian instance
4. Ensure the project key in the ticket exists

## Cache Issues

### Stale cached data

**Symptoms:**
- Old ticket/page data being used
- Changes in Jira/Confluence not reflected

**Solution:**
```bash
# Delete the cached file
rm .claude/cache/PROJ-XXX.md

# Re-invoke the skill to fetch fresh data
```

## Plugin Loading Issues

### Plugin not loading

**Symptoms:**
- Skills not available as slash commands
- No namespace like `/em-software-factory:skill-name`

**Solutions:**
1. Ensure Claude Code v2.1.81 or later: `claude --version`
2. Verify plugin directory structure:
   ```bash
   ls .claude/plugins/em-software-factory/.claude-plugin/plugin.json
   ```
3. Check `.claude-plugin/plugin.json` is valid JSON
4. Launch with `--plugin-dir` flag:
   ```bash
   claude --plugin-dir .claude/plugins/em-software-factory
   ```

### Skills not appearing

**Symptoms:**
- Plugin loads but skills don't show up

**Solutions:**
1. Verify skills are in `skills/` directory (not `.claude/skills/`)
2. Each skill should have a `SKILL.md` file
3. Check plugin.json has `"skills": "./skills"` entry
4. Restart Claude Code

## Permission Issues

### Hook scripts not executing

**Symptoms:**
- Hooks defined but not running
- No pre/post execution checks

**Solutions:**
1. Make hook scripts executable:
   ```bash
   chmod +x .claude/plugins/em-software-factory/hooks/*.sh
   ```
2. Verify hooks.json is properly configured
3. Check Claude Code settings for hook permissions

## Environment Variable Issues

### Environment variables not available

**Symptoms:**
- MCP tools fail with missing credentials
- Cannot connect to Jira/Confluence

**Solutions:**
1. Export variables in your shell profile (`~/.zshrc` or `~/.bashrc`):
   ```bash
   export JIRA_URL=https://your-company.atlassian.net
   export JIRA_EMAIL=your-email@company.com
   export JIRA_API_TOKEN=your_token
   export JIRA_PROJECT_KEY=PROJ
   ```
2. Source the profile: `source ~/.zshrc`
3. Verify: `env | grep JIRA`
4. Restart Claude Code

## Getting Help

If issues persist:
1. Check logs in Claude Code debug mode
2. Create an issue: https://github.com/EmergenceAI/EM-AISoftwareFactory/issues
3. Contact the AI/DevOps team internally
