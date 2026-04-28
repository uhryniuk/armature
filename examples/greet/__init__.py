"""Single-command example: greet <name> [--loud]."""

from dataclasses import dataclass
from typing import Annotated

from armature import Arg, CLI


@dataclass
class Greet:
    """Print a personalised greeting."""

    name: str
    loud: Annotated[bool, Arg(short="-l", help="shout the greeting")] = False

    def run(self) -> None:
        msg = f"Hello, {self.name}!"
        print(msg.upper() if self.loud else msg)


def main() -> None:
    CLI(Greet).run()
