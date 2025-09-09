from fastapi.testclient import TestClient
from backend import main
from backend.memory import MemoryManager
from backend.autonomy import AutonomyManager
from backend.conversations import ConversationManager


def setup_app(tmp_path):
    memory = MemoryManager(db_path=str(tmp_path / "memory.db"))
    autonomy = AutonomyManager(memory=memory)
    conversations = ConversationManager(db_path=str(tmp_path / "conversations.sqlite3"))
    main.memory_manager = memory
    main.autonomy_manager = autonomy
    main.conversation_manager = conversations
    return TestClient(main.app)


def test_healthcheck():
    client = TestClient(main.app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Dexter backend is up"}


def test_query_endpoint(tmp_path):
    client = setup_app(tmp_path)
    resp = client.post("/query", json={"query": "Hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["response"] == "Received your request: Hello"
    assert data["clarifications"] == [
        "Could you please provide more details about your request?",
        "What specific format or length do you expect?",
    ]
