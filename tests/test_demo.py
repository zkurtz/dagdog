"""Use the demo for unit testing."""

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
