# Foundations Knowledge Integration - COMPLETE ✅

## What Was Added

Extracted comprehensive engineering guidance from **em-foundations** repository into AI Software Factory knowledge base.

**Source:** https://github.com/EmergenceAI/em-foundations

### New Knowledge Files

```
knowledge/foundations/
├── overview.md      # Complete platform overview, 3-tier architecture, ADR links
└── standards.md     # Definition of Done, Engineering Principles, constraints
```

### KnowledgeEngine Enhancements

Added Foundations guidance methods to `orchestrator/knowledge.py`:

```python
# Get all Foundations guidance
engine.get_foundations_guidance()

# Get specific categories
engine.get_foundations_guidance('standards')
engine.get_foundations_guidance('overview')

# Get specific sections
engine.get_definition_of_done()
engine.get_engineering_principles()
engine.get_air_gapped_requirements()
```

---

## What em-foundations Is

**Engineering operating model, standards and architectural reference** for the Emergence AI platform.

### Organization

**Foundations Team (Platform)**
- 4-person team
- Owns plaza (platform infra, tooling, contracts, standards)
- Owns em-runtime craft component

**Product Teams**
- Build craft components (em-data-readiness, em-talk2data, em-runtime-ui, em-semi)

---

## Three-Tier Architecture

### 1. Plaza (Foundations - Internal Only, Never Shipped)

Platform infrastructure:
- em-foundations-infra (ArgoCD, Crossplane, OTEL Collector, Gateway)
- em-dagger-modules (CI/CD modules + GitHub Actions)
- em-charts (em-service base chart)
- Pacto contracts (platform-service, infrastructure contracts)
- Standards (repo structure, package structure)

**Provisions the data plane:**
- PostgreSQL (via Crossplane)
- Redis (via Crossplane)
- S3-compatible buckets (via Crossplane)
- Secrets (via Crossplane)

### 2. Craft (Shippable Base Product)

Single umbrella Helm chart with components:
- **em-runtime** (Foundations-owned)
- **em-data-readiness** (Product team)
- **em-talk2data** (Product team)
- **em-runtime-ui** (Product team)

All deployed the same way:
- Pacto contracts
- Dagger modules
- ArgoCD
- Zero-config deploy in any environment

### 3. Solutions (Customers)

Customer applications:
- Built via craft CLI (`emergence-cli`)
- Run off-platform
- Consume craft via SDK
- **NOT subject to plaza compliance**

---

## Critical Standards AI MUST Follow

### 1. Air-Gapped First (NON-NEGOTIABLE!)

**Every service MUST work in air-gapped, bare-metal Kubernetes:**
- ❌ **NO cloud-specific APIs** (GCP, AWS, Azure)
- ❌ **NO cloud IAM dependencies**
- ❌ **NO managed services** in application code
- ✅ **Helm charts MUST deploy** without cloud provider
- ✅ **Cloud services are environment overrides**, NOT baseline

**This is NOT aspirational** - em-runtime ships to customer environments!

### 2. Definition of Done (Every PR Must Have)

1. **Functionality** - Implemented and verified
2. **Testing** - 80% coverage, E2E tests, mypy, ruff
3. **Code Review** - Peer approval, CI passes, SonarCloud clean
4. **Contracts** - Pacto contract valid, published to OCI
5. **Configuration** - Explicit, versioned, no assumptions
6. **Observability** - Structured logs (JSON, no PII), metrics, traces
7. **Documentation** - OpenAPI, architecture, runbook updated
8. **Security** - No secrets in code, gitleaks passes, signed images
9. **Deployment** - Works via standard pipeline, air-gapped compatible

### 3. Allowed Infrastructure Dependencies

**ONLY these (via Crossplane):**
- PostgreSQL (Cloud SQL → CloudNativePG air-gapped)
- Redis (Memorystore → Redis operator air-gapped)
- S3 buckets (Cloud Storage → local PV with obstore)
- Secrets (Secret Manager → Vault)

**Everything else via em-runtime:**
- Auth: Keycloak
- Authz: OpenFGA
- Assets, governance

### 4. Engineering Principles (13 Total)

**Key ones for AI implementation:**

1. **Platform, not product-specific** - em-runtime has NO product logic
2. **Air-gapped first** - See above (critical!)
3. **Minimize dependencies** - Prefer extending over adding
4. **Clear ownership** - Each team owns their runtime behavior
5. **Thin slice first** - Walking skeleton, then iterate
6. **No stored credentials** - Workload identity only (ADR-001)
7. **Reuse Daggerverse modules** - Don't reimplement

### 5. Deployment Pattern

**Contract-driven deployment:**
- Contract carries Helm values + infrastructure claims
- No parallel maintenance
- Service CI → Dagger em-deploy → ArgoCD Applications + Crossplane claims

---

## Key Technical Constraints

### 1. Air-Gapped / Bare-Metal
- MUST work on any K8s cluster
- NO cloud-managed services in runtime path

### 2. Cloud-Agnostic
- NO GCP/AWS-specific dependencies in platform layer
- Use provider-agnostic abstractions

