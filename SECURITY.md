# Security policy

> Tip-cite bank: base main `fe90e148` (Ship 263) + this PR pending Steward resolve;
> provenance only; never `READY`, scores, bake-off results, or operational
> authorization.

## Repository scope

This policy applies to the public
[**kubernetes-gitops-homelab**](https://github.com/T-Py-T/kubernetes-gitops-homelab)
repository only. It does not cover private downstream homelab deployment
repositories, live cluster endpoints, or separate private trees such as
**homelab-gitops**.

The default branch is a documentation-only architecture case study. Current
cluster configuration, hostnames, secrets, Argo CD applications, Helm values, and
live deployment manifests are maintained outside this repository.

## What to report

Report privately if you find material that could grant unauthorized access,
including in current content or Git history:

- credentials, API keys, or passwords;
- private keys or certificates that authenticate to a live system;
- access tokens or session material; and
- current sensitive endpoints (for example, administrative URLs tied to an
  active home network).

## What is not in scope

The following are not treated as security incidents for this repository:

- architecture descriptions and diagrams that do not expose secrets;
- archival or example configuration that does not grant access to a running
  environment; and
- requests for operational support, incident response, or certification of
  production readiness.

## Reporting path

Do not open a public issue for sensitive findings.

Use [GitHub private vulnerability reporting](https://github.com/T-Py-T/kubernetes-gitops-homelab/security/advisories/new)
(**Report a vulnerability** on the repository **Security** tab). Include enough
detail to reproduce the finding (path, commit or tag, and redacted context).

Response is best-effort for this public case study; there is no guaranteed SLA.

## Related documentation

| Document | Role |
| --- | --- |
| [README.md](README.md) | Architecture overview and local validation |
| [docs/HIREABILITY.md](docs/HIREABILITY.md) | Discoverability and reviewer orientation |
| [docs/rebuild-runbook.md](docs/rebuild-runbook.md) | Generic rebuild sequence (non-secret) |
| [LICENSE](LICENSE) | License for current documentation |
| [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) | Historical and third-party material |
