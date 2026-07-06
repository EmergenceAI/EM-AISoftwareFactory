# Updating the Plugin

## If Installed as Git Submodule (Recommended)

### Update to Latest Version

```bash
# From your repository root
git submodule update --remote .claude/plugins/em-software-factory

# Commit the update
git add .claude/plugins/em-software-factory
git commit -m "Update EM Software Factory plugin"
```

### Update to Specific Version/Branch

```bash
cd .claude/plugins/em-software-factory
git checkout v1.2.0  # or specific branch
cd ../../../

git add .claude/plugins/em-software-factory
git commit -m "Update plugin to v1.2.0"
```

### Rollback to Previous Version

```bash
cd .claude/plugins/em-software-factory
git checkout <previous-commit-hash>
cd ../../../

git add .claude/plugins/em-software-factory
git commit -m "Rollback plugin to previous version"
```

## If Cloned Directly

### Update to Latest

```bash
cd .claude/plugins/em-software-factory
git pull origin main
```

### Update to Specific Version

```bash
cd .claude/plugins/em-software-factory
git fetch --tags
git checkout v1.2.0
```

## Verifying the Update

After updating:

1. **Check version:**
   ```bash
   cat .claude/plugins/em-software-factory/.claude-plugin/plugin.json | grep version
   ```

2. **Restart Claude Code:**
   ```bash
   claude --plugin-dir .claude/plugins/em-software-factory
   ```

3. **Verify skills are available:**
   ```
   /em-software-factory:code-review
   ```

## Benefits of Submodule Approach

- ✅ Single source of truth for SDLC skills
- ✅ Share improvements across all projects
- ✅ Version control for plugin updates
- ✅ Easy rollback if issues
- ✅ Consistent SDLC workflows across all company repositories

## Keeping Multiple Projects in Sync

If you have the plugin installed in multiple repositories:

```bash
# Update all projects with a script
for repo in project-a project-b project-c; do
  cd ~/dev/$repo
  git submodule update --remote .claude/plugins/em-software-factory
  git add .claude/plugins/em-software-factory
  git commit -m "Update EM Software Factory plugin"
  git push
done
```

## Release Notes

Check the plugin repository for release notes and changelogs:
https://github.com/EmergenceAI/EM-AISoftwareFactory/releases
