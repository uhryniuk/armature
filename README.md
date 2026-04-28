# armature

A zero-dependency Python library for building CLIs from plain dataclasses. No function decorators, no magic — just annotate a `@dataclass` and armature wires it into `argparse`.

```
pip install armature
```

Python 3.12+. Zero runtime dependencies.

---

## Quickstart

```python
from dataclasses import dataclass
from typing import Annotated
from armature import CLI, Arg

@dataclass
class Greet:
    """Print a greeting."""
    name: str
    loud: Annotated[bool, Arg(short="-l", help="shout it")] = False

    def run(self) -> None:
        msg = f"Hello, {self.name}!"
        print(msg.upper() if self.loud else msg)

if __name__ == "__main__":
    CLI(Greet).run()
```

```
$ python greet.py Alice
Hello, Alice!

$ python greet.py Alice --loud
HELLO, ALICE!

$ python greet.py Alice -l
HELLO, ALICE!
```

---

## How fields map to CLI arguments

| Field definition | CLI shape |
|---|---|
| `name: str` | positional: `prog Alice` |
| `count: int = 1` | option: `prog --count 5` |
| `verbose: bool = False` | flag: `prog --verbose` |
| `items: list[str]` | multi-value positional: `prog a b c` |
| `tag: str \| None = None` | optional option: `prog --tag v1` |

Underscores in field names become hyphens on the CLI (`dry_run` → `--dry-run`).

### Adding metadata

Use `Annotated[T, Arg(...)]` to attach help text, choices, or a short alias:

```python
from typing import Annotated
from armature import Arg

@dataclass
class Deploy:
    env: Annotated[str, Arg(
        help="target environment",
        choices=["prod", "staging"],
    )]
    verbose: Annotated[bool, Arg(short="-v")] = False
```

`Arg` fields:

| Field | Type | Description |
|---|---|---|
| `help` | `str` | Help text shown in `--help` output |
| `choices` | `list` | Restrict input to allowed values |
| `short` | `str` | Short flag alias, e.g. `"-v"` |
| `metavar` | `str` | Display name in usage string |

---

## Subcommands

### Flat — `CLI([A, B])`

Pass a list of command classes. The first token on the CLI becomes the subcommand name (lowercased class name):

```python
@dataclass
class Add:
    text: str
    def run(self) -> None: print(f"added: {self.text}")

@dataclass
class Done:
    id: int
    def run(self) -> None: print(f"done: {self.id}")

CLI([Add, Done]).run()
```

```
$ prog add "Buy milk"
added: Buy milk

$ prog done 3
done: 3
```

### Nested — `Annotated[A | B, SubCmd]`

Use `SubCmd` as an annotation marker for arbitrarily deep hierarchies:

```python
from armature import SubCmd

@dataclass
class Ls:
    filter: str = ""
    def run(self) -> None: print(f"ls {self.filter}")

@dataclass
class Rm:
    name: str
    def run(self) -> None: print(f"rm {self.name}")

@dataclass
class Image:
    cmd: Annotated[Ls | Rm, SubCmd]
    def run(self) -> None: self.cmd.run()

@dataclass
class App:
    cmd: Annotated[Image, SubCmd]
    debug: bool = False
    def run(self) -> None:
        if self.debug: print("[debug]")
        self.cmd.run()

CLI(App).run()
```

```
$ prog --debug image ls --filter ubuntu
[debug]
ls ubuntu

$ prog image rm nginx
rm nginx
```

`CLI.parse()` returns the full tree. Each level's flags are preserved:

```python
result = CLI(App).parse(["--debug", "image", "rm", "nginx"])
# result = App(debug=True, cmd=Image(cmd=Rm(name="nginx")))
```

> **Note:** `SubCmd` fields have no default value, so Python's dataclass rules require them to appear before any fields that have defaults.
>
> ```python
> @dataclass
> class Good:
>     cmd: Annotated[A | B, SubCmd]   # required first
>     verbose: bool = False            # default after
> ```

---

## Execution

### `parse()` — return the instance, do what you want

```python
args = CLI(Deploy).parse()
# args is a typed Deploy instance
run_deploy(args.env, dry_run=args.dry_run)
```

### `run()` — automatic dispatch

Three styles, all compatible:

**Method on the dataclass:**

```python
@dataclass
class Deploy:
    env: str
    def run(self) -> None:
        print(f"deploying to {self.env}")

CLI(Deploy).run()
```

**`@handler` decorator (separate data from logic):**

```python
from armature import handler

@dataclass
class Deploy:
    env: str  # pure data, no run() method

@handler(Deploy)
def deploy(cmd: Deploy) -> None:
    print(f"deploying to {cmd.env}")

CLI(Deploy).run()
```

`@handler` accepts any callable, including callable classes:

```python
@handler(Deploy)
class DeployHandler:
    def __call__(self, cmd: Deploy) -> None:
        ...
```

**Just call `parse()` and dispatch yourself:**

```python
result = CLI([Deploy, Rollback]).parse()
match result:
    case Deploy(env=env):
        deploy(env)
    case Rollback(version=v):
        rollback(v)
```

Dispatch priority when using `run()`: registered `@handler` > `run()` method > `RuntimeError`.

---

## Examples

The `examples/` directory contains three runnable CLIs:

| Example | Demonstrates |
|---|---|
| [`examples/greet`](examples/greet/__init__.py) | Single command, `Arg` metadata, short alias |
| [`examples/task`](examples/task/__init__.py) | Flat subcommands (`add`, `show`, `done`) |
| [`examples/dock`](examples/dock/__init__.py) | Nested subcommands (`image ls`, `image rm`, `pull`, `push`) |

Run any example from the repo root:

```
python -m examples.greet Alice --loud
python -m examples.task add "Buy milk"
python -m examples.dock image ls --filter ubuntu
```

---

## API reference

### `CLI(commands)`

| Form | Description |
|---|---|
| `CLI(MyCmd)` | Single command |
| `CLI([A, B, C])` | Flat subcommand dispatch |

**Methods:**

- `parse(argv=None) -> T` — parse and return a typed instance (`sys.argv` when `argv` is `None`)
- `run(argv=None) -> None` — parse, then dispatch to `@handler` or `run()` method

### `Arg(...)`

Field metadata descriptor. All fields optional. Use inside `Annotated[T, Arg(...)]`.

### `SubCmd`

Sentinel class. Use as `Annotated[A | B, SubCmd]` to mark a field as a subcommand dispatch point.

### `@handler(CommandClass)`

Register a callable as the execution handler for a command class. Takes precedence over `run()` methods.
