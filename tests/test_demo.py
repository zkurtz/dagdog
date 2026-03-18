"""Use the demo for unit testing."""

from dagdog import state as state_module
from demo import project


def test_demo() -> None:
    dog = project.create_demo(name="test")

    # Verify node selection syntax
    dog.state.delete()
    assert dog.index.index.is_monotonic_increasing
    indices = dog.index.index.to_list()
    assert dog.select("0+").index.to_list() == indices
    assert dog.select(f"+{indices[-1]}").index.to_list() == indices
    assert dog.select("(0)+").index.to_list() == indices[1:]
    assert dog.select(f"+({indices[-1]})").index.to_list() == indices[:-1]
    assert dog.select("+2").index.to_list() == [0, 2]

    # By default, node selection should avoid re-running nodes that are already in a valid run state:
    dog.state.delete()
    dog("+2")
    assert dog.select("+3").index.to_list() == [1, 3]

    # With force=True, however, a backfill runs all ancestors regardless of run state:
    assert dog.select("+3", force=True).index.to_list() == indices

    # You can also run the whole DAG at once, or an individual step by integer-reference
    dog()
    dog(0)


def test_refresh() -> None:
    dog = project.create_demo(name="test_refresh")
    dog.state.delete()

    # Run the entire DAG so all nodes are in a valid, fresh state
    dog()

    # Record finish times immediately after the run
    original_finish_times = {name: ns.finish_ns for name, ns in dog.state.nodes.items()}

    # refresh() with the 24-hour default should detect everything is up to date
    dog.refresh()
    after_noop_times = {name: ns.finish_ns for name, ns in dog.state.nodes.items()}
    assert after_noop_times == original_finish_times, "refresh() re-ran nodes that were already fresh"

    # Make the root node (task_0) appear to have run 25 hours ago (stale)
    old_ns = state_module.timestamp() - int(25 * 3600 * 1e9)
    root_name = dog.index.iloc[0]["name"]
    cache = dog.state
    cache.nodes[root_name] = state_module.NodeState(start_ns=old_ns, finish_ns=old_ns + 1000)
    cache.save()

    # refresh() should re-run all nodes (root is stale, so its descendants are stale too)
    dog.refresh()
    refreshed_times = {name: ns.finish_ns for name, ns in dog.state.nodes.items()}
    for name in original_finish_times:
        finish_time = refreshed_times[name]
        assert finish_time != original_finish_times[name], f"Node {name!r} should have been re-run"
        # The new finish time must be more recent than the artificially old timestamp
        assert finish_time is not None, f"Node {name!r} finish time should not be None after refresh"
        assert finish_time > old_ns, f"Node {name!r} finish time should be newer than the stale root timestamp"

    # With a generous max_hours (30h), the 25-hour-old root is within the window — no re-run needed
    pre_30h_times = {name: ns.finish_ns for name, ns in dog.state.nodes.items()}
    dog.refresh(max_hours=30)
    after_30h_times = {name: ns.finish_ns for name, ns in dog.state.nodes.items()}
    assert after_30h_times == pre_30h_times, "refresh(max_hours=30) re-ran nodes that were within the time window"
