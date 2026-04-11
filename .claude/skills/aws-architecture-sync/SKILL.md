---
name: aws-architecture-sync
description: Sync AWS architecture diagrams with Terraform changes. Orchestrates the aws-architecture-diagram skill to update the diagram and companion guide, then returns a PR review summary.
user-invocable: true
argument-hint: "provide parsed Terraform diff JSON and existing diagram file path"
---

# AWS Architecture Sync Skill

Inputs:
- Parsed Terraform diff (JSON from scripts/get_diff.py)
- Existing Draw.io XML (optional)
- Existing companion guide Markdown (optional)

## Workflow

### 1. Analyze the diff

Identify which AWS resources were added, modified, or deleted from the Terraform diff JSON.
Map each resource type to its architectural significance:
- What service does it represent?
- What nodes/edges need to be added, updated, or removed from the diagram?
- What is the impact on data flows, security, or scaling?

### 2. Delegate to `/aws-architecture-diagram`

Invoke the `/aws-architecture-diagram` skill in **update mode**, passing:
- The existing diagram XML
- A precise, explicit list of changes to apply:
  - Nodes to add (service type, label, position hint, parent group)
  - Nodes to remove (by id)
  - Edges to add (source, target, label)
  - Edges to remove (by id)
  - Any label or style updates

The diagram skill will apply the changes and regenerate both:
- The updated `docs/architecture.drawio`
- A fresh `docs/architecture.md` companion guide reflecting the current state

### 3. Return PR review summary

After the diagram skill completes, output the PR summary using EXACTLY this template (omit any section that has no rows):

```
### RISKS_START
- **[HIGH] Example risk title** — explanation and remediation
### RISKS_END

### SUMMARY_START

## Resources added

| Service | Role | Risk |
|---|---|---|
| **WAFv2 Web ACL** | L7 filtering (SQLi, XSS, rate-limiting) in front of the ALB | none |

## Resources modified (in-place)

| Service | Role | Change | Risk |
|---|---|---|---|
| **RDS PostgreSQL** | Document metadata store | Instance configuration update | none |

## Resources force-replaced (destroy + recreate)

| Service | Role | Change | Risk |
|---|---|---|---|
| **Application Load Balancer** | TLS termination, path-based routing to Fargate | Destroyed and recreated — DNS name changed | HIGH |

## Resources permanently deleted

| Service | Role | Risk |
|---|---|---|
| **WAFv2 Web ACL** | L7 filtering (SQLi, XSS, rate-limiting) for the ALB | HIGH |
```

If there are no HIGH or MEDIUM risks, omit the `### RISKS_START` / `### RISKS_END` block entirely.

Rules:
- **Added** = new resources not present in the base branch terraform; no "Change" column needed
- **Modified** = resources that existed in the base branch and have configuration changes
- **Force-replaced** = resources where Terraform will destroy and recreate (e.g. name/identifier changes)
- **Deleted** = resources removed entirely; no "Change" column needed
- **Role** = what the service does in this architecture — never the change description
- **Risk** values: HIGH / MEDIUM / LOW / none
- Omit sections with no rows; do not merge sections into one table
- No additional prose paragraphs after the tables
- Do NOT write "already up to date" or similar prose — if there are no diagram changes, still output the summary tables
