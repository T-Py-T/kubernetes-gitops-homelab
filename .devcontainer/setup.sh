#!/usr/bin/env bash
set -euo pipefail

expected_kubectl="v1.37.0"
expected_helm="v4.3.0"

actual_kubectl="$(kubectl version --client --output=yaml | awk '/gitVersion:/ {print $2; exit}')"
actual_helm="$(helm version --short | cut -d+ -f1)"

test "$actual_kubectl" = "$expected_kubectl"
test "$actual_helm" = "$expected_helm"
kubectl kustomize --help >/dev/null

printf 'kubectl %s, Helm %s, and kubectl kustomize are ready.\n' \
  "$actual_kubectl" "$actual_helm"