### 3. 4-Person Team
- Everything scales without linear overhead
- Self-service, automation-first

---

## Pacto Contracts (Critical!)

**Pacto** (https://trianalab.github.io/pacto/) - Eduardo's OSS contract system

**Already integrated:**
- 21 contracts across 4 repos
- CI validates on PR, publishes on merge
- Pacto operator deployed
- OCI distribution via ghcr.io/emergenceai/pactos/

**MUST remain general-purpose OSS:**
- ❌ Do NOT add business-specific features to Pacto
- ❌ Do NOT add OTLP checks, coverage, deployment logic
- ✅ Use existing mechanisms: Policy, Configuration, Plugins

---

## Repository Landscape

### Active V2 (Core)
- `em-runtime` - Core platform (monorepo: governance, assets, utils)
- `em-runtime-infra` - Current infra (→ em-foundations-infra)
- `em-data-readiness` - Craft component
- `em-talk2data` - Craft component
- `em-runtime-ui` - UI
- `em-semi` - Semiconductor platform
- `em-charts` - Helm charts (em-service)

### Repository Stats
- Total: 300 repos
- Abandoned: 178 (59%)
- With CODEOWNERS: 11%

---

## Architecture Decision Records (ADRs)

11 ADRs documented in em-foundations:

1. **ADR-001:** Vault as platform secret backend
2. **ADR-002:** Crossplane for database/cache provisioning
3. **ADR-003:** Contract-driven deployment
4. **ADR-004:** Dagger module design
5. **ADR-005:** Local deployment via air-gapped chart
6. **ADR-006:** Platform identity and access control
7. **ADR-007:** Internal gateway topology
8. **ADR-008:** Workload identity self-service
9. **ADR-009:** Contract-to-manifest output shape
10. **ADR-010:** Service exposure and gateways
11. **ADR-011:** Craft chart versioning and contract

**Full ADRs:** https://github.com/EmergenceAI/em-foundations/tree/main/decisions

---

## Writing Style (When Contributing to Docs)

From CLAUDE.md in em-foundations:

1. **British English** - standardisation, organisation
2. **Sentence case headings** - "Secrets management" not "Secrets Management"
3. **No Oxford comma** - "a, b and c" not "a, b, and c"
4. **Mermaid diagrams** - Never ASCII/box-drawing
5. **No repetition** - State once, link from everywhere
6. **Explain-before-use** - Concepts explained before referenced

---

## Usage in AI Software Factory

### When to Apply Foundations Standards

**Always when working on:**
- em-runtime (Foundations-owned)
- Craft components (em-data-readiness, em-talk2data, em-runtime-ui, em-semi)
- New services
- PRs to default branch

### Critical Checks Before PR

```
✅ Air-gapped compatible? (No cloud APIs)
✅ Test coverage >= 80%?
✅ Pacto contract valid?
✅ No secrets in code/logs?
✅ Documentation updated?
✅ Deploys via standard pipeline?
✅ gitleaks passes?
✅ Images signed with cosign?
```

### Using in Orchestrator

```python
from orchestrator import KnowledgeEngine

engine = KnowledgeEngine('knowledge')

# Get all Foundations guidance
foundations = engine.get_foundations_guidance()

# Get specific sections
dod = engine.get_definition_of_done()
principles = engine.get_engineering_principles()
air_gapped = engine.get_air_gapped_requirements()

# Use in prompts
prompt = f"""
Implement this feature following Foundations standards:

{dod}

{air_gapped}

Critical: MUST work air-gapped (no cloud APIs!)
"""
```

### Using in Skills

```python
# In skills/autonomous-implement/
from orchestrator import ensure_knowledge_fresh, KnowledgeEngine

# Sync knowledge
ensure_knowledge_fresh()

# Get standards
engine = KnowledgeEngine('knowledge')
dod = engine.get_definition_of_done()
air_gapped = engine.get_air_gapped_requirements()

# Include in implementation prompt
implementation_prompt = f"""
{task_description}

STANDARDS TO FOLLOW:
{dod}

AIR-GAPPED REQUIREMENTS (CRITICAL):
{air_gapped}
"""
```

---

## What Knowledge Was Extracted

### overview.md (Comprehensive Platform Overview)

**Content:**
- Three-tier architecture (plaza/craft/solutions)
- Organization structure (Foundations vs Product teams)
- Key technical constraints (air-gapped, cloud-agnostic, 4-person team)
- Architectural decisions (Pacto, Crossplane, Dagger, etc.)
- Repository landscape (300 repos, 59% abandoned)
- Reading order for engineers (9 architecture docs + 7 standards)
- Links to 11 ADRs
- Pacto integration details

**Size:** ~500 lines

### standards.md (Actionable Standards)

**Content:**
- Definition of Done (9-point checklist)
- Enforcement mechanisms (CI, Pacto, SonarCloud, etc.)
- 13 Engineering Principles (detailed)
- Key constraints summary
- Allowed infrastructure dependencies
- When to use these standards
- Critical checks reference

**Size:** ~350 lines

**Total Foundations Knowledge:** ~850 lines

---

## Integration Summary

### Files Created
1. `knowledge/foundations/overview.md` - Platform overview
2. `knowledge/foundations/standards.md` - Standards and principles
3. `FOUNDATIONS_KNOWLEDGE_COMPLETE.md` - This document

### Files Modified
1. `orchestrator/knowledge.py` - Added Foundations methods

### New Capabilities

**KnowledgeEngine now provides:**
- Complete platform overview
- Definition of Done checklist
- Engineering principles
- Air-gapped requirements
- ADR references
- Foundations standards

**Orchestrator can now:**
- Check air-gapped compatibility requirements
- Validate against Definition of Done
- Apply Engineering Principles
- Reference Foundations constraints
- Link to ADRs for decisions

---

## Testing Foundations Knowledge

```bash
# Test knowledge extraction
cd /Users/malamunisamy/Documents/Development/EM-AISoftwareFactory

python3 << 'EOF'
from orchestrator import KnowledgeEngine

engine = KnowledgeEngine('knowledge')

# Get Foundations guidance
foundations = engine.get_foundations_guidance()
print(f"Overview: {len(foundations['overview'])} chars")
print(f"Standards: {len(foundations['standards'])} chars")

# Get specific sections
dod = engine.get_definition_of_done()
print(f"\nDefinition of Done: {len(dod)} chars")

principles = engine.get_engineering_principles()
print(f"Engineering Principles: {len(principles)} chars")

air_gapped = engine.get_air_gapped_requirements()
print(f"Air-gapped Requirements: {len(air_gapped)} chars")

print("\n✅ Foundations knowledge loaded successfully!")
EOF
```

---

## Key Takeaways for AI Implementation

### 🚨 CRITICAL - Air-Gapped Requirements

**Before implementing ANYTHING:**
1. Check: Does it use cloud-specific APIs? → ❌ REJECT
2. Check: Does Helm chart need cloud provider? → ❌ REJECT
3. Check: Uses only PostgreSQL/Redis/S3/Secrets? → ✅ OK
4. Check: Deploys via Dagger em-deploy? → ✅ OK

### 📋 Every PR Must Have

1. 80% test coverage
2. Pacto contract valid
3. No secrets in code
4. Documentation updated
5. Air-gapped compatible
6. Deploys via standard pipeline

### 🎯 Minimize Dependencies

**Before adding anything:**
- Can PostgreSQL or Redis handle this?
- Can we extend existing service?
- Is it open source / self-hostable?

### 🏗️ Architecture Constraints

- **Platform layer:** Cloud-agnostic, air-gapped first
- **Craft components:** Follow plaza standards
- **Solutions:** NOT subject to compliance

---

## Next Steps

### Immediate
Knowledge is ready - no action needed! ✅

### When Implementing Features
1. Check air-gapped requirements
2. Follow Definition of Done
3. Apply Engineering Principles
4. Reference ADRs for decisions

### When Creating PRs
Use Definition of Done as checklist:
```bash
# Get DoD checklist
python3 -c "
from orchestrator import KnowledgeEngine
engine = KnowledgeEngine('knowledge')
print(engine.get_definition_of_done())
"
```

---

## Summary

### What Was Accomplished ✅

1. **Extracted 850 lines** of Foundations guidance
2. **Integrated into KnowledgeEngine** with dedicated methods
3. **Air-gapped requirements** now enforceable
4. **Definition of Done** available for validation
5. **Engineering Principles** guide implementation
6. **ADR links** for architectural decisions

### Knowledge Coverage

| Category | Lines | Status |
|----------|-------|--------|
| Platform Overview | ~500 | ✅ Complete |
| Standards & Principles | ~350 | ✅ Complete |
| **Total Foundations** | **~850** | **✅ Ready** |
| **Total Repository Knowledge** | **2,968** | **✅ Ready** |
| **GRAND TOTAL** | **3,818 lines** | **✅ Complete** |

### Repository Knowledge Summary

| Source | Lines | Status |
|--------|-------|--------|
| talk2data | 2,093 | ✅ |
| semi | 789 | ✅ |
| em-foundations | 850 | ✅ NEW! |
| data-readiness | 32 | ✅ |
| runtime | 31 | ✅ |
| runtime-ui | 23 | ✅ |

**AI Software Factory now has comprehensive knowledge base spanning 7 repositories + platform standards!** 🎉

---

## Questions?

**Q: How does AI use Foundations knowledge?**
A: KnowledgeEngine provides methods to get standards, DoD, principles, air-gapped requirements - use in prompts!

**Q: Is air-gapped really that important?**
A: YES! Non-negotiable. em-runtime ships to customer environments. No cloud APIs allowed.

**Q: What if I need to add a new dependency?**
A: Check Engineering Principle #3: Minimize Dependencies. Justify against complexity cost.

**Q: Where are the full ADRs?**
A: https://github.com/EmergenceAI/em-foundations/tree/main/decisions

**Q: What about Pacto?**
A: It's OSS - keep it general-purpose. No business-specific features!

**Q: How often should knowledge sync?**
A: Automatic before orchestrator runs. Manual: `./sync_knowledge.sh`
