<!--
EXTRACTED from em-foundations repository
Source: https://github.com/EmergenceAI/em-foundations
Last updated: 2026-06-29
This is the Foundations team's engineering operating model and standards
-->

# Emergence AI Foundations - Overview

## What This Is

Engineering operating model, standards and architectural reference for the Emergence AI platform.

**Repository:** https://github.com/EmergenceAI/em-foundations

**Purpose:** Living reference for platform standards, architecture decisions, and engineering practices.

## Source Documents

### Core Reading Order for Engineers

1. **Platform Model** - [plaza.md](https://github.com/EmergenceAI/em-foundations/blob/main/architecture/plaza.md)
   - Three tiers: plaza / craft / solutions
   - Compliance scope and glossary

2. **Architecture Overview** - [overview.md](https://github.com/EmergenceAI/em-foundations/blob/main/architecture/overview.md)
   - How components fit together
   - Dependency boundaries, SDK boundary, ownership

3. **Contract-based Governance** - [contracts.md](https://github.com/EmergenceAI/em-foundations/blob/main/architecture/contracts.md)
   - Pacto's role, validation chain, compliance

4. **Contract-driven Deployment** - [contract-driven-deployment.md](https://github.com/EmergenceAI/em-foundations/blob/main/architecture/contract-driven-deployment.md)
   - Single deployment interface

5. **Golden Path** - [golden-path.md](https://github.com/EmergenceAI/em-foundations/blob/main/architecture/golden-path.md)
   - What a craft component looks like

6. **Platform Modules (Dagger)** - [platform-modules.md](https://github.com/EmergenceAI/em-foundations/blob/main/architecture/platform-modules.md)
   - CI/CD modules, generated manifests, GitHub Actions

7. **Cluster Topology** - [cluster-topology.md](https://github.com/EmergenceAI/em-foundations/blob/main/architecture/cluster-topology.md)
   - Crossplane, infrastructure provisioning, secrets

8. **Observability** - [observability.md](https://github.com/EmergenceAI/em-foundations/blob/main/architecture/observability.md)
   - OTEL, Grafana Cloud, dashboards

9. **Documentation** - [documentation.md](https://github.com/EmergenceAI/em-foundations/blob/main/architecture/documentation.md)
   - Per-repo /docs folders, centralized portal

### Standards

10. **Ownership Model** - [ownership.md](https://github.com/EmergenceAI/em-foundations/blob/main/standards/ownership.md)
11. **Work Intake** - [work-intake.md](https://github.com/EmergenceAI/em-foundations/blob/main/standards/work-intake.md)
12. **Definition of Done** - [definition-of-done.md](https://github.com/EmergenceAI/em-foundations/blob/main/standards/definition-of-done.md)
13. **Operational Readiness** - [operational-readiness.md](https://github.com/EmergenceAI/em-foundations/blob/main/standards/operational-readiness.md)
14. **Engineering Principles** - [engineering-principles.md](https://github.com/EmergenceAI/em-foundations/blob/main/standards/engineering-principles.md)
15. **Repo Structure Standard** - [repo-structure.md](https://github.com/EmergenceAI/em-foundations/blob/main/standards/repo-structure.md)
16. **Package Structure Standard** - [package-structure.md](https://github.com/EmergenceAI/em-foundations/blob/main/standards/package-structure.md)

### Architecture Decision Records (ADRs)

- [ADR-001: Vault as the platform secret backend](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-001-vault-secrets.md)
- [ADR-002: Use Crossplane for database and cache provisioning](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-002-k8s-operators-for-databases.md)
- [ADR-003: Contract-driven deployment](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-003-contract-driven-deployment.md)
- [ADR-004: Dagger module design](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-004-dagger-module-design.md)
- [ADR-005: Local deployment via air-gapped chart install](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-005-local-deployment-air-gapped.md)
- [ADR-006: Platform identity and access control](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-006-platform-identity-rbac.md)
- [ADR-007: Internal gateway topology](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-007-internal-gateway-topology.md)
- [ADR-008: Workload identity self-service](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-008-workload-identity-self-service.md)
- [ADR-009: Contract-to-manifest output shape](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-009-contract-to-manifest-output.md)
- [ADR-010: Service exposure and gateways](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-010-service-exposure-and-gateways.md)
- [ADR-011: Craft chart versioning and the craft contract](https://github.com/EmergenceAI/em-foundations/blob/main/decisions/ADR-011-craft-chart-versioning-and-contract.md)

## Organization

### Foundations Team
- Platform team that owns plaza (platform infra, tooling, contracts, standards)
- Owns em-runtime craft component
- 4-person team

### Product Teams
- Build craft components (em-data-readiness, em-talk2data, em-runtime-ui, etc.)
- Earlier called "Solution Teams" - renamed to avoid collision with "solutions" tier

## Three-Tier Architecture

### Plaza (Foundations Team)
Internal platform - **never shipped**:
- em-foundations-infra (ArgoCD, Crossplane, OTEL Collector, Gateway)
- em-dagger-modules (CI/CD modules + GitHub Actions workflows)
- em-charts (em-service base chart)
- Published contracts (platform-service, infrastructure contracts)
- Repo/package standards

**Provisions the data plane:**
- PostgreSQL (via Crossplane)
- Redis (via Crossplane)
- S3-compatible buckets (via Crossplane)
- Secrets (via Crossplane)

### Craft (Foundations + Product Teams)
The shippable base product - **single umbrella Helm chart**:
- em-runtime (owned by Foundations)
- em-data-readiness (product team)
- em-talk2data (product team)
- em-runtime-ui (product team)

**All built and deployed the same way:**
- Pacto contracts
- Dagger modules
- ArgoCD
- Zero-config deploy in any environment

### Solutions (Customers / External Teams)
Customer applications built on the base product:
- Via craft CLI (`emergence-cli`) agent templating
- Run off-platform
- Consume craft via SDK
- **NOT subject to plaza compliance**

## Key Technical Constraints

1. **Air-gapped / bare-metal**
   - em-runtime must work on any K8s cluster
   - Air-gapped deployments supported
   - No cloud-managed services in runtime path

2. **Cloud-agnostic**
   - No GCP/AWS-specific dependencies in platform layer
   - Use provider-agnostic abstractions

3. **4-person team**
   - Everything must scale without linear overhead on Foundations
   - Self-service, automation-first

## Key Architectural Decisions

### Infrastructure Dependencies
- **PostgreSQL, Redis, S3-compatible buckets** as direct infra dependencies
- Provisioned via Crossplane:
  - GCP: Cloud SQL + Memorystore + Cloud Storage
  - Air-gapped: In-cluster operators

### Everything Else via em-runtime
- Auth: Keycloak
- Authz: OpenFGA
- Assets, governance

### Pacto Contracts
**The interface between plaza and craft components:**
- Ownership declarations
- Dependencies
- Compliance validation

**Each contract carries:**
- Policy (platform rules)
- Configuration (schema for validation)

**Contract types:**
- `platform-service` - Service structural policy + em-service chart schema
- `platform-policy` - Universal governance policy (ADR-010)
- Infrastructure contracts - postgres, redis, bucket, secrets, service-account

### Secrets Management
- Crossplane `SecretStoreClaim` for app secrets
- GCP Secret Manager on GCP
- Vault for air-gapped
- Infra secrets generated by Crossplane

### Observability
- **OTLP (all services)** → OTEL Collector (platform) → Grafana Cloud
- Air-gapped: Local Grafana stack

### Helm Chart Model
- **em-service** is platform default (in em-charts)
- Teams may use own charts (Keycloak, OpenFGA, Prefect)
- Must include `values.schema.json`
- Enforcement point is schema, not chart

### Contract-Driven Deployment
- Contract carries deployment config (Helm values) + infrastructure claims
- No parallel maintenance
- Service CI calls em-deploy to generate ArgoCD Applications + Crossplane claims

### Dagger Platform Modules
Reusable CI/CD modules that power entire pipeline:
- `em-version` - Versioning
- `em-pacto` - Contract validation
- `em-build` - Building
- `em-test` - Testing
- `em-deploy` - Deployment
- `em-sdk` - SDK operations
- `em-helm` - Helm operations

**Consumed through:** Reusable GitHub Actions workflows

### Crossplane Infrastructure Provisioning
**Cloud-agnostic XRDs with GCP compositions:**
- `PostgreSQLClaim` - Databases
- `RedisClaim` - Caches
- `BucketClaim` - Object storage
- `SecretStoreClaim` - Secrets

**Air-gapped compositions target:**
- CloudNativePG (PostgreSQL)
- Redis operator
- Vault (secrets)
- Buckets: provider-agnostic libraries (obstore) with local PV

## Repository Landscape

### Active V2 Repos (Core)
- `em-runtime` - Core platform product (monorepo: governance, assets, utils)
- `em-runtime-infra` - Current infra (being replaced by em-foundations-infra)
- `em-data-readiness` - Craft component (India-Tech-Dev)
- `em-talk2data` - Craft component (India-Tech-Dev)
- `em-runtime-ui` - UI
- `em-charts` - Helm charts (em-service base chart)
- `em-github-actions` - Legacy CI/CD (92+ repos, not in new golden path)

### V1 Repos (Reference)
- `em-services-infra` - V1 centralized infra
- `em-services-tool` - V1 self-service CLI (svcctl)
- `em-python-cookiecutter` - V1 service scaffolding
- `em-grafana-monitoring` - V1 Grafana Cloud management

### Repository Stats
- **Total:** 300 repos
- **Abandoned:** 178 repos (59%) - candidates for archival
- **Active with CODEOWNERS:** 11% (89% lack ownership)

## Critical: Pacto is OSS

**Pacto** (https://trianalab.github.io/pacto/) is Eduardo's open-source contract system.

**Already integrated:**
- 21 contracts published across 4 repos
- CI validates on PR, publishes on merge
- Pacto operator deployed with dashboard
- OCI distribution via ghcr.io/emergenceai/pactos/

**MUST remain general-purpose OSS:**
- Do NOT add business-specific features
- Do NOT add OTLP checks, coverage, deployment logic to Pacto itself
- Use existing mechanisms: Policy, Configuration, Plugins

## Writing Style (From CLAUDE.md)

When contributing to em-foundations or writing documentation:

1. **British English** - standardisation, organisation (not standardization, organization)
2. **Sentence case headings** - "Secrets management" not "Secrets Management"
3. **No Oxford comma** - "a, b and c" not "a, b, and c"
4. **Mermaid diagrams** - Never ASCII/box-drawing
5. **No repetition** - State once, link from everywhere else
6. **Explain-before-use** - Every concept explained before referenced
7. **Cross-reference** - Link to RFC decisions (D1-D9) where they apply

## Status

**Under active development by Foundations team.**

The RFC has not yet been approved by leadership - documents here are the pitch.

## Usage in AI Software Factory

This knowledge should be used when:
1. Working on em-runtime (owned by Foundations)
2. Working on craft components (em-data-readiness, em-talk2data, em-runtime-ui)
3. Making architectural decisions
4. Understanding deployment patterns
5. Understanding platform constraints (air-gapped, cloud-agnostic)
6. Writing documentation
7. Setting up new services

**Key files to reference:**
- Standards when creating PRs or new services
- ADRs when making architectural decisions
- Architecture docs when understanding system design
- Golden path when onboarding to platform
