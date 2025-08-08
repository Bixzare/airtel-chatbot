# Architecture Mémoire - Airtel Chatbot

## 🧠 Vue d'ensemble

Le chatbot Airtel Niger implémente un système de mémoire sophistiqué qui permet de maintenir le contexte conversationnel et d'optimiser les performances.

## 🏗️ Architecture mémoire

### 1. Mémoire à court terme (Session Memory)

**Fichier** : `backend/src/memory/checkpointer.py`

La mémoire à court terme utilise LangGraph's `MemorySaver` pour gérer l'état de conversation dans une session :

```python
class Checkpointer:
    def __init__(self, db_path: str = None):
        self.memory = MemorySaver()
        self.session_states = {}
        self.db_path = db_path
```

**Fonctionnalités :**
- **Historique de conversation** : Stockage des messages échangés
- **Documents récupérés** : Conservation des documents RAG utilisés
- **Appels d'outils** : Traçabilité des outils utilisés
- **État de session** : Gestion de l'état global de la conversation

### 2. Gestionnaire de sessions

**Fichier** : `backend/src/memory/session_manager.py`

Le gestionnaire de sessions assure la persistance et la gestion des sessions utilisateur :

```python
class SessionManager:
    def __init__(self, timeout_minutes: int = 30):
        self.sessions = {}
        self.timeout_minutes = timeout_minutes
        self.cleanup_interval = 300  # 5 minutes
```

**Fonctionnalités :**
- **Timeout automatique** : Nettoyage des sessions inactives
- **Persistance** : Sauvegarde de l'état des sessions
- **Récupération** : Restauration des sessions existantes
- **Monitoring** : Suivi des sessions actives

### 3. Mémoire à long terme (Future)

L'architecture est conçue pour être étendue avec une mémoire à long terme basée sur une base de données :

```python
class LongTermMemory:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = self._connect_db()
    
    def save_conversation(self, user_id: str, conversation: dict):
        """Sauvegarder une conversation complète."""
        pass
    
    def get_user_history(self, user_id: str) -> List[dict]:
        """Récupérer l'historique d'un utilisateur."""
        pass
```

## ⚙️ Configuration

### Variables d'environnement

```bash
# Timeout de session (minutes)
SESSION_TIMEOUT_MINUTES=30

# Chemin de la base de données (optionnel)
MEMORY_DB_PATH=./data/memory.db

# Intervalle de nettoyage (secondes)
CLEANUP_INTERVAL=300
```

### Paramètres de mémoire

```python
# Dans src/config/settings.py
class Settings:
    # Mémoire
    session_timeout_minutes: int = 30
    memory_db_path: Optional[str] = None
    cleanup_interval: int = 300
    
    # Optimisations
    max_history_tokens: int = 3000
    max_session_messages: int = 50
```

## 🔄 Cycle de vie d'une session

### 1. Création de session

```python
# Création automatique lors de la première requête
session_id = generate_session_id()
session_state = {
    "messages": [],
    "retrieved_docs": [],
    "tool_calls": [],
    "created_at": datetime.now(),
    "last_activity": datetime.now()
}
```

### 2. Mise à jour de session

```python
# Ajout d'un nouveau message
session_state["messages"].append(new_message)
session_state["last_activity"] = datetime.now()

# Sauvegarde de l'état
checkpointer.save_state(session_state, session_id)
```

### 3. Nettoyage de session

```python
# Vérification périodique des timeouts
def cleanup_expired_sessions():
    current_time = datetime.now()
    expired_sessions = []
    
    for session_id, session in sessions.items():
        if (current_time - session["last_activity"]).total_seconds() > timeout_seconds:
            expired_sessions.append(session_id)
    
    # Suppression des sessions expirées
    for session_id in expired_sessions:
        del sessions[session_id]
```

## 📊 Optimisations mémoire

### 1. Troncature de l'historique

