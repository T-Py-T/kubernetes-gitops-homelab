> [!IMPORTANT]
> **Historical repository**
>
> This repository documents an earlier Kubernetes homelab design and is no
> longer the active configuration. Current work has moved to
> [T-Py-T/nix-homelab](https://github.com/T-Py-T/nix-homelab). The material
> below is retained as historical design context; statuses, hardware details,
> deployment steps, and roadmap items should not be read as current operations.

# Homelab - K3s GitOps Platform (Historical)

This repository preserved an earlier GitOps platform design for K3s. It is not
maintained as a current or production-ready deployment.

---

## Overview

This homelab documented a **multi-repository GitOps pattern** with separate
repositories for platform, monitoring, and applications, orchestrated by
ArgoCD using an app-of-apps pattern. It served as a design for testing services,
container hardening, and DevSecOps practices.

### Historical Security References

The design notes referenced these sources for service testing and container
hardening:

- [**Repo1**](https://repo1.dso.mil/) - DoD approved charts and applications
- [**Ironbank**](https://ironbank.dso.mil/) - Hardened container registry

---

## Architecture Overview

### Cluster Strategy: "No In-Place Upgrades"

Instead of one monolithic cluster, the design used **multiple single-purpose
clusters** to explore isolation, security, and maintainability. Its documented
high-availability approach is historical and is not the current homelab state.

For development and staging, the design considered single-node clusters for
testing newer cluster operating systems such as Talos or K3D before migration,
while retaining the previous cluster as a fallback.

| Cluster | Purpose | Historical status at last update | Nodes |
|:--------|:--------|:-------|:------|
| **Prod** | End-user applications (stateless) | 🔄 Planned (OpenShift) | 3 control + 6 workers |
| **Staging** | Application testing & validation | ✅ Running (Talos/Omni) | 2 control + 4 workers |
| **Data** | Databases & persistent storage | 🔄 Planned (K3s) | 2 control + 2 workers |
| **Dev** | Development & container testing | ✅ Running (K3s) | 1 control + 2 workers |

### Why This Design Was Explored

- **Blast radius containment** - Issues don't affect other environments
- **Independent scaling** - Right-size each cluster for its workload
- **Easy disaster recovery** - Rebuild clusters from code, restore data from backups
- **Technology diversity** - Test different platforms (OpenShift, Talos, K3s)

---

## Documented Hardware Setup

**Historical philosophy**: inexpensive, small, upgradeable refurbished business PCs

### Base Hardware Stack

- **HP EliteDesk 800 G5 Mini** (Control Planes): i5-6400T, 16GB RAM, 240GB SSD
- **HP EliteDesk 800 G2 Mini** (Workers): i3-6100T, 8-16GB RAM, 240GB SSD
- **Documented cost**: ~$100-150 per node (refurbished)
- **Documented upgrade path**: RAM expandable for larger workloads

### Cluster Specifications

<details>
<summary><strong>Historical Production Cluster Plan (OpenShift)</strong></summary>

**Purpose**: Mission-critical applications with enterprise support

- **Control Plane**: 3x HP EliteDesk 800 G5 Mini (i5-6400T/16GB/240GB)
- **Workers**: 6x HP EliteDesk 800 G2 Mini (i5-6400T/16GB/240GB)
- **Features**: HA, automated failover, enterprise monitoring

</details>

<details>
<summary><strong>Historical Staging Cluster State (Talos/Omni)</strong></summary>

**Purpose**: Pre-production testing and validation

- **Control Plane**: 2x HP EliteDesk 800 G5 Mini (i5-6400T/16GB/240GB)
- **Workers**: 4x HP EliteDesk 800 G2 Mini (i3-6100T/8GB/240GB)
- **Features**: Immutable OS, declarative configuration

</details>

<details>
<summary><strong>Historical Data Cluster Plan (K3s)</strong></summary>

**Purpose**: Centralized databases and shared storage

- **Control Plane**: 2x HP EliteDesk 800 G5 Mini (i5-6400T/16GB/240GB)
- **Workers**: 2x HP EliteDesk 800 G2 Mini (i3-6100T/8GB/240GB)
- **Storage**: Synology DS224+ NAS with CSI integration

</details>

<details>
<summary><strong>Historical Development Cluster State (K3s)</strong></summary>

**Purpose**: Development, testing, and experimentation

- **Control Plane**: 1x HP EliteDesk 800 G5 Mini (i5-6400T/16GB/240GB)
- **Workers**: 2x HP EliteDesk 800 G2 Mini (i3-6100T/8GB/240GB)
- **Features**: Lightweight, fast iteration, disposable workloads

</details>

---

## Historical Deployment Strategy

### Multi-Repository GitOps Workflow

#### Historical Cluster Lifecycle — Deployment Order (Top → Bottom)

Each repository was intended to be managed as a separate ArgoCD project using
an app-of-apps pattern.

| Logo | Purpose|
|:----:|:-----|
| [homelab-gitops](https://github.com/T-Py-T/homelab-gitops)  | ArgoCD bootstrap + cluster scripts |
| [homelab-platform](https://github.com/T-Py-T/homelab-platform) | Core infrastructure (Istio, Vault, Keycloak) |
| [homelab-monitoring](https://github.com/T-Py-T/homelab-monitoring) | Observability (Prometheus, Grafana, ELK) |
| [homelab-apps](https://github.com/T-Py-T/homelab-applications) | End-user applications |

#### Intended Benefits of This Approach

- Dependency Control: Platform services deploy before apps that need them
- Team Separation: Different teams can own different repositories
- Independent Releases: Update monitoring without touching applications
- Security Boundaries: Separate access controls per repository type
- Scalability: Add new app repos without touching core infrastructure

## 🔧 Documented Technology Stack

### Core Platform

| Logo | Name | Description |
|:----:|:-----|:-----------|
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/svg/kubernetes.svg"> | [K3s](https://k3s.io/) | Lightweight Kubernetes - easy to install, half the memory, all in a binary < 100MB |
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/cilium.svg"> | [Cilium](https://cilium.io/) | eBPF-based networking, security, and observability |
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/svg/argo-cd.svg"> | [ArgoCD](https://argo-cd.readthedocs.io/) | Declarative GitOps continuous delivery |

### Platform Services

| Logo | Name | Description |
|:----:|:-----|:-----------|
| <img width="32" style="filter: invert(51%) sepia(86%) saturate(2331%) hue-rotate(195deg) brightness(97%) contrast(101%);" src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/istio.svg"> | [Istio](https://istio.io/) | Service mesh for security, observability, and traffic management |
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/svg/vault.svg"> | [HashiCorp Vault](https://www.vaultproject.io/) | Secrets management and PKI |
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/svg/keycloak.svg"> | [Keycloak](https://www.keycloak.org/) | Identity and access management |
| <img width="32" src="https://www.svgrepo.com/download/477066/lock.svg"> | [External Secrets](https://external-secrets.io/) | Vault integration for K8s secrets |
| <img width="32" src="https://avatars.githubusercontent.com/u/68448710?s=200&v=4">| [Kyverno](https://kyverno.io/) | Policy engine for security and governance |

### Monitoring Services

| Logo | Name | Description |
|:----:|:-----|:-----------|
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/svg/grafana.svg"> | [Grafana](https://grafana.com/) | The open observability platform |
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/svg/prometheus.svg"> | [Prometheus](https://prometheus.io/) | An open-source monitoring system with a dimensional data model, flexible query language, efficient time series database and modern alerting approach |
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/svg/elastic.svg"> | [Elastic Stack](https://www.elastic.co/) | Centralized logging and analytics |

### User Applications

| Logo | Name | Description |
|:----:|:-----|:-----------|
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/commafeed.svg"> | [Commafeed](https://www.commafeed.com/#/welcome) | Bloat free RSS feed reader |
| <img width="32" src="https://www.svgrepo.com/download/499807/home-page.svg"> | [Homepage](https://github.com/gethomepage/homepage) | My customized portal to my homelab & internet |
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/n8n.svg"> | [n8n](https://n8n.io/) | Secure, AI-native workflow automation |
| <img width="32" style="filter: invert(54%) sepia(94%) saturate(749%) hue-rotate(359deg) brightness(104%) contrast(101%);" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/wallabag.svg"> | [Wallabag](https://wallabag.org/) | Save articles & posts from the web for storage & reading later |
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/linkding.svg"> | [Linkding](https://github.com/sissbruecker/linkding) | Bookmark manager with tagging and search |


## Historical Roadmap (Not Active)

The following items were planning notes in this repository and are not current
commitments. See [nix-homelab](https://github.com/T-Py-T/nix-homelab) for the
active configuration and documentation.

### Version Upgrades

Using single node clusters to test version updates of each OS provider, K3s, Talos, CRC, etc.

### Enhanced Platform

Cert Manager + Cloudflare: Automated TLS certificate management
External DNS: Automatic DNS record management for services
CloudNativePG: PostgreSQL operator for database workloads

### Advanced Observability

Thanos: Long-term metrics storage and global query view
OpenTelemetry: Distributed tracing across all services

### Production Operations

Flagger: Automated canary deployments and progressive delivery
Velero: Comprehensive backup and disaster recovery
Renovate: Automated dependency updates with testing

## Current Project

For current code, documentation, and issue context, use
[T-Py-T/nix-homelab](https://github.com/T-Py-T/nix-homelab). This repository
remains available as a historical reference only.
