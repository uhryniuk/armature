"""E2E subprocess tests for the task example."""

import subprocess
from collections.abc import Callable

import pytest


@pytest.mark.e2e
def test_task_add(task: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = task("add", "Buy milk")
    assert result.returncode == 0
    assert "Added: Buy milk" in result.stdout


@pytest.mark.e2e
def test_task_show(task: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = task("show")
    assert result.returncode == 0
    assert "No tasks" in result.stdout


@pytest.mark.e2e
def test_task_done(task: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = task("done", "5")
    assert result.returncode == 0
    assert "task 5" in result.stdout


@pytest.mark.e2e
def test_task_help_exits_zero(task: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = task("--help")
    assert result.returncode == 0


@pytest.mark.e2e
def test_task_subcommand_help(task: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = task("add", "--help")
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


@pytest.mark.e2e
def test_task_unknown_subcommand_nonzero(task: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = task("delete", "1")
    assert result.returncode != 0


@pytest.mark.e2e
def test_task_add_missing_text_nonzero(task: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = task("add")
    assert result.returncode != 0
