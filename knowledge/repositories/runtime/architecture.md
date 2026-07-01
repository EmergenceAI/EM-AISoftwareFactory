<!--
AUTO-GENERATED from runtime
Last sync: 2026-06-29 06:53:27 UTC
Source commit: 75b67ca25effe1e76ecbbef03d20bf8fe1d40b84
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# runtime Architecture

## Overview

## Architecture

**Runtime Services:**

| Service | Description | Port |
|---------|-------------|------|
| **em-runtime-governance** | Data governance, organizations, projects, and permissions | 8001 |
| **em-runtime-assets** | Asset storage and management | 8002 |
| **em-runtime-utils** | Utility services and helpers | 8003 |
| **em-runtime-mcp** *(optional client)* | [MCP](https://modelcontextprotocol.io/) server (e.g. Claude Code) over HTTP. Default in Docker Compose (`make docker-run`, `http://localhost:8004/mcp`) and in the Helm chart (`/mcp` via Gateway when enabled). See [`packages/em_runtime_mcp/README.md`](packages/em_runtime_mcp/README.md) | 8004 |
| **em-runtime-search** | Unified search service | 8005 |

**Infrastructure:**
- PostgreSQL (multi-database)
- Redis (caching and sessions)
- Keycloak (identity and realm management)
- OpenFGA (relationship-based access control)
- Infisical (secrets management)

