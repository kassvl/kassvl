[![Status](https://img.shields.io/badge/Status-Open%20to%20Work%3A%20Junior%20Cloud%20%2F%20DevOps-2EA043?style=flat-square)](https://kadirhanemrememis.xyz)
[![Location](https://img.shields.io/badge/Location-Wroc%C5%82aw%2C%20Poland-1F6FEB?style=flat-square)](https://kadirhanemrememis.xyz)
[![Portfolio](https://img.shields.io/badge/Portfolio-kadirhanemrememis.xyz-0A0A0A?style=flat-square&logo=vercel&logoColor=white)](https://kadirhanemrememis.xyz)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-kadirhan--emre-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/kadirhan-emre)

```bash
$ whoami
kadirhan — cloud & devops engineer (in training)

$ cat /etc/motd
Final-year IT student in Wrocław. EPAM Cloud & DevOps Trainee ('26).
I build meshes, break them on purpose, and write the tooling that
answers the pager: deterministic incident response for Istio.

$ now
Open to work: junior Cloud / DevOps / Platform roles,
full-time or working-student. Wrocław preferred · EU remote OK ·
Karta Pobytu holder, no sponsorship needed_
```

## MeshMedic — deterministic first responder for Istio

<a href="https://github.com/kassvl/meshmedic">
  <img src="https://raw.githubusercontent.com/kassvl/meshmedic/main/demo/video/meshmedic-demo.gif" alt="MeshMedic demo: live fault to evidence-backed pull request to healed mesh" width="100%" />
</a>

Prometheus signal in → reviewed failure-catalog match → evidence-backed GitOps pull request out.
No LLM in the detection or remediation path, and no write access to the cluster.

- 19-scenario failure catalog — every entry live-verified on a kind + Istio Ambient testbed
- reads the ambient L4 mTLS denials in ztunnel telemetry that never reach request metrics
- the fix arrives as a PR carrying labeled PromQL evidence, config reads and a rollback plan
- learns per-service latency baselines (EWMA) and records unknown anomalies for human triage
- closes the loop: resolution report with MTTR once the incident recovers

**[meshmedic →](https://github.com/kassvl/meshmedic)** · **[mesh-incidents-bench →](https://github.com/kassvl/mesh-incidents-bench)** — the reproducible failure scenarios I built to score it honestly. Misses are published, author bias is disclosed.

## Selected work

| repo | what it is | built with |
|---|---|---|
| [meshmedic](https://github.com/kassvl/meshmedic) | Incident-time remediation for Istio: signal in, reviewable PR out | Go · Prometheus · Argo CD |
| [mesh-incidents-bench](https://github.com/kassvl/mesh-incidents-bench) | Reproducible mesh failure scenarios with ground truth and scoring rubrics | Bash · kind · Istio Ambient |
| [istio-ambient-aiops-thesis](https://github.com/kassvl/istio-ambient-aiops-thesis) | Engineering thesis: ambient vs sidecar cost + reliability, AIOps closed loop | Python · Kubernetes |
| [biometric-payment-infrastructure](https://github.com/kassvl/biometric-payment-infrastructure) | FinTech-grade Terraform IaC: EKS + Istio Ambient, PCI-DSS / GDPR / EU DORA mapped | Terraform · AWS |
| [multi-cluster-istio-mesh](https://github.com/kassvl/multi-cluster-istio-mesh) | Two-cluster zero-trust mesh lab: strict mTLS, default-deny policies | Istio · Kind · Kiali |
| [GitHealthCheck-CLI](https://github.com/kassvl/GitHealthCheck-CLI) | Offline Git repo auditor: 20+ quality metrics, single binary, zero network calls | Python |

## Stack

```text
languages       Go · Python · TypeScript · Bash · HCL
cloud           AWS (EKS, Aurora, WAF v2, IRSA, KMS) · OCI · GCP (lab)
orchestration   Kubernetes · Helm · Kind · kustomize
service mesh    Istio · Istio Ambient (ztunnel + waypoint) · Envoy · Gateway API
iac / gitops    Terraform · Argo CD · Flux · GitHub Actions · GitLab CI
observability   Prometheus · PromQL · Grafana · Loki · Kiali
security        mTLS · IRSA · External Secrets · Checkov · tfsec · Trivy
```

## Background

- B.Eng. Information Technology — WSB Merito Wrocław (2023 → 2027)
- Engineering thesis: *Istio Ambient Mesh vs the sidecar pattern, with an AIOps closed-loop controller*
- EPAM Cloud & DevOps Trainee (2026)
- Oracle Cloud Infrastructure 2025 Foundations Associate
- Turkish (native) · English (C1+) · Polish (A2–B1)

---

> Junior role and working-student inquiries welcome — [kadirhanemre@proton.me](mailto:kadirhanemre@proton.me) · Wrocław preferred, EU remote OK.
