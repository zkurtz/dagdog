"""DAG node tooling."""

from dataclasses import dataclass, field
from types import ModuleType
from typing import Callable

import networkx as nx


def is_click_command(func: Callable) -> bool:
    """Check if a function is decorated with @click.command."""
    class_name = func.__class__.__name__
    module_name = getattr(func.__class__, "__module__", "")
    return class_name in ("Command", "Group") and "click" in module_name


@dataclass
class Node:
    """Container for a single node of a dagdog DAG.

    Attributes:
        module: A python module containing a `__run__` method with no required arguments.
        parents: The list of other nodes that need to execute prior to this node.
    """

    module: ModuleType
    parents: list["Node"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate node attributes."""
        if is_click_command(self.run_method):
            do_not = "Remove the `@click.command()` decorator from the node module's `__run__` method."
            instead_do = "Instead, see https://gist.github.com/zkurtz/84e3158ed3fb618e338ce581bbe18912"
            raise ValueError(f"{do_not} {instead_do}")

    @property
    def run_method(self) -> Callable:
        """Return the run method of the node module."""
        return self.module.__run__

    def run(self) -> None:
        """Execute the task defined by the node module."""
        self.run_method()

    @property
    def name(self) -> str:
        """Name of the node, based on the provided module."""
        return self.module.__name__


def nodes2graph(nodes: list[Node]) -> nx.DiGraph:
    """Package a list of nodes as a networkx graph."""
    graph = nx.DiGraph()
    graph.add_nodes_from(node.module for node in nodes)
    edges = []
    for node in nodes:
        for parent in node.parents:
            edge = (parent.module, node.module)
            edges.append(edge)
    graph.add_edges_from(edges)
    return graph
