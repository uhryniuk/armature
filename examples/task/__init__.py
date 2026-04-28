"""Flat-subcommand example: task add|show|done."""

from dataclasses import dataclass

from armature import CLI


@dataclass
class Add:
    """Add a new task."""

    text: str

    def run(self) -> None:
        print(f"Added: {self.text}")


@dataclass
class Show:
    """Show all tasks."""

    def run(self) -> None:
        print("No tasks yet.")


@dataclass
class Done:
    """Mark a task as complete."""

    id: int

    def run(self) -> None:
        print(f"Marked task {self.id} as done.")


def main() -> None:
    CLI([Add, Show, Done]).run()
