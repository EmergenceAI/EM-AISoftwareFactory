<!--
AUTO-GENERATED from craft
Last sync: 2026-11-04 01:50:35 UTC
Source commit: 71f896aec73fed4d4847b03a2c4d3e41c348980f
DO NOT EDIT MANUALLY - Run ./sync_knowledge.sh to update
-->

# craft Architecture

## Overview

## Prerequisites (macOS)

```bash
brew install go node rust docker
corepack enable                    # activates the pnpm version declared in package.json
```

- **Go ≥1.24** — builds the `craft` CLI
- **Docker Desktop** — running, with at least 8 GB memory allocated (`craft local up` starts ~15 containers)
- **Node ≥18** and **pnpm 11.x** — `corepack enable` picks up the version from `packageManager` in `package.json`
- **Rust** — each bundle's `rust-toolchain.toml` pins the version and WASM targets; `cargo` installs them on first build

## Quick start
## What's here

| | |
|---|---|
| [`compute-plane-python/`](compute-plane-python/) | The compute plane. FastAPI, SQLAlchemy, DBOS, Redpanda. Executes workflows, manages runs, hosts the runtime for WASM and job components. |
| [`control-plane/`](control-plane/) | The control plane. Fastify, DBOS, Kubernetes. Creates and manages customer environments, handles bundle registration and entitlement delivery, owns the shared Keycloak deployment. |
| [`customer-ui/`](customer-ui/README.md) | The customer-facing portal. A Vite+ monorepo: the Craft SPA and the shared component library it is built from. |
