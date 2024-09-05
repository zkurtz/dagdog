"""DAG node tooling."""

from dataclasses import dataclass, field
from types import ModuleType


@dataclass
class Node:
    """Container for a single node of a dagdog DAG.

    Attributes:
        module: A python module containing a `__run__` method with no required arguments.
        parents: The list of other nodes that need to execute prior to this node.
    """

    module: ModuleType
    parents: list["Node"] = field(default_factory=list)

    def run(self) -> None:
        """Execute the task defined by the node module."""
        self.module.__run__()

    @property
    def name(self) -> str:
        """Name of the node, based on the provided module."""
        return self.module.__name__
