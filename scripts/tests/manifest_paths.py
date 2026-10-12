"""Shared paths and helpers for manifest and script contract tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_ROOT = REPO_ROOT / "fixtures"
APPS_ROOT = FIXTURES_ROOT / "apps"
GREETING_BASE = APPS_ROOT / "greeting-kustomize" / "base"
GREETING_STAGING = APPS_ROOT / "greeting-kustomize" / "overlays" / "staging"
HELM_CHART = APPS_ROOT / "queue-worker-helm"
KYVERNO_POLICY = FIXTURES_ROOT / "policies" / "require-part-of-label.yaml"

VALIDATE_MANIFESTS = REPO_ROOT / "scripts" / "validate-manifests.sh"
RENDERED_POLICY = REPO_ROOT / "scripts" / "validate-rendered-policy.py"
CI_INSTALL_TOOLS = REPO_ROOT / "scripts" / "ci-install-kubernetes-tools.sh"
TRIVY_SCAN = REPO_ROOT / "scripts" / "trivy-scan.sh"


def fixtures_present() -> bool:
    return GREETING_STAGING.is_dir() and HELM_CHART.is_dir()


def manifest_scripts_present() -> bool:
    return VALIDATE_MANIFESTS.is_file() and RENDERED_POLICY.is_file()


def kubernetes_tools_available() -> bool:
    for tool in ("kubectl", "helm"):
        if subprocess.run(["which", tool], capture_output=True).returncode != 0:
            return False
    return True


def load_policy_module():
    """Import validate-rendered-policy.py as a module (filename is not import-safe)."""
    import importlib.util

    if not RENDERED_POLICY.is_file():
        raise FileNotFoundError(RENDERED_POLICY)
    spec = importlib.util.spec_from_file_location("validate_rendered_policy", RENDERED_POLICY)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load policy module from {RENDERED_POLICY}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_policy_check(manifest: str, source: str = "unit-test") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(RENDERED_POLICY), "--source", source],
        input=manifest,
        text=True,
        capture_output=True,
        check=False,
        cwd=REPO_ROOT,
    )
