# Kubernetes GitOps Homelab

An architecture and operating-model case study for a multi-environment
Kubernetes homelab. The portfolio signal is the deployment system around the
workloads: isolated failure domains, ordered GitOps reconciliation, security
boundaries, observability, and a rebuild-first recovery strategy.

> [!IMPORTANT]
> The current default-branch tree is documentation-only. Live Argo CD
> applications, Helm values, hostnames, secrets, and environment-specific
> deployment manifests now remain in private downstream repositories. Earlier
> public commit history contains an archival implementation snapshot from
> before that boundary; it must not be interpreted as current infrastructure.

## Why this project matters

Cloud deployment examples are easy to create once and much harder to operate
repeatably. This design asks a stronger question:

**Can a cluster be rebuilt, validated, promoted, observed, and rolled back
through the same documented path every time?**

The public case study shows the intended answer:

- separate cluster lifecycle from workload configuration;
- reconcile platform, monitoring, and application layers in dependency order;
- test changes in disposable environments before promotion;
- keep current secrets and environment endpoints outside public source; and
- treat recovery as recreation from declared state instead of manual repair.

## Architecture

```mermaid
flowchart LR
    A[Cluster bootstrap] --> B[Networking and storage checks]
    B --> C[Argo CD bootstrap]
    C --> D[Platform services]
    D --> E[Monitoring and policy]
    E --> F[Applications]
    F --> G[Health and reconciliation checks]

    H[Private environment configuration] --> C
    H --> D
    H --> E
    H --> F
```

| Layer | Responsibility | Public evidence boundary |
| --- | --- | --- |
| Cluster | Distribution, node lifecycle, CNI, storage, and DNS | Architecture and operating contract |
| GitOps | Argo CD bootstrap, projects, sync ordering, and promotion | Current live definitions remain private |
| Platform | Ingress, identity, secrets, and policy | Service choices and dependency model |
| Observability | Metrics, dashboards, logs, and alert routing | Verification approach and failure signals |
| Applications | Namespaces, routes, values, and data services | Current workload inventory is intentionally omitted |

## Deployment contract

A deployment is not complete merely because manifests apply. The intended
operating sequence is:

1. Create or rebuild a cluster from a known configuration.
2. Verify node readiness, networking, DNS, ingress, and storage prerequisites.
3. Bootstrap Argo CD and register only the repositories required for the target
   environment.
4. Reconcile platform services before monitoring and application workloads.
5. Validate sync health, workload readiness, service reachability, and secret
   references.
6. Promote the same structure with bounded environment overrides.
7. Roll back through Git, or recreate the cluster when platform state is no
   longer trustworthy.

This is an operating contract, not a claim that every step is automated or has
completed successfully. The public repository does not claim current uptime,
production traffic, successful reconciliation, or a completed recovery drill.

## Cluster strategy

| Environment | Primary use | Change posture |
| --- | --- | --- |
| Development | Fast infrastructure and workload experiments | Disposable; optimize for feedback |
| Staging | Production-like validation | Rehearse upgrades and recovery before promotion |
| Data | Stateful services and storage experiments | Prioritize backup and restore behavior |
| Production | Stable end-user workloads | Prefer declared replacement over in-place drift |

The “no in-place upgrades” strategy is deliberate: trial a new Kubernetes or
node image in an isolated cluster, validate it, then move workloads while the
previous cluster remains the rollback boundary.

## Platform decisions

| Concern | Selected approach | Reasoning |
| --- | --- | --- |
| Lightweight Kubernetes | K3s and Talos experiments | Low-cost clusters with different lifecycle tradeoffs |
| Reconciliation | Argo CD app-of-apps | Visible dependency ordering and Git-backed rollback |
| Networking | Cilium with ingress and service-mesh experiments | Policy, observability, and load-balancing primitives |
| Secrets | Vault plus External Secrets | Secret material stays outside Git while references remain declarative |
| Policy | Kyverno | Admission-time guardrails expressed as Kubernetes resources |
| Metrics and logs | Prometheus, Grafana, and Loki/Elastic experiments | Make platform and workload failures inspectable |

## Evidence status

The historical repository record supports that the architecture was expressed
as versioned desired state and later split into separate repositories. It does
not prove that a cluster reached or maintained that state. No sanitized current
deployment logs, test reports, recovery timings, or telemetry are retained in
this public tree.

The next portfolio-grade artifact is a sanitized recovery-drill bundle with:

- exact cluster and tool versions;
- bootstrap and validation commands;
- failure criteria and rollback decision;
- timing from empty cluster to healthy reconciliation; and
- redacted raw command output.

Until that artifact exists, judge this repository as an architecture and
operating-model case study rather than a production-operations claim.

## Review checklist

- Are ownership and security boundaries explicit?
- Is deployment order deterministic?
- Can an environment be recreated without undocumented console work?
- Are validation and rollback part of the design?
- Are intended capabilities separated from retained evidence?

## Related public work

- [`nix-homelab`](https://github.com/T-Py-T/nix-homelab) covers reproducible
  host and service configuration for the successor environment.
- [`devops-install-scripts`](https://github.com/T-Py-T/devops-install-scripts)
  contains reusable CI/CD and deployment building blocks used across public
  cloud case studies.

This repository does not currently include a repository-wide license file.
