# SDLC Automation — Examples

Example code and reference architectures to accompany the **SDLC Automation** series [Here](https://www.cloudaifusion.com).

---

## Article 1: Architecture Drift: Using Claude Code to Keep Your Terraform Honest

> *What if your Terraform could draw its own architecture diagram?*

This repository contains the Terraform files used in the first article of the series. The article explores how architecture diagrams drift from the infrastructure they describe — and how a Claude Code skill can reverse-engineer accurate Draw.io diagrams directly from Terraform, closing that loop automatically.

Read the full article: [Architecture Drift: Using Claude Code to Keep Your Terraform Honest](https://www.cloudaifusion.com/p/architecture-drift-using-claude-code)

### The Skill

The `aws-architecture-diagram` Claude Code skill used in the article is published here:
**[github.com/oharu121/oharu-commands-skills-gems](https://github.com/oharu121/oharu-commands-skills-gems/tree/main/skills/aws-architecture-diagram)**

Once installed, point it at a folder of Terraform files with a simple prompt:

```
create an aws architecture diagram from the files in the terraform/aws folder
```

Add audience context to get different levels of detail from the same code:

```
create an aws architecture diagram from the files in the terraform/aws folder for a non technical audience
create an aws architecture diagram from the files in the terraform/aws folder for a technical audience
```

### The Example Terraform

The Terraform in this repo deploys a Document Management System on AWS ECS Fargate — a realistic, production-style stack that gives the skill something meaningful to work with.

```
examples/claude/skills/aws-architecture-diagram/
├── docs/
│   ├── three-tier-web-app.md        # Non-technical architecture description
│   ├── three-tier-web-app.drawio    # Draw.io diagram
│   ├── dms-production-fargate.md    # Technical architecture description
│   └── dms-production-fargate.drawio
└── terraform/aws/                   # Terraform files used in the article
    ├── main.tf
    ├── vpc.tf
    ├── alb.tf
    ├── ecs.tf
    ├── rds.tf
    ├── s3.tf
    ├── ecr.tf
    ├── iam.tf
    ├── security_groups.tf
    ├── cloudwatch.tf
    ├── variables.tf
    └── outputs.tf
```

The `docs/` folder contains the outputs the skill produced — both the Draw.io diagrams and the markdown architecture descriptions — so you can see what to expect before running it yourself.

**AWS services deployed:** VPC, ALB, ECS Fargate, RDS PostgreSQL, S3, ECR, Secrets Manager, CloudWatch, IAM

### Installing the Skill (Windows)

1. Clone the skills repository:
   ```
   git clone https://github.com/oharu121/oharu-commands-skills-gems.git
   ```

2. Copy the skill into Claude Code's skills folder:
   ```
   xcopy /E /I oharu-commands-skills-gems\skills\aws-architecture-diagram "%USERPROFILE%\.claude\skills\aws-architecture-diagram"
   ```

3. Add a read permission to `%USERPROFILE%\.claude\settings.json` so Claude Code doesn't prompt for file access on every run:
   ```json
   {
     "permissions": {
       "allow": [
         "Read(~/.claude/skills/**)"
       ]
     }
   }
   ```

Full instructions are in the article.

---

## Article 2: Giving Architects Superpowers on Every Terraform PR

> *Because reviewing raw HCL is not an architectural review.*

This article takes the diagram generation from Article 1 further — automating it inside GitHub Actions so every Terraform PR gets a visual architecture review and a structured risk analysis posted as a PR comment, at the moment the change is being made.

Read the full article: [Giving Architects Superpowers on Every Terraform PR](https://www.cloudaifusion.com/p/giving-architects-superpowers-on)

### What it does

Every time a PR touches your Terraform files, the reviewer gets:

- A visual diagram of the updated architecture — committed directly to the branch as a `.drawio` file and an inline PNG
- A risk analysis with HIGH / MEDIUM / LOW severity flags on the architectural implications of each change
- A resource table showing what changed, the service's role, and the impact — split by change type (modified, force-replaced, permanently deleted)

Two Claude Code skills power this under the hood. The `aws-architecture-sync` skill analyses the Terraform diff, determines which nodes and edges need adding or removing, and produces the risk summary that lands in the PR comment. The `aws-architecture-diagram` skill owns all the Draw.io XML generation. Both skills live as Markdown files in `.claude/skills/` in this repo.

### The Example

The example uses the same Document Management Service from Article 1 — running on ECS Fargate with RDS and S3. Two Terraform snapshots show the workflow in action:

```
examples/github/workflow/aws-architecture-sync/
├── docs/
│   ├── withwaf/                     # PR outputs: WAF added (security posture strengthened)
│   │   ├── architecture.drawio
│   │   ├── architecture.md
│   │   ├── architecture.png
│   │   └── pr.md                    # Example PR comment posted by the workflow
│   └── withoutwaf/                  # PR outputs: WAF removed (security posture weakened)
│       ├── architecture.drawio
│       ├── architecture.md
│       ├── architecture.png
│       └── pr.md                    # Example PR comment with HIGH/MEDIUM risk flags
├── terraform/aws/
│   ├── withwaf/                     # Full infrastructure including WAF Web ACL
│   └── withoutwaf/                  # Same infrastructure with WAF resources removed
└── aws-architecture-sync.yml        # The reusable GitHub Actions workflow
```

The `docs/` folder contains the exact PR comments and diagrams the workflow produced for each scenario — compare `withwaf/pr.md` and `withoutwaf/pr.md` to see the difference in what an architect sees when a security control is added versus removed.

### How it works

When a PR is opened against any file under `infra/terraform/aws/`:

1. A Python script diffs the branch against main and produces a `diff.json` of added, modified, and deleted AWS resources
2. Claude Code runs the `aws-architecture-sync` skill, which orchestrates the `aws-architecture-diagram` skill to update the diagram and regenerate the companion guide
3. The updated files are committed back to the PR branch
4. A PR comment is posted with the risk analysis, resource tables, diagram PNG, and links

### Setting it up

**Prerequisites:** A GitHub repository with Terraform files, and one of: an Anthropic API key, a Claude.ai OAuth token, or AWS Bedrock access.

**Step 1 — Create a docs folder**

```bash
mkdir docs
touch docs/.gitkeep
git add docs/.gitkeep
git commit -m "Add docs folder for architecture diagrams"
```

**Step 2 — Fork this repo and create the workflow file**

Fork `cloudaifusion/sdlc-automation` to your own GitHub org so you own the skills and workflow and can customise them. Then create `.github/workflows/aws-architecture-sync.yml` in your infrastructure repo:

```yaml
name: AWS Architecture Sync

on:
  pull_request:
    paths:
      - 'infra/terraform/aws/**'   # adjust to match your Terraform path
  workflow_dispatch:

jobs:
  architecture-review:
    uses: your-org/sdlc-automation/.github/workflows/aws-architecture-sync.yml@main
    permissions:
      contents: write
      pull-requests: write
      id-token: write
    with:
      terraform_path: infra/terraform/aws   # adjust to your Terraform path
      docs_path: docs
      diagram_name: architecture
      pr_number: ${{ github.event.pull_request.number }}
    secrets:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

Replace `your-org` with your GitHub org or username. The workflow accepts these inputs if your repo structure differs from the defaults:

| Input | Default | Description |
|---|---|---|
| `terraform_path` | `infra/terraform/aws` | Path to your `.tf` files |
| `docs_path` | `docs` | Where to write the diagram and guide |
| `diagram_name` | `architecture` | Base filename for the outputs |

**Step 3 — Add your secret**

Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret. Add one of:

- `ANTHROPIC_API_KEY`: Your key from [console.anthropic.com](https://console.anthropic.com)
- `CLAUDE_CODE_OAUTH_TOKEN`: Your Claude.ai OAuth token

The workflow will use whichever is available. The OAuth token takes priority.

**Step 4 — Trigger it**

Make any change to a file under your `terraform_path` and open a PR. The workflow will diff the changes, generate or update the diagram and companion guide, commit them back to the branch, and post a PR comment with the risk analysis.

The first run generates a diagram from scratch from all your current Terraform files. Every subsequent PR updates it incrementally based on the diff.

**Step 5 — View the diagram locally**

Install the Draw.io Integration extension in VS Code, pull the branch, and open `docs/architecture.drawio` for a fully interactive diagram — useful for deeper review sessions where you want to explore the full picture rather than just the diff.

### Optional: AWS Bedrock

To use AWS Bedrock instead of a direct API key — for data residency or cost billing reasons — add these GitHub repository variables:

| Variable | Example |
|---|---|
| `AWS_ROLE_ARN` | `arn:aws:iam::123456789:role/github-actions-role` |
| `AWS_REGION` | `eu-west-2` |
| `BEDROCK_MODEL_ID` | `eu.anthropic.claude-sonnet-4-6` |
| `USE_BEDROCK` | `true` |

Full setup instructions for GitHub OIDC trust with AWS Bedrock are in the article.

### Customising for your own conventions

The skills are just Markdown files — edit `.claude/skills/aws-architecture-sync/SKILL.md` or `.claude/skills/aws-architecture-diagram/SKILL.md` in your fork to match your conventions, then point your workflow at your fork:

```yaml
uses: your-org/sdlc-automation/.github/workflows/aws-architecture-sync.yml@main
```

### A note on CI errors you can safely ignore

You may see these messages in the workflow logs:

```
Failed to connect to the bus: Could not parse server address...
Exiting GPU process due to errors during initialization
```

These come from Draw.io (an Electron app) running headlessly in CI without a desktop session. They don't affect the output — as long as you see `PNG export succeeded` at the end, everything worked.

---

## About the Series

This is a series exploring how AI is changing the Software Development Lifecycle — from requirements and design through to deployment and operations. The focus is practical and production-grounded: tools and patterns that actually work, not just ones that look good in a demo.

Subscribe at [www.cloudaifusion.com](https://www.cloudaifusion.com) to follow along.
