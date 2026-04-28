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


# ---------------------------------------------------------------------------
# T27 — required named options + custom converter
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_required_named_becomes_flag() -> None:
    @dataclasses.dataclass
    class Cmd:
        namespace: Annotated[str, Arg(required=True)]
        resource: str

    result = CLI(Cmd).parse(["--namespace", "default", "pods"])
    assert result.namespace == "default"
    assert result.resource == "pods"


@pytest.mark.unit
def test_required_named_missing_exits() -> None:
    @dataclasses.dataclass
    class Cmd:
        namespace: Annotated[str, Arg(required=True)]

    with pytest.raises(SystemExit):
        CLI(Cmd).parse([])


@pytest.mark.unit
def test_required_named_short_alias() -> None:
    @dataclasses.dataclass
    class Cmd:
        namespace: Annotated[str, Arg(required=True, short="-n")]

    assert CLI(Cmd).parse(["-n", "kube-system"]).namespace == "kube-system"
    assert CLI(Cmd).parse(["--namespace", "default"]).namespace == "default"


@pytest.mark.unit
def test_converter_positional() -> None:
    @dataclasses.dataclass
    class Cmd:
        count: Annotated[str, Arg(converter=int)]

    result = CLI(Cmd).parse(["42"])
    assert result.count == 42
    assert isinstance(result.count, int)


@pytest.mark.unit
def test_converter_json_loads() -> None:
    import json

    @dataclasses.dataclass
    class Cmd:
        data: Annotated[str, Arg(converter=json.loads)]

    result = CLI(Cmd).parse(['{"key": "value"}'])
    assert result.data == {"key": "value"}


# ---------------------------------------------------------------------------
# T29 — environment variable fallbacks
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_env_var_sets_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_NS", "staging")

    @dataclasses.dataclass
    class Cmd:
        namespace: Annotated[str, Arg(env="MY_NS")] = "default"

    assert CLI(Cmd).parse([]).namespace == "staging"


@pytest.mark.unit
def test_env_var_cli_flag_takes_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_NS", "staging")

    @dataclasses.dataclass
    class Cmd:
        namespace: Annotated[str, Arg(env="MY_NS")] = "default"

    assert CLI(Cmd).parse(["--namespace", "prod"]).namespace == "prod"


@pytest.mark.unit
def test_env_var_type_conversion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_PORT", "8080")

    @dataclasses.dataclass
    class Cmd:
        port: Annotated[int, Arg(env="MY_PORT")] = 3000

    result = CLI(Cmd).parse([])
    assert result.port == 8080
    assert isinstance(result.port, int)


@pytest.mark.unit
def test_env_var_unset_falls_back_to_field_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MY_NS", raising=False)

    @dataclasses.dataclass
    class Cmd:
        namespace: Annotated[str, Arg(env="MY_NS")] = "default"

    assert CLI(Cmd).parse([]).namespace == "default"


@pytest.mark.unit
def test_env_var_help_text_annotation() -> None:
    @dataclasses.dataclass
    class Cmd:
        namespace: Annotated[str, Arg(help="target namespace", env="KUBECTL_NS")] = "default"

    import contextlib
    import io

    buf = io.StringIO()
    with pytest.raises(SystemExit):
        with contextlib.redirect_stdout(buf):
            CLI(Cmd).parse(["--help"])
    assert "KUBECTL_NS" in buf.getvalue()


# ---------------------------------------------------------------------------
# Hidden flags
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_hidden_flag_absent_from_help() -> None:
    import contextlib
    import io

    @dataclasses.dataclass
    class Cmd:
        secret: Annotated[str, Arg(hidden=True)] = "default"

    buf = io.StringIO()
    with pytest.raises(SystemExit):
        with contextlib.redirect_stdout(buf):
            CLI(Cmd).parse(["--help"])
    assert "--secret" not in buf.getvalue()


@pytest.mark.unit
def test_hidden_flag_still_accepted() -> None:
    @dataclasses.dataclass
    class Cmd:
        secret: Annotated[str, Arg(hidden=True)] = "default"

    assert CLI(Cmd).parse(["--secret", "shhh"]).secret == "shhh"


# ---------------------------------------------------------------------------
# Remainder / pass-through args
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_remainder_captures_passthrough() -> None:
    @dataclasses.dataclass
    class Cmd:
        extra: Annotated[list[str], Arg(remainder=True)]

    result = CLI(Cmd).parse(["--", "python", "-m", "pytest", "-x"])
    assert result.extra == ["--", "python", "-m", "pytest", "-x"]


