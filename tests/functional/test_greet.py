"""Functional tests for the greet example CLI."""

import pytest

from armature import CLI
from examples.greet import Greet


@pytest.mark.functional
def test_greet_basic(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Greet).run(["Alice"])
    assert capsys.readouterr().out == "Hello, Alice!\n"


@pytest.mark.functional
def test_greet_loud(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Greet).run(["Alice", "--loud"])
    assert capsys.readouterr().out == "HELLO, ALICE!\n"


@pytest.mark.functional
def test_greet_loud_short_alias(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Greet).run(["Bob", "-l"])
    assert capsys.readouterr().out == "HELLO, BOB!\n"


@pytest.mark.functional
def test_greet_parse_returns_typed_instance() -> None:
    result = CLI(Greet).parse(["Alice"])
    assert isinstance(result, Greet)
    assert result.name == "Alice"
    assert result.loud is False