**Fichier** : `backend/src/agent/rag_agent.py`

```python
# Troncature automatique pour éviter l'overflow
MAX_HISTORY_TOKENS = 3000

def trim_messages(messages: List[Message]) -> List[Message]:
    """Tronquer les messages pour respecter la limite de tokens."""
    return trim_messages(
        max_tokens=MAX_HISTORY_TOKENS,
        strategy="last",  # Garder les messages les plus récents
        token_counter=llm,
        include_system=True,
        allow_partial=False,
        start_on="human"
    )
```

### 2. Cache intelligent

**Fichier** : `backend/src/rag/cache.py`

```python
class RAGCache:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.access_times = {}
```

### 3. Gestion de la mémoire système

```python
import gc
import psutil

def monitor_memory_usage():
    """Surveiller l'utilisation mémoire et déclencher le garbage collector si nécessaire."""
    process = psutil.Process()
    memory_percent = process.memory_percent()
    
    if memory_percent > 80:
        logger.warning(f"Utilisation mémoire élevée: {memory_percent}%")
        gc.collect()
    
    return memory_percent
```

## 🔍 Monitoring et debugging

### 1. Métriques de session

```bash
# Endpoint pour les statistiques de session
curl http://localhost:8000/sessions

# Réponse attendue
{
  "active_sessions": 5,
  "total_sessions": 25,
  "expired_sessions": 20,
  "memory_usage_mb": 45.2,
  "average_session_duration_minutes": 12.5
}
```

### 2. Logs de mémoire

```python
# Logs détaillés pour le debugging
logger.info(f"Session {session_id} created")
logger.info(f"Session {session_id} updated with {len(messages)} messages")
logger.info(f"Session {session_id} expired after {duration} minutes")
logger.warning(f"Memory usage: {memory_percent}%")
```

### 3. Script de diagnostic mémoire

```bash
#!/bin/bash
# memory_diagnostic.sh

echo "=== Diagnostic Mémoire Airtel Chatbot ==="

# Sessions actives
echo "1. Sessions actives :"
curl -s http://localhost:8000/sessions | jq '.active_sessions'

# Utilisation mémoire système
echo "2. Utilisation mémoire système :"
ps aux | grep uvicorn | grep -v grep | awk '{print $4}'

# Logs de mémoire
echo "3. Logs de mémoire (dernières 10 lignes) :"
grep -i "memory\|session" backend/logs/app.log | tail -10

# Cache RAG
echo "4. Statistiques cache RAG :"
curl -s http://localhost:8000/performance | jq '.cache_stats'
```

## 🚨 Gestion des erreurs

### 1. Erreurs de session

```python
class SessionError(Exception):
    """Erreur liée à la gestion des sessions."""
    pass

def handle_session_error(session_id: str, error: Exception):
    """Gérer les erreurs de session."""
    logger.error(f"Session error for {session_id}: {error}")
    
    # Tentative de récupération
    try:
        # Supprimer la session problématique
        session_manager.remove_session(session_id)
        logger.info(f"Session {session_id} removed due to error")
    except Exception as e:
        logger.error(f"Failed to remove session {session_id}: {e}")
```

### 2. Erreurs de mémoire

```python
def handle_memory_error(error: Exception):
    """Gérer les erreurs de mémoire."""
    logger.error(f"Memory error: {error}")
    
    # Actions de récupération
    gc.collect()  # Forcer le garbage collection
    session_manager.cleanup_expired_sessions()  # Nettoyer les sessions
    
    # Vérifier l'utilisation mémoire
    memory_usage = monitor_memory_usage()
    if memory_usage > 90:
        logger.critical(f"Critical memory usage: {memory_usage}%")
        # Actions d'urgence (redémarrage, etc.)
```

## 🔧 Optimisations avancées

### 1. Mémoire persistante

