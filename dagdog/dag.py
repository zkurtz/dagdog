"""DAG components."""

import functools
from dataclasses import dataclass

import networkx as nx
import pandas as pd

from dagdog.nodes import Node


def nodes2graph(nodes: list[Node]) -> nx.DiGraph:
    """Package the nodes as a networkx graph."""
    graph = nx.DiGraph()
    modules = [node.module for node in nodes]
    graph.add_nodes_from(modules)
    edges = []
    for node in nodes:
        for parent in node.parents:
            edge = (parent.module, node.module)
            edges.append(edge)
    graph.add_edges_from(edges)
    return graph


@dataclass
class Dog:
    """Container for a dagdog DAG."""

    nodes: list[Node]

    def __post_init__(self) -> None:
        """Validate the input nodes."""
        if not nx.is_directed_acyclic_graph(self.dag):
            raise ValueError("The provided nodes do not form a DAG.")
        nodes = list(self.dag.nodes())
        if len(nodes) > len(set(nodes)):
            raise ValueError("The provided nodes (as indexed by node.module) need to be distinct.")

    @functools.cached_property
    def dag(self) -> nx.DiGraph:
        """A networkx digraph representation of the DAG."""
        return nodes2graph(self.nodes)

    @functools.cached_property
    def index(self) -> pd.DataFrame:
        """Represent the DAG as an ordered data frame of tasks."""
        sorted_modules = list(nx.topological_sort(self.dag))
        df = pd.DataFrame({"module": sorted_modules})
        df.index.name = "index"
        # Identify parents per module
        modules = df.reset_index().set_index("module")[["index"]]
        assert isinstance(modules, pd.DataFrame), "for pyright"
        modules["parents"] = [list(self.dag.predecessors(idx)) for idx in modules.index]
        # Translate parents back to indices of parents
        df["parents"] = [list(modules["index"].loc[parents]) for parents in modules["parents"]]
        df["name"] = [module.__name__ for module in sorted_modules]
        # Merge in the raw nodes
        module2node = {node.module: node for node in self.nodes}
        df["node"] = [module2node[module] for module in df["module"]]
        assert df.index.is_monotonic_increasing, "The index needs to be sorted."
        ret = df[["name", "parents", "node"]]
        assert isinstance(ret, pd.DataFrame), "for pyright"
        return ret

    def list(self) -> None:
        """Display the graph."""
        print(self.index)

    def run(self) -> None:
        """Run the entire DAG."""
        for node in self.index.node:
            node.run()
