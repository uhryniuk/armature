"""Unit tests for single-command CLI.parse()."""

import dataclasses
from typing import Annotated

import pytest

from armature import CLI, Arg


@pytest.mark.unit
def test_positional_str() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str

    assert CLI(Cmd).parse(["Alice"]).name == "Alice"


@pytest.mark.unit
def test_positional_int() -> None:
    @dataclasses.dataclass
    class Cmd:
        count: int

    result = CLI(Cmd).parse(["5"])
    assert result.count == 5
    assert isinstance(result.count, int)


@pytest.mark.unit
def test_positional_float() -> None:
    @dataclasses.dataclass
    class Cmd:
        value: float

    assert CLI(Cmd).parse(["3.14"]).value == pytest.approx(3.14)


@pytest.mark.unit
def test_flag_default_false() -> None:
    @dataclasses.dataclass
    class Cmd:
        verbose: bool = False

    assert CLI(Cmd).parse([]).verbose is False


@pytest.mark.unit
def test_flag_set() -> None:
    @dataclasses.dataclass
    class Cmd:
        verbose: bool = False

    assert CLI(Cmd).parse(["--verbose"]).verbose is True


@pytest.mark.unit
def test_short_alias() -> None:
    @dataclasses.dataclass
    class Cmd:
        verbose: Annotated[bool, Arg(short="-v")] = False

    assert CLI(Cmd).parse(["-v"]).verbose is True


@pytest.mark.unit
def test_option_default() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str = "default"

    assert CLI(Cmd).parse([]).name == "default"


@pytest.mark.unit
def test_option_override() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str = "default"

    assert CLI(Cmd).parse(["--name", "Alice"]).name == "Alice"


@pytest.mark.unit
def test_option_int() -> None:
    @dataclasses.dataclass
    class Cmd:
        count: int = 1

    assert CLI(Cmd).parse(["--count", "7"]).count == 7


@pytest.mark.unit
def test_choices_valid() -> None:
    @dataclasses.dataclass
    class Cmd:
        env: Annotated[str, Arg(choices=["prod", "staging"])]

    assert CLI(Cmd).parse(["prod"]).env == "prod"


@pytest.mark.unit
def test_choices_invalid() -> None:
    @dataclasses.dataclass
    class Cmd:
        env: Annotated[str, Arg(choices=["prod", "staging"])]

    with pytest.raises(SystemExit):
        CLI(Cmd).parse(["dev"])


@pytest.mark.unit
def test_help_exits_zero() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: Annotated[str, Arg(help="Your name")]

    with pytest.raises(SystemExit) as exc:
        CLI(Cmd).parse(["--help"])
    assert exc.value.code == 0


@pytest.mark.unit
def test_optional_type_default_none() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str | None = None

    assert CLI(Cmd).parse([]).name is None


@pytest.mark.unit
def test_optional_type_provided() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str | None = None

    assert CLI(Cmd).parse(["--name", "Alice"]).name == "Alice"


@pytest.mark.unit
def test_list_positional() -> None:
    @dataclasses.dataclass
    class Cmd:
        items: list[str]

    assert CLI(Cmd).parse(["a", "b", "c"]).items == ["a", "b", "c"]


@pytest.mark.unit
def test_list_option() -> None:
    @dataclasses.dataclass
    class Cmd:
        items: list[str] = dataclasses.field(default_factory=list)

    assert CLI(Cmd).parse(["--items", "x", "y"]).items == ["x", "y"]


@pytest.mark.unit
def test_list_option_default_empty() -> None:
    @dataclasses.dataclass
    class Cmd:
        items: list[str] = dataclasses.field(default_factory=list)

    assert CLI(Cmd).parse([]).items == []


@pytest.mark.unit
def test_underscore_to_hyphen() -> None:
    @dataclasses.dataclass
    class Cmd:
        dry_run: bool = False

    assert CLI(Cmd).parse(["--dry-run"]).dry_run is True


@pytest.mark.unit
def test_multiple_fields() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str
        count: int = 1
        verbose: bool = False

    result = CLI(Cmd).parse(["Alice", "--count", "3", "--verbose"])
    assert result.name == "Alice"
    assert result.count == 3
    assert result.verbose is True


@pytest.mark.unit
def test_not_dataclass_raises() -> None:
    class Plain:
        pass

    with pytest.raises(TypeError, match="must be decorated with @dataclass"):
        CLI(Plain).parse([])


@pytest.mark.unit
def test_empty_commands_list_raises() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        CLI([])


@pytest.mark.unit
def test_description_from_docstring() -> None:
    @dataclasses.dataclass
    class Deploy:
        """Deploy a service to an environment."""

        env: str

    # Just confirm it parses without error; description is in --help output
    assert CLI(Deploy).parse(["prod"]).env == "prod"


@pytest.mark.unit
def test_returns_typed_instance() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str

    result = CLI(Cmd).parse(["Alice"])
    assert isinstance(result, Cmd)
