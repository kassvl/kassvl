[![Status](https://img.shields.io/badge/Status-Open%20to%20Cloud%20%2F%20DevOps%20Internships-2EA043?style=flat-square)](https://kadirhanemrememis.xyz)
[![Location](https://img.shields.io/badge/Location-Wroc%C5%82aw%2C%20Poland-1F6FEB?style=flat-square)](https://kadirhanemrememis.xyz)
[![Work Auth](https://img.shields.io/badge/Work%20Auth-Karta%20Pobytu%20(EU)-8957E5?style=flat-square)](https://kadirhanemrememis.xyz)
[![EPAM](https://img.shields.io/badge/EPAM-Cloud%20%26%20DevOps%20Trainee-FF6B0B?style=flat-square)](https://kadirhanemrememis.xyz)
[![OCI](https://img.shields.io/badge/Oracle%20Cloud-2025%20Foundations%20Associate-F80000?style=flat-square&logo=oracle)](https://kadirhanemrememis.xyz)

### kassvl / README.md

```bash
$ whoami
kadirhan — cloud & devops engineer (in training)

$ cat /etc/motd
3rd-year IT student at WSB Merito Wrocław.
EPAM Cloud & DevOps Trainee (Feb–Apr 2026).
Building production-shaped AWS platforms — Terraform IaC,
EKS + Istio Ambient, DevSecOps CI gates — with EU compliance
baked in (PCI-DSS, GDPR, EU DORA).

$ now
Preparing for Cloud / DevOps / DevSecOps internships and
working-student roles · Wrocław preferred · EU remote OK_
```

[![Email](https://img.shields.io/badge/Email-kadirhanemre%40proton.me-6D4AFF?style=for-the-badge&logo=protonmail&logoColor=white)](mailto:kadirhanemre@proton.me)
[![Portfolio](https://img.shields.io/badge/Portfolio-kadirhanemrememis.xyz-0A0A0A?style=for-the-badge&logo=vercel&logoColor=white)](https://kadirhanemrememis.xyz)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-kadirhan--emre-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/kadirhan-emre)

---

## Tech Stack & Tooling

```text
languages       Python · TypeScript · Bash · HCL · SQL · YAML
cloud           AWS (EKS, Aurora, WAF v2, IRSA, KMS) · OCI · Azure · GCP (lab)
orchestration   Kubernetes 1.30 · Helm · Kustomize · Kind
service mesh    Istio · Istio Ambient (ztunnel + waypoint) · Envoy
iac             Terraform 1.9 · OpenTofu · Ansible
ci / cd         GitHub Actions · GitLab CI · Argo CD · Flux · Jenkins
observability   Prometheus · Grafana · Loki · Tempo · OpenTelemetry · Kiali
security        mTLS · OPA · IRSA · External Secrets Operator
                Checkov · tfsec · Trivy · Kyverno
compliance      PCI-DSS v4.0 · GDPR / Schrems II · EU DORA · CIS · NIST 800-53
```

---

##  Featured Projects

###  Secure Biometric Payment Infrastructure
> FinTech-grade Terraform IaC modeled after a regulated European payment processor.

- **7 Terraform 1.9 modules** across **2 AWS regions** (eu-central-1 primary + eu-west-1 DR)
- **EKS 1.30 + Istio Ambient** (ztunnel + waypoint) — sidecar-less mTLS
- **IRSA** + **External Secrets Operator** + **AWS Secrets Manager** — zero long-lived keys
- **3 CI scanners** (Checkov + tfsec + Trivy) gate every PR — fail blocks merge
- Compliance-mapped to **PCI-DSS v4.0, GDPR / Schrems II, EU DORA, CIS, NIST 800-53**

[**View Repository →**](https://github.com/kassvl/biometric-payment-infrastructure)

###  Multi-Cluster Istio Service Mesh
> Two-cluster Kubernetes mesh simulating AWS + GCP locally on Kind.

- Automatic **mTLS** verified via `istioctl x authz check`
- **AuthorizationPolicy + PeerAuthentication** enforced cluster-wide
- East-west gateway for true multi-cluster discovery **in roadmap**
- **Kiali + Prometheus + Grafana** for golden-signal observability

[**View Repository →**](https://github.com/kassvl/multi-cluster-istio-mesh)

###  GitHealthCheck CLI
> Audits Git repository health — 20+ quality metrics, single binary, zero network calls.

- Stale branches, large files, commit hygiene, contributor patterns
- SOLID / architecture pressure scoring without AST parsing
- Designed for OSS maintainers and enterprise repos enforcing org-wide standards

[**View Repository →**](https://github.com/kassvl/GitHealthCheck-CLI)

###  GreenFleet — Renewable Energy Forecasting
> FastAPI + Next.js 14 platform with 7-day ML forecasts.

- Battery-storage simulation for distributed off-grid sites
- Real-time telemetry ingestion + chart-grade dashboards
- Container-ready, K8s-deployable

[**View Repository →**](https://github.com/kassvl/Rxxxxx-GreenFleet)

---

##  Education & Certifications

| | |
|---|---|
| 🎓 **B.Eng. — Information Technology** · WSB Merito Wrocław | Sep 2023 → Jun 2027 |
| 💼 **EPAM Cloud & DevOps Trainee** · Wrocław | Feb 2026 – Apr 2026 |
| 🏅 **Oracle Cloud Infrastructure 2025 Foundations Associate** | 2025 |
| 🐧 **Introduction to Cloud Infrastructure (LFS151x)** · Linux Foundation | — |

**Engineering thesis:** *"Multi-Cluster Resiliency with Istio Ambient Mesh — a sidecar-less service-mesh architecture with AIOps-driven failover."*

---

##  Languages

`Turkish (Native)` · `English (C1+, full professional)` · `Polish (A2, improving)`

---

>  *Working student / internship inquiries welcome — Wrocław preferred, Warsaw / Kraków / Gdańsk / EU remote OK. Karta Pobytu holder, no sponsorship needed.
<!-- Profile views (optional, free counter) -->
<p align="center">
  <img src="https://komarev.com/ghpvc/?username=kassvl&label=Profile%20views&color=8957e5&style=flat-square" alt="Profile views" />
</p>
