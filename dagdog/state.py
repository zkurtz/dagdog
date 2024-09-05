"""Manage a cache for DAG node execution states."""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dagdog import nodes


def timestamp() -> int:
    """Current unix timestamp in nanoseconds."""
    return int(time.time_ns())


def load_json(path: Path) -> dict[str, Any]:
    """Load a json file as a dict."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def save_json(*, path: Path, data: dict[str, Any]) -> None:
    """Save a dictionary as a json file."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


@dataclass
class NodeState:
    """Track the execution state of a single node of a DAG.

    Attributes:
        start_ns: Unix timestamp marking the most recent beginning of execution of the node (if ever executed).
        finish_ns: Unix timestamp marking the most recent conclusion of execution of the node (if ever executed).
    """

    start_ns: int | None = None
    finish_ns: int | None = None


@dataclass
class Cache:
    """Track the execution of all nodes of a DAG."""

    nodes: dict[str, NodeState]
    path: Path

    @classmethod
    def init(cls, names: list[str], path: Path) -> "Cache":
        """Initialize null cache based on the list of DAG node names."""
        return Cache(
            nodes={name: NodeState() for name in names},
            path=path,
        )

    def save(self) -> None:
        """Save the cache as a json file at self.path."""
        data = {key: value.__dict__ for key, value in self.nodes.items()}
        save_json(path=self.path, data=data)

    def load(self) -> None:
        """Update values based on a json file."""
        data = load_json(self.path)
        nodes = {name: NodeState(**node) for name, node in data.items()}
        self.nodes.update(nodes)

    def delete(self) -> None:
        """Delete the cache."""
        self.path.unlink(missing_ok=True)

    def start(self, node: nodes.Node) -> None:  # pyright: ignore[reportInvalidTypeForm]
        """Update cache to reflect that `node` execution has begun."""
        self.nodes[node.name] = NodeState(start_ns=timestamp())
        self.save()

    def finish(self, node: nodes.Node) -> None:  # pyright: ignore[reportInvalidTypeForm]
        """Update cache to reflect that `node` execution has finished."""
        self.nodes[node.name] = NodeState(
            start_ns=self.nodes[node.name].start_ns,
            finish_ns=timestamp(),
        )
        self.save()