```python
import sqlite3
import json

class PersistentMemory:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    state TEXT,
                    created_at TIMESTAMP,
                    last_activity TIMESTAMP
                )
            """)
    
    def save_session(self, session_id: str, state: dict):
        """Sauvegarder une session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?)",
                (session_id, json.dumps(state), datetime.now(), datetime.now())
            )
    
    def load_session(self, session_id: str) -> Optional[dict]:
        """Charger une session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT state FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
```

### 2. Compression de mémoire

```python
import gzip
import pickle

class CompressedMemory:
    def __init__(self):
        self.compression_enabled = True
    
    def compress_state(self, state: dict) -> bytes:
        """Compresser l'état de session."""
        if self.compression_enabled:
            serialized = pickle.dumps(state)
            return gzip.compress(serialized)
        return pickle.dumps(state)
    
    def decompress_state(self, compressed_data: bytes) -> dict:
        """Décompresser l'état de session."""
        if self.compression_enabled:
            serialized = gzip.decompress(compressed_data)
            return pickle.loads(serialized)
        return pickle.loads(compressed_data)
```

## 📈 Métriques et alertes

### 1. Métriques clés

```python
class MemoryMetrics:
    def __init__(self):
        self.session_count = 0
        self.memory_usage = 0
        self.cache_hit_rate = 0
        self.average_session_duration = 0
    
    def update_metrics(self):
        """Mettre à jour les métriques."""
        self.session_count = len(session_manager.sessions)
        self.memory_usage = monitor_memory_usage()
        self.cache_hit_rate = rag_cache.get_hit_rate()
        self.average_session_duration = self.calculate_average_duration()
    
    def get_metrics(self) -> dict:
        """Récupérer toutes les métriques."""
        return {
            "session_count": self.session_count,
            "memory_usage_percent": self.memory_usage,
            "cache_hit_rate": self.cache_hit_rate,
            "average_session_duration_minutes": self.average_session_duration
        }
```

### 2. Alertes automatiques

```python
def check_memory_alerts():
    """Vérifier les alertes mémoire."""
    metrics = memory_metrics.get_metrics()
    
    # Alerte utilisation mémoire
    if metrics["memory_usage_percent"] > 80:
        send_alert("HIGH_MEMORY_USAGE", f"Memory usage: {metrics['memory_usage_percent']}%")
    
    # Alerte nombre de sessions
    if metrics["session_count"] > 100:
        send_alert("HIGH_SESSION_COUNT", f"Active sessions: {metrics['session_count']}")
    
    # Alerte cache inefficace
    if metrics["cache_hit_rate"] < 0.5:
        send_alert("LOW_CACHE_HIT_RATE", f"Cache hit rate: {metrics['cache_hit_rate']}")
```

## 🎯 Bonnes pratiques

### 1. Gestion des sessions
- **Timeout approprié** : 30 minutes par défaut, ajustable selon l'usage
- **Nettoyage automatique** : Suppression des sessions expirées
- **Persistance optionnelle** : Sauvegarde pour les sessions importantes
- **Monitoring actif** : Surveillance des métriques de session

### 2. Optimisation mémoire
- **Troncature intelligente** : Garder les messages les plus récents
- **Cache efficace** : Utiliser le cache RAG pour les requêtes répétées
- **Garbage collection** : Nettoyage automatique de la mémoire
- **Compression** : Compresser les données pour économiser l'espace

### 3. Monitoring
- **Métriques en temps réel** : Surveillance continue des performances
- **Alertes proactives** : Détection précoce des problèmes
- **Logs détaillés** : Traçabilité complète des opérations
- **Diagnostic automatique** : Scripts de diagnostic intégrés

## 🔗 Ressources utiles

- [Système de préchargement](preloading.md)
- [Configuration des performances](../configuration/performance.md)
- [Configuration des timeouts](../configuration/timeouts.md)
- [Guide de debugging](../troubleshooting/debugging.md)
- [Problèmes courants](../troubleshooting/common-issues.md)