@pytest.mark.unit
def test_remainder_empty_when_nothing_follows() -> None:
    @dataclasses.dataclass
    class Cmd:
        extra: Annotated[list[str], Arg(remainder=True)]

    assert CLI(Cmd).parse([]).extra == []


# ---------------------------------------------------------------------------
# Count action
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_count_single() -> None:
    @dataclasses.dataclass
    class Cmd:
        verbose: Annotated[int, Arg(short="-v", action="count")] = 0

    assert CLI(Cmd).parse(["-v"]).verbose == 1


@pytest.mark.unit
def test_count_stacked() -> None:
    @dataclasses.dataclass
    class Cmd:
        verbose: Annotated[int, Arg(short="-v", action="count")] = 0

    assert CLI(Cmd).parse(["-v", "-v", "-v"]).verbose == 3


@pytest.mark.unit
def test_count_default_zero() -> None:
    @dataclasses.dataclass
    class Cmd:
        verbose: Annotated[int, Arg(short="-v", action="count")] = 0

    assert CLI(Cmd).parse([]).verbose == 0


@pytest.mark.unit
def test_count_long_flag() -> None:
    @dataclasses.dataclass
    class Cmd:
        verbose: Annotated[int, Arg(action="count")] = 0

    assert CLI(Cmd).parse(["--verbose", "--verbose"]).verbose == 2


# ---------------------------------------------------------------------------
# Append action
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_append_multiple_flags() -> None:
    @dataclasses.dataclass
    class Cmd:
        tag: Annotated[list[str], Arg(action="append")]

    result = CLI(Cmd).parse(["--tag", "a", "--tag", "b", "--tag", "c"])
    assert result.tag == ["a", "b", "c"]


@pytest.mark.unit
def test_append_short_alias() -> None:
    @dataclasses.dataclass
    class Cmd:
        tag: Annotated[list[str], Arg(short="-t", action="append")]

    result = CLI(Cmd).parse(["-t", "x", "-t", "y"])
    assert result.tag == ["x", "y"]


@pytest.mark.unit
def test_append_default_empty() -> None:
    @dataclasses.dataclass
    class Cmd:
        tag: Annotated[list[str], Arg(action="append")]

    assert CLI(Cmd).parse([]).tag == []


# ---------------------------------------------------------------------------
# Version flag
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_version_flag_exits_zero() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str

    with pytest.raises(SystemExit) as exc:
        CLI(Cmd, version="1.2.3").parse(["--version"])
    assert exc.value.code == 0


@pytest.mark.unit
def test_version_short_flag() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str

    with pytest.raises(SystemExit) as exc:
        CLI(Cmd, version="0.9.0").parse(["-V"])
    assert exc.value.code == 0


@pytest.mark.unit
def test_version_in_output(capsys: pytest.CaptureFixture[str]) -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str

    with pytest.raises(SystemExit):
        CLI(Cmd, version="3.1.4").parse(["--version"])
    assert "3.1.4" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Epilog
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_epilog_in_help_output() -> None:
    import contextlib
    import io

    @dataclasses.dataclass
    class Cmd:
        name: str

    buf = io.StringIO()
    with pytest.raises(SystemExit):
        with contextlib.redirect_stdout(buf):
            CLI(Cmd, epilog="See also: https://example.com").parse(["--help"])
    assert "See also: https://example.com" in buf.getvalue()


# ---------------------------------------------------------------------------
# Import UX — re-exports
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_dataclass_re_export() -> None:
    from armature import dataclass  # noqa: PLC0415

    @dataclass
    class Cmd:
        name: str

    assert CLI(Cmd).parse(["Alice"]).name == "Alice"


@pytest.mark.unit
def test_field_re_export() -> None:
    from armature import dataclass, field  # noqa: PLC0415

    @dataclass
    class Cmd:
        items: list[str] = field(default_factory=list)

    assert CLI(Cmd).parse([]).items == []


@pytest.mark.unit
def test_annotated_re_export() -> None:
    from armature import Annotated  # noqa: PLC0415

    @dataclasses.dataclass
    class Cmd:
        verbose: Annotated[bool, Arg(short="-v")] = False

    assert CLI(Cmd).parse(["-v"]).verbose is True
