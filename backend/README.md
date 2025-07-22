# Airtel RAG Agent

A production-ready agentic RAG (Retrieval-Augmented Generation) pipeline using LangGraph, LangChain, Google embeddings, and an extensible tool system.

## Features
- ReAct agent with tool-calling (LangGraph)
- RAG with Google text-embedding-004 and FAISS
- Vector similarity search for accurate document retrieval
- Document chunking and processing
- Persistent conversation memory
- Automatic message history trimming
- Extensible tools system
- FastAPI streaming API
- Streaming responses for real-time feedback
- Automatic session management with timeout
- Modular, testable, and production-ready

## Memory Architecture

The chatbot implements a dual memory system:

1. **Short-Term Memory**: Uses LangGraph's `MemorySaver` for conversation state within a session
   - Stores conversation history, retrieved documents, and tool call results
   - Automatically managed by LangGraph's checkpointing system
   - Backed up by an in-memory dictionary for reliability

2. **Session Management**: 
   - Tracks active sessions with timeouts
   - Automatically clears inactive sessions after a configurable period
   - Provides APIs for session listing and manual clearing

3. **Future Long-Term Memory**:
   - The architecture is designed to be extended with database-backed long-term memory
   - The `Checkpointer` class includes a `db_path` parameter for future database integration
   - This will enable persistent memory across sessions and server restarts

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables in `.env`:
   ```
   GOOGLE_API_KEY=your_google_api_key
   MODEL_NAME=gemini-1.5-flash  # Optional, defaults to gemini-1.5-flash
   DOCUMENT_PATH=path/to/your/document.txt  # Optional, defaults to static_document.txt
   SESSION_TIMEOUT_MINUTES=30  # Optional, defaults to 30 minutes
   ```

3. Run the CLI for testing:
   ```bash
   # Interactive mode
   python -m src.cli --interactive
   
   # Single query mode
   python -m src.cli "What are Airtel's data plans?"
   ```

4. Run the API:
   ```bash
   python -m uvicorn src.api.main:app --reload
   ```

## Project Structure
```
src/
├── agent/
│   ├── __init__.py
│   ├── rag_agent.py        # LangGraph agent implementation
│   └── agent_state.py      # Agent state schema
├── tools/
│   ├── __init__.py
│   ├── base_tool.py        # Base tool interface
│   ├── rag_tool.py         # RAG retrieval tool
│   └── placeholder_tools.py # Additional tools
├── rag/
│   ├── __init__.py
│   ├── document_processor.py # Document chunking and processing
│   ├── embeddings.py        # Google embeddings wrapper
│   ├── vector_store.py      # FAISS vector store
│   └── static_document.txt  # Sample document
├── memory/
│   ├── __init__.py
│   ├── checkpointer.py     # Memory persistence
│   └── session_manager.py  # Session management with timeout
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration settings
└── api/
    ├── __init__.py
    └── main.py             # FastAPI endpoints with streaming support
```

## API Endpoints

- `GET /`: Health check endpoint
- `POST /chat`: Send a message to the chatbot (non-streaming)
  ```json
  {
    "session_id": "unique-session-id",
    "message": "What are Airtel's data plans?"
  }
  ```
- `POST /chat/stream`: Send a message to the chatbot with streaming response
  ```json
  {
    "session_id": "unique-session-id",
    "message": "What are Airtel's data plans?"
  }
  ```
- `DELETE /chat/{session_id}`: Clear a session's conversation history
- `GET /sessions`: List all active sessions and their information

## Streaming Responses

The API supports streaming responses for a better user experience:

1. **Server-Side**: The `/chat/stream` endpoint returns a Server-Sent Events (SSE) stream
2. **Client-Side**: The frontend consumes the stream and updates the UI in real-time
3. **Benefits**: Users see responses as they're generated, reducing perceived latency

**Implementation Note**: The streaming implementation uses LangChain's `astream()` method which is specifically designed for Google's Generative AI models. This approach provides token-by-token streaming without any warnings or compatibility issues.

## Message History Management

The chatbot implements smart conversation history management:

1. **Automatic Trimming**: Messages are automatically trimmed to prevent context window overflow
2. **Token Limit**: A maximum of 4000 tokens is maintained in the conversation history
3. **Retention Strategy**: The system message and most recent messages are prioritized
4. **Benefits**: Prevents token limit errors while maintaining conversation coherence

## Session Management

Sessions are automatically managed with the following features:

1. **Timeout**: Inactive sessions are automatically cleared after a configurable timeout period (default: 30 minutes)
2. **Memory**: Conversation history is preserved between requests within the same session
3. **Management**: Sessions can be manually cleared or listed via API endpoints

## RAG Pipeline

1. **Document Processing**: Documents are chunked into smaller pieces with the `DocumentProcessor`
2. **Embedding Generation**: Google's text-embedding-004 model converts text chunks to vector embeddings
3. **Vector Storage**: FAISS index stores embeddings for efficient similarity search
4. **Query Processing**: User queries are embedded and matched against document chunks
5. **Context Retrieval**: Most relevant chunks are retrieved and provided as context to the LLM
6. **Response Generation**: LLM generates a response based on the retrieved context

## Deployment

For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Next Steps

- Add more specialized tools (calculator, summarizer, etc.)
- Add database integration for persistent storage
- Add comprehensive test suite
- Implement more sophisticated memory management

## Dependencies
- langgraph>=0.2.0
- langchain>=0.3.0
- langchain-google-genai>=2.0.0
- langchain-text-splitters>=0.1.0
- faiss-cpu>=1.7.4
- fastapi>=0.104.0
- uvicorn>=0.24.0
- python-multipart>=0.0.6
- pydantic>=2.0.0
- python-dotenv>=1.0.0
- numpy>=1.24.0

## License
MIT 