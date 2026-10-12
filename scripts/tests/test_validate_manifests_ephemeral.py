"""Integration test for validate-manifests.sh using a temporary tracked fixtures tree."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from manifest_paths import REPO_ROOT, VALIDATE_MANIFESTS, kubernetes_tools_available

pytestmark = pytest.mark.skipif(
    not VALIDATE_MANIFESTS.is_file(),
    reason="validate-manifests.sh is not present on this branch yet",
)


MINIMAL_KUSTOMIZATION = """apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
labels:
  - pairs:
      app.kubernetes.io/part-of: ephemeral-fixture
    includeSelectors: false
"""

MINIMAL_DEPLOYMENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo
  labels:
    app.kubernetes.io/name: echo
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: echo
  template:
    metadata:
      labels:
        app.kubernetes.io/name: echo
    spec:
      automountServiceAccountToken: false
      containers:
        - name: app
          image: registry.k8s.io/e2e-test-images/echoserver:2.5
          resources:
            requests:
              cpu: 10m
              memory: 32Mi
            limits:
              cpu: 100m
              memory: 128Mi
"""


@pytest.fixture()
def ephemeral_fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "mini-repo"
    shutil.copytree(REPO_ROOT / "scripts", repo / "scripts")
    if (REPO_ROOT / "scripts" / "validate-rendered-policy.py").is_file():
        pass  # already copied with scripts/
    fixture_dir = repo / "fixtures" / "apps" / "echo-kustomize" / "base"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "kustomization.yaml").write_text(MINIMAL_KUSTOMIZATION)
    (fixture_dir / "deployment.yaml").write_text(MINIMAL_DEPLOYMENT)

    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "-m", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return repo


def test_validate_manifests_succeeds_on_ephemeral_kustomize(ephemeral_fixture_repo: Path) -> None:
    if not kubernetes_tools_available():
        pytest.skip("kubectl and helm are required")
    script = ephemeral_fixture_repo / "scripts" / "validate-manifests.sh"
    result = subprocess.run(
        [str(script)],
        cwd=ephemeral_fixture_repo,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"validate-manifests failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "echo-kustomize" in result.stdout
