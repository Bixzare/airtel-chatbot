# Airtel RAG Agent

A production-ready agentic RAG (Retrieval-Augmented Generation) pipeline using LangGraph, LangChain, Google embeddings, and an extensible tool system.

## Features
- ReAct agent with tool-calling (LangGraph)
- RAG with Google text-embedding-004 and FAISS
- Vector similarity search for accurate document retrieval
- Document chunking and processing
- Persistent conversation memory
- Extensible tools system
- FastAPI streaming API
- Modular, testable, and production-ready

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
│   └── checkpointer.py     # Memory persistence
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration settings
└── api/
    ├── __init__.py
    └── main.py             # FastAPI endpoints
```

## API Endpoints

- `GET /`: Health check endpoint
- `POST /chat`: Send a message to the chatbot
  ```json
  {
    "session_id": "unique-session-id",
    "message": "What are Airtel's data plans?"
  }
  ```
- `DELETE /chat/{session_id}`: Clear a session's conversation history

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
- Implement streaming responses
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