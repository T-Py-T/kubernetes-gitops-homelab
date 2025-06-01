# 🏠 Homelab

## 📖 Overview

This repo contains all of the configuration and documentation of my homelab.

The purpose of my homelab is the place where I can try out and learn new things. On the other hand, by self-hosting some applications, it makes me feel responsible for the entire process of deploying and maintaining an application from A to Z. It forces me to think about backup strategies, security, scalability and the ease of deployment and maintenance.

## 📊 Current State

### Implementation Status

| Category | Current | In Progress | Future |
|:---------|:--------|:------------|:-------|
| Cluster Management | Talos, Omni | - | Cluster API, Federation |
| Networking | Cilium, Cloudflare | Istio | OpenTelemetry |
| Observability | Prometheus, Grafana | ELK Stack | Thanos |
| Security | External Secrets | Kyverno, Vault | - |
| Storage | CloudNativePG, Synology CSI | OpenEBS | - |
| GitOps | FluxCD, GitHub Actions | - | Flagger |

### Active Projects

1. **Service Mesh Implementation**
   - Istio deployment for multi-cluster communication
   - Service discovery and load balancing
   - Traffic management with intelligent routing
   - Zero-trust security with mTLS
   - Integration with existing monitoring stack

2. **Enhanced Security Stack**
   - Kyverno for policy enforcement:
     - Pod Security Standards enforcement
     - Resource quotas and limits
     - Image registry restrictions
   - Vault for secrets:
     - PKI infrastructure
     - Dynamic database credentials
     - Integration with External Secrets

3. **Advanced Observability**
   - ELK Stack implementation:
     - Centralized logging architecture
     - Log retention and lifecycle policies
     - Kibana dashboards for key metrics
   - Enhanced Prometheus/Grafana:
     - Custom ServiceMonitors
     - Recording rules for common queries
     - AlertManager integration

### Future Roadmap

1. **Multi-cluster Management**
   - Tools: Cluster API, Crossplane
   - Benefits:
     - Infrastructure as Code for cluster lifecycle
     - Consistent cluster provisioning
     - Multi-cloud capability
   - Implementation Plan:
     - Start with development cluster
     - Create reusable cluster templates
     - Implement GitOps workflow

2. **Advanced Observability**
   - Tools: OpenTelemetry, Thanos, Jaeger
   - Benefits:
     - Distributed tracing
     - Long-term metrics storage
     - Cross-cluster monitoring
   - Implementation Plan:
     - Deploy Thanos for metrics retention
     - Add OpenTelemetry collectors
     - Implement trace sampling

3. **Progressive Delivery**
   - Tools: Flagger, Argo Rollouts
   - Benefits:
     - Automated canary releases
     - Traffic shifting
     - Metric-based promotion
   - Implementation Plan:
     - Begin with non-critical service
     - Define success metrics
     - Automate rollback procedures

4. **Backup & Disaster Recovery**
   - Tools: Velero, Restic
   - Benefits:
     - Cluster state backups
     - PV/PVC backup
     - Cross-cluster recovery
   - Implementation Plan:
     - Regular backup schedule
     - Backup validation process
     - DR testing procedures

## 🏗️ Architecture

### Cluster Design

