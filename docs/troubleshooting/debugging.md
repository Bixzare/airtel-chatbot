# Guide de Debugging - Airtel Chatbot

## 🔍 Techniques de debugging

### 1. Logs structurés

#### Format des logs
```
2024-01-15 10:30:15 - INFO - Server started on http://127.0.0.1:8000
2024-01-15 10:30:16 - INFO - Document preloaded: 150 chunks
2024-01-15 10:30:17 - INFO - Chat request received for session abc123
2024-01-15 10:30:18 - INFO - Response sent in 1.2 seconds
2024-01-15 10:30:19 - ERROR - LLM timeout after 20s
2024-01-15 10:30:20 - WARNING - Cache miss for query: "forfaits"
```

#### Niveaux de log
- **DEBUG** : Informations détaillées pour le développement
- **INFO** : Informations générales sur le fonctionnement
- **WARNING** : Situations anormales mais non critiques
- **ERROR** : Erreurs qui empêchent le bon fonctionnement
- **CRITICAL** : Erreurs critiques nécessitant une intervention

### 2. Surveillance en temps réel

#### Logs backend
```bash
# Logs en temps réel
tail -f backend/logs/app.log

# Filtrer par niveau
tail -f backend/logs/app.log | grep "ERROR\|WARNING"

# Filtrer par session
tail -f backend/logs/app.log | grep "session abc123"

# Filtrer par type d'événement
tail -f backend/logs/app.log | grep "response_time\|cache\|timeout"
```

#### Logs frontend
```bash
# Logs Next.js (dans le terminal où npm run dev est lancé)
# Les logs apparaissent automatiquement dans la console

# Logs du navigateur
# Ouvrir les DevTools (F12) > Console
```

### 3. Métriques de performance

#### Endpoint de métriques
```bash
# Métriques générales
curl http://localhost:8000/performance

# Métriques détaillées avec jq
curl -s http://localhost:8000/performance | jq '.'

# Surveillance continue
watch -n 5 'curl -s http://localhost:8000/performance | jq ".response_times"'
```

#### Métriques système
```bash
# Utilisation CPU et mémoire
htop

# Utilisation disque
df -h

# Processus en cours
ps aux | grep -E "(uvicorn|node)" | grep -v grep

# Ports utilisés
lsof -i :8000 -i :3000
```

## 🛠️ Outils de debugging

### 1. Script de diagnostic automatique

```bash
#!/bin/bash
# debug.sh

echo "=== Diagnostic Airtel Chatbot ==="
echo "Date: $(date)"
echo ""

# 1. État des processus
echo "1. Processus en cours :"
ps aux | grep -E "(uvicorn|node)" | grep -v grep || echo "Aucun processus trouvé"
echo ""

# 2. Ports utilisés
echo "2. Ports utilisés :"
lsof -i :8000 -i :3000 || echo "Aucun port utilisé"
echo ""

# 3. Variables d'environnement
echo "3. Variables critiques :"
env | grep -E "(GOOGLE_API_KEY|LLM_TIMEOUT|RAG_CACHE_ENABLED)" || echo "Variables non définies"
echo ""

# 4. Fichiers critiques
echo "4. Fichiers critiques :"
ls -la backend/.env 2>/dev/null || echo ".env non trouvé"
ls -la backend/src/rag/static_document.txt 2>/dev/null || echo "Document non trouvé"
echo ""

# 5. Test de l'API
echo "5. Test de l'API :"
curl -s http://localhost:8000/ 2>/dev/null | jq '.' || echo "API non accessible"
echo ""

# 6. Derniers logs
echo "6. Derniers logs (5 lignes) :"
tail -5 backend/logs/app.log 2>/dev/null || echo "Pas de logs trouvés"
echo ""

# 7. Métriques de performance
echo "7. Métriques de performance :"
curl -s http://localhost:8000/performance 2>/dev/null | jq '.' || echo "Métriques non accessibles"
echo ""

echo "=== Diagnostic terminé ==="
```

### 2. Debugging interactif

#### Debugging Python
```python
# Dans le code, ajouter des points d'arrêt
import pdb; pdb.set_trace()

# Ou utiliser ipdb pour une meilleure expérience
import ipdb; ipdb.set_trace()

# Debugging avec logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_function():
    logger.debug("Variable x = %s", x)
    logger.info("Fonction appelée avec paramètres: %s", params)
```

#### Debugging JavaScript/TypeScript
```typescript
// Console.log pour debugging
console.log('Variable:', variable);
console.table(arrayOfObjects);

// Debugger statement
debugger;

// Logging structuré
console.group('Section de debug');
console.log('Info 1');
console.log('Info 2');
console.groupEnd();
```

### 3. Profiling et performance

#### Profiling Python
```bash
# Profiling avec cProfile
python -m cProfile -o profile.stats start_server.py

# Analyser les résultats
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(10)"
```

#### Profiling Node.js
```bash
# Profiling avec --inspect
node --inspect npm run dev

# Ou avec --prof
node --prof npm run dev
```

## 🔧 Debugging spécifique

### 1. Debugging des imports

#### Problème "No module named 'src'"
```bash
# Vérifier le PYTHONPATH
echo $PYTHONPATH

# Ajouter le backend au PYTHONPATH
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Vérifier la structure
tree src/ || find src/ -type f -name "*.py"
```

