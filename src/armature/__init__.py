"""Armature — zero-dependency dataclass-driven CLI builder."""

from __future__ import annotations

__version__ = "0.1.0"
__all__ = ["CLI", "Arg", "SubCmd", "handler"]

import argparse
import dataclasses
import inspect
import os
import types as _builtin_types
from collections.abc import Callable
from typing import Annotated, Any, TypeVar, Union, get_args, get_origin, get_type_hints

_F = TypeVar("_F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# Public descriptors
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class Arg:
    """Metadata for a CLI argument field, used inside Annotated[T, Arg(...)].

    Example:
        env: Annotated[str, Arg(help="Target env", choices=["prod", "staging"])]
        verbose: Annotated[bool, Arg(short="-v")] = False
    """

    help: str = ""
    choices: list[Any] | None = None
    short: str | None = None
    metavar: str | None = None
    required: bool = False
    converter: Callable[[str], Any] | None = None
    env: str | None = None


class SubCmd:
    """Sentinel used in Annotated[T, SubCmd] to mark a field as a subcommand dispatch point.

    Example:
        cmd: Annotated[Deploy | Rollback, SubCmd]
    """


# ---------------------------------------------------------------------------
# Handler registry
# ---------------------------------------------------------------------------

_handler_registry: dict[type, Callable[..., Any]] = {}


def handler(command_cls: type) -> Callable[[_F], _F]:
    """Register a callable as the execution handler for a command dataclass.

    Example:
        @handler(Deploy)
        def deploy(cmd: Deploy) -> None:
            print(cmd.env)
    """

    def decorator(fn: _F) -> _F:
        _handler_registry[command_cls] = fn
        return fn

    return decorator


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class _Resolved:
    real_type: Any
    arg_meta: Arg | None
    is_subcmd: bool
    is_optional: bool = False


def _resolve_annotation(annotation: Any) -> _Resolved:
    """Extract real type and metadata from a raw field annotation."""
    if get_origin(annotation) is Annotated:
        inner = get_args(annotation)
        real_type, extras = inner[0], inner[1:]
        if any(e is SubCmd for e in extras):
            return _Resolved(real_type=real_type, arg_meta=None, is_subcmd=True)
        arg_meta = next((e for e in extras if isinstance(e, Arg)), None)
        return _Resolved(real_type=real_type, arg_meta=arg_meta, is_subcmd=False)

    if _is_union(annotation):
        type_args = get_args(annotation)
        non_none = [a for a in type_args if a is not type(None)]
        if len(non_none) == 1:
            return _Resolved(
                real_type=non_none[0], arg_meta=None, is_subcmd=False, is_optional=True
            )

    return _Resolved(real_type=annotation, arg_meta=None, is_subcmd=False)


def _is_union(type_: Any) -> bool:
    """Return True for both typing.Union and Python 3.10+ X | Y unions."""
    return get_origin(type_) is Union or isinstance(type_, _builtin_types.UnionType)


def _union_members(type_: Any) -> list[type]:
    """Unpack Union[A, B] / A | B into [A, B], excluding NoneType."""
    if _is_union(type_):
        return [a for a in get_args(type_) if a is not type(None)]
    return [type_]


def _subcmd_name(cls: type) -> str:
    """Return the CLI subcommand token for a class, honouring __armature_name__ overrides."""
    return getattr(cls, "__armature_name__", cls.__name__.lower())


def _field_cli_name(name: str) -> str:
    """Convert field name underscores to hyphens for CLI flags."""
    return name.replace("_", "-")


def _str_to_bool(value: str) -> bool:
    """Convert a string token to bool for positional boolean fields."""
    if value.lower() in ("1", "true", "yes"):
        return True
    if value.lower() in ("0", "false", "no"):
        return False
    raise argparse.ArgumentTypeError(f"expected true/false/yes/no/1/0, got {value!r}")


def _add_field(
    parser: argparse.ArgumentParser,
    field: dataclasses.Field[Any],
    resolved: _Resolved,
) -> None:
    """Register a single dataclass field onto an argparse parser."""
    real_type: Any = resolved.real_type
    meta = resolved.arg_meta

    kwargs: dict[str, Any] = {}
    if meta:
        help_text = meta.help
        if meta.env:
            help_text = f"{help_text} (env: {meta.env})" if help_text else f"env: {meta.env}"
        if help_text:
            kwargs["help"] = help_text
        if meta.choices is not None:
            kwargs["choices"] = meta.choices
        if meta.metavar:
            kwargs["metavar"] = meta.metavar

    has_default = (
        field.default is not dataclasses.MISSING
        or field.default_factory is not dataclasses.MISSING
        or resolved.is_optional
    )

    env_default: Any = dataclasses.MISSING
    if meta and meta.env:
        raw = os.environ.get(meta.env)
        if raw is not None:
            if meta.converter:
                try:
                    env_default = meta.converter(raw)
                except (ValueError, TypeError):
                    env_default = raw
            elif real_type is bool:
                try:
                    env_default = _str_to_bool(raw)
                except argparse.ArgumentTypeError:
                    env_default = raw
            else:
                try:
                    env_default = real_type(raw)
                except (ValueError, TypeError):
                    env_default = raw
            has_default = True

    if get_origin(real_type) is list:
        _add_list_field(parser, field, meta, real_type, kwargs, has_default)
        return

    effective_type: Any = (meta.converter if meta and meta.converter else None) or (
        _str_to_bool if real_type is bool else real_type
    )
    is_required_named = not has_default and meta is not None and meta.required

    if not has_default and not is_required_named:
        kwargs["type"] = effective_type
        parser.add_argument(field.name, **kwargs)
        return

    cli_name = _field_cli_name(field.name)
    flags = [f"--{cli_name}"]
    if meta and meta.short:
        flags.insert(0, meta.short)
    kwargs["dest"] = field.name

    if real_type is bool and not (meta and meta.converter):
        kwargs["action"] = "store_true"
        kwargs["default"] = (
            env_default if env_default is not dataclasses.MISSING
            else (field.default if field.default is not dataclasses.MISSING else False)
        )
    else:
        kwargs["type"] = effective_type
        if is_required_named:
            kwargs["required"] = True
        elif env_default is not dataclasses.MISSING:
            kwargs["default"] = env_default
        elif resolved.is_optional:
            kwargs["default"] = None
        else:
            kwargs["default"] = field.default if field.default is not dataclasses.MISSING else None

    parser.add_argument(*flags, **kwargs)


def _add_list_field(
    parser: argparse.ArgumentParser,
    field: dataclasses.Field[Any],
    meta: Arg | None,
    real_type: Any,
    kwargs: dict[str, Any],
    has_default: bool,
) -> None:
    """Register a list[T] field onto an argparse parser."""
    inner = get_args(real_type)[0] if get_args(real_type) else str
    kwargs["type"] = inner

    if not has_default:
        kwargs["nargs"] = "+"
        if meta and meta.metavar:
            kwargs["metavar"] = meta.metavar
        parser.add_argument(field.name, **kwargs)
    else:
        kwargs["nargs"] = "*"
        kwargs["default"] = field.default if field.default is not dataclasses.MISSING else []
        kwargs["dest"] = field.name
        cli_name = _field_cli_name(field.name)
        flags = [f"--{cli_name}"]
        if meta and meta.short:
            flags.insert(0, meta.short)
        parser.add_argument(*flags, **kwargs)


def _build_parser(parser: argparse.ArgumentParser, cls: type) -> None:
    """Populate an ArgumentParser from a dataclass's annotated fields."""
    hints = get_type_hints(cls, include_extras=True)
    for field in dataclasses.fields(cls):
        annotation = hints.get(field.name, field.type)
        resolved = _resolve_annotation(annotation)
        if resolved.is_subcmd:
            dest = f"_sub_{cls.__name__.lower()}_{field.name}"
            _add_subparsers(parser, resolved.real_type, dest)
        else:
            _add_field(parser, field, resolved)


def _add_subparsers(
    parser: argparse.ArgumentParser,
    type_: Any,
    dest: str,
) -> None:
    """Add a subparsers group for a SubCmd-annotated field, recursing into each member."""
    subparsers = parser.add_subparsers(dest=dest, required=True)
    for member_cls in _union_members(type_):
        sub = subparsers.add_parser(
            _subcmd_name(member_cls),
            description=inspect.getdoc(member_cls),
        )
        _build_parser(sub, member_cls)


def _reconstruct(cls: type, namespace: dict[str, Any]) -> Any:
    """Instantiate cls from a flat namespace dict, recursing into SubCmd fields."""
    hints = get_type_hints(cls, include_extras=True)
    init_kwargs: dict[str, Any] = {}
    for field in dataclasses.fields(cls):
        annotation = hints.get(field.name, field.type)
        resolved = _resolve_annotation(annotation)
        if resolved.is_subcmd:
            dest = f"_sub_{cls.__name__.lower()}_{field.name}"
            chosen_name = namespace.pop(dest)
            chosen_cls = next(
                c for c in _union_members(resolved.real_type)
                if _subcmd_name(c) == chosen_name
            )
            init_kwargs[field.name] = _reconstruct(chosen_cls, namespace)
        else:
            init_kwargs[field.name] = namespace.pop(field.name)
    return cls(**init_kwargs)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class CLI:
    """Entry point for building a CLI from one or more dataclasses.

    Single command:
        CLI(Deploy).parse()
        CLI(Deploy).parse(["prod", "--verbose"])

    Multiple subcommands:
        CLI([Deploy, Rollback]).parse()

    Nested subcommands (via SubCmd fields on the root class):
        CLI(Docker).parse()
    """

    def __init__(self, commands: type | list[type]) -> None:
        """Create a CLI from a single command class or a list of subcommand classes."""
        if isinstance(commands, list):
            if not commands:
                raise ValueError("commands list must not be empty")
            self._is_multi = True
            self._commands: list[type] = commands
            self._single_cls: type | None = None
        else:
            self._is_multi = False
            self._commands = []
            self._single_cls = commands

    def parse(self, argv: list[str] | None = None) -> Any:
        """Parse argv (or sys.argv when None) and return a typed dataclass instance."""
        if self._is_multi:
            return self._parse_multi(argv)
        assert self._single_cls is not None
        return self._parse_single(self._single_cls, argv)

    def run(self, argv: list[str] | None = None) -> None:
        """Parse argv and dispatch to a handler.

        Dispatch order:
            1. A callable registered with @handler(CommandClass)
            2. A run() method defined on the dataclass
            3. RuntimeError with a helpful message
        """
        result = self.parse(argv)
        cls = type(result)
        if cls in _handler_registry:
            fn = _handler_registry[cls]
            fn()(result) if isinstance(fn, type) else fn(result)
            return
        if hasattr(result, "run"):
            result.run()
            return
        raise RuntimeError(
            f"No handler for {cls.__name__}. "
            f"Define a run() method on {cls.__name__} or use @handler({cls.__name__})."
        )

    def _parse_single(self, cls: type, argv: list[str] | None) -> Any:
        if not dataclasses.is_dataclass(cls):
            raise TypeError(f"{cls.__name__} must be decorated with @dataclass")
        parser = argparse.ArgumentParser(description=inspect.getdoc(cls))
        _build_parser(parser, cls)
        namespace = vars(parser.parse_args(argv))
        return _reconstruct(cls, namespace)

    def _parse_multi(self, argv: list[str] | None) -> Any:
        root = argparse.ArgumentParser()
        subparsers = root.add_subparsers(dest="_root_cmd", required=True)
        for cls in self._commands:
            if not dataclasses.is_dataclass(cls):
                raise TypeError(f"{cls.__name__} must be decorated with @dataclass")
            sub = subparsers.add_parser(
                _subcmd_name(cls),
                description=inspect.getdoc(cls),
            )
            _build_parser(sub, cls)
        namespace = vars(root.parse_args(argv))
        chosen_name = namespace.pop("_root_cmd")
        chosen_cls = next(
            c for c in self._commands if _subcmd_name(c) == chosen_name
        )
        return _reconstruct(chosen_cls, namespace)
