from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.lib.policy import (
    check_devcontainer_directory,
    check_devcontainer_lock,
    check_devcontainer_manifest,
    check_npm_pins,
    check_workflow_triggers,
    devcontainer_tool_versions,
    helm_versions_equivalent,
    parse_setup_script_versions,
)


def test_devcontainer_manifest_matches_pins(repo_root: Path) -> None:
    check_devcontainer_manifest(repo_root)


def test_devcontainer_lock_matches_pins(repo_root: Path) -> None:
    check_devcontainer_lock(repo_root)


def test_npm_devcontainer_cli_is_pinned(repo_root: Path) -> None:
    check_npm_pins(repo_root)


def test_devcontainer_tree_has_no_mutable_or_privileged_patterns(repo_root: Path) -> None:
    check_devcontainer_directory(repo_root)


def test_all_workflows_trigger_only_on_pull_request(repo_root: Path) -> None:
    check_workflow_triggers(repo_root)


def test_setup_sh_versions_align_with_devcontainer(repo_root: Path) -> None:
    setup = repo_root / ".devcontainer" / "setup.sh"
    kubectl_setup, helm_setup = parse_setup_script_versions(setup)
    kubectl_dc, helm_dc = devcontainer_tool_versions(repo_root)
    assert kubectl_setup == kubectl_dc
    assert helm_versions_equivalent(helm_setup, helm_dc)


def test_setup_sh_passes_bash_syntax_check(repo_root: Path) -> None:
    setup = repo_root / ".devcontainer" / "setup.sh"
    result = subprocess.run(
        ["bash", "-n", str(setup)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_validate_sh_passes_bash_syntax_check(repo_root: Path) -> None:
    validate = repo_root / "scripts" / "validate.sh"
    result = subprocess.run(
        ["bash", "-n", str(validate)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_validate_sh_succeeds_in_clean_tree(run_validate) -> None:
    result = run_validate(env={"GITHUB_BASE_REF": ""})
    assert result.returncode == 0, (
        f"validate.sh failed (stdout={result.stdout!r}, stderr={result.stderr!r})"
    )
