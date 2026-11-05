#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

readonly KUBECTL_VERSION='1.37.0'
readonly HELM_VERSION='4.3.0'

install_dir="${repo_root}/.cache/ci-tools"
mkdir -p "$install_dir"

os="$(uname -s | tr '[:upper:]' '[:lower:]')"
arch="$(uname -m)"
case "$arch" in
  x86_64) arch='amd64' ;;
  aarch64 | arm64) arch='arm64' ;;
  *)
    echo "unsupported architecture: $arch" >&2
    exit 1
    ;;
esac

if [[ "$os" != 'linux' ]]; then
  echo "install kubectl ${KUBECTL_VERSION} and helm ${HELM_VERSION} locally" >&2
  exit 1
fi

if command -v kubectl >/dev/null 2>&1 &&
  command -v helm >/dev/null 2>&1 &&
  kubectl version --client --output=yaml | grep -q "v${KUBECTL_VERSION}" &&
  helm version --short | grep -q "v${HELM_VERSION}"; then
  exit 0
fi

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 1
  fi
}

require_command curl
require_command tar

kubectl_url="https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/${arch}/kubectl"
kubectl_path="${install_dir}/kubectl"

if [[ ! -x "$kubectl_path" ]]; then
  curl -fsSL "$kubectl_url" -o "$kubectl_path"
  chmod +x "$kubectl_path"
fi

helm_archive="helm-v${HELM_VERSION}-linux-${arch}.tar.gz"
helm_url="https://get.helm.sh/${helm_archive}"
helm_path="${install_dir}/linux-${arch}/helm"

if [[ ! -x "$helm_path" ]]; then
  curl -fsSL "$helm_url" -o "${install_dir}/${helm_archive}"
  tar -xzf "${install_dir}/${helm_archive}" -C "$install_dir"
fi

export PATH="${install_dir}/linux-${arch}:${install_dir}:${PATH}"

actual_kubectl="$(kubectl version --client --output=yaml | awk '/gitVersion:/ {print $2; exit}')"
actual_helm="$(helm version --short | cut -d+ -f1)"
test "$actual_kubectl" = "v${KUBECTL_VERSION}"
test "$actual_helm" = "v${HELM_VERSION}"
