"""A demo dagdog project."""

import code

from dagdog.dag import Dog, Node
from demo.tasks import task_0, task_1, task_2, task_3

# Define the tasks as DAG nodes, using "parents" to indicate where one task must precede another:
node_0 = Node(task_0)
node_1 = Node(task_1, parents=[node_0])
node_2 = Node(task_2, parents=[node_1])
node_3 = Node(task_3, parents=[node_1, node_2])

# Package the nodes as a DAG dog:
nodes = [
    node_0,
    node_1,
    node_2,
    node_3,
]
dog = Dog(nodes=nodes)

# Enter interactive mode
code.interact(local=locals())

# Consider calling `dag` methods such as:
dog.run()
