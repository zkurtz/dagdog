# dagdog

Lightweight DAGs for data analysis dev ops. By the time you finish a data analysis with this lil puppy, you'll never want to use a Jupyter notebook again because
- your code will already be closer to production-ready, as well as more understandable and reliable.
- you will have wasted less time waiting for your notebook to rerun, allowing you to iterate rapidly on modular components instead of rerunning your entire analysis after every code update.

Note that this is NOT a replacement for tools like [dagster](https://github.com/dagster-io/dagster) or [prefect](https://github.com/PrefectHQ/prefect). While those tools are more concerned with production and monitoring, `dagdog` is strictly a dev-ops tool, allowing a user to rapidly sketch out an analysis pipeline without worrying about production considerations. This allows proofs-of-concept to grow faster (and fail faster).

## Design goals

- Easiest-possible DAG that keeps track of the run status of all tasks and their relationships.
- Highly-configurable commands for execution of the DAG, including running a task in isolation, running only upstream tasks, or running only downstream tasks, etc.
- All configurations managed natively in python -- users don't need to mess with yaml or json files.
