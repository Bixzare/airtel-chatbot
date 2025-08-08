# Guide de démarrage rapide

## 🚀 Installation et configuration

### Prérequis
- Python 3.11+
- Node.js 18+
- Clé API Google (pour Gemini)

### 1. Configuration backend

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

### 2. Configuration frontend

```bash
cd frontend

# Installer les dépendances
npm install
```

### 3. Lancer l'application

**Backend :**
```bash
cd backend

# Méthode recommandée (avec préchargement)
python start_server.py

# Ou méthode classique
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend :**
```bash
cd frontend
npm run dev
```

## 🧪 Tests rapides

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

## 📊 Vérification du bon fonctionnement

### 1. Vérifier les logs backend
```
2024-01-15 10:30:15 - INFO - RAG Agent initialized successfully
2024-01-15 10:30:15 - INFO - Document preloaded: 150 chunks
2024-01-15 10:30:15 - INFO - Cache initialized with 1000 max entries
```

### 2. Vérifier les métriques
```bash
curl http://localhost:8000/performance
```

Réponse attendue :
```json
{
  "response_times": {
    "average_seconds": 1.5,
    "total_requests": 10
  },
  "cache_stats": {
    "size": 5,
    "max_size": 1000
  }
}
```

### 3. Test de conversation
Posez une question simple comme "Quels sont vos forfaits internet ?" et vérifiez que :
- La réponse arrive en moins de 3 secondes
- Le contenu est pertinent
- L'historique est conservé

## 🔧 Configuration avancée

### Optimisations de performance
Voir [Configuration des performances](configuration/performance.md)

### Gestion des timeouts
Voir [Configuration des timeouts](configuration/timeouts.md)

### Système de streaming
Voir [Configuration du streaming](configuration/streaming.md)

## 🚨 Problèmes courants

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
```

### Erreur de port déjà utilisé
```bash
# Changer le port
python -m uvicorn src.api.main:app --port 8001
```

## 📚 Prochaines étapes

1. **Déploiement** : [Déploiement local](deployment/local.md) ou [Déploiement Vercel](deployment/vercel.md)
2. **Optimisation** : [Configuration des performances](configuration/performance.md)
3. **Personnalisation** : [Système RAG](features/rag.md)
4. **Dépannage** : [Problèmes courants](troubleshooting/common-issues.md)
