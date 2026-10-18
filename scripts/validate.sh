#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 - <<'PY'
import json
from pathlib import Path

config = json.loads(Path(".devcontainer/devcontainer.json").read_text())
expected_image = (
    "mcr.microsoft.com/devcontainers/base:bookworm@"
    "sha256:3aacff4130e6cf04709f9cab1d7a6d3e1cc4bff6202bc61611831a18d3755673"
)
expected_feature = (
    "ghcr.io/devcontainers/features/kubectl-helm-minikube:1.3.1"
)

assert config["image"] == expected_image
assert set(config["features"]) == {expected_feature}
assert config["features"][expected_feature] == {
    "version": "1.37.0",
    "helm": "4.3.0",
    "minikube": "none",
}
assert "postAttachCommand" not in config
assert config.get("privileged") is not True

lock = json.loads(Path(".devcontainer/devcontainer-lock.json").read_text())
assert lock["features"][expected_feature]["resolved"] == (
    "ghcr.io/devcontainers/features/kubectl-helm-minikube@"
    "sha256:bbe8adf6b37fff8c67412ab0a4579f4c2f30bbaba1d9a5cebd9e38bade54025b"
)

package = json.loads(Path("package.json").read_text())
assert package["devDependencies"] == {
    "@devcontainers/cli": "0.89.0",
    "markdownlint-cli2": "0.17.2",
}

package_lock = json.loads(Path("package-lock.json").read_text())
locked_cli = package_lock["packages"]["node_modules/@devcontainers/cli"]
assert locked_cli["version"] == "0.89.0"
assert locked_cli["integrity"] == (
    "sha512-LzaoOGKQ/Zql6PsiZ4hVIYVZagzWkD65aG/1ou5/Kly5Y1PtjLg1yn7qu+"
    "LZCzVoAl6DZZ/pbz8qOO4RLNlqMg=="
)

locked_markdownlint = package_lock["packages"]["node_modules/markdownlint-cli2"]
assert locked_markdownlint["version"] == "0.17.2"
assert locked_markdownlint["integrity"] == (
    "sha512-XH06ZOi8wCrtOSSj3p8y3yJzwgzYOSa7lglNyS3fP05JPRzRGyjauBb5UvlLUSCGysMmULS1moxdRHHudV+g/Q=="
)
PY

bash -n .devcontainer/setup.sh scripts/ci-local.sh scripts/validate.sh

if grep -EnR \
  '(^|[^[:alnum:]_])(latest|master)([^[:alnum:]_]|$)|curl[^|]*\|[[:space:]]*(ba)?sh|postAttachCommand|"privileged"[[:space:]]*:[[:space:]]*true' \
  .devcontainer; then
  echo "mutable, piped, or privileged dev-container configuration found" >&2
  exit 1
fi

python3 - <<'PY'
import re
from pathlib import Path

workflow_dir = Path(".github/workflows")
workflows = sorted((*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")))
assert workflows, "at least one workflow is required"

for path in workflows:
    lines = path.read_text().splitlines()
    on_lines = [index for index, line in enumerate(lines) if line == "on:"]
    assert len(on_lines) == 1, f"{path}: use one block-style on section"

    events = []
    for line in lines[on_lines[0] + 1 :]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            break
        if re.match(r"^  \S", line):
            assert re.match(r"^  [A-Za-z0-9_-]+:", line), (
                f"{path}: workflow events must use canonical unquoted block keys"
            )
        match = re.match(r"^  ([A-Za-z0-9_-]+):", line)
        if match:
            events.append(match.group(1))

    assert events == ["pull_request", "workflow_dispatch"], (
        f"{path}: hosted workflows may trigger only on pull_request and "
        f"workflow_dispatch; got {events}"
    )

    text = path.read_text()
    assert "push:" not in text.split("on:")[1].split("jobs:")[0], (
        f"{path}: hosted workflows must not trigger on push"
    )

    assert "concurrency:" in text
    assert "cancel-in-progress: true" in text
    assert "github.workflow" in text and "github.ref" in text

    pr_section = text.split("pull_request:", 1)[1].split("workflow_dispatch:", 1)[0]
    assert "branches: [main]" in pr_section or (
        "branches:" in pr_section and "main" in pr_section
    ), f"{path}: pull_request must target main"
    assert "paths-ignore:" in pr_section, f"{path}: pull_request needs paths-ignore"
    assert "**.md" in pr_section and "docs/**" in pr_section, (
        f"{path}: pull_request paths-ignore must skip markdown and docs"
    )

    jobs_section = text.split("jobs:", 1)[1]
    job_names = re.findall(r"^  ([a-zA-Z0-9_-]+):\n", jobs_section, re.MULTILINE)
    assert job_names, f"{path}: expected at least one job"
    for job in job_names:
        job_block = re.search(
            rf"^  {re.escape(job)}:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
            jobs_section,
            re.MULTILINE | re.DOTALL,
        )
        assert job_block, f"{path}: could not parse job {job}"
        assert "timeout-minutes:" in job_block.group(1), (
            f"{path}: job {job} must set timeout-minutes"
        )
PY

if [[ -n "${GITHUB_BASE_REF:-}" ]] &&
  git rev-parse --verify --quiet "origin/${GITHUB_BASE_REF}" >/dev/null; then
  git diff --check "origin/${GITHUB_BASE_REF}...HEAD"
else
  git diff --check
  git diff --cached --check
  git diff-tree --check --no-commit-id --root -r HEAD
fi
