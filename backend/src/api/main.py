"""
FastAPI endpoint for LangGraph RAG agent.
"""

import logging
from typing import List, Dict, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
import uvicorn
import os
import time
from datetime import datetime
from typing import Dict
from langchain_core.messages import HumanMessage, AIMessage
from src.agent.rag_agent import LangGraphRAGAgent
from src.memory.session_manager import SessionManager
from src.memory.checkpointer import Checkpointer
from src.config.settings import Settings
from pydantic import BaseModel
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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

# Load settings
settings = Settings()

# Get session timeout from settings
session_timeout = settings.session_timeout_minutes
logger.info(f"Using session timeout of {session_timeout} minutes")

# Initialize session manager with configured timeout
session_manager = SessionManager(timeout_minutes=session_timeout)

# Initialize checkpointer for in-memory short-term memory
checkpointer = Checkpointer(db_path=settings.checkpoint_db_path)
logger.info("Using in-memory checkpointer for short-term memory")

# Initialize RAG agent with the checkpointer
document_path = os.environ.get("DOCUMENT_PATH", "src/rag/static_document.txt")
model_name = os.environ.get("MODEL_NAME", "gemini-1.5-flash")
agent = LangGraphRAGAgent(document_path, model_name, checkpointer=checkpointer)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


class SessionInfo(BaseModel):
    session_id: str
    message_count: int
    last_activity: datetime


@app.get("/")
async def root():
    """Health check endpoint for Vercel"""
    return {"status": "ok", "message": "Airtel RAG Agent API is running"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint for the RAG agent (non-streaming).

    Args:
        request: ChatRequest with session_id and message

    Returns:
        ChatResponse with the agent's response
    """
    try:
        session_id = request.session_id
        user_message = request.message
        logger.info(f"Received chat request for session {session_id}")

        # Get message history for this session
        messages = session_manager.get_session(session_id)
        messages.append(HumanMessage(content=user_message))

        # Invoke agent with memory
        response, updated_messages = agent.invoke_with_memory(
            messages, thread_id=session_id)

        # Update session history
        session_manager.update_session(session_id, updated_messages)

        # Also save to the agent's checkpointer for consistency
        state = {
            "messages": updated_messages,
            "retrieved_docs": [],
            "current_query": user_message,
            "tool_calls": []
        }
        agent.checkpointer.save_state(state, thread_id=session_id)

        logger.info(
            f"Successfully processed chat request for session {session_id}")
        return {"response": response, "session_id": session_id}

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint for the RAG agent.

    Args:
        request: ChatRequest with session_id and message

    Returns:
        StreamingResponse with the agent's response chunks
    """
    try:
        session_id = request.session_id
        user_message = request.message
        logger.info(f"Received streaming chat request for session {session_id}")

        # Get message history for this session
        messages = session_manager.get_session(session_id)
        messages.append(HumanMessage(content=user_message))

        # Define the streaming response generator
        async def response_generator():
            full_response = ""
            
            # Use the streaming method
            async for chunk in agent.invoke_with_memory_streaming(messages, thread_id=session_id):
                # Accumulate the full response
                full_response += chunk
                # Send each chunk as an SSE event
                yield f"data: {chunk}\n\n"
            
            # After streaming completes, update the session with the complete response
            updated_messages = messages + [AIMessage(content=full_response)]
            session_manager.update_session(session_id, updated_messages)
            
            # Send a completion event
            yield "data: [DONE]\n\n"
        
        # Return a streaming response
        return StreamingResponse(
            response_generator(),
            media_type="text/event-stream"
        )

    except Exception as e:
        logger.error(f"Error processing streaming chat request: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing streaming request: {str(e)}")


@app.delete("/chat/{session_id}")
async def clear_session(session_id: str):
    """
    Clear the message history for a session.

    Args:
        session_id: The session ID to clear

    Returns:
        Success message
    """
    session_cleared = session_manager.clear_session(session_id)
    state_cleared = agent.checkpointer.clear_state(session_id)
    
    if session_cleared or state_cleared:
        logger.info(f"Cleared session history for {session_id}")
        return {"status": "ok", "message": f"Session {session_id} cleared"}
    else:
        logger.warning(f"Session {session_id} not found")
        return {"status": "not_found", "message": f"Session {session_id} not found"}


@app.get("/sessions")
async def list_sessions():
    """
    List all active sessions and their information.

    Returns:
        List of session information
    """
    sessions = session_manager.get_all_sessions()
    session_info = []
    
    for session_id, data in sessions.items():
        session_info.append({
            "session_id": session_id,
            "message_count": len(data["messages"]),
            "last_activity": datetime.fromtimestamp(data["last_activity"])
        })
    
    return {"sessions": session_info, "count": len(session_info), "timeout_minutes": session_timeout}


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting Airtel RAG Agent API")
    # Any additional startup tasks can go here


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down Airtel RAG Agent API")
    # Any cleanup tasks can go here


if __name__ == "__main__":
    # Get port from environment variable (for Vercel) or default to 8000
    port = int(os.environ.get("PORT", 8000))
    # Use 0.0.0.0 for production deployment
    host = "0.0.0.0" if os.environ.get("VERCEL") else "127.0.0.1"
    uvicorn.run(app, host=host, port=port, reload=False)
