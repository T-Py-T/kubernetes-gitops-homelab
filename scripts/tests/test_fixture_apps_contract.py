"""Contract tests for tracked fixture apps not covered by PR #19 policy tests."""

from __future__ import annotations

import subprocess

import pytest
import yaml

from manifest_paths import (
    FIXTURES_ROOT,
    GREETING_BASE,
    GREETING_STAGING,
    HELM_CHART,
    KYVERNO_POLICY,
    REPO_ROOT,
    fixtures_present,
    kubernetes_tools_available,
    load_policy_module,
    run_policy_check,
)

pytestmark = pytest.mark.skipif(
    not fixtures_present(),
    reason="fixture apps are not present on this branch yet",
)


def _kustomize(path) -> str:
    if not kubernetes_tools_available():
        pytest.skip("kubectl and helm are required")
    result = subprocess.run(
        ["kubectl", "kustomize", str(path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_greeting_base_injects_part_of_label() -> None:
    rendered = _kustomize(GREETING_BASE)
    assert "app.kubernetes.io/part-of: validation-fixtures" in rendered


def test_greeting_staging_overlay_sets_two_replicas() -> None:
    rendered = _kustomize(GREETING_STAGING)
    assert "replicas: 2" in rendered


def test_greeting_rendered_manifests_pass_policy_script() -> None:
    if not (REPO_ROOT / "scripts" / "validate-rendered-policy.py").is_file():
        pytest.skip("validate-rendered-policy.py is not present")
    for overlay in (GREETING_BASE, GREETING_STAGING):
        rendered = _kustomize(overlay)
        result = run_policy_check(rendered, source=f"kustomize {overlay.relative_to(REPO_ROOT)}")
        assert result.returncode == 0, result.stderr


def test_greeting_service_uses_named_target_port() -> None:
    service_path = GREETING_BASE / "service.yaml"
    service = yaml.safe_load(service_path.read_text())
    port = service["spec"]["ports"][0]
    assert port["targetPort"] == "http"
    assert port["name"] == "http"


def test_helm_chart_values_pin_image_tag() -> None:
    values = yaml.safe_load((HELM_CHART / "values.yaml").read_text())
    tag = values["image"]["tag"]
    assert tag not in ("latest", "master")
    assert values["service"]["targetPort"] == 8080


def test_helm_template_passes_policy_script() -> None:
    if not kubernetes_tools_available():
        pytest.skip("kubectl and helm are required")
    if not (REPO_ROOT / "scripts" / "validate-rendered-policy.py").is_file():
        pytest.skip("validate-rendered-policy.py is not present")
    rendered = subprocess.run(
        ["helm", "template", "manifest-validate", str(HELM_CHART)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    result = run_policy_check(rendered, source="helm queue-worker-helm")
    assert result.returncode == 0, result.stderr


def test_kyverno_policy_enforces_part_of_on_workloads() -> None:
    policy = yaml.safe_load(KYVERNO_POLICY.read_text())
    rule = policy["spec"]["rules"][0]
    kinds = rule["match"]["any"][0]["resources"]["kinds"]
    assert "Deployment" in kinds
    assert "Service" in kinds
    pattern = rule["validate"]["pattern"]["metadata"]["labels"]
    assert "app.kubernetes.io/part-of" in pattern


def test_tracked_fixture_inventory_lists_both_apps() -> None:
    tracked = subprocess.run(
        ["git", "ls-files", str(FIXTURES_ROOT)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    tracked_text = "\n".join(tracked)
    assert "fixtures/apps/greeting-kustomize/" in tracked_text
    assert "fixtures/apps/queue-worker-helm/" in tracked_text
    assert "fixtures/policies/require-part-of-label.yaml" in tracked_text


def test_all_fixture_kustomization_overlays_are_discovered() -> None:
    """validate-manifests.sh validates every tracked kustomization.yaml under fixtures/."""
    listed = subprocess.run(
        [
            "git",
            "ls-files",
            "--",
            "fixtures/**/kustomization.yaml",
            "fixtures/**/kustomization.yml",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip().splitlines()
    listed = [line for line in listed if line]
    assert "fixtures/apps/greeting-kustomize/base/kustomization.yaml" in listed
    assert "fixtures/apps/greeting-kustomize/overlays/staging/kustomization.yaml" in listed
    assert len(listed) >= 2


def test_policy_module_loads_from_repo_script() -> None:
    if not (REPO_ROOT / "scripts" / "validate-rendered-policy.py").is_file():
        pytest.skip("validate-rendered-policy.py is not present")
    module = load_policy_module()
    assert module.REQUIRED_LABEL == "app.kubernetes.io/name"
