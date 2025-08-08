# Airtel Chatbot - Documentation

Un chatbot RAG (Retrieval-Augmented Generation) production-ready utilisant LangGraph, LangChain, Google embeddings et un système d'outils extensible.

## 🚀 Vue d'ensemble

Le chatbot Airtel Niger offre :
- **Agent RAG intelligent** avec appel d'outils (LangGraph)
- **Recherche vectorielle** avec Google text-embedding-004 et FAISS
- **Mémoire conversationnelle** persistante
- **API FastAPI** avec streaming
- **Système de cache** optimisé
- **Architecture modulaire** et extensible

## 📚 Table des matières

### 🏁 Démarrage
- [Guide de démarrage rapide](getting-started.md) - Installation et première utilisation
- [Déploiement local](deployment/local.md) - Configuration locale
- [Déploiement Vercel](deployment/vercel.md) - Déploiement sur Vercel

### ⚙️ Configuration
- [Optimisations de performance](configuration/performance.md) - Paramètres et optimisations
- [Configuration des timeouts](configuration/timeouts.md) - Gestion des délais d'attente
- [Configuration du streaming](configuration/streaming.md) - Activation/désactivation du streaming

### 🔧 Fonctionnalités
- [Système de préchargement](features/preloading.md) - Chargement optimisé des documents
- [Architecture mémoire](features/memory.md) - Gestion de la mémoire conversationnelle
- [Système RAG](features/rag.md) - Recherche et génération augmentée

### 🛠️ Dépannage
- [Problèmes courants](troubleshooting/common-issues.md) - Solutions aux erreurs fréquentes
- [Guide de débogage](troubleshooting/debugging.md) - Techniques de débogage

## 🎯 Quick Start

```bash
# 1. Cloner le projet
git clone <repository-url>
cd airtel-chatbot

# 2. Configuration backend
cd backend
pip install -r requirements.txt
cp env.example .env
# Éditer .env avec vos clés API

# 3. Lancer le serveur
python start_server.py

# 4. Configuration frontend
cd ../frontend
npm install
npm run dev
```

## 📊 Architecture

```
airtel-chatbot/
├── backend/                 # API FastAPI avec RAG
│   ├── src/
│   │   ├── agent/          # Agent LangGraph
│   │   ├── rag/            # Système RAG
│   │   ├── tools/          # Outils extensibles
│   │   └── api/            # Endpoints FastAPI
│   └── tests/              # Tests automatisés
├── frontend/               # Interface Next.js
│   ├── app/               # Pages et API routes
│   └── components/        # Composants React
└── docs/                  # Documentation (ce dossier)
```

## 🔗 Liens utiles

- **Backend API** : http://localhost:8000
- **Frontend** : http://localhost:3000
- **Documentation API** : http://localhost:8000/docs
- **Métriques de performance** : http://localhost:8000/performance

## 📝 Contribution

Pour contribuer à la documentation :
1. Modifiez les fichiers dans le dossier `docs/`
2. Mettez à jour cette table des matières si nécessaire
3. Testez les liens et la cohérence

## 🆘 Support

En cas de problème :
1. Consultez le [guide de dépannage](troubleshooting/common-issues.md)
2. Vérifiez les [logs de performance](configuration/performance.md)
3. Testez avec les [scripts de test](../backend/tests/)
