# Guide Rapide - Optimisations de Performance

## 🚀 Démarrage rapide

### 1. Variables d'environnement recommandées

```bash
# .env
LLM_TIMEOUT=20
RAG_CACHE_ENABLED=true
MAX_CONCURRENT_REQUESTS=10
```

### 2. Démarrer le serveur

```bash
cd backend
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Tester les performances

```bash
# Installer aiohttp si pas déjà fait
pip install aiohttp

# Lancer le test de performance
python test_performance.py
```

## 📊 Surveillance en temps réel

### Endpoint de performance
```bash
curl http://localhost:8000/performance
```

### Logs de performance
Les logs incluent maintenant les temps de réponse :
```
2024-01-15 10:30:15 - Successfully processed chat request for session abc123 in 1.23s
```

## ⚡ Optimisations principales

### 1. Cache RAG
- **Activation** : `RAG_CACHE_ENABLED=true`
- **Taille** : 1000 entrées max
- **TTL** : 1 heure
- **Bénéfice** : Réponses instantanées pour requêtes répétées

### 2. Configuration LLM optimisée
- **Temperature** : 0.1 (plus rapide)
- **Top_p** : 0.8 (plus rapide)
- **Top_k** : 20 (plus rapide)
- **Timeout** : 20s (plus rapide)

### 3. Traitement de documents optimisé
- **Chunks** : 400 caractères (au lieu de 500)
- **Overlap** : 50 caractères (au lieu de 100)
- **Résultats** : 2 documents (au lieu de 3)

### 4. Mémoire réduite
- **Tokens d'historique** : 3000 (au lieu de 4000)
- **Bénéfice** : Traitement plus rapide

## 🎯 Résultats attendus

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Temps de réponse moyen | 3-5s | 1-2s | 60-70% |
| Requêtes répétées | 3-5s | 0.1-0.5s | 90-95% |
| Utilisation mémoire | 100% | 80% | 20% |

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

## 🚨 Dépannage

### Problème : Réponses lentes
1. Vérifier `RAG_CACHE_ENABLED=true`
2. Réduire `LLM_TIMEOUT`
3. Vérifier la connexion internet

### Problème : Cache inefficace
1. Vérifier les logs de cache
2. Augmenter la taille du cache
3. Réduire le TTL

### Problème : Qualité dégradée
1. Augmenter `chunk_size`
2. Augmenter `max_results`
3. Augmenter `temperature`

## 📈 Métriques à surveiller

1. **Temps de réponse moyen** : < 2s
2. **Taux de succès** : > 95%
3. **Taille du cache** : < 80% de la capacité
4. **Utilisation mémoire** : < 80%

## 🎯 Recommandations

1. **Tester** avec `test_performance.py`
2. **Surveiller** l'endpoint `/performance`
3. **Ajuster** selon l'usage réel
4. **Documenter** les changements 