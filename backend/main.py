from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from autonomy import AutonomyManager
from memory import MemoryManager
from conversations import ConversationManager

# Instantiate memory and autonomy managers
memory_manager = MemoryManager()
autonomy_manager = AutonomyManager(memory=memory_manager)

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
    """
        Handle user queries by forwarding the request to the primary language model,
    asking clarifying questions via the autonomy manager, and returning the final response.
    """
        session_id = "default"
    conversation_manager.add_message(session_id, "user", request.query)
    # conversation_manager.add_message(session_id, "assistant", response)


    clarifications = await autonomy_manager.ask_clarifications(request.query)
    response = await autonomy_manager.process_request(request.query)
        conversation_manager.add_message(session_id, "assistant", response)

return {"response": response, "clarifications": clarifications}

