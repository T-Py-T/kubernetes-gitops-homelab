#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

readonly KUBECONFORM_VERSION='0.8.0'
readonly KUBECONFORM_LINUX_AMD64_SHA256='9bc2bffbf71f261128533edaf912153948b7ff238f9a531ae6d34466ec287883'

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 1
  fi
}

require_command kubectl
require_command helm
require_command curl
require_command tar
require_command sha256sum

ensure_kubeconform() {
  if command -v kubeconform >/dev/null 2>&1; then
    return
  fi

  local os arch archive_name install_dir tarball_url
  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  arch="$(uname -m)"
  case "$arch" in
    x86_64) arch='amd64' ;;
    aarch64 | arm64) arch='arm64' ;;
    *)
      echo "unsupported architecture for kubeconform download: $arch" >&2
      exit 1
      ;;
  esac

  if [[ "$os" != 'linux' ]]; then
    echo "install kubeconform v${KUBECONFORM_VERSION} locally to validate manifests" >&2
    exit 1
  fi

  archive_name="kubeconform-linux-${arch}.tar.gz"
  install_dir="${repo_root}/.cache/kubeconform/${KUBECONFORM_VERSION}"
  tarball_url="https://github.com/yannh/kubeconform/releases/download/v${KUBECONFORM_VERSION}/${archive_name}"

  if [[ ! -x "${install_dir}/kubeconform" ]]; then
    mkdir -p "$install_dir"
    curl -fsSL "$tarball_url" -o "${install_dir}/${archive_name}"
    if [[ "$arch" == 'amd64' ]]; then
      echo "${KUBECONFORM_LINUX_AMD64_SHA256}  ${install_dir}/${archive_name}" |
        sha256sum -c -
    fi
    tar -xzf "${install_dir}/${archive_name}" -C "$install_dir" kubeconform
  fi

  export PATH="${install_dir}:${PATH}"
}

kubernetes_version() {
  kubectl version --client --output=yaml |
    awk -F'"' '/gitVersion:/ {print $2; exit}' |
    sed -E 's/^v//' |
    sed -E 's/\+.*$//'
}

kubeconform_validate() {
  local source_label="$1"
  local k8s_version="$2"
  if ! kubeconform -summary -kubernetes-version "$k8s_version" \
    -ignore-missing-schemas \
    -output text \
    -verbose -; then
    echo "kubeconform failed for ${source_label}" >&2
    exit 1
  fi
}

mapfile -t kustomizations < <(
  git ls-files -z -- '**/kustomization.yaml' '**/kustomization.yml' |
    tr '\0' '\n' | sed '/^$/d' | sort -u
)

mapfile -t charts < <(
  git ls-files -z -- '**/Chart.yaml' |
    tr '\0' '\n' | sed '/^$/d' | sort -u
)

if ((${#kustomizations[@]} == 0 && ${#charts[@]} == 0)); then
  printf 'No tracked Kustomize or Helm manifests to validate.\n'
  exit 0
fi

ensure_kubeconform
k8s_version="$(kubernetes_version)"

for kustomization in "${kustomizations[@]}"; do
  overlay_dir="$(dirname "$kustomization")"
  printf 'Validating Kustomize overlay %s\n' "$overlay_dir"
  kubectl kustomize "$overlay_dir" |
    kubeconform_validate "kustomize ${overlay_dir}" "$k8s_version"
done

for chart_file in "${charts[@]}"; do
  chart_dir="$(dirname "$chart_file")"
  printf 'Validating Helm chart %s\n' "$chart_dir"
  helm lint "$chart_dir"
  helm template manifest-validate "$chart_dir" |
    kubeconform_validate "helm ${chart_dir}" "$k8s_version"
done

printf 'Kustomize, Helm, and kubeconform checks passed.\n'
