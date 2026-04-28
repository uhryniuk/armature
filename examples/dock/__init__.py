"""Nested-subcommand example: dock pull|push|image ls|rm."""

from dataclasses import dataclass
from typing import Annotated

from armature import CLI, SubCmd


@dataclass
class Ls:
    """List images."""

    filter: str = ""

    def run(self) -> None:
        suffix = f" (filter: {self.filter!r})" if self.filter else ""
        print(f"listing images{suffix}")


@dataclass
class Rm:
    """Remove an image."""

    name: str
    force: bool = False

    def run(self) -> None:
        prefix = "[force] " if self.force else ""
        print(f"{prefix}removing {self.name!r}")


@dataclass
class Image:
    """Manage images."""

    cmd: Annotated[Ls | Rm, SubCmd]

    def run(self) -> None:
        self.cmd.run()


@dataclass
class Pull:
    """Pull an image from a registry."""

    name: str

    def run(self) -> None:
        print(f"pulling {self.name!r}")


@dataclass
class Push:
    """Push an image to a registry."""

    name: str
    tag: str = "latest"

    def run(self) -> None:
        print(f"pushing {self.name!r}:{self.tag}")


@dataclass
class Dock:
    """A docker-like CLI built with armature."""

    cmd: Annotated[Pull | Push | Image, SubCmd]
    debug: bool = False

    def run(self) -> None:
        if self.debug:
            print("[debug]")
        self.cmd.run()


def main() -> None:
    CLI(Dock).run()
