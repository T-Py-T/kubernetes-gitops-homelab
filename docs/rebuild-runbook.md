# Generic cluster rebuild runbook

This runbook describes the order and evidence expected from a disposable
homelab rebuild. Replace every placeholder with commands from the private
environment repository; do not copy hostnames, tokens, kubeconfigs, or secret
values into this public project.

## 1. Record the change boundary

- Capture the current cluster and node-image versions.
- Record the Git revisions for cluster configuration and applications.
- Export only the backups required by the recovery plan.
- Confirm how to return traffic to the previous cluster.

## 2. Create an isolated cluster

Provision new nodes or virtual machines from the selected machine definition.
Keep the existing environment running until the replacement has passed its
checks.

Verify the basic control plane:

```bash
kubectl get nodes -o wide
kubectl get pods --all-namespaces
```

All nodes should be ready before GitOps bootstrap begins.

## 3. Check the platform foundation

Validate networking, DNS, ingress, and storage in that order. Use small
synthetic workloads rather than an application with important data.

Evidence should include:

- pod-to-pod and pod-to-service connectivity;
- internal and external DNS resolution;
- ingress routing and certificate issuance;
- creation, attachment, and deletion of a temporary persistent volume; and
- the expected network-policy behavior.

## 4. Bootstrap Argo CD

Install Argo CD from the pinned version used by the environment repository,
then register only the repositories required for this cluster. Bootstrap the
root application or application set and observe reconciliation:

```bash
argocd app list
argocd app get <root-application>
```

Do not continue while platform applications are out of sync or degraded.

## 5. Reconcile by layer

Apply layers in dependency order:

1. ingress, identity, secret delivery, and policy controllers;
2. metrics, logs, dashboards, and alert routing;
3. stateless applications;
4. stateful services and restored data.

For each layer, record the Git revision, Argo CD health, workload readiness,
and one user-visible or protocol-level check.

## 6. Exercise recovery

Restore one bounded synthetic dataset or disposable application. Confirm that
the service can read it after a pod restart and, when applicable, after a node
restart. Keep the test separate from irreplaceable home data.

## 7. Promote or roll back

Move traffic only after health, route, observability, and restore checks pass.
If a check fails, return to the previous cluster or Git revision and retain the
failure log for the next rehearsal.

## Rebuild record

Keep a dated record in the private environment repository containing:

- cluster and node versions;
- configuration revisions;
- start and finish time;
- check results and logs;
- backup and restore scope;
- deviations from this runbook; and
- the final promote or rollback decision.
