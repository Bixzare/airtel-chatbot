# Optimisations de Performance - Airtel Chatbot

## 🚀 Vue d'ensemble

Ce document détaille les optimisations de performance mises en place pour réduire les temps de réponse du chatbot de 3-5 secondes à 1-2 secondes.

## ⚡ Optimisations principales

### 1. Configuration LLM optimisée

**Fichier** : `backend/src/agent/rag_agent.py`

| Paramètre | Avant | Après | Impact |
|-----------|-------|-------|--------|
| **Temperature** | 0.2 | 0.1 | Réponses plus rapides et cohérentes |
| **Top_p** | 0.9 | 0.8 | Génération plus rapide |
| **Top_k** | 40 | 20 | Sélection plus rapide |
| **Timeout** | 30s | 20s | Défini par `LLM_TIMEOUT` |

### 2. Optimisation du traitement de documents

**Fichier** : `backend/src/tools/rag_tool.py`

| Paramètre | Avant | Après | Impact |
|-----------|-------|-------|--------|
| **Taille des chunks** | 500 | 400 caractères | Traitement plus rapide |
| **Overlap** | 100 | 50 caractères | Moins de redondance |
| **Nombre de résultats** | 3 | 2 documents | Recherche plus rapide |

### 3. Optimisation de la mémoire

**Fichier** : `backend/src/config/settings.py`

| Paramètre | Avant | Après | Impact |
|-----------|-------|-------|--------|
| **Tokens d'historique** | 4000 | 3000 | Traitement plus rapide |
| **Taille des chunks** | 1000 | 800 caractères | Moins de mémoire |
| **Overlap** | 200 | 100 caractères | Optimisation mémoire |
| **Résultats max** | 5 | 3 documents | Recherche plus rapide |

### 4. Système de cache RAG

**Fichier** : `backend/src/rag/cache.py`

- **Cache en mémoire** pour les requêtes fréquentes
- **TTL** : 1 heure par défaut
- **Taille max** : 1000 entrées
- **Activation** : Contrôlée par `RAG_CACHE_ENABLED`

### 5. Prompt système optimisé

**Fichier** : `backend/src/prompts/system_prompt3.py`

- **Instructions de vitesse** ajoutées
- **Réponses concises** prioritaires
- **Explications inutiles** évitées

## 📊 Variables d'environnement

```bash
# .env
# Timeout LLM (secondes)
LLM_TIMEOUT=20

# Activation du cache RAG
RAG_CACHE_ENABLED=true

# Nombre max de requêtes concurrentes
MAX_CONCURRENT_REQUESTS=10
```

## 🎯 Résultats attendus

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| **Temps de réponse moyen** | 3-5s | 1-2s | 60-70% |
| **Requêtes répétées** | 3-5s | 0.1-0.5s | 90-95% |
| **Utilisation mémoire** | 100% | 80% | 20% |
| **Taille des chunks** | 1000 | 800 caractères | 20% |
| **Résultats RAG** | 5 | 3 documents | 40% |

## 📈 Surveillance

### Endpoint de performance
```bash
curl http://localhost:8000/performance
```

**Réponse** :
```json
{
  "response_times": {
    "average_seconds": 1.5,
    "min_seconds": 0.8,
    "max_seconds": 3.2,
    "total_requests": 50
  },
  "cache_stats": {
    "size": 25,
    "max_size": 1000,
    "ttl_seconds": 3600
  },
  "settings": {
    "llm_timeout": 20,
    "max_history_tokens": 3000,
    "rag_cache_enabled": true
  }
}
```

### Logs de performance
Les logs incluent maintenant les temps de réponse :
```
2024-01-15 10:30:15 - Successfully processed chat request for session abc123 in 1.23s
```

## 🔧 Ajustements possibles

### Pour plus de vitesse (qualité réduite)
```python
# Dans src/config/settings.py
chunk_size: int = 300
max_results: int = 1
max_history_tokens: int = 2000
```

### Pour plus de qualité (vitesse réduite)
```python
# Dans src/config/settings.py
chunk_size: int = 1000
max_results: int = 5
max_history_tokens: int = 4000
```

## 🚨 Points d'attention

### 1. Qualité des réponses
- Les optimisations peuvent affecter la qualité
- Surveiller les métriques de satisfaction
- Ajuster selon les besoins

### 2. Utilisation mémoire
- Le cache consomme de la RAM
- Surveiller l'utilisation mémoire
- Ajuster `cache_max_size` si nécessaire

### 3. Cache invalidation
- Le cache peut contenir des données obsolètes
- Implémenter une stratégie d'invalidation
- Surveiller les métriques de cache

## 🔧 Optimisations supplémentaires possibles

### 1. Cache persistant
- Sauvegarder le cache sur disque
- Restaurer au redémarrage
- Réduire le temps de démarrage

### 2. Pré-calcul des embeddings
- Calculer les embeddings à l'avance
- Sauvegarder dans une base de données
- Éliminer le calcul en temps réel

### 3. Load balancing
- Répartir les requêtes sur plusieurs instances
- Utiliser Redis pour le cache partagé
- Améliorer la scalabilité

### 4. Optimisation du modèle
- Utiliser un modèle plus léger pour certaines tâches
- Modèle spécialisé pour les questions fréquentes
- Réduire la complexité des prompts

## 📋 Métriques à surveiller

1. **Temps de réponse moyen** : < 2s
2. **Taux de succès** : > 95%
3. **Taille du cache** : < 80% de la capacité
4. **Utilisation mémoire** : < 80%

## 🎯 Recommandations

1. **Surveiller** les métriques de performance
2. **Ajuster** les paramètres selon l'usage
3. **Tester** avec différents types de requêtes
4. **Optimiser** progressivement sans perdre en qualité
5. **Documenter** les changements de performance

## 🧪 Tests de performance

### Script de test automatisé
```bash
cd backend
python tests/test_performance.py
```

### Test manuel
```bash
# Test de charge simple
for i in {1..10}; do
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"test$i\", \"message\": \"Test message $i\"}"
done
```

### Surveillance en temps réel
```bash
# Surveiller les logs
tail -f backend/logs/app.log | grep "response_time"

# Surveiller les métriques
watch -n 5 'curl -s http://localhost:8000/performance | jq'
```
