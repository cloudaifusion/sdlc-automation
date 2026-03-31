# DMS Production Architecture — eu-west-2 (London)

## Overview

A containerised Document Management System (DMS) running on ECS Fargate with path-based ALB routing, a managed PostgreSQL database, and private S3 storage for documents. All compute runs in private subnets across two Availability Zones with outbound internet access via a single NAT Gateway.

---

## Components

| Service | Resource Name | Role | Why chosen |
|---|---|---|---|
| Internet Gateway | `dms-production-igw` | Entry point for public traffic from the internet | Required for internet-facing ALB in public subnets |
| Application Load Balancer | `dms-production-alb` | Terminates HTTP, routes by path to frontend or API | Path-based routing (`/api/*`) allows one ALB to front both services |
| NAT Gateway | `dms-production-nat` (+ Elastic IP) | Outbound internet access for private subnet resources | Fargate tasks need outbound access (ECR pulls, CloudWatch, Secrets Manager) without exposing a public IP |
| ECS Cluster | `dms-production-cluster` | Logical grouping for Fargate services; Container Insights enabled | Serverless — no EC2 instances to manage or patch |
| Frontend Service | `dms-production-frontend` | Serves the UI; Fargate task (0.25 vCPU, 512 MB) on port 80 | Stateless container, scales horizontally; circuit breaker + auto-rollback for safe deploys |
| API Service | `dms-production-api` | .NET API (ASP.NET Core) on port 8080; Fargate task (0.5 vCPU, 1024 MB) | Reads environment + secrets at startup; ECS Exec enabled for live debugging |
| RDS PostgreSQL 17 | `dms-production-postgres` | Primary relational store for DMS data | `db.t4g.micro` on gp3; 7-day automated backups; accessible only from the API security group |
| ECR | `dms-production-api` / `dms-production-frontend` | Stores container images; scan-on-push enabled; lifecycle keeps last 10 images | Private registry in-region — images are pulled via NAT Gateway |
| S3 Documents Bucket | `dms-documents-<account>-production` | Stores uploaded documents | Server-side AES256 encryption; versioning enabled; all public access blocked; CORS configured for presigned URL browser uploads |
| Secrets Manager | `/dms/production/db-connection-string` | Stores the PostgreSQL connection string injected at task startup | Avoids baking credentials into task definitions or environment variables |
| CloudWatch Logs | `/ecs/dms-production/api` (30 d) / `/ecs/dms-production/frontend` (14 d) | Centralised log storage for both Fargate services | awslogs driver configured on each container |

---

## Data Flows

### Inbound request (browser → API)

1. Browser sends `HTTP :80` to the ALB's public DNS name via the Internet Gateway.
2. ALB listener evaluates path rules:
   - `/* ` (default) → forwards to the **Frontend** target group (port 80).
   - `/api/*` (priority 10) → forwards to the **API** target group (port 8080).
3. Target group health checks (`GET /health` for API, `GET /` for frontend) ensure traffic only reaches healthy tasks.
4. The **API Service** queries **RDS PostgreSQL** on TCP port 5432 — the RDS security group only accepts connections from the API security group.

### Document upload / download

5. The API uses its IAM task role (`s3:PutObject`, `s3:GetObject`) to read or write documents in the **S3 Documents Bucket**.
6. For browser-initiated uploads, the API can issue S3 presigned URLs (CORS configured: GET, PUT, HEAD).

### Container startup

7. At startup, ECS injects the DB connection string from **Secrets Manager** (`GetSecretValue`) into the API container as the environment variable `ConnectionStrings__DefaultConnection`.

### Outbound (private subnet egress)

8. Fargate tasks in the private subnets route `0.0.0.0/0` through the **NAT Gateway** → **Internet Gateway** for:
   - Pulling container images from **ECR**.
   - Sending logs to **CloudWatch Logs** via the `awslogs` driver.
   - Calling **Secrets Manager** at task startup.

---

## Key Design Decisions

**Serverless compute (Fargate)**: No EC2 instances to patch or right-size. The ECS execution role grants least-privilege access to ECR and CloudWatch; the API task role separately grants only the S3 actions required.

**Path-based routing on a single ALB**: One ALB handles both services. The frontend is the default action; the `/api/*` path rule (priority 10) captures API traffic before the default. This avoids two separate load balancers and a split DNS setup.

**Private subnets for all compute and data**: The ALB is the only internet-facing resource. Fargate tasks, RDS, and the NAT Gateway's Elastic IP are the only components in the public subnet boundary — and only the NAT Gateway has an EIP. RDS is locked to the API security group at the port level.

**Single NAT Gateway**: Cost-optimised for production at this scale. For stricter HA (AZ failure tolerance for outbound traffic), a NAT Gateway per AZ should be added.

**Deployment safety**: Both services have the ECS circuit breaker enabled with auto-rollback. A failed deployment will automatically revert to the previous task definition revision.

**S3 document access**: All public access is blocked on the bucket. The API issues presigned URLs for direct browser uploads/downloads, keeping document bytes off the API container and reducing load.

---

## Cost / Scaling Notes

- **Fargate**: Scales per task. Current desired count is 1 for both services — add an Application Auto Scaling policy on ECS CPU/memory metrics for production load.
- **RDS `db.t4g.micro`**: Suitable for low-to-moderate workloads. Multi-AZ is disabled (configurable); enable for HA and zero-downtime patching in production.
- **S3**: Pay-per-use; versioning adds storage cost proportional to change frequency.
- **NAT Gateway**: Billed per hour plus per-GB data processed. ECR image pulls and CloudWatch log writes all route through it — minimise unnecessary outbound calls.
- **CloudWatch Logs**: Retention is set to 30 days (API) and 14 days (Frontend) to balance observability cost.