#### Problème de dépendances
```bash
# Lister les packages installés
pip list | grep -E "(langchain|fastapi|uvicorn)"

# Vérifier les conflits
pip check

# Réinstaller proprement
pip uninstall -r requirements.txt
pip install -r requirements.txt
```

### 2. Debugging des timeouts

#### Analyser les patterns de timeout
```bash
# Extraire les timeouts des logs
grep "timeout" backend/logs/app.log | awk '{print $1, $2, $NF}' | sort

# Analyser par session
grep "timeout" backend/logs/app.log | grep -o "session [a-zA-Z0-9]*" | sort | uniq -c

# Analyser par heure
grep "timeout" backend/logs/app.log | awk '{print $1, $2}' | sort | uniq -c
```

#### Debugging des timeouts LLM
```python
# Ajouter des logs détaillés
import time

def call_llm(prompt):
    start_time = time.time()
    logger.info(f"LLM call started at {start_time}")
    
    try:
        response = llm.invoke(prompt)
        end_time = time.time()
        logger.info(f"LLM call completed in {end_time - start_time:.2f}s")
        return response
    except Exception as e:
        end_time = time.time()
        logger.error(f"LLM call failed after {end_time - start_time:.2f}s: {e}")
        raise
```

### 3. Debugging du cache

#### Analyser l'efficacité du cache
```bash
# Extraire les statistiques de cache
grep "cache" backend/logs/app.log | grep -E "(hit|miss)" | tail -20

# Calculer le taux de hit
cache_hits=$(grep "cache hit" backend/logs/app.log | wc -l)
cache_misses=$(grep "cache miss" backend/logs/app.log | wc -l)
total=$((cache_hits + cache_misses))
hit_rate=$(echo "scale=2; $cache_hits / $total * 100" | bc)
echo "Cache hit rate: ${hit_rate}%"
```

#### Debugging du cache RAG
```python
# Ajouter des logs détaillés pour le cache
def get_cached_result(query):
    if self.cache:
        cached = self.cache.get(query)
        if cached:
            logger.debug(f"Cache HIT for query: {query[:50]}...")
            return cached
        else:
            logger.debug(f"Cache MISS for query: {query[:50]}...")
    return None
```

### 4. Debugging des sessions

#### Analyser les sessions
```bash
# Lister les sessions actives
curl -s http://localhost:8000/sessions | jq '.'

# Analyser les sessions dans les logs
grep "session" backend/logs/app.log | grep -o "session [a-zA-Z0-9]*" | sort | uniq -c

# Identifier les sessions problématiques
grep "ERROR\|WARNING" backend/logs/app.log | grep "session" | tail -10
```

## 📊 Monitoring avancé

### 1. Alertes automatiques

#### Script de surveillance
```bash
#!/bin/bash
# monitor.sh

while true; do
    # Vérifier la réponse de l'API
    response=$(curl -s -w "%{http_code}" http://localhost:8000/ -o /dev/null)
    
    if [ "$response" != "200" ]; then
        echo "ALERTE: API non accessible (HTTP $response)"
        # Envoyer une notification (email, Slack, etc.)
    fi
    
    # Vérifier les temps de réponse
    avg_time=$(curl -s http://localhost:8000/performance | jq -r '.response_times.average_seconds')
    
    if (( $(echo "$avg_time > 5" | bc -l) )); then
        echo "ALERTE: Temps de réponse élevé: ${avg_time}s"
    fi
    
    # Vérifier l'utilisation mémoire
    memory_usage=$(ps aux | grep uvicorn | grep -v grep | awk '{print $4}' | head -1)
    
    if (( $(echo "$memory_usage > 80" | bc -l) )); then
        echo "ALERTE: Utilisation mémoire élevée: ${memory_usage}%"
    fi
    
    sleep 60
done
```

### 2. Logs centralisés

#### Configuration de logging avancée
```python
# Dans src/config/logging.py
import logging
import logging.handlers
import os

def setup_logging():
    # Créer le dossier de logs
    os.makedirs('logs', exist_ok=True)
    
    # Configuration du logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Handler pour fichier avec rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
```

## 🎯 Bonnes pratiques

### 1. Logging
- **Utiliser des niveaux appropriés** : DEBUG pour le développement, INFO pour la production
- **Logs structurés** : Inclure des métadonnées (session_id, user_id, etc.)
- **Rotation des logs** : Éviter que les fichiers deviennent trop gros
- **Sensibilisation** : Ne pas logger d'informations sensibles

### 2. Monitoring
- **Métriques clés** : Temps de réponse, taux d'erreur, utilisation ressources
- **Alertes proactives** : Détecter les problèmes avant qu'ils n'affectent les utilisateurs
- **Dashboards** : Visualiser les métriques en temps réel
- **Rétention** : Conserver les logs et métriques pour analyse

### 3. Debugging
- **Reproduire le problème** : Créer un cas de test minimal
- **Isoler les composants** : Tester chaque partie séparément
- **Documenter les solutions** : Noter les problèmes et leurs résolutions
- **Outils appropriés** : Utiliser les bons outils pour chaque type de problème

## 🔗 Ressources utiles

- [Problèmes courants](common-issues.md)
- [Configuration des performances](../configuration/performance.md)
- [Configuration des timeouts](../configuration/timeouts.md)
- [Déploiement local](../deployment/local.md)
- [Guide de démarrage rapide](../getting-started.md)
