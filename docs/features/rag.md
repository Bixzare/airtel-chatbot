# Système RAG - Airtel Chatbot

## 🔍 Vue d'ensemble

Le système RAG (Retrieval-Augmented Generation) est le cœur du chatbot Airtel Niger. Il combine la recherche vectorielle avec la génération de texte pour fournir des réponses précises basées sur la connaissance d'Airtel.

## 🏗️ Architecture RAG

### 1. Pipeline RAG complet

```
Document → Chunking → Embeddings → Vector Store → Query → Retrieval → Generation → Response
```

### 2. Composants principaux

#### Document Processor
**Fichier** : `backend/src/rag/document_processor.py`

```python
class DocumentProcessor:
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
```

**Fonctionnalités :**
- **Chunking intelligent** : Découpage des documents en chunks optimisés
- **Préservation du contexte** : Overlap entre chunks pour maintenir la cohérence
- **Métadonnées** : Conservation des informations de source
- **Multi-format** : Support TXT, PDF, DOCX

#### Vector Store
**Fichier** : `backend/src/rag/vector_store.py`

```python
class VectorStore:
    def __init__(self, embedding_dim: int = 768):
        self.embedding_dim = embedding_dim
        self.documents = []
        self.embeddings = []
        self.index = None
        self.embedding_model = GoogleEmbeddings()
```

**Fonctionnalités :**
- **Embeddings Google** : Utilisation de text-embedding-004
- **Index FAISS** : Recherche vectorielle rapide
- **Similarité cosinus** : Calcul de similarité optimisé
- **Persistance** : Sauvegarde et chargement des index

#### RAG Tool
**Fichier** : `backend/src/tools/rag_tool.py`

```python
class RAGTool(BaseTool):
    def __init__(self, document_path: str, additional_documents: List[str] = None):
        self.processor = DocumentProcessor(chunk_size=400, chunk_overlap=50)
        self.vector_store = VectorStore(embedding_dim=768)
        self.cache = RAGCache() if settings.rag_cache_enabled else None
```

## ⚙️ Configuration

### Variables d'environnement

```bash
# Document principal
DOCUMENT_PATH=src/rag/static_document.txt

# Documents additionnels (optionnel)
ADDITIONAL_DOCUMENTS=doc1.txt,doc2.txt

# Paramètres RAG
CHUNK_SIZE=400
CHUNK_OVERLAP=50
MAX_RESULTS=2
SIMILARITY_THRESHOLD=0.7

# Cache RAG
RAG_CACHE_ENABLED=true
RAG_CACHE_SIZE=1000
RAG_CACHE_TTL=3600
```

### Paramètres optimisés

```python
# Dans src/config/settings.py
class Settings:
    # RAG Configuration
    chunk_size: int = 400
    chunk_overlap: int = 50
    max_results: int = 2
    similarity_threshold: float = 0.7
    
    # Cache Configuration
    rag_cache_enabled: bool = True
    rag_cache_size: int = 1000
    rag_cache_ttl: int = 3600
```

## 🔄 Workflow RAG

### 1. Préparation des documents

```python
def prepare_documents(document_path: str) -> List[Document]:
    """Préparer les documents pour l'indexation."""
    # Charger le document
    with open(document_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Découper en chunks
    chunks = text_splitter.split_text(content)
    
    # Créer les objets Document
    documents = []
    for i, chunk in enumerate(chunks):
        doc = Document(
            page_content=chunk,
            metadata={
                "source": document_path,
                "chunk_id": i,
                "chunk_size": len(chunk)
            }
        )
        documents.append(doc)
    
    return documents
```

### 2. Génération des embeddings

```python
def generate_embeddings(documents: List[Document]) -> List[List[float]]:
    """Générer les embeddings pour tous les chunks."""
    embeddings = []
    
    for doc in documents:
        # Générer l'embedding
        embedding = embedding_model.embed_query(doc.page_content)
        embeddings.append(embedding)
    
    return embeddings
```

### 3. Recherche vectorielle

```python
def similarity_search(query: str, k: int = 2) -> List[Document]:
    """Rechercher les documents les plus similaires."""
    # Générer l'embedding de la requête
    query_embedding = embedding_model.embed_query(query)
    
    # Recherche dans l'index FAISS
    distances, indices = index.search(
        np.array([query_embedding]), k
    )
    
    # Récupérer les documents correspondants
    results = []
    for idx in indices[0]:
        if idx < len(documents):
            results.append(documents[idx])
    
    return results
```

### 4. Génération de réponse

