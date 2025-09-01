from __future__ import annotations

import argparse as ap
from typing import Optional
import inspect
from functools import wraps
from abc import ABC

class ArgType(ABC):
    pass

class Positional(ArgType):
    def __init__(self, name: str, kind: Optional[type] = None, *args, **kwargs):
        self._name = name
        self._kind = kind
        self._args: tuple = args
        self._kwargs: dict = kwargs
    
    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

class Option(ArgType):
    _short: Optional[str]
    _long: Optional[str]
    _kind: type
    _prefix: str
    
    def __init__(
        self,
        long: str, 
        short: Optional[str] = None, 
        kind: type = str,
        prefix: str = "-"
    ):
        self._short = short
        self._long = long
        self._kind = kind
        self._prefix = prefix

    @property
    def short(self) -> str | None:
        return self._short

    @property
    def long(self) -> str | None:
        return self._long

    @property
    def kind(self) -> type:
        return self._kind

    @property
    def prefix(self) -> str:
        return self._prefix

class Flag(Option):
    def __init__(
        self,
        long: str, 
        short: Optional[str] = None, 
        **kwargs,
    ):
        super().__init__(long, short, kind = bool, **kwargs)


# The wrapper around argparse
class Command(ArgType):
    _postitionals: list[Positional] = []
    _commands: list[Command] = []
    _options: list[Option] = []
    _flags: list[Flag] = []
    _parser: ap.ArgumentParser

    def __init__(self, *_, **kwargs):
        self._parser = ap.ArgumentParser()

    # TODO all of the arguments destructured
    def parse(self) -> dict:
        return {}

    # TODO this should be the decorator wrapper around command.
    def command(self, key: Optional[str] = None):
        print(key)
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                sig = inspect.signature(func)
                bound_args = {}
        
                for name, param in sig.parameters.items():
                    # Skip if already passed via args or kwargs
                    if name in kwargs:
                        continue
                    
                    # Get expected type form signature
                    expected_type = param.annotation if param.annotation is not inspect.Parameter.empty else str
        
                    # # Try to convert input to expected type
                    # try:
                    #     bound_args[name] = expected_type(name)
                    # except Exception as e:
                    #     raise ValueError(f"Could not convert input '{name}' to {expected_type}: {e}")
                
                return func(**bound_args)
            
            # Execute the function actually at runtime
            # TODO parse the args and pass them into the wrapper func.
            # wrapper()
            return wrapper
        return decorator

    # TODO decorator around the flag
    def flag(self):
        pass

    # TODO decorator for providing functionality when root command is called
    def root(self):
        pass

    def add(self, arg: ArgType) -> Command:
        match arg.__class__.__name__:
            # TODO Add the command to this parser
            # TODO add as a subparser
            case Command.__name__:
                # print("passed command")
                pass
            # TODO Add the positional to this parser
            case Positional.__name__:
                # print("passed postition ")
                pass
            # TODO Add the positional to this parser
            case Option.__name__:
                # print("passed option")
                pass
            case Flag.__name__:
                # print("passed flag")
                pass
            case _:
                raise ValueError(f"Cannot add object '{arg}' of type '{type(arg)}")
        return self


# @wp.root()
# def hello():
#     print("hello world")

# import inspect
# from typing import get_type_hints
#
# sig = inspect.signature(howdy)
# hints = get_type_hints(howdy)
#
# for name, param in sig.parameters.items():
#     hint = hints.get(name, None)
#     print(f"{name}: {hint}")
