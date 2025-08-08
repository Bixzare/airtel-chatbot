# Airtel RAG Agent - Backend

A production-ready agentic RAG (Retrieval-Augmented Generation) pipeline using LangGraph, LangChain, Google embeddings, and an extensible tool system.

## 🚀 Quick Start

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp env.example .env
# Éditer .env avec votre clé API Google

# Lancer le serveur
python start_server.py
```

## 📚 Documentation complète

Pour une documentation détaillée, consultez le dossier [`../docs/`](../docs/) :

- [Guide de démarrage rapide](../docs/getting-started.md)
- [Configuration des performances](../docs/configuration/performance.md)
- [Déploiement local](../docs/deployment/local.md)
- [Déploiement Vercel](../docs/deployment/vercel.md)
- [Problèmes courants](../docs/troubleshooting/common-issues.md)

## 🔧 Features

- **ReAct agent** avec appel d'outils (LangGraph)
- **RAG** avec Google text-embedding-004 et FAISS
- **Recherche vectorielle** pour une récupération précise de documents
- **Mémoire conversationnelle** persistante
- **API FastAPI** avec streaming
- **Système de cache** optimisé
- **Architecture modulaire** et extensible

## 🧪 Tests

```bash
# Test interactif
python -m src.cli --interactive

# Test simple
python -m src.cli "What are Airtel's data plans?"

# Test de performance
python tests/test_performance.py

# Test du préchargement
python tests/test_preloading.py
```

## 🌐 API Endpoints

- **GET `/`** - Health check
- **POST `/chat`** - Endpoint de chat
- **GET `/performance`** - Métriques de performance
- **GET `/docs`** - Documentation API (Swagger)

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
- aiohttp>=3.9.0

## License
MIT 