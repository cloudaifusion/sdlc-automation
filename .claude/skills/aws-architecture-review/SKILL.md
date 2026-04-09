---
name: aws-architecture-review
description: Generate incremental AWS architecture reviews and Draw.io XML updates from Terraform changes.
user-invocable: true
argument-hint: "provide parsed Terraform diff JSON and optional existing diagram XML"
---

# AWS Architecture Review Skill

Inputs:  
- Parsed Terraform diff (JSON from scripts/get_diff.py)  
- Existing Draw.io XML (optional)  
- Existing summary Markdown (optional)

Workflow:  
1. Analyze diff for added/removed/modified high-level AWS services.  
2. Determine architecture impact (data flow, scaling, security).  
3. Update the Draw.io diagram — add, modify, or remove nodes and edges to reflect the Terraform changes.
4. Update the companion guide to reflect the current architecture state.
5. Produce a review summary of what changed and why.

## Output 1 — Updated Draw.io diagram

Write the full updated diagram to `docs/architecture.drawio`.  
Follow the same icon styles, layout, and conventions defined in the `aws-architecture-diagram` skill.

## Output 2 — Updated companion guide

Write the updated companion guide to `docs/architecture.md`.  
The companion guide describes the **current state** of the architecture (not just what changed). Include:
- **Overview**: 1-2 sentence summary of what the architecture does
- **Components**: Table of each AWS service, its role, and why it was chosen
- **Data flows**: Step-by-step explanation of each flow
- **Key design decisions**: Brief notes on architectural choices

## Output 3 — Review summary

Write a concise PR review summary covering:
- What resources were added, modified, or removed
- Architecture impact (data flow changes, security implications, scaling effects)
- Any risks or recommendations

Output the review summary as the final text response (it will be posted as a PR comment).

## Output convention for XML

XML updates must be wrapped between:

DIAGRAM_XML_START

<mxCell id="svc-new-lambda" ... />

DIAGRAM_XML_END
