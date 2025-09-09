from backend.memory import MemoryManager


def test_memory_add_and_query(tmp_path):
    db_file = tmp_path / "memory.db"
    mem = MemoryManager(db_path=str(db_file), short_term_limit=3)
    mem.add_message("user", "hello")
    mem.add_message("assistant", "hi")
    context = mem.get_recent_context()
    assert context[-1]["content"] == "hi"
    assert len(context) == 2
    mem.add_knowledge("Dexter", "is", "agent")
    assert ("is", "agent") in mem.query_knowledge("Dexter")


def test_neural_network_learning(tmp_path):
    db_file = tmp_path / "memory.db"
    neural_file = tmp_path / "neural.json"
    mem = MemoryManager(db_path=str(db_file), short_term_limit=3, neural_path=str(neural_file))
    baseline = mem.predict("hello")
    mem.add_message("user", "hello")
    updated = mem.predict("hello")
    assert updated != baseline
    assert neural_file.exists()
