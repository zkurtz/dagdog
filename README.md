# dagdog

Lightweight DAGs for data analysis dev ops. By the time you finish a project with this lil puppy, you'll never want to use a Jupyter notebook again because
- you will have wasted less time waiting for your notebook to rerun, by iterating rapidly on modular components instead of rerunning your entire analysis after every code update.
- your code will already be closer to production-ready, as well as more understandable and reliable.

Note that this is NOT a replacement for tools like [dagster](https://github.com/dagster-io/dagster) or [prefect](https://github.com/PrefectHQ/prefect). Those tools emphasize production and monitoring, while `dagdog` is strictly a dev-ops tool, allowing a user to rapidly sketch out an analysis pipeline without worrying about production considerations. This allows proofs-of-concept to grow faster (and fail faster).

## Getting started

See the README and demo project inside `/demo`. In brief, here's how to work with `dagdog`:
- Structure your data analysis pipeline as a collection of python modules, with each module defining exactly one task.
- Within each module, define a `__run__` method. (You might choose to call `__run__` from under `if __name__ == "main":`, but `dagdog` does not care about that and will access `__run__` directly.)
- Create a project entrypoint script, imitating `demo/project.py` to define the execution order of your tasks.
- Call your project entrypoint, dropping you into an interactive python session, where you can finally call any of the various execution and introspection methods on the `dog` DAG object.


## Development

Install [pyenv and its virtualenv plugin](https://github.com/pyenv/pyenv-virtualenv). Then:
```
pyenv install 3.11.4
pyenv global 3.11.4
pyenv virtualenv 3.11.4 dagdog
pyenv activate dagdog
```

Install poetry:
```
curl -sSL https://install.python-poetry.org | python3 -
```

Set up git hooks:
```
pre-commit install
```

## Design goals

- Easiest-possible usage of a DAG to coordinate execution of a collection of tasks during data analysis dev ops.
- Flexible commands for execution of the DAG, including running a task in isolation, running only upstream tasks, or running only downstream tasks, etc.
- All configurations managed natively in python -- users don't need to mess with yaml or json files.
- Prioritize simplicity above feature-completeness.