```python
def generate_response(query: str, context_docs: List[Document]) -> str:
    """Générer une réponse basée sur le contexte."""
    # Préparer le contexte
    context = "\n\n".join([doc.page_content for doc in context_docs])
    
    # Créer le prompt
    prompt = f"""
    Contexte sur Airtel Niger:
    {context}
    
    Question: {query}
    
    Réponse basée uniquement sur le contexte fourni:
    """
    
    # Générer la réponse
    response = llm.invoke(prompt)
    return response.content
```

## 🚀 Optimisations RAG

### 1. Cache intelligent

**Fichier** : `backend/src/rag/cache.py`

```python
class RAGCache:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, query: str) -> Optional[List[str]]:
        """Récupérer un résultat du cache."""
        if query in self.cache:
            # Vérifier le TTL
            if time.time() - self.access_times[query] < self.ttl_seconds:
                self.hit_count += 1
                self.access_times[query] = time.time()
                return self.cache[query]
            else:
                # Expiré, supprimer
                del self.cache[query]
                del self.access_times[query]
        
        self.miss_count += 1
        return None
    
    def set(self, query: str, results: List[str]):
        """Stocker un résultat dans le cache."""
        # Gestion de la taille max
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[query] = results
        self.access_times[query] = time.time()
    
    def get_stats(self) -> dict:
        """Obtenir les statistiques du cache."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl_seconds
        }
```

### 2. Recherche hybride

```python
def hybrid_search(query: str, k: int = 2) -> List[Document]:
    """Recherche combinant similarité vectorielle et mots-clés."""
    # Recherche vectorielle
    vector_results = similarity_search(query, k)
    
    # Recherche par mots-clés
    keyword_results = keyword_search(query, k)
    
    # Combiner et dédupliquer
    combined_results = combine_results(vector_results, keyword_results)
    
    # Trier par score combiné
    scored_results = score_results(combined_results, query)
    
    return scored_results[:k]
```

### 3. Préchargement optimisé

```python
def preload_documents():
    """Précharger les documents pour optimiser les performances."""
    logger.info("Starting document preloading...")
    
    # Charger le document principal
    document_path = os.environ.get("DOCUMENT_PATH", "src/rag/static_document.txt")
    
    if os.path.exists(document_path):
        documents = processor.load_file(document_path)
        vector_store.add_documents(documents)
        logger.info(f"Loaded {len(documents)} chunks from {document_path}")
    else:
        logger.warning(f"Document not found: {document_path}")
    
    # Charger les documents additionnels
    additional_docs = os.environ.get("ADDITIONAL_DOCUMENTS", "").split(",")
    for doc_path in additional_docs:
        if doc_path.strip() and os.path.exists(doc_path.strip()):
            try:
                docs = processor.load_file(doc_path.strip())
                vector_store.add_documents(docs)
                logger.info(f"Loaded {len(docs)} chunks from {doc_path}")
            except Exception as e:
                logger.error(f"Error loading {doc_path}: {e}")
    
    # Test de réchauffement
    test_query = "Airtel services"
    test_results = vector_store.similarity_search(test_query, k=1)
    logger.info(f"Preloading test completed: {len(test_results)} results")
```

## 📊 Monitoring RAG

### 1. Métriques de performance

```python
class RAGMetrics:
    def __init__(self):
        self.total_queries = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.average_response_time = 0
        self.embedding_generation_time = 0
        self.search_time = 0
    
    def update_metrics(self, query_time: float, cache_hit: bool):
        """Mettre à jour les métriques."""
        self.total_queries += 1
        
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        # Mettre à jour le temps moyen
        self.average_response_time = (
            (self.average_response_time * (self.total_queries - 1) + query_time) 
            / self.total_queries
        )
    
    def get_metrics(self) -> dict:
        """Obtenir toutes les métriques."""
        cache_hit_rate = (
            self.cache_hits / self.total_queries 
            if self.total_queries > 0 else 0
        )
        
        return {
            "total_queries": self.total_queries,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "average_response_time": self.average_response_time,
            "embedding_generation_time": self.embedding_generation_time,
            "search_time": self.search_time
        }
```

### 2. Endpoint de monitoring

```python
@app.get("/rag-metrics")
async def get_rag_metrics():
    """Obtenir les métriques RAG."""
    return {
        "rag_metrics": rag_metrics.get_metrics(),
        "cache_stats": rag_tool.cache.get_stats() if rag_tool.cache else None,
        "vector_store": {
            "total_documents": len(vector_store.documents),
            "embedding_dimension": vector_store.embedding_dim,
            "index_size": vector_store.index.ntotal if vector_store.index else 0
        }
    }
```

