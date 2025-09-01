# wampum
Library for writing testable, typed and simple CLI's in Python with zero dependencies 🐍

## Design

Commands can be created via register with the Wampum()
Commands can be created via the Command decorator

Commands can be created by having classes that inherit the Command object.

At it's root, wampum is going to have zero dependencies
- relies entirely on stdlib with argparse
- Ideally with a plugin system later on.

```python

wp = Wampum()
wp.flag

wp2 = wp.command()

wp3 = Wampum()
wp.add_command(wp3)

@wp.command
def hello(arg1: str, arg2: int):
    print(f"{arg1} is of type {type(arg1)}")
    print(f"{arg2} is of type {type(arg2)}")

@wp.flag
def word(arg1: str, arg2: int):
    print(f"{arg1} is of type {type(arg1)}")
    print(f"{arg2} is of type {type(arg2)}")



$ cli --world hello


```


```python

import wampum as wp

@wp.command
def hello(arg1: str, arg2: int):
    print(f"{arg1} is of type {type(arg1)}")
    print(f"{arg2} is of type {type(arg2)}")

@wp.prehook(hello)
def hello_prehook()

@wp.flag
def word(arg1: str, arg2: int):
    print(f"{arg1} is of type {type(arg1)}")
    print(f"{arg2} is of type {type(arg2)}")


$ cli --world hello


```
