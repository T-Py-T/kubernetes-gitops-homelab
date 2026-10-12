"""Regression tests for manifest render and policy scripts."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATE_MANIFESTS = REPO_ROOT / "scripts" / "validate-manifests.sh"
POLICY_SCRIPT = REPO_ROOT / "scripts" / "validate-rendered-policy.py"
HELM_CHART = REPO_ROOT / "fixtures" / "apps" / "queue-worker-helm"
KUSTOMIZE_OVERLAY = (
    REPO_ROOT / "fixtures" / "apps" / "greeting-kustomize" / "overlays" / "staging"
)


def run(
    *args: str,
    check: bool = True,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=check,
        input=input_text,
    )


def require_kubernetes_tools() -> None:
    for tool in ("kubectl", "helm"):
        if subprocess.run(["which", tool], capture_output=True).returncode != 0:
            raise unittest.SkipTest(f"{tool} is not installed")


class ValidateManifestsTest(unittest.TestCase):
    def test_kustomize_staging_overlay_renders_two_replicas(self) -> None:
        require_kubernetes_tools()
        result = run("kubectl", "kustomize", str(KUSTOMIZE_OVERLAY))
        self.assertIn("replicas: 2", result.stdout)

    def test_helm_service_target_port_matches_container(self) -> None:
        require_kubernetes_tools()
        rendered = run(
            "helm",
            "template",
            "manifest-validate",
            str(HELM_CHART),
        ).stdout
        self.assertIn("targetPort: 8080", rendered)
        self.assertIn("containerPort: 8080", rendered)

    def test_policy_script_rejects_floating_image_tags(self) -> None:
        bad_manifest = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo
  labels:
    app.kubernetes.io/name: demo
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: demo
  template:
    metadata:
      labels:
        app.kubernetes.io/name: demo
    spec:
      automountServiceAccountToken: false
      containers:
        - name: app
          image: nginx:latest
          resources:
            requests:
              cpu: 10m
              memory: 32Mi
            limits:
              cpu: 100m
              memory: 128Mi
"""
        result = run(
            "python3",
            str(POLICY_SCRIPT),
            "--source",
            "unit-test",
            input_text=bad_manifest,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("floating image tag", result.stderr)

    def test_validate_manifests_script_succeeds_on_fixtures(self) -> None:
        require_kubernetes_tools()
        if not VALIDATE_MANIFESTS.is_file():
            self.fail("validate-manifests.sh is missing")
        result = run(str(VALIDATE_MANIFESTS), check=False)
        if result.returncode != 0:
            self.fail(
                f"validate-manifests failed:\nstdout={result.stdout}\nstderr={result.stderr}"
            )


if __name__ == "__main__":
    unittest.main()
