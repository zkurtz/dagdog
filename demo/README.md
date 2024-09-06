# dagdog demo

Step-by-step usage of dagdog:

1. Organize all of your work as a collection of python modules, each defining a `__run__` method. For example, see the modules inside of `demo/tasks/`.
2. Create a script like `demo/project.py` that packages all of your individual `__run__` modules into a dagdog DAG.
3. Run your project script to enter the interactive python prompt, and call methods on you "dog" DAG to execute the DAG or parts of the DAG.

To run the actual demo, you would need to clone this repo, set up the dev environment, and run `python demo/project.py`.

```
python demo/project.py
```

The result is a summary table of the tasks in your DAG, ending with an interactive prompt:

```
                    name parents                                               node                                             module
index
0      demo.tasks.task_0      []  Node(module=<module 'demo.tasks.task_0' from '...  <module 'demo.tasks.task_0' from '/Users/me/De...
1      demo.tasks.task_1     [0]  Node(module=<module 'demo.tasks.task_1' from '...  <module 'demo.tasks.task_1' from '/Users/me/De...
2      demo.tasks.task_2     [0]  Node(module=<module 'demo.tasks.task_2' from '...  <module 'demo.tasks.task_2' from '/Users/me/De...
3      demo.tasks.task_3  [1, 2]  Node(module=<module 'demo.tasks.task_3' from '...  <module 'demo.tasks.task_3' from '/Users/me/De...

>>>
```

To run the entire dag, simply call the runner:
```
>>> dog()
Starting execution of the entire DAG

Starting execution of task demo.tasks.task_0
Running task 0

Starting execution of task demo.tasks.task_1
Running task 1

Starting execution of task demo.tasks.task_2
Running task 2

Starting execution of task demo.tasks.task_3
Running task 3
```

Alternatively, maybe you are actively working on, say, `task_2`, and so you want to run only that task. You can do that like this:
```
>>> dog(2)

Starting execution of task demo.tasks.task_2
Running task 2
```

Now suppose you're done iterating on task 2 and are ready to move on. Presumably you want to run the rest of the graph downstream of task 2 so that your final analysis (`task_3`) ends up being up-to-date with respect to any outputs of task 2. You can do this in either of the following ways:

```
dog("+3")  # runs task 3 after running any upstream tasks that need to be run to maintain proper execution order
dog("(2)+")  # runs everything downstream of task 2 (i.e. excluding 2, since it already ran)
```

Either method runs only task 3, since that is the only task downstream of task 2.

Note that the `dog("+3")` command runs only task 3 in this case, since all upstream tasks were already run in the proper order. Suppose, however, that we first go back and run task 0: `dog(0)`. This means that tasks 1 and 2 are no longer necessarily up-to-date, and if we again go run `dog("+3")`, this will execute all of `1, 2, 3`.

In case you're worried that your cache has become somehow corrupted, feel free to delete it like `dog.state.delete()` to start fresh. Also note the option to use the `force` keyword. For example, `dog("+2", force=True)` runs all associated tasks (0 and 2) regardless of whether task 0 already ran.
