"""Demo task."""

import click


@click.option(
    "--blah",
    is_flag=True,
    help="A click option is OK, just don't apply @click.command directly on the function.",
)
def __run__(blah: bool = True) -> None:
    """Trivial demo task."""
    print("Running task 1")
    del blah
