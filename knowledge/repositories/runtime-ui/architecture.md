<!--
AUTO-GENERATED from runtime-ui
Last sync: 2026-06-29 06:53:27 UTC
Source commit: 3c84f56de5f64bb8c919c0e0fd32a8bf61c9520a
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# runtime-ui Architecture

## Overview

## Architecture

| Workspace | Purpose |
| --------- | ------- |
| `core/` | Host SPA — auth, routing, navigation, and all current features |
| `packages/ui-common/` | Shared design system (`@emergence-ai/em-ui-common`) |
| `tools/create-emergence-app/` | CLI for scaffolding new micro-frontends |
| `apps/` | Reserved for future micro-frontends (currently empty) |

`core` acts as the Module Federation **host**. It handles authentication (Keycloak), routing (TanStack Router), and loads remote micro-frontend apps dynamically at the `/apps` route when available.

