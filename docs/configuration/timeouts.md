# Guide de Configuration des Timeouts - Airtel Chatbot

## 🕐 Types de Timeouts

### 1. **LLM Timeout** (Timeout du modèle de langage)
- **Fichier** : `backend/src/config/settings.py`
- **Variable** : `LLM_TIMEOUT`
- **Défaut** : 20 secondes
- **Usage** : Contrôle le temps d'attente pour les réponses du modèle Gemini

### 2. **Session Timeout** (Timeout de session)
- **Fichier** : `backend/src/config/settings.py`
- **Variable** : `SESSION_TIMEOUT_MINUTES`
- **Défaut** : 30 minutes
- **Usage** : Contrôle la durée de vie des sessions utilisateur

### 3. **HTTP Timeout** (Timeout des requêtes HTTP)
- **Fichier** : `backend/src/api/main.py`
- **Variable** : `HTTP_TIMEOUT`
- **Défaut** : 30 secondes
- **Usage** : Contrôle le timeout des requêtes HTTP

## ⚙️ Configuration

### Méthode 1 : Variables d'environnement (Recommandée)

Créez un fichier `.env` dans le dossier `backend/` :

```bash
# Timeouts
LLM_TIMEOUT=60                    # 60 secondes pour le LLM
SESSION_TIMEOUT_MINUTES=60        # 60 minutes pour les sessions
HTTP_TIMEOUT=45                   # 45 secondes pour les requêtes HTTP

# Autres configurations
RAG_CACHE_ENABLED=true
MAX_CONCURRENT_REQUESTS=10
GOOGLE_API_KEY=your_api_key_here
```

### Méthode 2 : Modification directe du code

Dans `backend/src/config/settings.py` :

```python
# Performance optimization settings
llm_timeout: int = int(os.environ.get("LLM_TIMEOUT", 60))  # Augmenté à 60s
session_timeout_minutes: int = int(os.environ.get("SESSION_TIMEOUT_MINUTES", 60))
```

Dans `backend/src/api/main.py` :

```python
# HTTP timeout settings
HTTP_TIMEOUT = int(os.environ.get("HTTP_TIMEOUT", 45))  # Augmenté à 45s
```

## 📊 Recommandations par usage

### Pour le développement
```bash
LLM_TIMEOUT=30
SESSION_TIMEOUT_MINUTES=30
HTTP_TIMEOUT=20
```

### Pour la production avec trafic modéré
```bash
LLM_TIMEOUT=45
SESSION_TIMEOUT_MINUTES=60
HTTP_TIMEOUT=30
```

### Pour la production avec trafic élevé
```bash
LLM_TIMEOUT=60
SESSION_TIMEOUT_MINUTES=120
HTTP_TIMEOUT=45
```

### Pour les réponses complexes/longues
```bash
LLM_TIMEOUT=120
SESSION_TIMEOUT_MINUTES=60
HTTP_TIMEOUT=90
```

## 🔍 Vérification des timeouts

### 1. Vérifier les timeouts actuels
```bash
curl http://localhost:8000/performance
```

### 2. Tester avec un timeout spécifique
```bash
# Test avec curl
curl --max-time 60 http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "Bonjour"}'
```

### 3. Surveiller les logs de timeout
```bash
# Filtrer les logs de timeout
tail -f backend/logs/app.log | grep -i timeout
```

## 🚨 Gestion des erreurs de timeout

### Erreur LLM Timeout
```
Error: LLM request timed out after 20 seconds
```

**Solutions :**
1. Augmenter `LLM_TIMEOUT` dans `.env`
2. Vérifier la connexion internet
3. Réduire la complexité de la requête

### Erreur Session Timeout
```
Error: Session expired after 30 minutes
```

**Solutions :**
1. Augmenter `SESSION_TIMEOUT_MINUTES`
2. Implémenter un refresh automatique
3. Sauvegarder l'état de la conversation

### Erreur HTTP Timeout
```
Error: HTTP request timed out after 30 seconds
```

**Solutions :**
1. Augmenter `HTTP_TIMEOUT`
2. Optimiser les requêtes
3. Implémenter un retry automatique

## 📈 Monitoring des timeouts

### Métriques à surveiller
```bash
# Endpoint de performance
curl http://localhost:8000/performance | jq '.timeouts'

# Logs de timeout
grep -c "timeout" backend/logs/app.log

# Statistiques des sessions
curl http://localhost:8000/sessions | jq '.active_sessions'
```

### Alertes recommandées
- **LLM Timeout > 50%** : Augmenter le timeout ou optimiser
- **Session Timeout > 10%** : Réduire la durée ou améliorer l'UX
- **HTTP Timeout > 20%** : Optimiser les requêtes

## 🔧 Optimisations avancées

### 1. Timeout adaptatif
```python
# Ajuster le timeout selon la complexité de la requête
def get_adaptive_timeout(query_complexity):
    base_timeout = 20
    if query_complexity == "high":
        return base_timeout * 2
    elif query_complexity == "low":
        return base_timeout * 0.5
    return base_timeout
```

### 2. Retry automatique
```python
# Implémenter un système de retry
def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except TimeoutError:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

### 3. Circuit breaker
```python
# Protéger contre les cascades de timeout
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
```

## 📝 Logs et debugging

### Format des logs de timeout
```
2024-01-15 10:30:15 - WARNING - LLM timeout after 20s for session abc123
2024-01-15 10:30:16 - INFO - Retrying request for session abc123
2024-01-15 10:30:18 - ERROR - Max retries reached for session abc123
```

### Debugging des timeouts
```bash
# Analyser les patterns de timeout
grep "timeout" backend/logs/app.log | awk '{print $1, $2}' | sort | uniq -c

# Identifier les sessions problématiques
grep "timeout" backend/logs/app.log | grep -o "session [a-zA-Z0-9]*" | sort | uniq -c
```

## 🎯 Recommandations finales

1. **Commencer conservateur** : Utiliser des timeouts élevés en développement
2. **Optimiser progressivement** : Réduire les timeouts selon les métriques
3. **Surveiller activement** : Mettre en place des alertes
4. **Documenter les changements** : Noter l'impact des modifications
5. **Tester en charge** : Valider les timeouts sous stress
