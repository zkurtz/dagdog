"""DAG components."""

from dataclasses import dataclass, field
from types import ModuleType


@dataclass
class Node:
    """Container for a single node of a dagdog DAG."""

    module: ModuleType
    parents: list["Node"] = field(default_factory=list)

    def run(self) -> None:
        """Execute the task defined by the node module."""
        self.module.__run__()


@dataclass
class Dog:
    """Container for a dagdog DAG."""

    nodes: list[Node]

    def run(self) -> None:
        """Run the entire DAG."""
        for node in self.nodes:
            node.run()
