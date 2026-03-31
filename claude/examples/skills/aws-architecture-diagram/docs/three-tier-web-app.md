# Your Application on AWS — Plain-English Guide

## Overview

This diagram shows how your web application runs in the cloud. When a user opens a browser and visits your site, their request travels through several layers of infrastructure before reaching the right service — all within a secure, private network hosted on Amazon Web Services (AWS).

---

## What Each Component Does

| Diagram Label | What It Is (Technical) | What It Does for You |
|---|---|---|
| **Users** | End users | The people who visit and use your application |
| **Internet Door** | Internet Gateway | The secure entrance/exit point between the internet and your private network |
| **Traffic Director** | Application Load Balancer (ALB) | Receives all incoming requests and routes them to the right service — website pages go one way, data requests go another |
| **Outbound Access** | NAT Gateway | Allows your internal servers to download updates and software packages without being exposed to the internet |
| **Website** | Frontend (ECS Fargate) | Serves the web pages and user interface that people see in their browser |
| **API Server** | Backend API (ECS Fargate) | Handles the business logic — processing requests, reading/writing data, applying rules |
| **Database** | RDS PostgreSQL | Stores all your application data (records, users, history) with automatic 7-day backups |
| **File Storage** | Amazon S3 | Stores uploaded documents and files, encrypted and private, with version history |
| **App Images** | Elastic Container Registry (ECR) | Stores the packaged application code that the Website and API Server load when they start up |
| **Secrets Vault** | AWS Secrets Manager | Securely stores sensitive credentials (like the database password) so they never appear in code |
| **Monitoring & Logs** | Amazon CloudWatch | Collects activity logs from all running services so issues can be investigated quickly |

---

## How a User Request Flows (Step by Step)

```
① User opens your website in a browser
       ↓
   Passes through the Internet Door into your private network
       ↓
② Traffic Director receives the request and decides where to send it:
       │
       ├─► ② Web page request → Website serves the page back to the user
       │
       └─► ③ Data request (e.g. saving a form) → API Server handles the logic
                   │
                   ├─► ④ Reads & writes records in the Database
                   │
                   └─► ⑤ Stores or retrieves files from File Storage
```

---

## Background Operations (Dashed Arrows)

These happen automatically and are not triggered by user actions:

| What Happens | When |
|---|---|
| Website and API Server pull their **App Images** | Every time a new version is deployed or the server restarts |
| API Server reads the **database password** from the Secrets Vault | At startup, before accepting any requests |
| Both servers send **activity logs** to Monitoring & Logs | Continuously, while running |

---

## Security Design

Everything in the **Private Zones** (application servers and database) is invisible to the internet — there is no direct path in. The only way traffic enters is through the **Traffic Director**, which sits in the public zone and only forwards recognised requests.

- **Passwords and credentials** are never stored in the application code — only in the Secrets Vault
- **Files** in File Storage are encrypted and not publicly accessible
- **Outbound Access** lets servers reach the internet for updates, but nothing can reach them back from outside

---

## Resilience and Availability

- The network is configured across **two separate physical locations** (Availability Zones) within the London region, so a hardware failure in one location does not take the application down
- The **Traffic Director** automatically stops sending traffic to any server that becomes unhealthy and rolls back a bad deployment
- **Database backups** are retained for 7 days

---

## Where This Lives

All infrastructure runs in **AWS EU West 2 (London)**, keeping data within the UK/EU for compliance purposes.
