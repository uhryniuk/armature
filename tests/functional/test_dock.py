"""Functional tests for the dock nested-subcommand example."""

import pytest

from armature import CLI
from examples.dock import Dock, Image, ListImages, Pull, Push, RemoveImage


@pytest.mark.functional
def test_dock_pull(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Dock).run(["pull", "ubuntu"])
    assert capsys.readouterr().out == "pulling 'ubuntu'\n"


@pytest.mark.functional
def test_dock_push_default_tag(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Dock).run(["push", "myapp"])
    assert capsys.readouterr().out == "pushing 'myapp':latest\n"


@pytest.mark.functional
def test_dock_push_custom_tag(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Dock).run(["push", "myapp", "--tag", "v2"])
    assert capsys.readouterr().out == "pushing 'myapp':v2\n"


@pytest.mark.functional
def test_dock_image_ls(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Dock).run(["image", "ls"])
    assert capsys.readouterr().out == "listing images\n"


@pytest.mark.functional
def test_dock_image_ls_filter(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Dock).run(["image", "ls", "--filter", "ubuntu"])
    assert capsys.readouterr().out == "listing images (filter: 'ubuntu')\n"


@pytest.mark.functional
def test_dock_image_rm(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Dock).run(["image", "rm", "ubuntu"])
    assert capsys.readouterr().out == "removing 'ubuntu'\n"


@pytest.mark.functional
def test_dock_image_rm_force(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Dock).run(["image", "rm", "ubuntu", "--force"])
    assert capsys.readouterr().out == "[force] removing 'ubuntu'\n"


@pytest.mark.functional
def test_dock_debug_flag(capsys: pytest.CaptureFixture[str]) -> None:
    CLI(Dock).run(["--debug", "pull", "ubuntu"])
    out = capsys.readouterr().out
    assert "[debug]" in out
    assert "pulling" in out


@pytest.mark.functional
def test_dock_parse_returns_full_tree() -> None:
    result = CLI(Dock).parse(["image", "rm", "ubuntu"])
    assert isinstance(result, Dock)
    assert isinstance(result.cmd, Image)
    assert isinstance(result.cmd.cmd, RemoveImage)
    assert result.cmd.cmd.name == "ubuntu"


@pytest.mark.functional
def test_dock_parse_pull_branch() -> None:
    result = CLI(Dock).parse(["pull", "nginx"])
    assert isinstance(result.cmd, Pull)
    assert result.cmd.name == "nginx"


@pytest.mark.functional
def test_dock_parse_push_branch() -> None:
    result = CLI(Dock).parse(["push", "myapp", "--tag", "rc1"])
    assert isinstance(result.cmd, Push)
    assert result.cmd.tag == "rc1"


@pytest.mark.functional
def test_dock_parse_ls_branch() -> None:
    result = CLI(Dock).parse(["image", "ls", "--filter", "alpine"])
    assert isinstance(result.cmd, Image)
    assert isinstance(result.cmd.cmd, ListImages)
    assert result.cmd.cmd.filter == "alpine"
