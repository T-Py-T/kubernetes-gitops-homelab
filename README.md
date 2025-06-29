# Homelab - K3s GitOps Platform

 **Complete GitOps platform on K3s** - Deploy production-ready infrastructure in minutes with enterprise-grade security, monitoring, and automation.

---

## Overview

This homelab implements a **multi-repository GitOps pattern** with separate repos for platform, monitoring, and applications - all orchestrated by ArgoCD using app-of-apps patterns. Perfect for testing new services, container hardening, and DevSecOps practices.

### Military-Grade Security

I use these cluster for testing new services, and conainter hardening for DevSecOps, using platforms like:

- [**Repo1**](https://repo1.dso.mil/) - DoD approved charts and applications
- [**Ironbank**](https://ironbank.dso.mil/) - Hardened container registry

---

## Architecture Overview

### Cluster Strategy: "No In-Place Upgrades"

Instead of one monolithic cluster, I run **multiple single-purpose clusters** for better isolation, security, and maintainability. Current approach is HA(High Availability, Fault tolerant) clusters.

For the Dev and Staging cluster I am looking at SinglNode Clusters to allow me to quickly brink up and test a new version cluster OS (Like Talos or K3D). I can test a newer cluster OS and validate before migrating. and have my fallback previous cluster. 

| Cluster | Purpose | Status | Nodes |
|:--------|:--------|:-------|:------|
| **Prod** | End-user applications (stateless) | 🔄 Planned (OpenShift) | 3 control + 6 workers |
| **Staging** | Application testing & validation | ✅ Running (Talos/Omni) | 2 control + 4 workers |
| **Data** | Databases & persistent storage | 🔄 Planned (K3s) | 2 control + 2 workers |
| **Dev** | Development & container testing | ✅ Running (K3s) | 1 control + 2 workers |

### Why This Design?

- **Blast radius containment** - Issues don't affect other environments
- **Independent scaling** - Right-size each cluster for its workload
- **Easy disaster recovery** - Rebuild clusters from code, restore data from backups
- **Technology diversity** - Test different platforms (OpenShift, Talos, K3s)

---

## Hardware Setup

**Philosophy**: Cheap, small, upgradeable refurbished business PCs

### Base Hardware Stack

- **HP EliteDesk 800 G5 Mini** (Control Planes): i5-6400T, 16GB RAM, 240GB SSD
- **HP EliteDesk 800 G2 Mini** (Workers): i3-6100T, 8-16GB RAM, 240GB SSD
- **Cost**: ~$100-150 per node (refurbished)
- **Upgrade path**: RAM easily expandable for larger workloads

### Cluster Specifications

<details>
<summary><strong> Production Cluster (Planned - OpenShift)</strong></summary>

**Purpose**: Mission-critical applications with enterprise support

- **Control Plane**: 3x HP EliteDesk 800 G5 Mini (i5-6400T/16GB/240GB)
- **Workers**: 6x HP EliteDesk 800 G2 Mini (i5-6400T/16GB/240GB)
- **Features**: HA, automated failover, enterprise monitoring

</details>

<details>
<summary><strong> Staging Cluster (Running - Talos/Omni)</strong></summary>

**Purpose**: Pre-production testing and validation

- **Control Plane**: 2x HP EliteDesk 800 G5 Mini (i5-6400T/16GB/240GB)
- **Workers**: 4x HP EliteDesk 800 G2 Mini (i3-6100T/8GB/240GB)
- **Features**: Immutable OS, declarative configuration

</details>

<details>
<summary><strong> Data Cluster (Planned - K3s)</strong></summary>

**Purpose**: Centralized databases and shared storage

- **Control Plane**: 2x HP EliteDesk 800 G5 Mini (i5-6400T/16GB/240GB)
- **Workers**: 2x HP EliteDesk 800 G2 Mini (i3-6100T/8GB/240GB)
- **Storage**: Synology DS224+ NAS with CSI integration

</details>

<details>
<summary><strong> Dev Cluster (Running - K3s)</strong></summary>

**Purpose**: Development, testing, and experimentation

- **Control Plane**: 1x HP EliteDesk 800 G5 Mini (i5-6400T/16GB/240GB)
- **Workers**: 2x HP EliteDesk 800 G2 Mini (i3-6100T/8GB/240GB)
- **Features**: Lightweight, fast iteration, disposable workloads

</details>

---

## Deployment Strategy

## GitOps Workflow

### Multi-Repository Pattern

``` sh
Deployment Order (Top → Bottom)
├──  homelab-gitops     ← ArgoCD bootstrap + cluster scripts
├── homelab-platform   ← Core infrastructure (Istio, Vault, Keycloak)  
├──  homelab-monitoring ← Observability (Prometheus, Grafana, ELK)
└──  homelab-apps      ← End-user applications
```

Benefits of This Approach

- Dependency Control: Platform services deploy before apps that need them
- Team Separation: Different teams can own different repositories
- Independent Releases: Update monitoring without touching applications
- Security Boundaries: Separate access controls per repository type
- Scalability: Add new app repos without touching core infrastructure

## Why This Approach?

**Multi-Repo Pattern**: Team isolation, independent releases, clear boundaries  
**Production Ready**: Security-first, disposable clusters, comprehensive automation

### Repository Orchestration

Each repo managed as separate ArgoCD project with app-of-apps pattern for complete production infrastructure release cycle management.

#### Multi-Repository GitOps Pattern

Cluster lifecycle (GitOps Focused) - In order top to bottom

``` sh
├── [homelab-gitops](https://github.com/T-Py-T/homelab-gitops)          #  ArgoCD bootstrap + cluster scripts
├── [homelab-platform](https://github.com/T-Py-T/homelab-platform)      #  Core infrastructure (Istio, Vault, Keycloak)
├── [homelab-monitoring](https://github.com/T-Py-T/homelab-monitoring)  #  Observability stack (Prometheus, Grafana, logging)
└── [homelab-apps](https://github.com/T-Py-T/homelab-applications)      #  End-user applications
```

**Benefits:** Dependency control, team separation, independent release cycles

## 🔧 Technology Stack

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


🌟 Future Roadmap

⚙️ Version upgrades
Using single node clusters to test version updates of each OS provider, K3s, Talos, CRC, etc.

🔄 Enhanced Platform
Cert Manager + Cloudflare: Automated TLS certificate management
External DNS: Automatic DNS record management for services
CloudNativePG: PostgreSQL operator for database workloads

📊 Advanced Observability
Thanos: Long-term metrics storage and global query view
OpenTelemetry: Distributed tracing across all services

🚀 Production Operations
Flagger: Automated canary deployments and progressive delivery
Velero: Comprehensive backup and disaster recovery
Renovate: Automated dependency updates with testing

🤝 **Contributing**
**Found this helpful? Here's how you can contribute:**

⭐ Star the repositories if this helped your learning
🐛 Report issues or suggest improvements
📖 Share your experience - write about your own homelab journey
🔀 Fork and adapt for your own needs


💬 Questions? Open an issue or start a discussion in any of the repository links above!