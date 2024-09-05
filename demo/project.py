"""A demo dagdog project.

Run as: `python demo/project.py`
"""

import code

from dagdog.dag import Dog, Node
from demo.tasks import task_0, task_1, task_2, task_3


def create_demo(name: str = "demo") -> Dog:
    """Generate a demo dog DAG."""
    # Define the tasks as DAG nodes, using "parents" to indicate where one task must precede another:
    node_0 = Node(task_0)
    node_1 = Node(task_1, parents=[node_0])
    node_2 = Node(task_2, parents=[node_0])
    node_3 = Node(task_3, parents=[node_1, node_2])

    # Package the nodes as a DAG dog:
    nodes = [
        node_0,
        node_1,
        node_2,
        node_3,
    ]
    return Dog(
        nodes=nodes,
        name=name,
    )


if __name__ == "__main__":
    # Start an interactive session to run or inspect the DAG dog:
    dog = create_demo()
    dog.ls()
    code.interact(local=locals(), banner="")
    # Try running commands like these to observe execution over the DAG:
    # dog("0+")
    # dog("2+")
    # dog("+3")
    # dog("+3", force=True)
