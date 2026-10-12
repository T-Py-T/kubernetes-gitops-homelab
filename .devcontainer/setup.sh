#!/usr/bin/env bash
set -euo pipefail

ensure_python3() {
  if command -v python3 >/dev/null 2>&1 &&
    python3 -c "import yaml" >/dev/null 2>&1; then
    return
  fi
  sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-yaml
}

ensure_python3

expected_kubectl="v1.37.0"
expected_helm="v4.3.0"

actual_kubectl="$(kubectl version --client --output=yaml | awk '/gitVersion:/ {print $2; exit}')"
actual_helm="$(helm version --short | cut -d+ -f1)"

test "$actual_kubectl" = "$expected_kubectl"
test "$actual_helm" = "$expected_helm"
kubectl kustomize --help >/dev/null

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"${repo_root}/scripts/validate-manifests.sh"
python3 -m unittest discover -s "${repo_root}/scripts/tests" -p 'test_*.py'

printf 'kubectl %s, Helm %s, and kubectl kustomize are ready.\n' \
  "$actual_kubectl" "$actual_helm"
