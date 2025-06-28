# 🏠 Homelab - K3s GitOps Platform

## 📖 Overview

Complete GitOps platform on K3s - deploy production-ready infrastructure in minutes.

**Multi-Repository Pattern**: Separate repos for platform, monitoring, and applications - all orchestrated by ArgoCD projects using app-of-apps patterns for production infrastructure release cycles. This cluster helps with backup strategies, security, scalability and the ease of deployment and maintenance.

I use this these cluster for testing new services, and conainter hardening for DevSecOps, using platforms like:

- [Repo1](https://repo1.dso.mil/) for managed DoD approved charts and apps.
- [Ironbank](https://ironbank.dso.mil/) a public container registry of hardened images.

## 📊 Current State

### Implementation Status

| Category | Current | In Progress | Future |
|:---------|:--------|:------------|:-------|
| **Platform** | K3s + Cilium + ArgoCD + Istio + Vault + Keycloak + ELK + External Secrets + Kyverno | Extended cluster policies | Cert Manager + Cloudflare |
| **Monitoring** | Prometheus + Grafana | EFK Stack | Thanos + OpenTelemetry  |
| **Applications** | Commafeed + Homepage + Linkding + N8N + Wallabag | App Deployment Patterns | Progressive Delivery |

## 🏗️ Architecture Design

### Hardware Setup

- I use a combination of refurbished mini PCs:
- These  are great because they are small and cheap to buy when you get them refurbished from a reseller.
- They are about $100-150 USD each. The only problem is that the for larger workloads, the base RAM needs to be upgraded adding additional cost

#### Prod Cluster - PLANNED

- Control Plane - HP ELITEDESK 800 G5 MINI i5-6400T/16GB/240GB SSD - x3
- Worker Nodes - HP ELITEDESK 800 G2 MINI i5-6400T/16GB/240GB SSD - x6

#### Staging Cluster - Installed

- Control Plane - HP ELITEDESK 800 G5 MINI i5-6400T/16GB/240GB SSD - x2
- Worker Nodes - HP ELITEDESK 800 G2 MINI i3-6100T/8GB/240GB SSD - x4

#### Dev Cluster - Installed

- Control Plane - HP ELITEDESK 800 G5 MINI i5-6400T/16GB/240GB SSD - x1
- Worker Nodes - HP ELITEDESK 800 G2 MINI i3-6100T/8GB/240GB SSD - x2

## ⚙️ Deployment Strategy

### Repository Orchestration

Each repo managed as separate ArgoCD project with app-of-apps pattern for complete production infrastructure release cycle management.

#### Multi-Repository GitOps Pattern

Cluster lifecycle (GitOps Focused) - In order top to bottom
├── [homelab-gitops](https://github.com/T-Py-T/homelab-gitops)          # 🎯 ArgoCD bootstrap + cluster scripts
├── [homelab-platform](https://github.com/T-Py-T/homelab-platform)      # 🏗️ Core infrastructure (Istio, Vault, Keycloak)
├── [homelab-monitoring](https://github.com/T-Py-T/homelab-monitoring)  # 📊 Observability stack (Prometheus, Grafana, logging)
└── [homelab-apps](https://github.com/T-Py-T/homelab-applications)      # 🚀 End-user applications

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
| <img width="32" src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/istio.svg"> | [Istio](https://istio.io/) | Service mesh for security, observability, and traffic management |
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
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/wallabag.svg"> | [Wallabag](https://wallabag.org/) | Save articles & posts from the web for storage & reading later |
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/linkding.svg"> | [Linkding](https://github.com/sissbruecker/linkding) | Bookmark manager with tagging and search |

## 🎯 Future Roadmap

## 🌐 Infrastructure Details

### 🔄 Network Design
I use [Cilium](https://cilium.io/) as my CNI. I use LoadBalancer IPAM to assign IP addresses to my LoadBalancer services and use Cilium as an ingress controller. This way, I don't need to install and maintain a seperate ingress controller like Traefik, which I used in the past.

### 💾 Storage Configuration

I am looking at purchaing a Synology DS224+ as a NAS. Future plan is to use Synology CSI driver to provision Persistent Volumes from my clusters directly on the NAS. I plan to create an NFS share for data that needs to be shared between clusters.

### 🔐 Secret Management

[Vault](https://www.hashicorp.com/en/products/vault) - The overall goal of the system is to use hashicorp vault as the method of holding and pulling secrets.

### Enhanced Platform Features

- **Cert Manager + Cloudflare**: Automated TLS certificate management
- **Synology CSI**: Driver for persistent storage from an NFS
- **External DNS**: Automatic DNS record management
- **CloudNativePG**: PostgreSQL operator for database workloads
- **Thanos + OpenTelemetry**: Long-term metrics storage and distributed tracing

### Advanced Operations

- **Cluster API**: Declarative multi-cluster management
- **Flagger**: Canary deployments and progressive delivery
- **Velero**: Cluster state backups and disaster recovery
- **Renovate**: Automated dependency updates

## 🔧 Quick Start

### Prerequisites

- Ansible for cluster provisioning
- kubectl for cluster management
- Git for GitOps workflows

### Deploy Platform

```bash
# 1. Bootstrap ArgoCD
git clone homelab-gitops && cd homelab-gitops
./scripts/bootstrap-cluster.sh

# 2. Deploy platform services  
kubectl apply -f platform-project.yaml

# 3. Add monitoring
kubectl apply -f monitoring-project.yaml

# 4. Add applications
kubectl apply -f applications-project.yaml
```

## 🌟 Why This Approach?

**Multi-Repo Pattern**: Team isolation, independent releases, clear boundaries  
**Production Ready**: Security-first, disposable clusters, comprehensive automation
