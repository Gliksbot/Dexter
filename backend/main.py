from fastapi import FastAPI
from pydantic import BaseModel
from .autonomy import AutonomyManager
from .memory import MemoryManager
from .conversations import ConversationManager
from .collaboration import CollaborationHub

# Instantiate core managers
memory_manager = MemoryManager()
collaboration_hub = CollaborationHub()
autonomy_manager = AutonomyManager(
    memory=memory_manager, collaboration=collaboration_hub
)

conversation_manager = ConversationManager()
app = FastAPI(title="Dexter Backend")


class QueryRequest(BaseModel):
    query: str


@app.get("/")
async def read_root():
    """Health check endpoint."""
    return {"message": "Dexter backend is up"}


@app.post("/query")
async def handle_query(request: QueryRequest):
    """Handle a user query and return Dexter's response."""
    session_id = "default"
    conversation_manager.add_message(session_id, "user", request.query)

    clarifications = await autonomy_manager.ask_clarifications(request.query)
    response = await autonomy_manager.process_request(request.query)

    conversation_manager.add_message(session_id, "assistant", response)

    return {"response": response, "clarifications": clarifications}

