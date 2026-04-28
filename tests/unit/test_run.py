"""Unit tests for CLI.run() dispatch and the @handler decorator."""

import dataclasses
from collections.abc import Generator

import pytest

import armature
from armature import CLI, handler


@pytest.fixture(autouse=True)
def _clear_registry() -> Generator[None, None, None]:
    yield
    armature._handler_registry.clear()


# ---------------------------------------------------------------------------
# run() method dispatch
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_calls_run_method(capsys: pytest.CaptureFixture[str]) -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str

        def run(self) -> None:
            print(f"hello {self.name}")

    CLI(Cmd).run(["Alice"])
    assert capsys.readouterr().out == "hello Alice\n"


@pytest.mark.unit
def test_run_no_handler_raises() -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str

    with pytest.raises(RuntimeError, match="No handler"):
        CLI(Cmd).run(["Alice"])


# ---------------------------------------------------------------------------
# @handler decorator dispatch
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_handler_registered_and_called(capsys: pytest.CaptureFixture[str]) -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str

    @handler(Cmd)
    def _h(cmd: Cmd) -> None:
        print(f"handled {cmd.name}")

    CLI(Cmd).run(["Alice"])
    assert capsys.readouterr().out == "handled Alice\n"


@pytest.mark.unit
def test_handler_receives_typed_instance() -> None:
    received: list[object] = []

    @dataclasses.dataclass
    class Cmd:
        value: int

    @handler(Cmd)
    def _h(cmd: Cmd) -> None:
        received.append(cmd)

    CLI(Cmd).run(["42"])
    assert len(received) == 1
    assert isinstance(received[0], Cmd)
    assert received[0].value == 42  # type: ignore[union-attr]


@pytest.mark.unit
def test_handler_takes_precedence_over_run_method(capsys: pytest.CaptureFixture[str]) -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str

        def run(self) -> None:
            print("run() called")

    @handler(Cmd)
    def _h(cmd: Cmd) -> None:
        print("handler called")

    CLI(Cmd).run(["Alice"])
    assert capsys.readouterr().out == "handler called\n"


@pytest.mark.unit
def test_handler_callable_class(capsys: pytest.CaptureFixture[str]) -> None:
    @dataclasses.dataclass
    class Cmd:
        name: str

    @handler(Cmd)
    class _H:
        def __call__(self, cmd: Cmd) -> None:
            print(f"class handler: {cmd.name}")

    CLI(Cmd).run(["Bob"])
    assert capsys.readouterr().out == "class handler: Bob\n"


# ---------------------------------------------------------------------------
# run() with subcommands
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_run_flat_subcommands(capsys: pytest.CaptureFixture[str]) -> None:
    @dataclasses.dataclass
    class Alpha:
        def run(self) -> None:
            print("alpha")

    @dataclasses.dataclass
    class Beta:
        def run(self) -> None:
            print("beta")

    CLI([Alpha, Beta]).run(["beta"])
    assert capsys.readouterr().out == "beta\n"


@pytest.mark.unit
def test_run_subcommand_with_handler(capsys: pytest.CaptureFixture[str]) -> None:
    @dataclasses.dataclass
    class Deploy:
        env: str

    @handler(Deploy)
    def _h(cmd: Deploy) -> None:
        print(f"deploying to {cmd.env}")

    CLI([Deploy]).run(["deploy", "prod"])
    assert capsys.readouterr().out == "deploying to prod\n"
