#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! command -v trivy >/dev/null 2>&1; then
  echo "trivy: not installed; skipping container and config vulnerability scan" >&2
  exit 0
fi

severity=(--severity HIGH,CRITICAL)
scan_flags=(--scanners vuln --ignore-unfixed)

collect_images() {
  python3 - <<'PY'
import json
import re
from pathlib import Path

images: list[str] = []

devcontainer = Path(".devcontainer/devcontainer.json")
if devcontainer.is_file():
    config = json.loads(devcontainer.read_text())
    image = config.get("image")
    if isinstance(image, str) and image.strip():
        images.append(image.strip())
fixture_root = Path("fixtures")
if fixture_root.is_dir():
    image_field = re.compile(r"^\s*image:\s*['\"]?([^'\"#\s]+)")
    repo_field = re.compile(r"^\s*repository:\s*['\"]?([^'\"#\s]+)")
    tag_field = re.compile(r"^\s*tag:\s*['\"]?([^'\"#\s]+)")
    for path in sorted(fixture_root.rglob("*.y*ml")):
        repository = None
        tag = None
        for line in path.read_text().splitlines():
            match = image_field.match(line)
            if match:
                images.append(match.group(1))
                repository = None
                tag = None
                continue
            match = repo_field.match(line)
            if match:
                repository = match.group(1)
                continue
            match = tag_field.match(line)
            if match:
                tag = match.group(1).strip("'\"")
        if repository and tag:
            images.append(f"{repository}:{tag}")

for image in dict.fromkeys(images):
    print(image)
PY
}

mapfile -t images < <(collect_images)

if ((${#images[@]} > 0)); then
  for image in "${images[@]}"; do
    echo "trivy image scan: ${image}"
    if ! trivy image "${scan_flags[@]}" "${severity[@]}" --exit-code 1 "${image}"; then
      echo "trivy image scan failed for ${image}" >&2
      exit 1
    fi
  done
else
  echo "trivy image scan: no container images discovered"
fi

config_targets=(.devcontainer .github)
if [[ -d fixtures ]]; then
  config_targets+=(fixtures)
fi

for target in "${config_targets[@]}"; do
  echo "trivy config scan: ${target}"
  trivy config "${severity[@]}" --exit-code 1 "${target}"
done
