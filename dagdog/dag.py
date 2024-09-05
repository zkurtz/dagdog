"""DAG components."""

import functools
import re
from dataclasses import dataclass

import networkx as nx
import pandas as pd

from dagdog.nodes import Node


def nodes2graph(nodes: list[Node]) -> nx.DiGraph:
    """Package the nodes as a networkx graph."""
    graph = nx.DiGraph()
    graph.add_nodes_from(node.module for node in nodes)
    edges = []
    for node in nodes:
        for parent in node.parents:
            edge = (parent.module, node.module)
            edges.append(edge)
    graph.add_edges_from(edges)
    return graph


def extract_int_from_selection(str) -> int:
    """Extract the integer k from strings of the from "k+", "(k)+", "+k", etc."""
    match = re.search(r"\d+", str)
    if match:
        return int(match.group())
    else:
        raise ValueError("No integer found in the string")


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
        ret = df[["name", "parents", "node", "module"]]
        assert isinstance(ret, pd.DataFrame), "for pyright"
        return ret

    def list(self) -> None:
        """Display the graph."""
        print(self.index)

    def select(self, selection: str, force: bool = False) -> pd.DataFrame:
        """Slice the index based on a selection specification."""
        idx = extract_int_from_selection(selection)
        node = self.index.loc[idx].node.module
        if selection.endswith("+"):
            nodes = set(nx.descendants(self.dag, node))
        elif selection.startswith("+"):
            nodes = set(nx.ancestors(self.dag, node))
        else:
            nodes = set()
        if "(" not in selection:
            nodes.add(node)
        return self.index.loc[self.index.module.isin(nodes)]

    def __call__(self, select: int | str | None = None, force: bool = False) -> None:
        """Execute nodes of the DAG.

        Terminology: The DAG has "valid state" with respect to execution of a node if all upstream nodes have already
        executed and in the proper temporal order.

        Args:
            select: Defines the set of nodes to execute. Options:
              - if select is `None`: Run the entire graph
              - if select is an integer: Run only the node corresponding to that entry of the index
              - "+k": Run the kth node including after running any upstream nodes needed to achieve valid state.
              - "k+": Run the kth node and its downstream nodes
              - "+(k)" or "(k)+": Same as above, but excluding kth node.
            force: If True and select is of the form "+k" or "+(k)", runs all upstream nodes regardless of current
                state validity.
        """
        if select is None:
            for node in self.index.node:
                node.run()
            return None
        if isinstance(select, int):
            node = self.index.node.loc[int]
            node.run()
            return None
        selection = self.select(select, force=force)
        for task in selection.itertuples():
            task.node.run()  # pyright: ignore[reportAttributeAccessIssue]
        return None
