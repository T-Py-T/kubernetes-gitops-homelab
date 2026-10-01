# Hireability and discoverability

> Tip-cite bank: base main `e6cbc96` + this PR pending Steward; provenance only; never
> `READY`.

This page orients reviewers and search tools on **kubernetes-gitops-homelab**
without claiming release readiness, operational authorization, benchmark scores,
or a homelab “bake-off” result.

## Purpose

Public, documentation-only GitOps architecture for a multi-environment Kubernetes
homelab managed with Argo CD. Cluster endpoints, application manifests, Helm values,
hostnames, and secrets live in private downstream repositories so the design stays
reusable without exposing a running home network.

## Stack (operating model)

| Layer | Technologies |
| --- | --- |
| Kubernetes | K3s and Talos experiments |
| GitOps | Argo CD app-of-apps |
| Networking | Cilium, ingress, service-mesh experiments |
| Secrets | Vault with External Secrets |
| Policy | Kyverno admission policies |
| Observability | Prometheus, Grafana, Loki/Elastic experiments |

Concrete versions and environment-specific values belong to downstream deployment
repositories, not this tree.

## Smallest verifiable demo

This repository validates itself locally and in pull-request CI; it does not
connect to a cluster or downstream environment.

```bash
git clone https://github.com/T-Py-T/kubernetes-gitops-homelab.git
cd kubernetes-gitops-homelab
./scripts/validate.sh
pre-commit run --all-files
```

These checks exercise repository policy, shell scripts, Markdown, and the pinned
development container definition. They do not prove a live GitOps sync or workload
health.

## Review path (hiring-oriented)

1. [README.md](../README.md) — architecture layers, deployment flow, and validation
   checklist framing.
2. [rebuild-runbook.md](rebuild-runbook.md) — ordered rebuild evidence without
   private placeholders.
3. [.devcontainer/devcontainer.json](../.devcontainer/devcontainer.json) — pinned
   Kubernetes, Helm, and authoring tooling versions.

This shows inspectable documentation and bounded local validation; it is not live
cluster evidence and implies no score or `READY` status.

## Suggested GitHub topics

Repository maintainers may apply topic tags such as:

`kubernetes`, `gitops`, `argocd`, `homelab`, `devops`, `platform-engineering`

Topics aid search only; they do not certify operational readiness or results.

## License

Current documentation and repository-specific configuration are under the
[MIT License](../LICENSE). Historical and third-party material is not relicensed;
see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Related docs

| Document | Role |
| --- | --- |
| [../README.md](../README.md) | Architecture overview and using this repository |
| [rebuild-runbook.md](rebuild-runbook.md) | Generic cluster rebuild sequence |
| [../SECURITY.md](../SECURITY.md) | Reporting sensitive material in this public repo |
| [../THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) | Third-party and historical notices |

Related public repositories: [`nix-homelab`](https://github.com/T-Py-T/nix-homelab),
[`devops-install-scripts`](https://github.com/T-Py-T/devops-install-scripts).
