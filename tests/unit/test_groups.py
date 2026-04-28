"""Unit tests for mutually exclusive argument groups."""

import dataclasses
from typing import Annotated

import pytest

from armature import CLI, Arg


@dataclasses.dataclass
class OutputCmd:
    resource: str
    as_json: Annotated[bool, Arg(group="output")] = False
    as_yaml: Annotated[bool, Arg(group="output")] = False
    as_table: Annotated[bool, Arg(group="output")] = True


@pytest.mark.unit
def test_mutually_exclusive_two_flags_exits() -> None:
    with pytest.raises(SystemExit):
        CLI(OutputCmd).parse(["pods", "--as-json", "--as-yaml"])


@pytest.mark.unit
def test_mutually_exclusive_one_flag_parses() -> None:
    result = CLI(OutputCmd).parse(["pods", "--as-json"])
    assert result.as_json is True
    assert result.as_yaml is False
    assert result.resource == "pods"


@pytest.mark.unit
def test_mutually_exclusive_defaults_when_none_set() -> None:
    result = CLI(OutputCmd).parse(["pods"])
    assert result.as_json is False
    assert result.as_yaml is False
    assert result.as_table is True


@pytest.mark.unit
def test_fields_in_different_groups_both_settable() -> None:
    @dataclasses.dataclass
    class Cmd:
        resource: str
        as_json: Annotated[bool, Arg(group="output")] = False
        wide: Annotated[bool, Arg(group="display")] = False

    result = CLI(Cmd).parse(["pods", "--as-json", "--wide"])
    assert result.as_json is True
    assert result.wide is True


@pytest.mark.unit
def test_ungrouped_fields_unaffected() -> None:
    @dataclasses.dataclass
    class Cmd:
        resource: str
        verbose: bool = False
        as_json: Annotated[bool, Arg(group="output")] = False

    result = CLI(Cmd).parse(["pods", "--verbose", "--as-json"])
    assert result.verbose is True
    assert result.as_json is True
