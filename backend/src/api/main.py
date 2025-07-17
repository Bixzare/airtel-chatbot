"""
FastAPI endpoint for LangGraph RAG agent.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.agent.rag_agent import LangGraphRAGAgent
from langchain_core.messages import HumanMessage
from typing import Dict, List, Optional
import uvicorn 
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Airtel RAG Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory session store for message history
session_histories: Dict[str, List] = {}

# Initialize RAG agent
document_path = os.environ.get("DOCUMENT_PATH", "src/rag/static_document.txt")
model_name = os.environ.get("MODEL_NAME", "gemini-1.5-flash")
agent = LangGraphRAGAgent(document_path, model_name)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
async def root():
    """Health check endpoint for Vercel"""
    return {"status": "ok", "message": "Airtel RAG Agent API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint for the RAG agent.
    
    Args:
        request: ChatRequest with session_id and message
        
    Returns:
        ChatResponse with the agent's response
    """
    try:
        session_id = request.session_id
        user_message = request.message
        logger.info(f"Received chat request for session {session_id}")
        
        # Get or create message history for this session
        messages = session_histories.get(session_id, [])
        messages.append(HumanMessage(content=user_message))
        
        # Invoke agent with memory
        response, updated_messages = agent.invoke_with_memory(messages, thread_id=session_id)
        
        # Update session history
        session_histories[session_id] = updated_messages
        
        logger.info(f"Successfully processed chat request for session {session_id}")
        return {"response": response, "session_id": session_id}
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.delete("/chat/{session_id}")
async def clear_session(session_id: str):
    """
    Clear the message history for a session.
    
    Args:
        session_id: The session ID to clear
        
    Returns:
        Success message
    """
    if session_id in session_histories:
        del session_histories[session_id]
        logger.info(f"Cleared session history for {session_id}")
        return {"status": "ok", "message": f"Session {session_id} cleared"}
    else:
        logger.warning(f"Session {session_id} not found")
        return {"status": "not_found", "message": f"Session {session_id} not found"}

if __name__ == "__main__":
    # Get port from environment variable (for Vercel) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    # Use 0.0.0.0 for production deployment
    host = "0.0.0.0" if os.environ.get("VERCEL") else "127.0.0.1"
    uvicorn.run(app, host=host, port=port, reload=False)
