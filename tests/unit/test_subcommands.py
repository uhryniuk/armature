"""Unit tests for flat and nested subcommand parsing."""

import dataclasses
from typing import Annotated

import pytest

from armature import CLI, Arg, SubCmd


# ---------------------------------------------------------------------------
# Flat subcommands  CLI([A, B])
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class Deploy:
    """Deploy a service."""

    env: str
    verbose: bool = False


@dataclasses.dataclass
class Rollback:
    """Rollback to a prior version."""

    version: str


@pytest.mark.unit
def test_flat_dispatch_first_command() -> None:
    result = CLI([Deploy, Rollback]).parse(["deploy", "prod"])
    assert isinstance(result, Deploy)
    assert result.env == "prod"


@pytest.mark.unit
def test_flat_dispatch_second_command() -> None:
    result = CLI([Deploy, Rollback]).parse(["rollback", "v1.2.3"])
    assert isinstance(result, Rollback)
    assert result.version == "v1.2.3"


@pytest.mark.unit
def test_flat_dispatch_with_flags() -> None:
    result = CLI([Deploy, Rollback]).parse(["deploy", "staging", "--verbose"])
    assert isinstance(result, Deploy)
    assert result.verbose is True


@pytest.mark.unit
def test_flat_unknown_subcommand_exits() -> None:
    with pytest.raises(SystemExit):
        CLI([Deploy, Rollback]).parse(["noop"])


@pytest.mark.unit
def test_flat_missing_subcommand_exits() -> None:
    with pytest.raises(SystemExit):
        CLI([Deploy, Rollback]).parse([])


@pytest.mark.unit
def test_flat_subcommand_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as exc:
        CLI([Deploy, Rollback]).parse(["deploy", "--help"])
    assert exc.value.code == 0


# ---------------------------------------------------------------------------
# Two-level nesting  Annotated[A | B, SubCmd]
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class ImageLs:
    """List images."""

    filter: str = ""


@dataclasses.dataclass
class ImageRm:
    """Remove an image."""

    image: str
    force: bool = False


@dataclasses.dataclass
class Image:
    """Manage images."""

    cmd: Annotated[ImageLs | ImageRm, SubCmd]


@dataclasses.dataclass
class Docker:
    """Docker-like root command."""

    cmd: Annotated[Deploy | Image, SubCmd]
    debug: bool = False


@pytest.mark.unit
def test_two_level_leaf_returned() -> None:
    result = CLI(Docker).parse(["image", "imagels"])
    assert isinstance(result, Docker)
    assert isinstance(result.cmd, Image)
    assert isinstance(result.cmd.cmd, ImageLs)


@pytest.mark.unit
def test_two_level_root_flag_preserved() -> None:
    result = CLI(Docker).parse(["--debug", "image", "imagels"])
    assert result.debug is True


@pytest.mark.unit
def test_two_level_leaf_args_preserved() -> None:
    result = CLI(Docker).parse(["image", "imagerm", "ubuntu"])
    assert isinstance(result.cmd.cmd, ImageRm)
    assert result.cmd.cmd.image == "ubuntu"


@pytest.mark.unit
def test_two_level_leaf_flag_preserved() -> None:
    result = CLI(Docker).parse(["image", "imagerm", "ubuntu", "--force"])
    assert result.cmd.cmd.force is True


@pytest.mark.unit
def test_two_level_deploy_branch() -> None:
    result = CLI(Docker).parse(["deploy", "prod"])
    assert isinstance(result.cmd, Deploy)
    assert result.cmd.env == "prod"


# ---------------------------------------------------------------------------
# Three-level nesting  foo bar baz
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class Baz:
    """Baz command."""

    value: str


@dataclasses.dataclass
class Bar:
    """Bar command."""

    cmd: Annotated[Baz, SubCmd]
    flag: bool = False


@dataclasses.dataclass
class Foo:
    """Foo root command."""

    cmd: Annotated[Bar, SubCmd]
    debug: bool = False


@pytest.mark.unit
def test_three_level_full_parse() -> None:
    result = CLI(Foo).parse(["--debug", "bar", "--flag", "baz", "hello"])
    assert isinstance(result, Foo)
    assert result.debug is True
    assert isinstance(result.cmd, Bar)
    assert result.cmd.flag is True
    assert isinstance(result.cmd.cmd, Baz)
    assert result.cmd.cmd.value == "hello"


@pytest.mark.unit
def test_three_level_defaults_respected() -> None:
    result = CLI(Foo).parse(["bar", "baz", "world"])
    assert result.debug is False
    assert result.cmd.flag is False
    assert result.cmd.cmd.value == "world"


@pytest.mark.unit
def test_three_level_missing_leaf_exits() -> None:
    with pytest.raises(SystemExit):
        CLI(Foo).parse(["bar"])
