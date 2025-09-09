from fastapi.testclient import TestClient
from backend import main
from backend.memory import MemoryManager
from backend.autonomy import AutonomyManager
from backend.conversations import ConversationManager
from backend.collaboration import CollaborationHub


def setup_app(tmp_path):
    memory = MemoryManager(db_path=str(tmp_path / "memory.db"))
    collaboration = CollaborationHub()
    autonomy = AutonomyManager(memory=memory, collaboration=collaboration)
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
        "What is your primary goal regarding hello?",
        "Are there any specific constraints or preferences for hello?",
        "What would a successful outcome look like?",
    ]
