# How to run

```
python -m uvicorn src.api.main:app

```

# LangGraph RAG Agent

A production-ready agentic RAG (Retrieval-Augmented Generation) pipeline using LangGraph, LangChain, Google embeddings, and an extensible tool system.

## Features
- ReAct agent with tool-calling (LangGraph)
- RAG with Google text-embedding-004
- In-memory vector store (FAISS)
- Persistent conversation memory
- Extensible tools (search, calculator, summarizer, etc.)
- FastAPI streaming API
- Modular, testable, and production-ready

## Project Structure
```
src/
├── agent/
│   ├── __init__.py
│   ├── rag_agent.py
│   └── agent_state.py
├── tools/
│   ├── __init__.py
│   ├── base_tool.py
│   ├── rag_tool.py
│   └── placeholder_tools.py
├── rag/
│   ├── __init__.py
│   ├── document_processor.py
│   ├── embeddings.py
│   └── vector_store.py
├── memory/
│   ├── __init__.py
│   └── checkpointer.py
├── config/
│   ├── __init__.py
│   └── settings.py
└── api/
    ├── __init__.py
    └── main.py
```

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables in `.env`:
   - `GOOGLE_API_KEY`
   - `TAVILY_API_KEY`
   - `LANGSMITH_API_KEY`
   - `LANGSMITH_TRACING=true`
3. Run the API:
   ```bash
   uvicorn src.api.main:app --reload
   ```

## Development Sequence
1. Google embeddings integration
2. In-memory vector store
3. Document processing
4. RAG tool
5. LangGraph agent
6. Memory & persistence
7. API endpoints & streaming
8. Testing & docs

## Dependencies
- langgraph>=0.2.0
- langchain>=0.3.0
- langchain-google-genai>=2.0.0
- faiss-cpu>=1.7.4
- fastapi>=0.104.0
- uvicorn>=0.24.0
- python-multipart>=0.0.6
- pydantic>=2.0.0

## License
MIT 