"""Shell and pin contract tests for manifest-related scripts (not covered by PR #19)."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

from manifest_paths import (
    CI_INSTALL_TOOLS,
    REPO_ROOT,
    TRIVY_SCAN,
    VALIDATE_MANIFESTS,
    manifest_scripts_present,
)

pytestmark = pytest.mark.skipif(
    not manifest_scripts_present(),
    reason="manifest validation scripts are not present on this branch yet",
)


def _bash_syntax(path: Path) -> None:
    result = subprocess.run(
        ["bash", "-n", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_validate_manifests_passes_shellcheck_syntax() -> None:
    _bash_syntax(VALIDATE_MANIFESTS)


def test_ci_install_tools_passes_bash_syntax() -> None:
    assert CI_INSTALL_TOOLS.is_file(), "ci-install-kubernetes-tools.sh is missing"
    _bash_syntax(CI_INSTALL_TOOLS)


def test_trivy_scan_passes_bash_syntax_when_present() -> None:
    if not TRIVY_SCAN.is_file():
        pytest.skip("trivy-scan.sh is not on this branch yet")
    _bash_syntax(TRIVY_SCAN)


def test_ci_install_pins_match_devcontainer_feature_versions() -> None:
    text = CI_INSTALL_TOOLS.read_text()
    kubectl_match = re.search(r"readonly KUBECTL_VERSION='([^']+)'", text)
    helm_match = re.search(r"readonly HELM_VERSION='([^']+)'", text)
    assert kubectl_match and helm_match

    config = json.loads((REPO_ROOT / ".devcontainer" / "devcontainer.json").read_text())
    feature_key = "ghcr.io/devcontainers/features/kubectl-helm-minikube:1.3.1"
    opts = config["features"][feature_key]
    assert kubectl_match.group(1) == opts["version"]
    assert helm_match.group(1) == opts["helm"]


def test_validate_manifests_pins_kubeconform_version() -> None:
    text = VALIDATE_MANIFESTS.read_text()
    assert "readonly KUBECONFORM_VERSION='0.8.0'" in text
    assert "KUBECONFORM_LINUX_AMD64_SHA256" in text


def test_validate_manifests_only_scans_fixtures_tree() -> None:
    text = VALIDATE_MANIFESTS.read_text()
    assert "readonly FIXTURES_ROOT='fixtures'" in text
    assert 'git ls-files -z -- "${FIXTURES_ROOT}/**/kustomization.yaml"' in text
