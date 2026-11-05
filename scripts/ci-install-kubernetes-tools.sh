#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

readonly KUBECTL_VERSION='1.37.0'
readonly HELM_VERSION='4.3.0'
# https://dl.k8s.io/release/v1.37.0/bin/linux/<arch>/kubectl.sha256
readonly KUBECTL_LINUX_AMD64_SHA256='6129359f4e1f3848a5572ccb0b26cf28b8ca08cef38c95a765b2f64a2c961a2f'
readonly KUBECTL_LINUX_ARM64_SHA256='922df28df248cc00a9e025f947704f1d1482de64ece54cfe57e61f19eaf1eef3'
# https://get.helm.sh/helm-v4.3.0-linux-<arch>.tar.gz.sha256
readonly HELM_LINUX_AMD64_SHA256='86584a54def73570558f66f5111cc53dfed56689637ae32c1201205d494f54fb'
readonly HELM_LINUX_ARM64_SHA256='31c5794dd55c66a51e6b7d2e2ac7a114ae8b1de41ff1d9ba51748ac973b06a08'

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
require_command sha256sum

kubectl_expected_sha256() {
  case "$arch" in
    amd64) printf '%s' "$KUBECTL_LINUX_AMD64_SHA256" ;;
    arm64) printf '%s' "$KUBECTL_LINUX_ARM64_SHA256" ;;
    *)
      echo "unsupported architecture for kubectl checksum: $arch" >&2
      exit 1
      ;;
  esac
}

helm_expected_sha256() {
  case "$arch" in
    amd64) printf '%s' "$HELM_LINUX_AMD64_SHA256" ;;
    arm64) printf '%s' "$HELM_LINUX_ARM64_SHA256" ;;
    *)
      echo "unsupported architecture for helm checksum: $arch" >&2
      exit 1
      ;;
  esac
}

verify_file_sha256() {
  local file_path="$1"
  local expected="$2"
  local label="$3"
  if [[ -z "$expected" ]]; then
    echo "missing SHA-256 for ${label} on linux/${arch}" >&2
    exit 1
  fi
  if ! echo "${expected}  ${file_path}" | sha256sum -c -; then
    echo "SHA-256 mismatch for ${label}; remove ${file_path} and retry" >&2
    exit 1
  fi
}

kubectl_url="https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/${arch}/kubectl"
kubectl_path="${install_dir}/kubectl"
kubectl_sha256="$(kubectl_expected_sha256)"

if [[ ! -x "$kubectl_path" ]]; then
  curl -fsSL "$kubectl_url" -o "$kubectl_path"
  verify_file_sha256 "$kubectl_path" "$kubectl_sha256" "kubectl"
  chmod +x "$kubectl_path"
else
  verify_file_sha256 "$kubectl_path" "$kubectl_sha256" "cached kubectl"
fi

helm_archive="helm-v${HELM_VERSION}-linux-${arch}.tar.gz"
helm_url="https://get.helm.sh/${helm_archive}"
helm_path="${install_dir}/linux-${arch}/helm"
helm_tarball_path="${install_dir}/${helm_archive}"
helm_sha256="$(helm_expected_sha256)"

if [[ ! -x "$helm_path" ]]; then
  curl -fsSL "$helm_url" -o "$helm_tarball_path"
  verify_file_sha256 "$helm_tarball_path" "$helm_sha256" "helm archive"
  tar -xzf "$helm_tarball_path" -C "$install_dir"
else
  if [[ ! -f "$helm_tarball_path" ]]; then
    echo "missing cached ${helm_tarball_path}; remove ${install_dir}/linux-${arch} and retry" >&2
    exit 1
  fi
  verify_file_sha256 "$helm_tarball_path" "$helm_sha256" "cached helm archive"
fi

export PATH="${install_dir}/linux-${arch}:${install_dir}:${PATH}"

actual_kubectl="$(kubectl version --client --output=yaml | awk '/gitVersion:/ {print $2; exit}')"
actual_helm="$(helm version --short | cut -d+ -f1)"
test "$actual_kubectl" = "v${KUBECTL_VERSION}"
test "$actual_helm" = "v${HELM_VERSION}"
