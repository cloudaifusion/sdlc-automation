# SDLC Automation — Examples

Example code and reference architectures to accompany the **SDLC Automation** series [Here](https://www.cloudaifusion.com).

## Architecture Drift: Using Claude Code to Keep Your Terraform Honest

> *What if your Terraform could draw its own architecture diagram?*

This repository contains the Terraform files used in the first article of the series. The article explores how architecture diagrams drift from the infrastructure they describe — and how a Claude Code skill can reverse-engineer accurate Draw.io diagrams directly from Terraform, closing that loop automatically.

Read the full article: [Architecture Drift: Using Claude Code to Keep Your Terraform Honest](https://www.cloudaifusion.com/p/architecture-drift-using-claude-code)

---

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

---

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

---

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

### About the Series

This is the first in a series exploring how AI is changing the Software Development Lifecycle — from requirements and design through to deployment and operations. The focus is practical and production-grounded: tools and patterns that actually work, not just ones that look good in a demo.

Subscribe at [www.cloudaifusion.com](https://www.cloudaifusion.com) to follow along.
