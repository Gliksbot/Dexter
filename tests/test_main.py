from fastapi.testclient import TestClient
from backend import main
from backend.memory import MemoryManager
from backend.autonomy import AutonomyManager
from backend.conversations import ConversationManager
from backend.collaboration import CollaborationHub


def setup_app(tmp_path):
    memory = MemoryManager(db_path=str(tmp_path / "memory.db"))
    collaboration = CollaborationHub()

    def stub_questions(query: str, minimum: int = 3):
        return [f"Clarify {i+1} about {query}?" for i in range(minimum)]

    autonomy = AutonomyManager(
        memory=memory,
        collaboration=collaboration,
        question_generator=stub_questions,
    )
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
    assert len(data["clarifications"]) >= 3
    assert all(isinstance(q, str) and q for q in data["clarifications"])
