<!--
EXTRACTED from em-foundations repository
Source: https://github.com/EmergenceAI/em-foundations/blob/main/standards/
Last updated: 2026-06-29
Engineering standards from the Foundations team
-->

# Engineering Standards - Foundations Team

## Definition of Done (Per-PR Checklist)

Every PR merged to a default branch must satisfy ALL of the following:

### 1. Functionality
The intended behaviour is implemented and verified.

### 2. Automated Testing
- **Unit test coverage >= 80%** (line/instruction)
- **E2E or integration tests** where change impacts service boundaries or critical flows
- **Static type analysis** runs at build time (mypy for Python)
- **Code formatter and linter** run at build time (ruff for Python)

### 3. Code Review
- **At least one peer approval** required before merging
- **All CI checks must pass** - cannot be overridden
- **SonarCloud issues** reviewed and resolved (exceptions require manager approval)

### 4. Contracts (Pacto)
- Valid Pacto contract published to OCI registry
- Validated against platform service policy
- Configuration schemas validated (deployment + infrastructure claims)
- Environment-specific override files validated for all target environments

### 5. Configuration
- All required configuration explicitly defined
- Configuration is versioned
- No implicit or undocumented assumptions

### 6. Observability
The change includes appropriate signals:
- **Structured logs** for new behaviour (JSON to STDOUT, no PII)
- **Business metrics** where change introduces measurable outcomes
- **Trace instrumentation** for new service boundaries or external calls
- **Alerts updated** if change introduces new failure modes

### 7. Documentation
Documentation updated to reflect the change:
- **API documentation** (OpenAPI spec) regenerated if endpoints changed
- **Architecture documentation** updated if structure or dependencies changed
- **On-call runbook** updated if new failure modes, config or operational procedures

### 8. Security
Per ADR-001:
- **No secrets, credentials or PII** in code, logs or configuration
- **gitleaks passes** (em-test module) - no secrets in source or git history
- **Container image signed** with cosign + SBOM + CVE attestations (em-build)
- **New secrets declared** in Pacto `secrets` configuration before use
- **Security-sensitive changes** flagged for security review (auth, data handling, external integrations)

### 9. Deployment Readiness
- Can be deployed through standard pipeline (Dagger em-deploy → ArgoCD + em-service chart)
- Does not break air-gapped compatibility

## Enforcement Mechanisms

| Aspect | Enforcement |
|--------|-------------|
| Testing + coverage | CI pipeline (Dagger em-test module), threshold enforced |
| Code quality + type analysis | SonarCloud, mypy/ruff in CI |
| Code review | GitHub branch protection (required approvals + checks) |
| Contracts | Pacto validate in CI, operator at runtime |
| Deployment | Contract-driven: Dagger em-deploy → ArgoCD |
| Security | gitleaks in CI, cosign + SBOM + CVE in CI, Kyverno runtime gates, GitHub push protection |

---

## Engineering Principles

### 1. We Build a Platform, Not Product-Specific Solutions
**What this means:**
- em-runtime contains NO product-specific logic (except runtime-configured connectors)
- Platform components are versioned and consumable, not modified in-place
- Contributions must be generalisable - use-case-specific changes go to owning team

### 2. Air-Gapped First (Critical!)
**Every service MUST work in air-gapped, bare-metal Kubernetes:**
- Application code CANNOT depend on cloud-specific APIs, IAM or managed services
- Helm charts MUST deploy successfully without cloud provider access
- Cloud-managed services (Cloud SQL, Memorystore) are environment overrides, NOT baseline
- **This is not aspirational** - em-runtime ships to customer environments

**Accountability:**
- Foundations: em-runtime air-gapped deployability
- Each team: Their own services' air-gapped compatibility

### 3. Minimize Dependencies
Before adding new dependency:
- Prefer extending what we have
- Every dependency adds operational burden for customers
- All dependencies MUST be open source or self-hostable
- Justify against cost of complexity

