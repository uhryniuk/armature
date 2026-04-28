"""E2E subprocess tests for the dock nested-subcommand example."""

import subprocess
from collections.abc import Callable

import pytest


@pytest.mark.e2e
def test_dock_pull(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("pull", "ubuntu")
    assert result.returncode == 0
    assert "pulling" in result.stdout
    assert "ubuntu" in result.stdout


@pytest.mark.e2e
def test_dock_push_default_tag(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("push", "myapp")
    assert result.returncode == 0
    assert "myapp" in result.stdout
    assert "latest" in result.stdout


@pytest.mark.e2e
def test_dock_push_custom_tag(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("push", "myapp", "--tag", "v2")
    assert result.returncode == 0
    assert "v2" in result.stdout


@pytest.mark.e2e
def test_dock_image_ls(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("image", "ls")
    assert result.returncode == 0
    assert "listing" in result.stdout


@pytest.mark.e2e
def test_dock_image_ls_filter(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("image", "ls", "--filter", "ubuntu")
    assert result.returncode == 0
    assert "ubuntu" in result.stdout


@pytest.mark.e2e
def test_dock_image_rm(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("image", "rm", "nginx")
    assert result.returncode == 0
    assert "nginx" in result.stdout


@pytest.mark.e2e
def test_dock_image_rm_force(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("image", "rm", "nginx", "--force")
    assert result.returncode == 0
    assert "force" in result.stdout.lower()


@pytest.mark.e2e
def test_dock_debug_flag(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("--debug", "pull", "ubuntu")
    assert result.returncode == 0
    assert "[debug]" in result.stdout


@pytest.mark.e2e
def test_dock_help_exits_zero(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("--help")
    assert result.returncode == 0


@pytest.mark.e2e
def test_dock_image_help(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("image", "--help")
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


@pytest.mark.e2e
def test_dock_unknown_subcommand_nonzero(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("exec", "ubuntu")
    assert result.returncode != 0


@pytest.mark.e2e
def test_dock_image_rm_missing_name_nonzero(dock: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = dock("image", "rm")
    assert result.returncode != 0
