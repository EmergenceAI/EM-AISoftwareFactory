<!--
AUTO-GENERATED from craft
Last sync: 2026-11-04 01:50:35 UTC
Source commit: 71f896aec73fed4d4847b03a2c4d3e41c348980f
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# craft Coding Conventions

## Code Style

### TypeScript/JavaScript (from package.json)
```json
{
  "scripts": {
    "format": "biome check .",
    "format:fix": "biome check --write .",
    "lint": "pnpm -C control-plane lint",
    "typecheck": "pnpm -C control-plane typecheck",
    "test": "pnpm -C control-plane test",
    "test:int": "pnpm -C control-plane test:int",
    "dep:check": "pnpm -C control-plane dep:check",
    "changeset": "changeset"
  },
  "eslintConfig": null,
  "prettier": null
}
```

## Testing Conventions

- Test files: `**/*.test.ts` or `**/*.spec.ts`
