# Système de Préchargement des Documents

## Vue d'ensemble

Le système de préchargement des documents a été implémenté pour optimiser les performances du chatbot en chargeant et en mettant en cache les documents statiques au démarrage du serveur. Cela permet d'éviter les délais de chargement lors des premières requêtes utilisateur.

## Fonctionnalités

### 1. Préchargement Automatique
- **Démarrage du serveur** : Le document static_document.txt est automatiquement chargé lors du démarrage de l'API
- **Document unique** : Chargement optimisé du document principal
- **Gestion d'erreurs** : Fallback automatique en cas d'échec du préchargement

### 2. Optimisations de Performance
- **Embeddings précalculés** : Les embeddings des documents sont générés au démarrage
- **Cache intelligent** : Système de cache pour les requêtes fréquentes
- **Chunks optimisés** : Taille de chunks réduite (400 caractères) pour des réponses plus rapides

### 3. Monitoring et Logs
- **Logs détaillés** : Suivi du processus de préchargement
- **Métriques de performance** : Temps de chargement et statistiques
- **Statistiques de cache** : Monitoring de l'efficacité du cache

## Configuration

### Variables d'Environnement

```bash
# Document principal
DOCUMENT_PATH=src/rag/static_document.txt

# Modèle LLM
MODEL_NAME=gemini-1.5-flash

# Timeout LLM
LLM_TIMEOUT=60
```

### Paramètres de Cache

```python
# Dans src/config/settings.py
rag_cache_enabled = True
cache_max_size = 1000
cache_ttl_seconds = 3600
```

## Architecture

### 1. Fonction de Préchargement (`preload_documents`)

```python
def preload_documents():
    """
    Preload static documents to warm up the RAG system and improve response times.
    """
    # 1. Vérification des documents
    # 2. Initialisation de l'agent RAG
    # 3. Chargement des documents multiples
    # 4. Test de requête pour réchauffer le système
    # 5. Logs de performance
```

### 2. RAGTool Optimisé

```python
class RAGTool:
    def __init__(self, document_path, additional_documents=None):
        # Chargement du document principal
        # Génération des embeddings
        # Initialisation du cache
```

### 3. Agent RAG Single Document

```python
class LangGraphRAGAgent:
    def __init__(self, document_path):
        # Initialisation avec document unique
        # RAGTool optimisé
```

## Utilisation

### Démarrage du Serveur

```bash
# Le préchargement se fait automatiquement
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Test du Préchargement

```bash
# Script de test dédié
python test_preloading.py
```

### Monitoring

```bash
# Vérifier les métriques de performance
curl http://localhost:8000/performance

# Surveiller les logs de préchargement
tail -f backend/logs/app.log | grep "preload"
```

## Logs de Préchargement

### Logs de Démarrage
```
2024-01-15 10:30:15 - INFO - Starting document preloading...
2024-01-15 10:30:15 - INFO - Loading document: src/rag/static_document.txt
2024-01-15 10:30:16 - INFO - Document loaded: 150 chunks
2024-01-15 10:30:16 - INFO - Generating embeddings...
2024-01-15 10:30:18 - INFO - Embeddings generated successfully
2024-01-15 10:30:18 - INFO - Cache initialized with 1000 max entries
2024-01-15 10:30:18 - INFO - Preloading completed in 3.2 seconds
```

### Logs de Performance
```
2024-01-15 10:30:19 - INFO - First request processed in 0.8 seconds
2024-01-15 10:30:20 - INFO - Cache hit for query: "forfaits internet"
2024-01-15 10:30:21 - INFO - Average response time: 1.2 seconds
```

## Optimisations

### 1. Chargement Parallèle
```python
import asyncio

async def preload_documents_async():
    """Chargement asynchrone des documents pour plus de rapidité."""
    tasks = [
        load_document("doc1.txt"),
        load_document("doc2.txt"),
        initialize_cache()
    ]
    await asyncio.gather(*tasks)
```

### 2. Cache Persistant
```python
class PersistentCache:
    def __init__(self, cache_file="cache.pkl"):
        self.cache_file = cache_file
        self.load_cache()
    
    def save_cache(self):
        """Sauvegarder le cache sur disque."""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
```

### 3. Validation des Documents
```python
def validate_document(document_path):
    """Valider la structure et le contenu du document."""
    if not os.path.exists(document_path):
        raise FileNotFoundError(f"Document not found: {document_path}")
    
    with open(document_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if len(content.strip()) == 0:
        raise ValueError(f"Document is empty: {document_path}")
    
    return content
```

## Dépannage

### Problème : Document non trouvé
```
Error: Document not found: src/rag/static_document.txt
```

**Solutions :**
1. Vérifier le chemin du document
2. Créer le document s'il n'existe pas
3. Ajuster `DOCUMENT_PATH` dans `.env`

### Problème : Préchargement lent
```
Warning: Preloading took more than 10 seconds
```

**Solutions :**
1. Réduire la taille des chunks
2. Optimiser les embeddings
3. Utiliser un cache persistant

### Problème : Cache inefficace
```
Warning: Cache hit rate below 50%
```

**Solutions :**
1. Augmenter la taille du cache
2. Ajuster le TTL
3. Analyser les patterns de requêtes

## Métriques de Performance

### Endpoint de Performance
```bash
curl http://localhost:8000/performance
```

**Réponse attendue :**
```json
{
  "preloading": {
    "document_chunks": 150,
    "preload_time_seconds": 3.2,
    "cache_size": 25,
    "cache_hit_rate": 0.75
  },
  "response_times": {
    "average_seconds": 1.2,
    "first_request_seconds": 0.8
  }
}
```

### Surveillance Continue
```bash
# Script de surveillance
watch -n 30 'curl -s http://localhost:8000/performance | jq ".preloading"'
```

## Recommandations

### 1. Optimisation du Démarrage
- **Précharger les documents** au démarrage
- **Utiliser un cache persistant** pour les redémarrages rapides
- **Valider les documents** avant le chargement

### 2. Monitoring
- **Surveiller les temps de préchargement**
- **Tracer les taux de cache hit**
- **Analyser les patterns d'utilisation**

### 3. Maintenance
- **Mettre à jour les documents** régulièrement
- **Nettoyer le cache** périodiquement
- **Optimiser les chunks** selon l'usage

## Tests

### Test de Préchargement
```bash
cd backend
python test_preloading.py
```

### Test de Performance
```bash
cd backend
python test_performance.py
```

### Test Manuel
```bash
# Vérifier le préchargement
curl http://localhost:8000/performance | jq '.preloading'

# Tester une requête
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "Bonjour"}'
```
