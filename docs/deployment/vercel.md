# Déploiement Vercel - Airtel Chatbot

## 🚀 Vue d'ensemble

Ce guide détaille le déploiement du backend Airtel Chatbot sur Vercel, une plateforme serverless qui offre un déploiement simple et rapide.

## 📋 Prérequis

- Compte Vercel (gratuit)
- Vercel CLI installé
- Projet Git configuré
- Clé API Google configurée

## ⚙️ Configuration

### 1. Fichiers configurés pour Vercel

#### `app.py` - Point d'entrée
```python
# Point d'entrée pour Vercel
from src.api.main import app

# Vercel utilise cette variable par défaut
handler = app
```

#### `vercel.json` - Configuration Vercel
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  }
}
```

#### `src/api/main.py` - Application FastAPI
```python
# Endpoint de santé pour Vercel
@app.get("/")
async def health_check():
    return {"status": "healthy", "service": "airtel-chatbot"}
```

### 2. Variables d'environnement

Dans le dashboard Vercel, configurez les variables suivantes :

```bash
# Obligatoire
GOOGLE_API_KEY=your_google_api_key_here

# Optionnel
MODEL_NAME=gemini-1.5-flash
DOCUMENT_PATH=src/rag/static_document.txt
SESSION_TIMEOUT_MINUTES=30
LLM_TIMEOUT=20
RAG_CACHE_ENABLED=true
```

## 🚀 Déploiement

### Méthode 1 : Vercel CLI (Recommandée)

```bash
# Installer Vercel CLI
npm install -g vercel

# Se connecter à Vercel
vercel login

# Déployer depuis le dossier backend
cd backend
vercel

# Pour la production
vercel --prod
```

### Méthode 2 : Dashboard Vercel

1. Connectez-vous à [vercel.com](https://vercel.com)
2. Cliquez sur "New Project"
3. Importez votre repository Git
4. Configurez les variables d'environnement
5. Déployez

### Méthode 3 : GitHub Integration

1. Connectez votre repository GitHub à Vercel
2. Configurez les variables d'environnement
3. Chaque push sur `main` déclenche un déploiement automatique

## 🔧 Configuration avancée

### Build Commands personnalisées

Dans `vercel.json` :
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ],
  "functions": {
    "app.py": {
      "maxDuration": 30
    }
  }
}
```

### Variables d'environnement par environnement

```bash
# Production
GOOGLE_API_KEY=prod_key_here
LLM_TIMEOUT=30
RAG_CACHE_ENABLED=true

# Preview (staging)
GOOGLE_API_KEY=staging_key_here
LLM_TIMEOUT=60
RAG_CACHE_ENABLED=false
```

## 🌐 Endpoints disponibles

### Endpoints principaux
- **GET `/`** - Health check (pour Vercel)
- **POST `/chat`** - Endpoint de chat
- **GET `/performance`** - Métriques de performance
- **GET `/docs`** - Documentation API (Swagger)

### Exemple d'utilisation
```bash
# Test de santé
curl https://your-app.vercel.app/

# Test de chat
curl -X POST https://your-app.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "Bonjour"}'

# Métriques
curl https://your-app.vercel.app/performance
```

## 📊 Monitoring et logs

### Logs Vercel
```bash
# Voir les logs en temps réel
vercel logs

# Logs d'une fonction spécifique
vercel logs --function=app.py
```

### Métriques de performance
```bash
# Endpoint de métriques
curl https://your-app.vercel.app/performance
```

### Dashboard Vercel
- **Analytics** : Temps de réponse, requêtes
- **Functions** : Logs, erreurs, performance
- **Settings** : Variables d'environnement, domaines

## 🚨 Limitations Vercel

### Contraintes techniques
- **Timeout** : 10s (Hobby), 60s (Pro)
- **Payload** : 4.5MB max
- **Mémoire** : 1024MB max
- **Cold starts** : Délai au premier appel

### Optimisations recommandées
```python
# Réduire la taille des chunks
chunk_size = 300  # Au lieu de 400

# Optimiser les timeouts
LLM_TIMEOUT = 15  # Au lieu de 20

# Activer le cache
RAG_CACHE_ENABLED = True
```

## 🔄 Déploiement continu

### GitHub Actions (optionnel)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

### Variables d'environnement automatiques
```bash
# Dans les secrets GitHub
VERCEL_TOKEN=your_vercel_token
ORG_ID=your_org_id
PROJECT_ID=your_project_id
```

## 🚨 Dépannage

### Erreur "Function timeout"
```
Error: Function execution timed out
```

**Solutions :**
1. Réduire `LLM_TIMEOUT`
2. Optimiser les requêtes
3. Passer au plan Pro (60s timeout)

### Erreur "Payload too large"
```
Error: Payload size exceeds 4.5MB limit
```

**Solutions :**
1. Réduire la taille des documents
2. Optimiser les embeddings
3. Utiliser un cache externe

### Erreur "Cold start"
```
Error: First request takes too long
```

**Solutions :**
1. Activer le cache RAG
2. Optimiser le préchargement
3. Utiliser des fonctions préchauffées

### Erreur "Import module"
```
Error: No module named 'src'
```

**Solutions :**
1. Vérifier `PYTHONPATH` dans `vercel.json`
2. S'assurer que `app.py` importe correctement
3. Vérifier la structure des dossiers

## 📈 Performance

### Métriques à surveiller
- **Temps de réponse** : < 10s (Hobby), < 60s (Pro)
- **Taux de succès** : > 95%
- **Cold starts** : < 5s
- **Mémoire utilisée** : < 1024MB

### Optimisations
```python
# Dans src/config/settings.py
# Optimisations pour Vercel
llm_timeout: int = 15
chunk_size: int = 300
max_results: int = 2
rag_cache_enabled: bool = True
```

## 🔗 Domaines personnalisés

### Configuration DNS
```bash
# Ajouter un domaine personnalisé
vercel domains add your-domain.com

# Configurer les enregistrements DNS
# A @ 76.76.19.19
# CNAME www your-app.vercel.app
```

### SSL automatique
- Vercel fournit automatiquement un certificat SSL
- Redirection HTTP vers HTTPS automatique
- Support des certificats wildcard

## 🎯 Bonnes pratiques

### 1. Développement
- Tester localement avant déploiement
- Utiliser des variables d'environnement
- Optimiser pour les contraintes Vercel

### 2. Déploiement
- Utiliser des branches pour les tests
- Configurer les variables d'environnement
- Surveiller les logs après déploiement

### 3. Production
- Utiliser le plan Pro pour plus de ressources
- Configurer des alertes
- Surveiller les métriques régulièrement

### 4. Sécurité
- Ne pas exposer les clés API
- Utiliser des variables d'environnement
- Configurer les CORS si nécessaire

## 🔗 Liens utiles

- [Documentation Vercel](https://vercel.com/docs)
- [Guide de démarrage rapide](../getting-started.md)
- [Configuration des performances](../configuration/performance.md)
- [Problèmes courants](../troubleshooting/common-issues.md)
