from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.lib.policy import find_repo_root


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return find_repo_root()


@pytest.fixture(scope="session")
def validate_script(repo_root: Path) -> Path:
    path = repo_root / "scripts" / "validate.sh"
    assert path.is_file()
    return path


@pytest.fixture()
def run_validate(repo_root: Path, validate_script: Path):
    def _run(*, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        import os

        merged = os.environ.copy()
        if env:
            merged.update(env)
        return subprocess.run(
            [str(validate_script)],
            cwd=repo_root,
            env=merged,
            capture_output=True,
            text=True,
            check=False,
        )

    return _run
