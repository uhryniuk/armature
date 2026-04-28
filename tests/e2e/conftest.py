"""Shared fixtures for e2e subprocess tests."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent


def _make_runner(module: str) -> Callable[..., subprocess.CompletedProcess[str]]:
    def run(*args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{REPO_ROOT}:{existing}" if existing else str(REPO_ROOT)
        return subprocess.run(
            [sys.executable, "-m", module, *args],
            check=False, capture_output=True,
            text=True,
            env=env,
            cwd=str(REPO_ROOT),
        )

    return run


@pytest.fixture(scope="session")
def greet() -> Callable[..., subprocess.CompletedProcess[str]]:
    """Run the greet example with given argv."""
    return _make_runner("examples.greet")


@pytest.fixture(scope="session")
def task() -> Callable[..., subprocess.CompletedProcess[str]]:
    """Run the task example with given argv."""
    return _make_runner("examples.task")


@pytest.fixture(scope="session")
def dock() -> Callable[..., subprocess.CompletedProcess[str]]:
    """Run the dock example with given argv."""
    return _make_runner("examples.dock")