I use [Talos Linux](https://www.talos.dev/). Talos is lightweight and minimal, and provides production grade security by default. After running plain Talos for a while, I switched to using [Sidero Omni](https://www.siderolabs.com/platform/saas-for-kubernetes/) to manage my Talos clusters. Omni allows me to freely add nodes and destroy them, scaling my clusters as desired.

I am currently testing out a new architecture of single-node clusters where the workloads are scheduled on the control plane. A wise man taught me the phrase "no in-place upgrades", and I desire to move in that direction. Instead of one big cluster, I'm now running several. Omni makes this extremely easy.

| Number | Name | Description |
|:------:|:-----|:-----------:|
| 1 | Prod | Contains all end-user applications. Stateless, fully provisioned from code. Can be torn down and spun up within minutes on different hardware. |
| 2 | Dev | Contains all end-user applications. Stateless, fully provisioned from code. Can be torn down and spun up within minutes on different hardware. |
| 3 | Data | Contains all my databases & state. Multi-node. Can be fully restored from Blob storage. |

### Hardware Setup

I use a combination of HP ELITEDESK mini pc's, old laptops and sometimes a few virtual machines. The mini PC's are great because they are small and cheap to buy when you get them refurbished from a reseller.

**Prod Cluster**
- Control Plane
    - HP ELITEDESK 800 G5 MINI i5-6400T/16GB/240GB SSD
    - HP ELITEDESK 800 G5 MINI i5-6400T/16GB/240GB SSD
- Worker Nodes
    - HP ELITEDESK 800 G2 MINI i5-6400T/16GB/240GB SSD
    - HP ELITEDESK 800 G2 MINI i5-6400T/16GB/240GB SSD
    - HP ELITEDESK 800 G2 MINI i5-6400T/16GB/240GB SSD

**Dev Cluster**
- Control Plane
    - HP ELITEDESK 800 G5 MINI i5-6400T/16GB/240GB SSD
- Worker Nodes
    - HP ELITEDESK 800 G2 MINI i3-6100T/8GB/240GB SSD
    - HP ELITEDESK 800 G2 MINI i3-6100T/8GB/240GB SSD
    - HP ELITEDESK 800 G2 MINI i3-6100T/8GB/240GB SSD

## 🔧 Technology Stack

### Core Infrastructure

Everything needed to run my cluster & deploy my applications

| Logo | Name | Description |
|:----:|:-----|:-----------|
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/svg/cert-manager.svg"> | [Cert Manager](https://cert-manager.io/) | X.509 certificate management for Kubernetes |
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/cilium.svg"> | [Cilium](https://cilium.io/) | My CNI of choice, used on all clusters. eBPF-based Networking, Observability, Security |
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/cloudflare-zero-trust.png"> | [Cloudflare Zero Trust](https://developers.cloudflare.com/cloudflare-one/) | Used for private tunnels to expose public services (without requiring a public IP) |
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/postgresql.svg"> | [CloudNativePG](https://cloudnative-pg.io/) | Database operator for running PostgreSQL clusters |
| <img width="32" src="https://www.svgrepo.com/download/530451/dns.svg"> | [External DNS](https://github.com/kubernetes-sigs/external-dns) | Synchronizes exposed Kubernetes Services and Ingresses with DNS providers |
| <img width="32" src="https://www.svgrepo.com/download/477066/lock.svg"> | [External Secrets Operator](https://external-secrets.io/latest/) | Used to sync my secrets from Azure Key Vaults to my cluster |
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/flux-cd.svg"> | [Flux CD](https://fluxcd.io/) | My GitOps solution of choice. Better than Argo |
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/svg/grafana.svg"> | [Grafana](https://grafana.com/) | The open observability platform |
| <img width="32" src="https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/svg/prometheus.svg"> | [Prometheus](https://prometheus.io/) | An open-source monitoring system with a dimensional data model, flexible query language, efficient time series database and modern alerting approach |
| <img width="32" src="https://www.svgrepo.com/download/374041/renovate.svg"> | [Renovate](https://github.com/renovatebot/renovate) | Automated dependency updates |
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/synology.svg"> | [Synology CSI Driver](https://github.com/SynologyOpenSource/synology-csi) | Used to provision Persistent Volumes directly on my Synology |

### User Applications

End User Applications

| Logo | Name | Description |
|:----:|:-----|:-----------|
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/commafeed.svg"> | [Commafeed](https://www.commafeed.com/#/welcome) | Bloat free RSS feed reader |
| <img width="32" src="https://www.svgrepo.com/download/499807/home-page.svg"> | [Homepage](https://github.com/gethomepage/homepage) | My customized portal to my homelab & internet |
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/n8n.svg"> | [n8n](https://n8n.io/) | Secure, AI-native workflow automation |
| <img width="32" src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/wallabag-light.svg"> | [Wallabag](https://wallabag.org/) | Save articles & posts from the web for storage & reading later |

## ⚙️ Detailed Implementation

### Production Features
Detailed breakdown of production-ready features:

#### Cluster Management
- **Sidero Omni** for cluster lifecycle
- Multi-cluster architecture with separation of concerns
- **Talos Linux** for secure, minimal OS

#### Network & Security
- **Cilium** as CNI with:
  - LoadBalancer IPAM
  - Native ingress controller
  - Network policies
- **Cloudflare Zero Trust** for secure access

#### GitOps & CI/CD
- **Flux CD** for GitOps deployments
- **GitHub Actions** for CI/CD pipelines
- **Renovate** for dependency updates

#### Storage & Databases
- **CloudNativePG** for PostgreSQL operations
- **Synology CSI Driver** for persistent storage
- NFS shares for cross-cluster data

### Deployment Plans

#### Ready to Deploy
Technologies understood and planned for immediate implementation:

- **Service Mesh & Traffic Management**
  - [ ] Istio implementation plan:
    - Service mesh architecture
    - Traffic management
    - Security policies
    - Observability integration

- **Observability Stack**
  - [ ] Prometheus & Grafana deployment:
    - Metric collection
    - Custom dashboards
    - AlertManager configuration
  - [ ] ELK Stack setup:
    - Centralized logging
    - Log retention policies
    - Search and analytics

- **Security & Compliance**
  - [ ] Kyverno policies:
    - Pod security standards
    - Resource quotas
    - Image policy
  - [ ] Trivy scanning:
    - Image vulnerability scanning
    - Infrastructure scanning
    - CI/CD integration
  - [ ] HashiCorp Vault:
    - Secrets management
    - Dynamic credentials
    - PKI management

- **Storage Solutions**
  - [ ] OpenEBS:
    - Local PV provisioner
    - Volume replication
    - Backup integration

#### Future Exploration
Technologies identified for future learning and implementation:

1. **Multi-cluster Management**
   - Cluster API for declarative management
   - Federation for workload distribution
   - Benefits: Standardized cluster provisioning, easier scaling
   - Approach: Start with test cluster, document patterns

2. **Advanced Observability**
   - OpenTelemetry for tracing
   - Thanos for long-term metrics
   - Benefits: Better troubleshooting, historical analysis
   - Approach: Begin with single service tracing

3. **Progressive Delivery**
   - Flagger for canary deployments
   - Benefits: Safer deployments, automated rollbacks
   - Approach: Start with non-critical service

4. **Backup & Disaster Recovery**
   - Tools: Velero, Restic
   - Benefits:
     - Cluster state backups
     - PV/PVC backup
     - Cross-cluster recovery
   - Implementation Plan:
     - Regular backup schedule
     - Backup validation process
     - DR testing procedures

## 🌐 Infrastructure Details

### 🔄 Network Design
I use [Cilium](https://cilium.io/) as my CNI. I use LoadBalancer IPAM to assign IP addresses to my LoadBalancer services and use Cilium as an ingress controller. This way, I don't need to install and maintain a seperate ingress controller like Traefik, which I used in the past.

### 💾 Storage Configuration
I use a Synology DS224+ as a NAS. I use the Synology CSI driver to provision Persistent Volumes from my clusters directly on the NAS. I also have an NFS share for data that needs to be shared between clusters.

### 🔐 Secret Management

Azure Key Vaults are used to store my secrets. I sync them to my cluster using the External Secrets Operator.

## 🚧 In Progress (Updates)

## Secret-Management

[Vault](https://www.hashicorp.com/en/products/vault)
The overall goal of the system is to use hashicorp vault as the method of holding and pulling secrets.