from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional


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
    Handle user queries by forwarding the request to the primary LLM.
    In a full implementation this would use the autonomy manager to ask
    clarifying questions and orchestrate collaboration between multiple
    language models. For now it simply echoes the query back.
    """
    # TODO: integrate autonomy manager and collaboration engine
    return {"response": f"Received: {request.query}", "clarifications": []}
