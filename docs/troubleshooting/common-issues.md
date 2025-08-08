# Problèmes Courants - Airtel Chatbot

## 🚨 Erreurs fréquentes et solutions

### 1. Erreurs d'importation

#### "No module named 'src'"
```
ModuleNotFoundError: No module named 'src'
```

**Solutions :**
```bash
# Solution 1 : Ajouter au PYTHONPATH
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Solution 2 : Installer en mode développement
pip install -e .

# Solution 3 : Exécuter depuis le bon répertoire
cd backend
python -m src.cli
```

#### "No module named 'langchain'"
```
ModuleNotFoundError: No module named 'langchain'
```

**Solutions :**
```bash
# Réinstaller les dépendances
pip install -r requirements.txt

# Ou installer manuellement
pip install langchain langchain-google-genai langgraph
```

### 2. Erreurs de configuration

#### "GOOGLE_API_KEY not set"
```
Error: GOOGLE_API_KEY environment variable not set
```

**Solutions :**
```bash
# Vérifier le fichier .env
cat .env | grep GOOGLE_API_KEY

# Définir la variable directement
export GOOGLE_API_KEY=your_key_here

# Ou ajouter dans .env
echo "GOOGLE_API_KEY=your_key_here" >> .env
```

#### "Document not found"
```
FileNotFoundError: Document not found: src/rag/static_document.txt
```

**Solutions :**
```bash
# Vérifier l'existence du fichier
ls -la src/rag/static_document.txt

# Créer le fichier s'il n'existe pas
touch src/rag/static_document.txt

# Ou ajuster le chemin dans .env
echo "DOCUMENT_PATH=./src/rag/static_document.txt" >> .env
```

### 3. Erreurs de port

#### "Port already in use"
```
OSError: [Errno 48] Address already in use
```

**Solutions :**
```bash
# Identifier le processus
lsof -i :8000

# Tuer le processus
kill -9 <PID>

# Ou utiliser un port différent
python -m uvicorn src.api.main:app --port 8001
```

#### "Port 3000 already in use"
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solutions :**
```bash
# Identifier le processus
lsof -i :3000

# Tuer le processus
kill -9 <PID>

# Ou utiliser un port différent
npm run dev -- --port 3001
```

### 4. Erreurs de performance

#### "LLM timeout"
```
Error: LLM request timed out after 20 seconds
```

**Solutions :**
```bash
# Augmenter le timeout dans .env
echo "LLM_TIMEOUT=60" >> .env

# Vérifier la connexion internet
ping google.com

# Réduire la complexité de la requête
```

#### "Response too slow"
```
Warning: Response time exceeds 5 seconds
```

**Solutions :**
```bash
# Activer le cache RAG
echo "RAG_CACHE_ENABLED=true" >> .env

# Optimiser les paramètres
echo "chunk_size=300" >> .env
echo "max_results=2" >> .env

# Vérifier les métriques
curl http://localhost:8000/performance
```

### 5. Erreurs de mémoire

#### "Out of memory"
```
MemoryError: Unable to allocate memory
```

**Solutions :**
```bash
# Réduire la taille des chunks
echo "chunk_size=200" >> .env

# Réduire le nombre de résultats
echo "max_results=1" >> .env

# Redémarrer le serveur
pkill -f uvicorn
python start_server.py
```

#### "Cache full"
```
Warning: Cache size exceeds 80% capacity
```

**Solutions :**
```bash
# Augmenter la taille du cache
echo "cache_max_size=2000" >> .env

# Réduire le TTL
echo "cache_ttl_seconds=1800" >> .env

# Nettoyer le cache
curl -X POST http://localhost:8000/clear-cache
```

### 6. Erreurs de réseau

#### "Connection refused"
```
ConnectionError: Connection refused
```

**Solutions :**
```bash
# Vérifier que le serveur est démarré
ps aux | grep uvicorn

# Redémarrer le serveur
cd backend
python start_server.py

# Vérifier les logs
tail -f logs/app.log
```

#### "CORS error"
```
CORS error: No 'Access-Control-Allow-Origin' header
```

**Solutions :**
```python
# Dans src/api/main.py, ajouter CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7. Erreurs de session

#### "Session expired"
```
Error: Session expired after 30 minutes
```

**Solutions :**
```bash
# Augmenter le timeout de session
echo "SESSION_TIMEOUT_MINUTES=60" >> .env

# Redémarrer le serveur
pkill -f uvicorn
python start_server.py
```

#### "Session not found"
```
Error: Session not found
```

**Solutions :**
```bash
# Vérifier les sessions actives
curl http://localhost:8000/sessions

# Nettoyer les sessions expirées
curl -X POST http://localhost:8000/clear-sessions
```

## 🔧 Outils de diagnostic

### Script de diagnostic
```bash
#!/bin/bash
# diagnostic.sh

echo "=== Diagnostic Airtel Chatbot ==="

# Vérifier les processus
echo "1. Processus en cours :"
ps aux | grep -E "(uvicorn|node)" | grep -v grep

# Vérifier les ports
echo "2. Ports utilisés :"
lsof -i :8000 -i :3000

# Vérifier les variables d'environnement
echo "3. Variables d'environnement :"
env | grep -E "(GOOGLE_API_KEY|LLM_TIMEOUT|RAG_CACHE_ENABLED)"

# Vérifier les fichiers
echo "4. Fichiers critiques :"
ls -la backend/.env
ls -la backend/src/rag/static_document.txt

# Tester l'API
echo "5. Test de l'API :"
curl -s http://localhost:8000/ || echo "API non accessible"

# Vérifier les logs
echo "6. Derniers logs :"
tail -5 backend/logs/app.log 2>/dev/null || echo "Pas de logs trouvés"
```

### Commandes de diagnostic rapide
```bash
# État général du système
curl http://localhost:8000/performance

# Logs en temps réel
tail -f backend/logs/app.log

# Utilisation des ressources
htop

# Test de connectivité
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "test"}'
```

## 📊 Monitoring préventif

### Métriques à surveiller
```bash
# Surveillance continue
watch -n 30 'curl -s http://localhost:8000/performance | jq'

# Alertes automatiques
while true; do
  response_time=$(curl -s http://localhost:8000/performance | jq -r '.response_times.average_seconds')
  if (( $(echo "$response_time > 5" | bc -l) )); then
    echo "ALERTE: Temps de réponse élevé: ${response_time}s"
  fi
  sleep 60
done
```

### Logs à surveiller
```bash
# Erreurs critiques
grep -i "error\|exception\|timeout" backend/logs/app.log

# Performances
grep "response_time\|cache" backend/logs/app.log

# Sessions
grep "session" backend/logs/app.log
```

## 🎯 Prévention

### Checklist de démarrage
- [ ] Variables d'environnement configurées
- [ ] Fichiers de documents présents
- [ ] Ports disponibles
- [ ] Connexion internet active
- [ ] Clé API Google valide

### Maintenance régulière
- [ ] Nettoyer les logs anciens
- [ ] Vérifier l'espace disque
- [ ] Mettre à jour les dépendances
- [ ] Tester les performances
- [ ] Sauvegarder les configurations

## 🔗 Ressources utiles

- [Guide de démarrage rapide](../getting-started.md)
- [Configuration des performances](../configuration/performance.md)
- [Configuration des timeouts](../configuration/timeouts.md)
- [Déploiement local](../deployment/local.md)
- [Logs et debugging](../troubleshooting/debugging.md)