**Before Adding:**
| Component | Ask |
|-----------|-----|
| New database | Can PostgreSQL or Redis serve this? |
| New queue | Can Redis Streams handle this? |
| New service | Can existing service be extended? |
| New SDK/library | Does existing dependency cover this? |

### 4. Clear Ownership Enables Scalable Systems
- Each team owns its runtime behaviour and operational responsibility
- Platform teams are NOT default operators for all systems
- Shared code is NOT a shared dumping ground
- Multi-team changes go through clear interfaces

### 5. Work is Planned, Visible and Protected
- Work from prioritised backlog in fixed, short cycles
- Committed work is protected from interruption
- New requests go to backlog, NOT inserted mid-cycle
- Priority changes require explicit replanning

### 6. Focus Over Context Switching
- Teams given space to complete work without disruption
- Context switching treated as a cost
- Urgent work handled through explicit reprioritisation

### 7. Delivery is Incremental and Continuous
- Small, meaningful increments vs large, infrequent releases
- Partial progress is valid and expected
- Each increment moves system forward in usable/testable way

### 8. Start with a Thin Slice (Walking Skeleton First)
- First iteration: smallest end-to-end implementation
- Non-essential features deferred
- UI designs are proposals, NOT complete delivery requirements

### 9. Engineering Delivers; Product Decides Value
**Engineering owns:**
- Working outcomes meeting operational readiness standard
- Quality, operational readiness, technical standards

**Product owns:**
- Value determination
- Scope, priority, release timing

### 10. Sustainable Pace Over Deadline Pressure
- Optimise for consistent, predictable delivery
- Deadlines do NOT override clarity, quality, sustainability
- Capacity and prioritisation drive delivery, not imposed deadlines

### 11. Operational Work Must Be Explicit
- Reactive operational work is REAL work
- Visible and accounted for in planning
- Increased operational demand = reduced delivery commitments

### 12. Workload Identity Over Stored Credentials
**Per ADR-001:**
- Application secrets in Vault, NEVER long-lived K8s Secrets
- Database/cache credentials ONLY in Vault KV and pod tmpfs
- Bucket access uses cloud-native Workload Identity (no HMAC keys)
- Per-secret authorization is policy-based from `service.owner.team`

### 13. Reuse Vetted Daggerverse Modules
- Prefer well-maintained published Dagger modules over reimplementing
- Pin to specific commit, mirror for air-gapped use
- Reimplement only when no suitable module exists

**Examples:**
- em-helm uses official dagger/dagger/helm module
- em-build uses trivy daggerverse module for SBOM/CVE
- em-version.release uses node daggerverse module for changesets

---

## Key Constraints Summary

### Technical Constraints
1. **Air-gapped / bare-metal** - MUST work on any K8s cluster
2. **Cloud-agnostic** - NO GCP/AWS-specific dependencies in platform
3. **4-person team** - Everything scales without linear overhead

### Infrastructure Dependencies (The Only Ones Allowed)
- **PostgreSQL** (Crossplane: Cloud SQL or CloudNativePG)
- **Redis** (Crossplane: Memorystore or Redis operator)
- **S3-compatible buckets** (Crossplane: Cloud Storage or local PV with obstore)
- **Secrets** (Crossplane: Secret Manager or Vault)

### Everything Else via em-runtime
- Auth: Keycloak
- Authz: OpenFGA
- Assets, governance

---

## When to Use These Standards

**Always:**
- When working on em-runtime (Foundations-owned)
- When working on craft components (em-data-readiness, em-talk2data, em-runtime-ui)
- When creating new services
- When making PRs to default branch

**Critical Checks:**
- ✅ Air-gapped compatible? (No cloud-specific APIs)
- ✅ Test coverage >= 80%?
- ✅ Pacto contract valid?
- ✅ No secrets in code/logs?
- ✅ Documentation updated?
- ✅ Can deploy via standard pipeline?

**References:**
- Full standards: https://github.com/EmergenceAI/em-foundations/tree/main/standards
- ADRs: https://github.com/EmergenceAI/em-foundations/tree/main/decisions
- Architecture: https://github.com/EmergenceAI/em-foundations/tree/main/architecture
