---
name: aws-architecture-review
description: Review Terraform changes and update AWS architecture diagrams and documentation. Orchestrates the aws-architecture-diagram skill to apply changes.
user-invocable: true
argument-hint: "provide parsed Terraform diff JSON and existing diagram file path"
---

# AWS Architecture Review Skill

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

After the diagram skill completes, return a concise PR review summary as the final text response. This will be posted as a PR comment. Include:
- What resources were added, modified, or removed
- Architecture impact (data flow changes, security implications, scaling effects)
- Any risks or recommendations (e.g. removing a load balancer leaves services without ingress)
