"""Repository policy checks mirrored from scripts/validate.sh for unit testing."""

from __future__ import annotations

import json
import re
from pathlib import Path

EXPECTED_DEVCONTAINER_IMAGE = (
    "mcr.microsoft.com/devcontainers/base:bookworm@"
    "sha256:3aacff4130e6cf04709f9cab1d7a6d3e1cc4bff6202bc61611831a18d3755673"
)
EXPECTED_KUBECTL_HELM_FEATURE = (
    "ghcr.io/devcontainers/features/kubectl-helm-minikube:1.3.1"
)
EXPECTED_FEATURE_OPTIONS = {
    "version": "1.37.0",
    "helm": "4.3.0",
    "minikube": "none",
}
EXPECTED_FEATURE_RESOLVED = (
    "ghcr.io/devcontainers/features/kubectl-helm-minikube@"
    "sha256:bbe8adf6b37fff8c67412ab0a4579f4c2f30bbaba1d9a5cebd9e38bade54025b"
)
EXPECTED_DEVCONTAINERS_CLI_VERSION = "0.89.0"
EXPECTED_DEVCONTAINERS_CLI_INTEGRITY = (
    "sha512-LzaoOGKQ/Zql6PsiZ4hVIYVZagzWkD65aG/1ou5/Kly5Y1PtjLg1yn7qu+"
    "LZCzVoAl6DZZ/pbz8qOO4RLNlqMg=="
)

# Mirrors the grep -E pattern in scripts/validate.sh (POSIX classes expressed in Python).
DEVCONTAINER_MUTABLE_PATTERN = re.compile(
    r"(^|[^A-Za-z0-9_])(latest|master)([^A-Za-z0-9_]|$)"
    r"|curl[^|]*\|\s*(ba)?sh"
    r"|postAttachCommand"
    r'|"privileged"\s*:\s*true'
)


def find_repo_root(start: Path | None = None) -> Path:
    """Return the repository root (parent of scripts/)."""
    if start is None:
        start = Path(__file__).resolve()
    current = start if start.is_dir() else start.parent
    while current != current.parent:
        if (current / "scripts" / "validate.sh").is_file():
            return current
        current = current.parent
    raise FileNotFoundError("could not locate repository root from {start}")


def check_devcontainer_manifest(repo_root: Path) -> None:
    config_path = repo_root / ".devcontainer" / "devcontainer.json"
    config = json.loads(config_path.read_text())

    if config["image"] != EXPECTED_DEVCONTAINER_IMAGE:
        raise AssertionError("devcontainer.json image pin does not match policy")

    features = config.get("features") or {}
    if set(features) != {EXPECTED_KUBECTL_HELM_FEATURE}:
        raise AssertionError("devcontainer.json features set does not match policy")

    if features[EXPECTED_KUBECTL_HELM_FEATURE] != EXPECTED_FEATURE_OPTIONS:
        raise AssertionError("devcontainer.json feature options do not match policy")

    if "postAttachCommand" in config:
        raise AssertionError("postAttachCommand is not allowed in devcontainer.json")

    if config.get("privileged") is True:
        raise AssertionError("privileged devcontainer is not allowed")


def check_devcontainer_lock(repo_root: Path) -> None:
    lock_path = repo_root / ".devcontainer" / "devcontainer-lock.json"
    lock = json.loads(lock_path.read_text())
    resolved = lock["features"][EXPECTED_KUBECTL_HELM_FEATURE]["resolved"]
    if resolved != EXPECTED_FEATURE_RESOLVED:
        raise AssertionError("devcontainer-lock.json resolved feature pin does not match policy")


def check_npm_pins(repo_root: Path) -> None:
    package = json.loads((repo_root / "package.json").read_text())
    dev_deps = package.get("devDependencies") or {}
    if dev_deps != {"@devcontainers/cli": EXPECTED_DEVCONTAINERS_CLI_VERSION}:
        raise AssertionError("package.json devDependencies do not match policy")

    package_lock = json.loads((repo_root / "package-lock.json").read_text())
    locked_cli = package_lock["packages"]["node_modules/@devcontainers/cli"]
    if locked_cli["version"] != EXPECTED_DEVCONTAINERS_CLI_VERSION:
        raise AssertionError("package-lock.json @devcontainers/cli version does not match policy")
    if locked_cli["integrity"] != EXPECTED_DEVCONTAINERS_CLI_INTEGRITY:
        raise AssertionError("package-lock.json @devcontainers/cli integrity does not match policy")


def check_devcontainer_directory(repo_root: Path) -> None:
    """Reject mutable tags, curl|bash installs, and privileged hooks under .devcontainer."""
    devcontainer_dir = repo_root / ".devcontainer"
    for path in sorted(devcontainer_dir.rglob("*")):
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text().splitlines(), start=1):
            if DEVCONTAINER_MUTABLE_PATTERN.search(line):
                raise AssertionError(
                    f"{path.relative_to(repo_root)}:{line_no}: "
                    "mutable, piped, or privileged dev-container configuration"
                )


def check_workflow_triggers(repo_root: Path) -> None:
    workflow_dir = repo_root / ".github" / "workflows"
    workflows = sorted((*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")))
    if not workflows:
        raise AssertionError("at least one workflow is required")

    for path in workflows:
        lines = path.read_text().splitlines()
        on_lines = [index for index, line in enumerate(lines) if line == "on:"]
        if len(on_lines) != 1:
            raise AssertionError(f"{path}: use one block-style on section")

        events: list[str] = []
        for line in lines[on_lines[0] + 1 :]:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if not line.startswith(" "):
                break
            if re.match(r"^  \S", line):
                if not re.match(r"^  [A-Za-z0-9_-]+:", line):
                    raise AssertionError(
                        f"{path}: workflow events must use canonical unquoted block keys"
                    )
            match = re.match(r"^  ([A-Za-z0-9_-]+):", line)
            if match:
                events.append(match.group(1))

        if events != ["pull_request"]:
            raise AssertionError(
                f"{path}: hosted workflows may trigger only on pull_request; got {events}"
            )


def parse_setup_script_versions(setup_sh: Path) -> tuple[str, str]:
    """Read expected kubectl and Helm versions from .devcontainer/setup.sh."""
    text = setup_sh.read_text()
    kubectl_match = re.search(r'expected_kubectl="([^"]+)"', text)
    helm_match = re.search(r'expected_helm="([^"]+)"', text)
    if not kubectl_match or not helm_match:
        raise ValueError(f"could not parse version pins from {setup_sh}")
    return kubectl_match.group(1), helm_match.group(1)


def devcontainer_tool_versions(repo_root: Path) -> tuple[str, str]:
    """Return (kubectl, helm) versions from devcontainer.json feature options."""
    config = json.loads((repo_root / ".devcontainer" / "devcontainer.json").read_text())
    opts = config["features"][EXPECTED_KUBECTL_HELM_FEATURE]
    kubectl = f"v{opts['version']}"
    helm = opts["helm"]
    return kubectl, helm


def helm_versions_equivalent(setup_helm: str, devcontainer_helm: str) -> bool:
    """Helm pins omit a leading v in devcontainer.json but setup.sh compares CLI output."""
    return setup_helm.removeprefix("v") == devcontainer_helm.removeprefix("v")
