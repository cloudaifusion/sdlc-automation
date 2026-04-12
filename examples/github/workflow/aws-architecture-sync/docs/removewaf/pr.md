## 🏗️ AWS Architecture Review

**4 resource(s) changed** — 1 added/modified, 3 removed


### ⚠️ Architecture Risks

- **HIGH — WAF Web ACL deleted (`dms-production-waf`)**: All inbound HTTP traffic now reaches the ALB unfiltered. OWASP managed rules (SQLi, XSS, known bad IPs) that were blocking threats at the edge are gone. Any application-layer exploit protection previously handled by WAF must now be handled entirely at the application level.
- **MEDIUM — WAF access logs deleted (`aws-waf-logs-dms-production`)**: Loss of allow/block decision logs and source IP visibility that was used for threat analysis. Incident response for web-layer attacks will have a significant blind spot.

## Resources modified (in-place)

| Service | Role | Change | Risk |
|---|---|---|---|
| **CloudWatch Logs** | ECS application log groups for API and frontend containers | Log group configuration updated (retention or naming) | none |

## Resources permanently deleted

| Service | Role | Risk |
|---|---|---|
| **WAF Web ACL** (`dms-production-waf`) | Regional web application firewall associated with the ALB; blocked SQLi, XSS, and OWASP common threats on all inbound traffic | HIGH |
| **WAF Web ACL Association** | Binding between WAF Web ACL and the ALB that enforced inspection of all inbound requests | HIGH |
| **WAF Logging Configuration** (`aws-waf-logs-dms-production`) | Streamed WAF allow/block decisions and source IPs to CloudWatch for threat analysis and incident response | MEDIUM |

---

![Architecture Diagram](https://github.com/cloudaifusion/s3presignedurl/raw/archupdate/docs/architecture.png)

📖 [View companion guide](https://github.com/cloudaifusion/s3presignedurl/blob/archupdate/docs/architecture.md) · 🔍 [View workflow run](https://github.com/cloudaifusion/s3presignedurl/actions/runs/24302400856)
