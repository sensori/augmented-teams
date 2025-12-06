# Domain Model Diagram: {solution_name}

**File Name**: `{solution_name_slug}-domain-model-diagram.md`
**Location**: `{solution_folder}/docs/domain/shaping/{solution_name_slug}-domain-model-diagram.md`

## Solution Purpose
{solution_purpose}

---

## Domain Model Diagram

The following Mermaid diagrams visualize the domain model structure:

### Bounded Contexts Overview

```mermaid
{domain_model_bounded_contexts_diagram}
```

### Aggregates and Relationships

```mermaid
{domain_model_aggregates_diagram}
```

### Integration Points

```mermaid
{domain_model_integration_diagram}
```

**Diagram Notes:**
- Bounded contexts are shown as separate containers
- Aggregates are grouped within their bounded contexts
- Relationships show dependencies and associations
- Integration points indicate how bounded contexts interact

---

## Legend

- 🏛️ **Bounded Context** - Explicit boundary within which a domain model applies
- 📦 **Aggregate** - Cluster of domain objects treated as a single unit
- 🔗 **Relationship** - Connection between aggregates or bounded contexts
- 🔌 **Integration Point** - Interface between bounded contexts

---

## Source Material

{source_material}

