# DMS AWS Architecture

Region: **eu-west-2** (London)

## Overview

The Document Management System (DMS) runs on AWS using ECS Fargate for compute, RDS PostgreSQL for persistence, and S3 for document storage. Clients never upload files through the API — they receive a short-lived presigned URL and PUT directly to S3. All inbound traffic is inspected by AWS WAF before reaching the load balancer.

---

## Components

| Service | Resource | Purpose |
|---|---|---|
| WAF Web ACL | `dms-production-waf` | Regional WAF associated with the ALB; inspects all inbound HTTP traffic, blocks common web exploits (OWASP rules); access logs stream to CloudWatch |
| Application Load Balancer | `dms-production-alb` | Public entry point behind WAF; routes `/api/*` to API, default to frontend |
| ECS Fargate — API | `dms-production-api` | .NET 10 minimal API; generates presigned S3 URLs, persists metadata to RDS |
| ECS Fargate — Frontend | `dms-production-frontend` | React 19 SPA served by nginx |
| RDS PostgreSQL 17 | `dms-production-postgres` | Relational store for document metadata; private subnet only |
| S3 | `dms-documents-<account>-production` | Encrypted object store; versioning enabled; CORS allows browser PUT |
| ECR | `dms-production-api` / `dms-production-frontend` | Container image registry; lifecycle policy retains last 10 images |
| Secrets Manager | `dms/production/db-connection-string` | RDS connection string injected into the API task at launch |
| CloudWatch Logs (ECS) | `/ecs/dms-production/api` + `/frontend` | Structured application logs; 30-day (API) and 14-day (frontend) retention |
| CloudWatch Logs (WAF) | `aws-waf-logs-dms-production` | WAF access logs showing allowed/blocked requests; used for threat analysis |
| NAT Gateway | `dms-production-nat` | Outbound internet for private subnet resources (ECR pulls, AWS APIs) |

---

## Network Layout

```
Internet
   │
   ▼
Internet Gateway
   │
   ▼
WAF Web ACL  (inspects & filters all inbound traffic)
   │
   ▼
┌──────────────────── VPC  10.0.0.0/16 ─────────────────────────┐
│                                                                 │
│  ┌── Public Subnets (eu-west-2a / 2b) ──────────────────────┐ │
│  │  ALB (:80)          NAT Gateway                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌── Private Subnets (eu-west-2a / 2b) ─────────────────────┐ │
│  │  Frontend Fargate (:80)    API Fargate (:8080)            │ │
│  │                            RDS PostgreSQL (:5432)         │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Flows

### 1. Web UI request

```
User → IGW → WAF → ALB → Frontend Fargate (port 80)
```

WAF evaluates the request against managed rule groups before it reaches the ALB. The ALB default listener rule forwards passing traffic to the frontend target group. The React SPA is served by nginx inside the Fargate container.

### 2. API request

```
User → IGW → WAF → ALB (/api/*) → API Fargate (port 8080)
```

WAF inspects the request first. The listener rule with priority 10 matches `/api/*` and forwards to the API target group.

### 3. File upload (presigned URL workflow)

```
1. Browser → POST /api/documents/upload-url  →  API returns presigned S3 PUT URL (15 min TTL)
2. Browser → PUT <presigned-url>             →  S3 directly (bypasses API)
3. Browser → POST /api/documents/confirm     →  API verifies object exists, writes metadata to RDS
```

No file data transits the API. The S3 bucket has CORS configured to allow browser PUT requests from any origin (tighten to your domain post-deployment). The direct S3 PUT bypasses WAF as it goes to the S3 presigned endpoint directly.

---

## Security

- **WAF Web ACL**: associated with the ALB; evaluates AWS Managed Rules (common rule set) on every inbound request; blocks SQLi, XSS, and known bad inputs before they reach the application layer
- **ALB security group**: inbound TCP 80 from `0.0.0.0/0`
- **API security group**: inbound TCP 8080 from ALB SG only
- **Frontend security group**: inbound TCP 80 from ALB SG only
- **RDS security group**: inbound TCP 5432 from API SG only; no public access
- **S3 bucket**: all public access blocked; server-side AES-256 encryption; versioning enabled
- **IAM task role** (`api-task-role`): `s3:PutObject` + `s3:GetObject` on the documents bucket only
- **IAM execution role**: `AmazonECSTaskExecutionRolePolicy` + `secretsmanager:GetSecretValue` for the DB secret

---

## Observability

| Log group | Retention | Contents |
|---|---|---|
| `/ecs/dms-production/api` | 30 days | API application logs (awslogs driver) |
| `/ecs/dms-production/frontend` | 14 days | nginx access + error logs |
| `aws-waf-logs-dms-production` | configurable | WAF allow/block decisions, rule match details, source IPs |

Container Insights is enabled on the ECS cluster for CPU/memory metrics. WAF metrics (blocked requests, rule match counts) are also available in CloudWatch Metrics under the `AWS/WAFV2` namespace.

---

## Deployment Circuit Breaker

Both ECS services have `deployment_circuit_breaker` enabled with automatic rollback. If a new task fails its health check (`/health` for API, `/` for frontend), ECS rolls back to the previous task definition automatically.
