"""
FastAPI endpoint for LangGraph RAG agent.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from pydantic import BaseModel
from src.agent.rag_agent import LangGraphRAGAgent
from langchain_core.messages import HumanMessage
from typing import Dict
import uvicorn 
import os

app = FastAPI()

# In-memory session store for message history
session_histories: Dict[str, list] = {}
agent = LangGraphRAGAgent('src/rag/static_document.txt')

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.get("/")
async def root():
    """Health check endpoint for Vercel"""
    return {"status": "ok", "message": "Airtel RAG Agent API is running"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_message = request.message
    # Get or create message history for this session
    messages = session_histories.get(session_id, [])
    messages.append(HumanMessage(content=user_message))
    response, updated_messages = agent.invoke_with_memory(messages, thread_id=session_id)
    session_histories[session_id] = updated_messages
    return {"response": response} 


if __name__ == "__main__":
    # Get port from environment variable (for Vercel) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    # Use 0.0.0.0 for production deployment
    host = "0.0.0.0" if os.environ.get("VERCEL") else "127.0.0.1"
    uvicorn.run(app, host=host, port=port, reload=False)