## 🔧 Personnalisation

### 1. Ajout de nouveaux documents

```python
def add_document(document_path: str):
    """Ajouter un nouveau document au système RAG."""
    if not os.path.exists(document_path):
        raise FileNotFoundError(f"Document not found: {document_path}")
    
    # Traiter le document
    documents = processor.load_file(document_path)
    
    # Ajouter au vector store
    vector_store.add_documents(documents)
    
    # Vider le cache si nécessaire
    if rag_tool.cache:
        rag_tool.cache.clear()
    
    logger.info(f"Added {len(documents)} chunks from {document_path}")
```

### 2. Optimisation des chunks

```python
def optimize_chunking(document_path: str, target_chunk_size: int = 400):
    """Optimiser la taille des chunks pour un document spécifique."""
    # Analyser le document
    with open(document_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tester différentes tailles de chunks
    chunk_sizes = [200, 300, 400, 500, 600]
    results = {}
    
    for size in chunk_sizes:
        processor = DocumentProcessor(chunk_size=size, chunk_overlap=size//8)
        chunks = processor.load_file(document_path)
        
        # Évaluer la qualité (exemple simplifié)
        avg_chunk_length = sum(len(chunk.page_content) for chunk in chunks) / len(chunks)
        results[size] = {
            "num_chunks": len(chunks),
            "avg_length": avg_chunk_length,
            "coverage": len(chunks) * avg_chunk_length / len(content)
        }
    
    return results
```

### 3. Filtrage de contenu

```python
def filter_documents(documents: List[Document], filters: dict) -> List[Document]:
    """Filtrer les documents selon des critères."""
    filtered_docs = []
    
    for doc in documents:
        # Vérifier les filtres
        include_doc = True
        
        if "min_length" in filters:
            if len(doc.page_content) < filters["min_length"]:
                include_doc = False
        
        if "max_length" in filters:
            if len(doc.page_content) > filters["max_length"]:
                include_doc = False
        
        if "keywords" in filters:
            if not any(keyword in doc.page_content.lower() 
                      for keyword in filters["keywords"]):
                include_doc = False
        
        if include_doc:
            filtered_docs.append(doc)
    
    return filtered_docs
```

## 🚨 Gestion des erreurs

### 1. Erreurs d'embedding

```python
def handle_embedding_error(error: Exception, query: str):
    """Gérer les erreurs de génération d'embeddings."""
    logger.error(f"Embedding error for query '{query}': {error}")
    
    # Fallback vers recherche par mots-clés
    try:
        keyword_results = keyword_search(query, k=2)
        logger.info("Using keyword search fallback")
        return keyword_results
    except Exception as fallback_error:
        logger.error(f"Fallback also failed: {fallback_error}")
        return []
```

### 2. Erreurs de recherche

```python
def handle_search_error(error: Exception, query: str):
    """Gérer les erreurs de recherche vectorielle."""
    logger.error(f"Search error for query '{query}': {error}")
    
    # Retourner une réponse générique
    return [{
        "text": "Je ne peux pas accéder à l'information demandée pour le moment. "
                "Veuillez reformuler votre question ou contacter le support Airtel.",
        "source": "fallback",
        "score": 0.0
    }]
```

## 🎯 Bonnes pratiques

### 1. Optimisation des performances
- **Cache intelligent** : Utiliser le cache RAG pour les requêtes répétées
- **Chunks optimisés** : Taille de chunks adaptée au contenu
- **Préchargement** : Charger les documents au démarrage
- **Recherche hybride** : Combiner similarité vectorielle et mots-clés

### 2. Qualité des réponses
- **Contexte approprié** : Sélectionner le bon nombre de chunks
- **Filtrage** : Éliminer les résultats non pertinents
- **Validation** : Vérifier la cohérence des réponses
- **Feedback** : Collecter les retours utilisateurs

### 3. Maintenance
- **Mise à jour des documents** : Maintenir la base de connaissances à jour
- **Monitoring** : Surveiller les métriques de performance
- **Optimisation continue** : Ajuster les paramètres selon l'usage
- **Backup** : Sauvegarder régulièrement les index

## 🔗 Ressources utiles

- [Système de préchargement](preloading.md)
- [Architecture mémoire](memory.md)
- [Configuration des performances](../configuration/performance.md)
- [Guide de debugging](../troubleshooting/debugging.md)
- [Problèmes courants](../troubleshooting/common-issues.md)
