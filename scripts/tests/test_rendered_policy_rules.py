"""Unit tests for scripts/validate-rendered-policy.py beyond PR #17's single negative case."""

from __future__ import annotations

import pytest

from manifest_paths import RENDERED_POLICY, load_policy_module, run_policy_check

pytestmark = pytest.mark.skipif(
    not RENDERED_POLICY.is_file(),
    reason="validate-rendered-policy.py is not present on this branch yet",
)

GOOD_DEPLOYMENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo
  labels:
    app.kubernetes.io/name: demo
    app.kubernetes.io/part-of: fixtures
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
          image: registry.k8s.io/e2e-test-images/echoserver:2.5
          resources:
            requests:
              cpu: 10m
              memory: 32Mi
            limits:
              cpu: 100m
              memory: 128Mi
"""


def test_accepts_well_formed_deployment() -> None:
    result = run_policy_check(GOOD_DEPLOYMENT)
    assert result.returncode == 0, result.stderr


def test_rejects_missing_part_of_label() -> None:
    policy = load_policy_module()
    document = policy.load_documents(GOOD_DEPLOYMENT)[0]
    document["metadata"]["labels"].pop("app.kubernetes.io/part-of")
    errors = policy.check_document(document, "unit-test")
    assert any("app.kubernetes.io/part-of" in message for message in errors)


def test_rejects_missing_name_label() -> None:
    bad = GOOD_DEPLOYMENT.replace("app.kubernetes.io/name: demo\n", "", 1)
    result = run_policy_check(bad)
    assert result.returncode != 0
    assert "app.kubernetes.io/name" in result.stderr


def test_rejects_floating_latest_image_tag() -> None:
    bad = GOOD_DEPLOYMENT.replace("echoserver:2.5", "nginx:latest")
    result = run_policy_check(bad)
    assert result.returncode != 0
    assert "floating image tag" in result.stderr


def test_rejects_missing_resource_limits() -> None:
    bad = GOOD_DEPLOYMENT.replace("            limits:\n              cpu: 100m\n              memory: 128Mi\n", "")
    result = run_policy_check(bad)
    assert result.returncode != 0
    assert "resources.limits" in result.stderr


def test_rejects_automount_service_account_token() -> None:
    bad = GOOD_DEPLOYMENT.replace("automountServiceAccountToken: false", "automountServiceAccountToken: true")
    result = run_policy_check(bad)
    assert result.returncode != 0
    assert "automountServiceAccountToken" in result.stderr


def test_rejects_service_without_explicit_target_port() -> None:
    manifest = """apiVersion: v1
kind: Service
metadata:
  name: demo
  labels:
    app.kubernetes.io/name: demo
    app.kubernetes.io/part-of: fixtures
spec:
  selector:
    app.kubernetes.io/name: demo
  ports:
    - name: http
      port: 80
"""
    result = run_policy_check(manifest)
    assert result.returncode != 0
    assert "targetPort" in result.stderr


def test_check_document_api_matches_cli() -> None:
    policy = load_policy_module()
    errors = policy.check_document(
        policy.load_documents(GOOD_DEPLOYMENT)[0],
        "api",
    )
    assert errors == []
