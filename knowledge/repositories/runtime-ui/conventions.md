<!--
AUTO-GENERATED from runtime-ui
Last sync: 2026-06-29 06:53:27 UTC
Source commit: 3c84f56de5f64bb8c919c0e0fd32a8bf61c9520a
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# runtime-ui Coding Conventions

## Code Style

### TypeScript/JavaScript (from package.json)
```json
{
  "scripts": {
    "dev": "npm run build --workspace=@emergence-ai/em-ui-common && concurrently --names \"ui-common,core,insights-analyst,registry\" --prefix-colors \"cyan,white,magenta,yellow\" \"npm run dev:ui-common\" \"npm run dev:core\" \"npm run dev:insights-analyst\" \"npm run dev:registry\"",
    "dev:core": "npm run dev --workspace=core",
    "dev:ui-common": "npm run dev --workspace=@emergence-ai/em-ui-common",
    "dev:insights-analyst": "npm run dev --workspace=@apps/insights-analyst-app",
    "dev:registry": "node scripts/mock-registry.js",
    "build": "npm run build --workspaces --if-present",
    "test": "npm run test --workspaces --if-present",
    "test:ci": "npm run test:ci --workspaces --if-present",
    "lint": "npm run lint --workspaces --if-present",
    "fmt:check": "npm run fmt:check --workspaces --if-present",
    "typecheck": "npm run typecheck --workspaces --if-present",
    "prepare": "husky",
    "storybook": "npm run storybook --workspace=@emergence-ai/em-ui-common"
  },
  "eslintConfig": null,
  "prettier": null
}
```

## Testing Conventions

- Test files: `**/*.test.ts` or `**/*.spec.ts`
