"""Functional tests for the task example CLI."""

import pytest

from armature import CLI
from examples.task import Add, Done, Show


@pytest.mark.functional
def test_task_add(capsys: pytest.CaptureFixture[str]) -> None:
    CLI([Add, Show, Done]).run(["add", "Buy milk"])
    assert capsys.readouterr().out == "Added: Buy milk\n"


@pytest.mark.functional
def test_task_show(capsys: pytest.CaptureFixture[str]) -> None:
    CLI([Add, Show, Done]).run(["show"])
    assert capsys.readouterr().out == "No tasks yet.\n"


@pytest.mark.functional
def test_task_done(capsys: pytest.CaptureFixture[str]) -> None:
    CLI([Add, Show, Done]).run(["done", "3"])
    assert capsys.readouterr().out == "Marked task 3 as done.\n"


@pytest.mark.functional
def test_task_add_returns_add_instance() -> None:
    result = CLI([Add, Show, Done]).parse(["add", "Buy milk"])
    assert isinstance(result, Add)
    assert result.text == "Buy milk"


@pytest.mark.functional
def test_task_done_returns_done_instance() -> None:
    result = CLI([Add, Show, Done]).parse(["done", "7"])
    assert isinstance(result, Done)
    assert result.id == 7
