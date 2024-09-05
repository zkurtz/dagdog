"""DAG node tooling."""

from dataclasses import dataclass, field
from types import ModuleType

import networkx as nx


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
