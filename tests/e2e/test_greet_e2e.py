"""E2E subprocess tests for the greet example."""

import subprocess
from collections.abc import Callable

import pytest


@pytest.mark.e2e
def test_greet_basic(greet: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = greet("Alice")
    assert result.returncode == 0
    assert result.stdout == "Hello, Alice!\n"


@pytest.mark.e2e
def test_greet_loud_flag(greet: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = greet("Alice", "--loud")
    assert result.returncode == 0
    assert result.stdout == "HELLO, ALICE!\n"


@pytest.mark.e2e
def test_greet_loud_short_alias(greet: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = greet("Bob", "-l")
    assert result.returncode == 0
    assert result.stdout == "HELLO, BOB!\n"


@pytest.mark.e2e
def test_greet_help_exits_zero(greet: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = greet("--help")
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


@pytest.mark.e2e
def test_greet_missing_arg_nonzero(greet: Callable[..., subprocess.CompletedProcess[str]]) -> None:
    result = greet()
    assert result.returncode != 0
