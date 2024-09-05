"""DAG components."""

import functools
import re
from dataclasses import dataclass
from pathlib import Path

import networkx as nx
import pandas as pd

from dagdog import state
from dagdog.nodes import Node


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
    name: str
    state_dir: Path = Path.home() / ".cache" / "dagdog"

    def __post_init__(self) -> None:
        """Validate the input nodes."""
        if not nx.is_directed_acyclic_graph(self.dag):
            raise ValueError("The provided nodes do not form a DAG.")
        if not self.index["name"].is_unique:
            raise ValueError("The provided nodes need to be distinct, at least in name.")
        self.state_dir.mkdir(exist_ok=True, parents=True)

    @functools.cached_property
    def dag(self) -> nx.DiGraph:
        """A networkx digraph representation of the DAG."""
        return nodes2graph(self.nodes)

    @property
    def state(self) -> state.Cache:
        """The execution state of each node of the DAG."""
        cache = state.Cache.init(
            names=list(self.index["name"]),
            path=self.state_dir / f"{self.name}.json",
        )
        if cache.path.is_file():
            cache.load()
        return cache

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
        # Merge in the raw nodes
        module2node = {node.module: node for node in self.nodes}
        df["node"] = [module2node[module] for module in df["module"]]
        df["name"] = [node.name for node in df["node"]]
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

    def _run_node(self, node: Node) -> None:
        """Execute a node, updating the DAG state before and after execution."""
        self.state.start(node)
        node.run()
        self.state.finish(node)

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
                self._run_node(node)
        elif isinstance(select, int):
            node = self.index.node.loc[int]
            self._run_node(node)
        else:
            selection = self.select(select, force=force)
            for row in selection.itertuples():
                self._run_node(row.node)  # pyright: ignore[reportAttributeAccessIssue]
