# Déploiement Local - Airtel Chatbot

## 🏠 Configuration locale

### Prérequis
- Python 3.11+
- Node.js 18+
- Git
- Clé API Google (pour Gemini)

### 1. Cloner le projet
```bash
git clone <repository-url>
cd airtel-chatbot
```

### 2. Configuration backend

```bash
cd backend

# Installer les dépendances
pip install -r requirements.txt

# Configuration des variables d'environnement
cp env.example .env
```

Éditer le fichier `.env` :
```bash
# Clé API Google (obligatoire)
GOOGLE_API_KEY=your_google_api_key_here

# Configuration optionnelle
MODEL_NAME=gemini-1.5-flash
DOCUMENT_PATH=src/rag/static_document.txt
SESSION_TIMEOUT_MINUTES=30
LLM_TIMEOUT=20
RAG_CACHE_ENABLED=true
```

### 3. Configuration frontend

```bash
cd frontend

# Installer les dépendances
npm install
```

## 🚀 Lancer l'application

### Méthode 1 : Script optimisé (Recommandée)
```bash
cd backend
python start_server.py
```

### Méthode 2 : Uvicorn direct
```bash
cd backend
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

### Méthode 3 : Fichier principal
```bash
cd backend
python src/api/main.py
```

### Frontend
```bash
cd frontend
npm run dev
```

## 🧪 Tests locaux

### Test du backend
```bash
cd backend

# Test interactif
python -m src.cli --interactive

# Test simple
python -m src.cli "What are Airtel's data plans?"

# Test de performance
python tests/test_performance.py

# Test du préchargement
python tests/test_preloading.py
```

### Test de l'API
```bash
# Test de santé
curl http://localhost:8000/

# Test de chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "Bonjour"}'

# Métriques de performance
curl http://localhost:8000/performance
```

## 🌐 Accès à l'application

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Métriques** : http://localhost:8000/performance

## 🔧 Configuration avancée

### Variables d'environnement supplémentaires
```bash
# Performance
LLM_TIMEOUT=30
RAG_CACHE_ENABLED=true
MAX_CONCURRENT_REQUESTS=10

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Développement
DEBUG=true
RELOAD=true
```

### Configuration des ports
```bash
# Backend sur un port différent
python -m uvicorn src.api.main:app --port 8001

# Frontend sur un port différent
npm run dev -- --port 3001
```

### Configuration du proxy (si nécessaire)
```bash
# Avec nginx
location /api/ {
    proxy_pass http://localhost:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 🚨 Dépannage local

### Erreur "No module named 'src'"
```bash
# Solution : Ajouter le backend au PYTHONPATH
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Erreur "GOOGLE_API_KEY not set"
```bash
# Vérifier le fichier .env
cat .env | grep GOOGLE_API_KEY

# Ou définir la variable directement
export GOOGLE_API_KEY=your_key_here
```

### Erreur de port déjà utilisé
```bash
# Vérifier les processus
lsof -i :8000
lsof -i :3000

# Tuer le processus
kill -9 <PID>

# Ou changer le port
python -m uvicorn src.api.main:app --port 8001
```

### Erreur de dépendances
```bash
# Réinstaller les dépendances
cd backend
pip uninstall -r requirements.txt
pip install -r requirements.txt

# Ou utiliser un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 📊 Monitoring local

### Logs en temps réel
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs (dans le terminal où npm run dev est lancé)
```

### Métriques de performance
```bash
# Surveillance continue
watch -n 5 'curl -s http://localhost:8000/performance | jq'

# Test de charge simple
for i in {1..10}; do
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"test$i\", \"message\": \"Test $i\"}"
done
```

### Utilisation des ressources
```bash
# CPU et mémoire
htop

# Disque
df -h

# Réseau
netstat -tulpn | grep :8000
```

## 🔄 Développement

### Mode développement avec rechargement automatique
```bash
# Backend avec rechargement
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

# Frontend avec rechargement (déjà activé par défaut)
npm run dev
```

### Debugging
```bash
# Backend avec debug
python -m uvicorn src.api.main:app --reload --log-level debug

# Frontend avec debug
npm run dev -- --debug
```

### Tests unitaires
```bash
cd backend
python -m pytest tests/

# Avec couverture
python -m pytest tests/ --cov=src
```

## 📝 Logs et debugging

### Format des logs
```
2024-01-15 10:30:15 - INFO - Server started on http://127.0.0.1:8000
2024-01-15 10:30:15 - INFO - Document preloaded: 150 chunks
2024-01-15 10:30:16 - INFO - Chat request received for session abc123
2024-01-15 10:30:17 - INFO - Response sent in 1.2 seconds
```

### Debugging des erreurs
```bash
# Logs d'erreur
grep "ERROR" backend/logs/app.log

# Logs de performance
grep "response_time" backend/logs/app.log

# Logs de session
grep "session" backend/logs/app.log
```

## 🎯 Bonnes pratiques

### 1. Environnement de développement
- Utiliser un environnement virtuel Python
- Séparer les configurations dev/prod
- Utiliser des variables d'environnement

### 2. Monitoring
- Surveiller les logs en temps réel
- Tester les performances régulièrement
- Vérifier l'utilisation des ressources

### 3. Sécurité
- Ne pas commiter les clés API
- Utiliser des ports non-standard en dev
- Limiter l'accès réseau

### 4. Performance
- Activer le cache RAG
- Optimiser les timeouts
- Surveiller les métriques

## 🔗 Liens utiles

- [Guide de démarrage rapide](../getting-started.md)
- [Configuration des performances](../configuration/performance.md)
- [Configuration des timeouts](../configuration/timeouts.md)
- [Problèmes courants](../troubleshooting/common-issues.md)
